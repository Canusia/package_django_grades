# Django Grades

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
