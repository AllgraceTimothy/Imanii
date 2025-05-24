from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from .constants import ROLE_CHOICES, GENDER_CHOICES, LAB_TEST_CHOICES, PROCEDURE_CHOICES, FEMALE_SPECIFIC_FIELDS, BLOOD_GROUP_CHOICES, RH_FACTOR_CHOICES
from django.db import models
from django.utils import timezone
import random
from django.conf import settings
from datetime import date

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, role=None, secret_code=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')
        if not role:
            raise ValueError('Users must have a role')


        if role == 'medic':
            if secret_code != settings.MEDIC_SECRET_CODE:
                raise ValueError('Invalid secret code for medic registration')
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(username, email, password, role='admin')
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    imanis_code =models.CharField(max_length=10, unique=True, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def save(self, *args, **kwargs):
        if not self.imanis_code and self.role in ['patient', 'medic']:
            prefix = 'P-' if self.role == 'patient' else 'C-'
            while True:
                num = random.randint(0, 9999) if self.role == 'patient' else random.randint(0, 999)
                code = f"{prefix}{num:04}" if self.role == 'patient' else f"{prefix}{num:03}"
                if not User.objects.filter(imanis_code=code).exists():
                    self.imanis_code = code
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"


class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=15)
    contact_email = models.EmailField()
    next_of_kin_name = models.CharField(max_length=100)
    next_of_kin_phone = models.CharField(max_length=15)
    next_of_kin_email = models.EmailField()

    def __str__(self):
        return f"{self.full_name} ({self.user.username})"

    @property
    def age(self):
        today = date.today()
        if self.date_of_birth:
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

class MedicalInfo(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE)

    height_cm = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(30), MaxValueValidator(300)],
        help_text="Height in centimeters"
    )
    weight_kg = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(2), MaxValueValidator(500)],
        help_text="Weight in kilograms"
    )
    blood_group = models.CharField(
        max_length=2,
        choices=BLOOD_GROUP_CHOICES,
        blank=True,
        null=True
    )
    rh_factor = models.CharField(
        max_length=8,
        choices=RH_FACTOR_CHOICES,
        blank=True,
        null=True
    )
    allergies = models.TextField(blank=True)
    chronic_conditions = models.TextField(
        blank=True,
        help_text="List any chronic conditions like Diabetes, Hypertension, etc."
    )
    medical_history = models.TextField(blank=True)
    past_surgeries = models.TextField(
        blank=True,
        help_text="Describe past surgeries (type, date, outcome)"
    )

    def __str__(self):
        return f"Medical Info for {self.user.username}"

    @property
    def bmi(self):
        """Returns the BMI calculated from height and weight, or None if insufficient data."""
        if self.height_cm and self.weight_kg:
            height_m = self.height_cm / 100
            return round(self.weight_kg / (height_m ** 2), 2)
        return None

class MedicalExam(models.Model):
    medic = models.ForeignKey(User, on_delete=models.CASCADE, related_name='treatments')
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_treatments')
    date = models.DateField(auto_now_add=True)

    blood_pressure = models.CharField(max_length=20, blank=True, help_text="e.g., 120/80")
    heart_rate = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Beats per minute (e.g, 72)")
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="Body temperature in °C")
    respiratory_rate = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Breaths per minute (e.g, 16)")
    oxygen_saturation = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Oxygen saturation in % (e.g., 98)")

    lab_test = models.CharField(max_length=20, choices=LAB_TEST_CHOICES)
    lab_test_result = models.TextField(blank=True, help_text="Result or notes for the lab test")

    procedure = models.CharField(max_length=20, choices=PROCEDURE_CHOICES)
    procedure_result = models.TextField(blank=True, help_text="Result or notes for the procedure")

    # Gender-specific fields
    is_pregnant = models.BooleanField(null=True, blank=True)
    pregnancy_weeks = models.IntegerField(null=True, blank=True)
    last_menstrual_period = models.DateField(null=True, blank=True)
    menstrual_cycle_notes = models.TextField(blank=True)

    # Clinical content
    diagnosis = models.TextField()
    prescribed_medications = models.TextField(blank=True)
    follow_up_instructions = models.TextField(blank=True)
    lifestyle_recommendations = models.TextField(blank=True)

    referred_to_specialist = models.CharField(max_length=255, blank=True)

    # Final notes
    review_notes = models.TextField(help_text="General review or summary of visit & any other comments", blank=True)

    def __str__(self):
        return f"Treatment by {self.medic.username} for {self.patient.username} on {self.date}"
