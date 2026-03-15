from ..models import Batch
from django import forms

class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = '__all__'
        labels = {
            'department': 'Department',
            'title': 'Batch Title',
            'name': 'Batch Name',
            'start_date': 'Start Date',
            'program': 'Program',
            'status': 'Status',
        }



        widgets = {
            'department': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'program': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], attrs={'class': 'form-control'}),
        }

