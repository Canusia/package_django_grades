import os
from django.apps import AppConfig


class GradesConfig(AppConfig):
    """Production app config - when installed via pip."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_grades'
    verbose_name = 'Grades'
    path = os.path.dirname(os.path.abspath(__file__))

    CONFIGURATORS = [
        {
            'app': 'django_grades',
            'name': 'class_section_grades',
            'title': 'Class Grades Settings',
            'description': 'Configure grade scale and GPA points, grade submission window dates, reminder notifications, email templates for grades due and submitted confirmations, and unofficial transcript templates.',
            'categories': [
                '3'
            ]
        },
    ]

    REPORTS = [
        {
            'app': 'django_grades',
            'name': 'grade_by_highschool',
            'title': 'Grade Distribution by High School',
            'description': 'Analyze grade distribution, success rates, and DFW rates by high school',
            'categories': [
                'High School'
            ],
            'available_for': [
                'ce'
            ]
        },
        {
            'app': 'django_grades',
            'name': 'grade_by_course',
            'title': 'Grade Distribution by Course',
            'description': 'Analyze grade distribution, success rates, and DFW rates by course',
            'categories': [
                'Classes'
            ],
            'available_for': [
                'ce'
            ]
        },
        {
            'app': 'django_grades',
            'name': 'grade_by_demographics',
            'title': 'Grade Distribution by Demographics',
            'description': 'Analyze grade distribution by gender, ethnicity, first-gen status, grade level, or parent education',
            'categories': [
                'Students'
            ],
            'available_for': [
                'ce'
            ]
        },
    ]

    def ready(self):
        """Import signals when app is ready."""
        import django_grades.signals


class DevGradesConfig(AppConfig):
    """Development app config - when using as submodule."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_grades.django_grades'
    verbose_name = 'Dev - Grades'

    CONFIGURATORS = [
        {
            'app': 'django_grades.django_grades',
            'name': 'class_section_grades',
            'title': 'Class Grades Settings',
            'description': 'Configure grade scale and GPA points, grade submission window dates, reminder notifications, email templates for grades due and submitted confirmations, and unofficial transcript templates.',
            'categories': [
                '3'
            ]
        },
    ]

    REPORTS = [
        {
            'app': 'django_grades.django_grades',
            'name': 'grade_by_highschool',
            'title': 'Grade Distribution by High School',
            'description': 'Analyze grade distribution, success rates, and DFW rates by high school',
            'categories': [
                'High School'
            ],
            'available_for': [
                'ce'
            ]
        },
        {
            'app': 'django_grades.django_grades',
            'name': 'grade_by_course',
            'title': 'Grade Distribution by Course',
            'description': 'Analyze grade distribution, success rates, and DFW rates by course',
            'categories': [
                'Classes'
            ],
            'available_for': [
                'ce'
            ]
        },
        {
            'app': 'django_grades.django_grades',
            'name': 'grade_by_demographics',
            'title': 'Grade Distribution by Demographics',
            'description': 'Analyze grade distribution by gender, ethnicity, first-gen status, grade level, or parent education',
            'categories': [
                'Students'
            ],
            'available_for': [
                'ce'
            ]
        },
    ]

    def ready(self):
        """Import signals when app is ready."""
        import django_grades.django_grades.signals
