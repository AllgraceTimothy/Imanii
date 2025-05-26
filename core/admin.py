from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, PatientProfile, MedicalInfo, MedicalExam

class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'first_name', 'last_name', 'imanis_code', 'role', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'imanis_code')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'role', 'imanis_code')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important Dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )

    readonly_fields = ('imanis_code', 'date_joined', 'last_login')

admin.site.register(User, UserAdmin)

@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth', 'gender', 'get_age', 'contact_email', 'phone_number')
    search_fields = ('full_name', 'user__email', 'contact_email')
    list_filter = ('gender', 'marital_status')

    def get_age(self, obj):
        return obj.age
    get_age.short_description = 'Age'


@admin.register(MedicalInfo)
class MedicalInfoAdmin(admin.ModelAdmin):
    list_display = ('medic', 'patient', 'blood_group', 'rh_factor', 'height_cm', 'weight_kg', 'bmi_display')
    search_fields = ('user__email',)
    list_filter = ('blood_group', 'rh_factor')

    def bmi_display(self, obj):
        return obj.bmi
    bmi_display.short_description = 'BMI'


@admin.register(MedicalExam)
class MedicalExamAdmin(admin.ModelAdmin):
    list_display = ('medic', 'patient', 'date', 'diagnosis', 'lab_test', 'procedure', 'is_pregnant')
    search_fields = ('medic__email', 'patient__email', 'diagnosis', 'lab_test', 'procedure')
    list_filter = ('date', 'medic', 'lab_test', 'procedure', 'is_pregnant')

    readonly_fields = ('date',)
