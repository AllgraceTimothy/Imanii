from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, PatientProfile, MedicalInfo, MedicalExam

class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'imanis_code')
    ordering = ('date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Personal Info'), {'fields': ('role', 'imanis_code')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important Dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'imanis_code', 'password1', 'password2'),
        }),
    )


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'date_of_birth', 'gender', 'get_age')
    search_fields = ('full_name', 'user__username', 'contact_email')
    list_filter = ('gender',)

    def get_age(self, obj):
        return obj.age
    get_age.short_description = 'Age'


@admin.register(MedicalInfo)
class MedicalInfoAdmin(admin.ModelAdmin):
    list_display = ('user', 'chronic_conditions', 'blood_group', 'rh_factor')
    search_fields = ('user__username',)
    list_filter = ('blood_group', 'rh_factor')


@admin.register(MedicalExam)
class TreatmentAdmin(admin.ModelAdmin):
    list_display = ('medic', 'patient', 'date', 'diagnosis')
    search_fields = ('medic__username', 'patient__username', 'diagnosis')
    list_filter = ('date', 'medic', 'is_pregnant')

admin.site.register(User, UserAdmin)
