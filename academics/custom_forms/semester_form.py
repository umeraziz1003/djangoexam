from django import forms
from ..models import Semester

class SemesterForm(forms.ModelForm):
    class Meta:
        model = Semester
        fields = '__all__'
        labels = {
            'batch': 'Batch',
            'semester_number': 'Semester Number',
            'semester_year': 'Semester Year',
        }
        widgets = {
            'batch': forms.Select(attrs={'class': 'form-control'}),
            'semester_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'semester_year': forms.NumberInput(attrs={'class': 'form-control'}),
        }