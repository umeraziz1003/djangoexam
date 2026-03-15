from django import forms

from .models import ExamSplitConfig, GradeScale, ExamRules


class ExamSplitConfigForm(forms.ModelForm):
    class Meta:
        model = ExamSplitConfig
        fields = ["sessional_max", "midterm_max", "terminal_max"]
        labels = {
            "sessional_max": "Sessional (Max)",
            "midterm_max": "Midterm (Max)",
            "terminal_max": "Terminal (Max)",
        }
        widgets = {
            "sessional_max": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "midterm_max": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "terminal_max": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
        }

    def clean(self):
        cleaned = super().clean()
        total = (cleaned.get("sessional_max") or 0) + (cleaned.get("midterm_max") or 0) + (cleaned.get("terminal_max") or 0)
        if total != 100:
            raise forms.ValidationError("Total of Sessional + Midterm + Terminal must be 100.")
        return cleaned


class GradeScaleForm(forms.ModelForm):
    class Meta:
        model = GradeScale
        fields = ["min_percentage", "max_percentage", "grade", "grade_point", "is_active"]
        labels = {
            "min_percentage": "Min %",
            "max_percentage": "Max %",
            "grade": "Grade",
            "grade_point": "Grade Point",
            "is_active": "Active",
        }
        widgets = {
            "min_percentage": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 100, "step": "0.01"}),
            "max_percentage": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 100, "step": "0.01"}),
            "grade": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. A"}),
            "grade_point": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 4, "step": "0.01"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ExamRulesForm(forms.ModelForm):
    class Meta:
        model = ExamRules
        fields = [
            "min_cgpa_dropout",
            "min_cgpa_probation",
            "max_probations_allowed",
            "failed_marks_threshold",
            "improvement_min",
            "improvement_max",
            "no_drop_after_semester",
            "can_drop",
        ]
        labels = {
            "min_cgpa_dropout": "Minimum CGPA for Dropout",
            "min_cgpa_probation": "Minimum CGPA for Probation",
            "max_probations_allowed": "Max Probations Allowed",
            "failed_marks_threshold": "Failed Marks Threshold",
            "improvement_min": "Improvement Eligibility Min",
            "improvement_max": "Improvement Eligibility Max",
            "no_drop_after_semester": "No Drop After Semester",
            "can_drop": "Allow Drop",
        }
        widgets = {
            "min_cgpa_dropout": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": 0, "max": 4}),
            "min_cgpa_probation": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": 0, "max": 4}),
            "max_probations_allowed": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "failed_marks_threshold": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 100, "step": "0.01"}),
            "improvement_min": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 100, "step": "0.01"}),
            "improvement_max": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 100, "step": "0.01"}),
            "no_drop_after_semester": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "can_drop": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
