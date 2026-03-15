from django import forms
from ..models import Session

class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = '__all__'
        labels = {
            
            'name': 'Session Name',
            'start_date': 'Start Date',
            'end_date': 'End Date',
            'is_active': 'Is Active'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),

            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }



