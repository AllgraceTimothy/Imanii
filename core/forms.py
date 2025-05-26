from django import forms
from .models import User, PatientProfile, MedicalInfo, MedicalExam
import re
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from .constants import LAB_TEST_CHOICES, PROCEDURE_CHOICES
from django.forms import widgets
from django.forms import fields as form_fields
from django.forms import widgets as form_widgets

class PatientRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")

        if password != confirm:
            self.add_error('confirm_password', "Passwords do not match")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'patient'
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class MedicRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    secret_code = forms.CharField(widget=forms.PasswordInput, help_text="Enter the secret code provided by the administrator.")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")

        if password != confirm:
            self.add_error('confirm_password', "Passwords do not match")

    def clean_secret_code(self):
        code = self.cleaned_data.get('secret_code')
        if code != settings.MEDIC_SECRET_CODE:
            raise forms.ValidationError("Invalid secret code.")
        return code

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'medic'
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class PatientProfileForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'Select a date'}
        )
    )

    class Meta:
        model = PatientProfile
        fields = [
            'date_of_birth', 'gender', 'marital_status',
            'phone_number', 'contact_email',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_email'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class MedicalInfoForm(forms.ModelForm):
    class Meta:
        model = MedicalInfo
        fields = [
            'height_cm',
            'weight_kg',
            'blood_group',
            'rh_factor',
            'allergies',
            'chronic_conditions',
            'medical_history',
            'past_surgeries',
            'current_medications',
        ]

class MedicalForm(forms.ModelForm):
    def __init__(self, *args, gender=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Hide gender-specific fields if not female
        if gender != 'female':
            for field in ['is_pregnant', 'pregnancy_weeks', 'last_menstrual_period', 'menstrual_cycle_notes']:
                self.fields.pop(field, None)

    class Meta:
        model = MedicalExam
        exclude = ['medic', 'patient', 'date']
        widgets = {
            'blood_pressure': forms.TextInput(attrs={'placeholder': 'e.g., 120/80', 'class': 'form-control'}),
            'heart_rate': forms.NumberInput(attrs={'min': 0, 'class': 'form-control', 'placeholder': 'e.g., 72'}),
            'temperature': forms.NumberInput(attrs={'step': '0.1', 'min': 30, 'max': 45, 'class': 'form-control', 'placeholder': 'e.g., 36.5 °C'}),
            'respiratory_rate': forms.NumberInput(attrs={'min': 0, 'max': 60, 'class': 'form-control', 'placeholder': 'e.g., 18'}),
            'oxygen_saturation': forms.NumberInput(attrs={'min': 0, 'max': 100, 'class': 'form-control', 'placeholder': 'e.g., 98%'}),
            'diagnosis': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'prescribed_medications': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'follow_up_instructions': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'lifestyle_recommendations': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'pregnancy_weeks': forms.NumberInput(attrs={'min': 0, 'class': 'form-control'}),
            'last_menstrual_period': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'Select a date'}
            ),
            'menstrual_cycle_notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'referred_to_specialist': forms.TextInput(attrs={'class': 'form-control'}),
            'review_notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'lab_test': forms.Select(attrs={'class': 'form-control'}),
            'lab_test_result': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'procedure': forms.Select(attrs={'class': 'form-control'}),
            'procedure_result': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }
