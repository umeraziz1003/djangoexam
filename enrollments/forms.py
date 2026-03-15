from django import forms

from admission.models import Student
from courses.models import CourseOffering
from .models import Enrollment


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ["student", "course_offering"]
        labels = {
            "student": "Student",
            "course_offering": "Course Offering",
        }
        widgets = {
            "student": forms.Select(attrs={"class": "form-select"}),
            "course_offering": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["student"].queryset = Student.objects.filter(is_active=True).order_by("roll_no")
        self.fields["course_offering"].queryset = CourseOffering.objects.select_related(
            "course",
            "semester",
            "session",
        ).order_by("course__course_code")
