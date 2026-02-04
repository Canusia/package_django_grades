"""
Utility functions for django_grades app.
"""
import datetime


def is_submit_grades_open():
    """
    Check if grade submission window is currently open.

    Returns True if current date is within the configured
    start_date and end_date range in class_section_grades settings.
    """
    try:
        from .settings.class_section_grades import class_section_grades

        now = datetime.datetime.now()
        settings = class_section_grades.from_db()

        start_date = datetime.datetime.strptime(
            settings.get('start_date'),
            '%m/%d/%Y'
        )
        if now < start_date:
            return False

        end_date = datetime.datetime.strptime(
            settings.get('end_date'),
            '%m/%d/%Y'
        )
        if now > end_date:
            return False
        return True
    except:
        return False


def grades_page_header_for_instructor():
    """
    Get the appropriate page header message for instructor grades page.

    Returns grades_open message if submission window is open,
    otherwise returns grades_closed message.
    """
    from .settings.class_section_grades import class_section_grades

    settings = class_section_grades.from_db()

    header = settings.get('grades_closed')
    if is_submit_grades_open():
        header = settings.get('grades_open')

    return header
