# Django Grades

> [!WARNING]
> **ARCHIVED — superseded by [`Canusia/package-grades`](https://github.com/Canusia/package-grades).**
>
> This repo was the first cut of extracting the grades app out of the MyCE host
> tree. `package-grades` (the `myce_grades` distribution, app label `grades`)
> replaced it and is a strict superset: every view, URL, form, setting, report,
> management command, template, and static file here also exists there, plus
> grading periods and interim marks (`models.py` + migrations), the CE
> grading-period admin and HS-admin period entry, a `services/` layer
> (`gating`, `periods`, `reminders`, `period_reminders`, `roster`, `transcript`,
> `window`), roster-confirmation gating, the real `grade_status_submitted`
> instructor email, and a test suite. `utils.py` here lives on as
> `grades/services/window.py` there (`grades_page_header_for_instructor` →
> `page_header_for_instructor`).
>
> No tenant deployment installs this package. Do not add features or fix bugs
> here — send them to `package-grades` instead.

A Django app for managing student grades in MyCE (My Community Education) platform.

## Features

- Grade submission interface for instructors
- Grade viewing for students
- Unofficial transcript generation (PDF)
- Configurable grade scales and GPA points
- Grade submission window management
- Email notifications for grades due and submitted
- Grade distribution reports by high school, course, and demographics

## Installation

### Via pip from GitHub
```bash
pip install git+https://github.com/Canusia/package_django_grades.git
```

### Via Git Submodule (Development)
```bash
git submodule add https://github.com/Canusia/package_django_grades.git django_grades
pip install -e ./django_grades
```

## Configuration

### 1. Add to INSTALLED_APPS
```python
# Production (pip install)
INSTALLED_APPS += ['django_grades.apps.GradesConfig']

# Development (submodule)
INSTALLED_APPS += ['django_grades.django_grades.apps.DevGradesConfig']
```

### 2. Include URLs
```python
# Production
path('instructor/grades/', include('django_grades.urls.instructor')),
path('student/grades/', include('django_grades.urls.student')),

# Development
path('instructor/grades/', include('django_grades.django_grades.urls.instructor')),
path('student/grades/', include('django_grades.django_grades.urls.student')),
```

### 3. Static Files
```python
STATICFILES_DIRS += [
    os.path.join(get_package_path("django_grades"), 'staticfiles')
]
```

### 4. Run Migrations
```bash
python manage.py migrate
```

### 5. Register Settings and Reports
```bash
python manage.py register_settings
python manage.py register_reports
```

### 6. Add Required Student Utilities

The student views require two utilities in your `student` app. Create these files if they don't exist:

**student/views/decorators.py:**
```python
"""
Decorators for student portal views.
"""
import functools

from django.shortcuts import redirect
from django.contrib import messages

from cis.utils import registration_terms as get_registration_terms


def verify_account_complete(view_func):
    """
    Decorator that restricts access to users who have completed account verification.

    Checks:
    1. User has a usable password set
    2. User has a PSID assigned
    3. FERPA form is completed for current registration terms
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect('/')

        student = request.user.student
        if not student.user.has_usable_password() or student.user.psid in ['', None]:
            return redirect('student:complete_signup', student_id=student.id)

        registration_terms = get_registration_terms()
        regis_terms = list(registration_terms.values_list('code', flat=True))

        if student.meta.get('ferpa_completed_for', '') != regis_terms:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Please review this information',
                'list-group-item-warning'
            )
            return redirect('student:ferpa')

        return view_func(request, *args, **kwargs)
    return wrapper
```

**student/views/utils.py:**
```python
"""
Utility functions for student portal views.
"""


def get_current_student(request):
    """
    Get the Student object for the currently authenticated user.
    """
    if request.user.is_anonymous:
        return None

    try:
        return request.user.student
    except AttributeError:
        return None
```

> **Note:** Fallback implementations are included in django_grades, but for full functionality (FERPA checks, PSID validation), add the complete implementations above.

### 7. Add Student Model Method for Transcript Generation

Add the `generate_unofficial_transcript` method to your `Student` model (e.g., `cis/models/student.py`):

```python
def generate_unofficial_transcript(self, request=None):
    """
    Generate an unofficial transcript PDF for the student.
    """
    import pdfkit
    from django.conf import settings
    from django.template import Context, Template
    from django.template.loader import get_template
    from django.http import HttpResponse
    from datetime import datetime
    from cis.models.section import StudentRegistration

    # Import settings based on DEBUG mode
    if settings.DEBUG:
        from django_grades.django_grades.settings.class_section_grades import class_section_grades
    else:
        from django_grades.settings.class_section_grades import class_section_grades

    base_template = 'student/transcript.html'
    template = get_template(base_template)

    template_settings = class_section_grades.from_db()

    student = self
    student_name = f"{student.user.first_name} {student.user.last_name}"
    student_id = student.suid or student.user.psid or ''
    highschool_name = student.highschool.name if student.highschool else ''
    generated_date = datetime.now().strftime('%B %d, %Y at %I:%M %p')

    student_context = Context({
        'student_name': student_name,
        'student_id': student_id,
        'highschool': highschool_name,
        'generated_date': generated_date,
    })

    header_template = Template(template_settings.get('transcript_template_header', ''))
    footer_template = Template(template_settings.get('transcript_template_footer', ''))
    table_header_template = Template(template_settings.get('transcript_table_header', ''))
    row_template = Template(template_settings.get('transcript_row_template', ''))

    header_html = header_template.render(student_context)
    footer_html = footer_template.render(student_context)
    table_header_html = table_header_template.render(Context({}))

    transcript_statuses = template_settings.get('transcript_registration_status', ['registered'])

    registrations = StudentRegistration.objects.filter(
        student=student,
        status__in=transcript_statuses
    ).select_related(
        'class_section', 'class_section__term', 'class_section__course',
        'class_section__teacher', 'class_section__teacher__user'
    ).order_by('-class_section__term__code', 'class_section__course__name')

    rows = []
    for reg in registrations:
        teacher_name = ''
        if reg.class_section.teacher and reg.class_section.teacher.user:
            teacher = reg.class_section.teacher.user
            teacher_name = f"{teacher.first_name} {teacher.last_name}"

        row_context = Context({
            'term': str(reg.class_section.term) if reg.class_section.term else '',
            'course_name': reg.class_section.course.name if reg.class_section.course else '',
            'course_title': reg.class_section.course.title if reg.class_section.course else '',
            'teacher': teacher_name,
            'credit_hours': reg.class_section.course.credit_hours if reg.class_section.course else '',
            'grade': reg.submitted_grade or '',
        })
        rows.append(row_template.render(row_context))

    rows_html = '\n'.join(rows)

    html = template.render({
        'header': header_html,
        'table_header': table_header_html,
        'rows': rows_html,
        'footer': footer_html,
    })

    if request and request.GET.get('mode') == 'page':
        return HttpResponse(html)

    options = {
        'page-size': 'Letter',
        'margin-top': '0.5in',
        'margin-right': '0.5in',
        'margin-bottom': '0.5in',
        'margin-left': '0.5in',
    }
    pdf = pdfkit.from_string(html, False, options)

    return pdf
```

### 8. Add Transcript Template

Create `student/templates/student/transcript.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Unofficial Transcript</title>
    <style>
        body { font-family: Arial, sans-serif; font-size: 12px; line-height: 1.4; color: #333; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f5f5f5; }
        .text-muted { color: #666; }
        .text-center { text-align: center; }
        .row { display: flex; flex-wrap: wrap; }
        .col-6 { width: 50%; }
        .col-8 { width: 66.666%; }
        .col-12 { width: 100%; }
        hr { border: 0; border-top: 1px solid #ddd; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        {{ header|safe }}
        <table>
            <thead>{{ table_header|safe }}</thead>
            <tbody>{{ rows|safe }}</tbody>
        </table>
        {{ footer|safe }}
    </div>
</body>
</html>
```

### 9. Add Student Base Templates

Create `student/templates/student/base_student.html`:

```html
{% extends "student/logged-base.html" %}

{% load static %}
{% load templatehelpers %}
{% load crispy_forms_tags %}

{% block body %}
<link rel="stylesheet" href="{% static 'student/css/student.css' %}">
{% block extra_css %}{% endblock %}

<main>
    {% block page_header %}
    {{intro|safe}}
    {% include "student/partials/_breadcrumb.html" with page_name=page_name %}
    {% endblock %}

    <div class="row">
        <div class="col-12">
            {% block messages %}
            {% include "cis/messages.html" %}
            {% endblock %}

            {% block content %}
            {% endblock %}
        </div>
    </div>
</main>
{% endblock %}
```

Create `student/templates/student/partials/_breadcrumb.html`:

```html
<nav aria-label="breadcrumb">
    <ol class="breadcrumb">
        <li class="breadcrumb-item"><a href="{% url 'student:dashboard' %}">Home</a></li>
        {% if parent_page %}
        <li class="breadcrumb-item"><a href="{{ parent_url }}">{{ parent_page }}</a></li>
        {% endif %}
        <li class="breadcrumb-item active" aria-current="page">{{ page_name }}</li>
    </ol>
</nav>
```

### 10. Add Instructor Base Templates

Create `instructor/templates/instructor/base_instructor.html`:

```html
{% extends "cis/logged-base.html" %}

{% load static %}
{% load templatehelpers %}

{% block body %}
{% block extra_css %}{% endblock %}

<main>
    {% block page_header %}
    {{intro|safe}}
    {% include "instructor/partials/_breadcrumb.html" with page_name=page_name %}
    {% endblock %}

    <div class="row">
        <div class="col-12">
            {% block messages %}
            {% include "cis/messages.html" %}
            {% endblock %}

            {% block content %}
            {% endblock %}
        </div>
    </div>
</main>
{% endblock %}
```

Create `instructor/templates/instructor/partials/_breadcrumb.html`:

```html
<nav aria-label="breadcrumb">
    <ol class="breadcrumb">
        <li class="breadcrumb-item"><a href="{% url 'instructor:dashboard' %}">Home</a></li>
        {% if parent_page %}
        <li class="breadcrumb-item"><a href="{{ parent_url }}">{{ parent_page }}</a></li>
        {% endif %}
        <li class="breadcrumb-item active" aria-current="page">{{ page_name }}</li>
    </ol>
</nav>
```

### 11. Add Grades Tab to Class Section Admin

To display grades in the CE admin class section view, add the following to `cis/templates/cis/sections/index.html`:

In the tab navigation (inside `<ul class="nav nav-tabs">`):
```html
<li class="nav-item">
    <a class="nav-link" data-toggle="tab" href="#grades">Grades</a>
</li>
```

In the tab content (inside `<div class="tab-content">`):
```html
<div class="tab-pane" id="grades">
    {% include "grades/partials/_sections_grades_tab.html" %}
</div>
```

## Usage

### Instructor Portal
- `/instructor/grades/` - View classes with pending grades
- `/instructor/grades/class_section/<uuid>` - Submit grades for a class

### Student Portal
- `/student/grades/` - View grades
- `/student/grades/download/` - Download unofficial transcript

## Management Commands

```bash
# Send grade reminder emails to instructors with pending grades
python manage.py notify_grades_pending
```

## Reports

Three reports are available in the CE portal:
- **Grade Distribution by High School** - Analyze success rates and DFW rates by school
- **Grade Distribution by Course** - Analyze grade distribution by course
- **Grade Distribution by Demographics** - Analyze by gender, ethnicity, etc.

## Requirements

- Python 3.8+
- Django 3.2+

## License

MIT License
