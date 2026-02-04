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
