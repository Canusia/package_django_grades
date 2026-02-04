# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Django app for managing student grades in the MyCE platform. Provides grade submission for instructors, grade viewing for students, unofficial transcript generation, and grade analytics reports.

## Package Structure

```
django_grades/                # Repo root
├── setup.py / setup.cfg      # Package config
├── django_grades/            # Django app
│   ├── apps.py               # GradesConfig + DevGradesConfig
│   ├── signals.py            # Grade-related signals
│   ├── urls.py               # Main URL config
│   ├── urls/                 # Role-based URLs
│   │   ├── instructor.py     # /instructor/grades/
│   │   └── student.py        # /student/grades/
│   ├── views/
│   │   ├── instructor.py     # Grade submission views
│   │   └── student.py        # Grade viewing, transcript download
│   ├── forms/
│   │   └── section.py        # ClassSectionGradeForm, formset
│   ├── settings/
│   │   └── class_section_grades.py  # Grade scale, submission window, templates
│   ├── reports/              # CE reports
│   │   ├── grade_by_highschool.py
│   │   ├── grade_by_course.py
│   │   └── grade_by_demographics.py
│   ├── management/commands/
│   │   └── notify_grades_pending.py  # Email reminders
│   ├── templates/grades/
│   └── staticfiles/
```

## App Configurations

**Production (pip install):**
- `django_grades.apps.GradesConfig`
- Import paths: `django_grades.views.instructor`

**Development (submodule):**
- `django_grades.django_grades.apps.DevGradesConfig`
- Import paths: `django_grades.django_grades.views.instructor`

## Key Settings (class_section_grades)

Stored in `Setting` model with key `{CAMPUS_CODE_PREFIX}_class_grades`:
- `grade_scale` - List of {grade, points} for GPA calculation
- `terms` - Terms with grade submission open
- `start_date` / `end_date` - Submission window
- `reminder_dates` / `cron` - Notification schedule
- `grades_due_email` - Reminder template
- `grades_submitted_email` - Confirmation template
- `transcript_*` - Unofficial transcript templates

## URL Routes

**Instructor:**
- `grades/` → `class_grades` - List classes needing grades
- `grades/class_section/<uuid>` → `class_section_grade` - Submit grades

**Student:**
- `grades/` → `grades` - View grades
- `grades/download/` → `download_transcript` - PDF transcript

## Integration Points

- **CIS models:** Term, ClassSection, StudentRegistration
- **Student app:** get_current_student, verify_account_complete
- **Settings framework:** Registered via CONFIGURATORS in apps.py
- **Reports framework:** Registered via REPORTS in apps.py
- **CronTab:** notify_grades_pending command scheduling
