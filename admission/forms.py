from django import forms

from academics.models import Batch, Department, Semester, Session
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['full_name', 'father_name', 'date_of_birth', 'cnic', 'roll_no', 'registration_no', 'batch']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Ali Raza'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Ahmed Raza'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'cnic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 35202-1234567-8'}),
            'roll_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CS-2024-001'}),
            'registration_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. REG-2024-1001'}),
            'batch': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'full_name': 'Full Name',
            'father_name': 'Father Name',
            'date_of_birth': 'Date of Birth',
            'cnic': 'CNIC',
            'roll_no': 'Roll Number',
            'registration_no': 'Registration Number',
            'batch': 'Batch',
        }

