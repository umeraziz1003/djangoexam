from django import forms
from ..models import Session, Department, Batch

class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ["name", "start_date", "end_date", "is_active", "departments", "batches"]
        labels = {
            
            'name': 'Session Name',
            'start_date': 'Start Date',
            'end_date': 'End Date',
            'is_active': 'Is Active',
            'departments': 'Departments',
            'batches': 'Batches',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),

            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'departments': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'batches': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }



