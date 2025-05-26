from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, PatientProfile
from datetime import date

@receiver(post_save, sender=User)
def create_patient_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'patient':
      PatientProfile.objects.get_or_create(
        user=instance,
        defaults={
            'date_of_birth': date(2000, 1, 1),
            'gender': '',
            'marital_status': '',
            'phone_number': '',
            'contact_email': instance.email,
            'emergency_contact_name': '',
            'emergency_contact_phone': '',
            'emergency_contact_email': '',
          }
      )
