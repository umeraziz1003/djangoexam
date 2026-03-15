from django import forms
from .models import Course

class CourseForm(forms.ModelForm):
    COURSE_TYPE_CHOICES = [
        ("Core", "Core"),
        ("Elective", "Elective"),
    ]
    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("INACTIVE", "Inactive"),
    ]

    class Meta:
        model = Course
        fields = ["department", "course_code", "course_title", "credit_hours", "course_type", "status"]
        labels = {
            "department": "Program",
            "course_code": "Course Code",
            "course_title": "Course Title",
            "credit_hours": "Credit Hours",
            "course_type": "Course Type",
            "status": "Status",
        }
        widgets = {
            "department": forms.Select(attrs={"class": "form-select"}),
            "course_code": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. CS-101"}),
            "course_title": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Introduction to Programming"}),
            "credit_hours": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 6}),
            "course_type": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["course_type"].choices = self.COURSE_TYPE_CHOICES
        self.fields["status"].choices = self.STATUS_CHOICES
