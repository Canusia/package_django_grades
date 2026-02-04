"""
Grade-related forms for class sections.
"""
from django import forms
from django.forms.formsets import BaseFormSet

from cis.models.section import StudentRegistration
from ..settings.class_section_grades import class_section_grades


class ClassSectionGradeForm(forms.Form):
    student = forms.CharField(
        label='',
        widget=forms.HiddenInput
    )

    student_id = forms.CharField(
       widget=forms.HiddenInput
    )
    grade = forms.ChoiceField(
        required=True,
        label='',
        choices=()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        grade_settings = class_section_grades.from_db()

        grades = grade_settings.get('grades', '').split(',')
        grade_choices = [('', '')] + [
            (grade, grade) for grade in grades
        ]
        self.fields['grade'].choices = grade_choices


class ClassSectionGradeFormSet(BaseFormSet):
    def save(self):
        for form in self.forms:
            try:
                data = form.cleaned_data
            except:
                data = form.data

            grade = data.get('grade')
            student_id = data.get('student_id')

            registration = StudentRegistration.objects.filter(
                pk=student_id
            ).update(
                grade=grade
            )
