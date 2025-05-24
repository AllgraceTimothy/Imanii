from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('register/patient/', views.register_patient, name='register_patient'),
    path('register/medic/', views.register_medic, name='register_medic'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/', views.patient_profile, name='patient_profile'),
    path('medical-info/', views.medical_info, name='medical_info'),
    path('medic/dashboard/', views.medic_dashboard, name='medic_dashboard'),
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('medic/patient/<int:patient_id>/', views.view_patient, name='view_patient'),
    path('medic/patient/<int:patient_id>/medical-info/', views.update_patient_medical_info, name='update_patient_medical_info'),
    path('medical-exam/create/<int:patient_id>/', views.create_medical_exam, name='create_medical_exam'),
    path('medical-exam/<int:exam_id>/', views.view_medical_exam, name='view_medical_exam'),
    path('My-exams/', views.view_past_exams, name='view_past_exams'),
]
