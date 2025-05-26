from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from .forms import PatientRegisterForm, MedicRegisterForm, PatientProfileForm, MedicalInfoForm, MedicalForm
from django.contrib.auth.decorators import login_required
from .models import PatientProfile, MedicalInfo, User, MedicalExam
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import logging
logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'core/home.html')

def register_patient(request):
    if request.method == 'POST':
        form = PatientRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '🎉 Patient Account created successfully 🎉')
            return redirect('login')
    else:
        form = PatientRegisterForm()
    return render(request, 'core/register.html', {'form': form, 'title': 'Patient Registration'})

def register_medic(request):
    if request.method == 'POST':
        form = MedicRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '🎉 Medic Account created successfully 🎉')
            return redirect('login')
    else:
        form = MedicRegisterForm()
    return render(request, 'core/register.html', {'form': form, 'title': 'Medic Registration'})


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login was successful')

            if user.role == 'medic':
                return redirect('medic_dashboard')
            elif user.role == 'patient':
                return redirect('patient_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'core/login.html', {'title': 'Login'})
    
@login_required
def patient_profile(request):
    try:
        profile = request.user.patientprofile
    except PatientProfile.DoesNotExist:
        profile = None

    full_name = f"{request.user.first_name} {request.user.last_name}"

    if request.method == 'POST':
        form = PatientProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.full_name = full_name
            profile.save()
            return redirect('patient_dashboard')
    else:
        form = PatientProfileForm(instance=profile)

    return render(request, 'core/patient_profile.html', {
        'form': form,
        'full_name': full_name,
    })

@login_required
def medical_info(request):
    if request.user.role != 'patient':
        return redirect('dashboard')  # prevent medics from accessing this

    med_info = MedicalInfo.objects.filter(patient=request.user).order_by('-date_created').first()
    med_info_fields = {}

    if med_info:
        for field in med_info._meta.fields:
            if field.name in ['id', 'patient', 'medic', 'date_created']:
                continue
            field_name = field.verbose_name.title()
            field_value = getattr(med_info, field.name)
            med_info_fields[field_name] = field_value

        med_info_fields['Entered By'] = f"Dr. {med_info.medic.last_name} ({med_info.medic.imanis_code})"
        med_info_fields['Date Created'] = med_info.date_created.strftime('%Y-%m-%d %H:%M')
    else:
        med_info_fields = {}

    # Include age from PatientProfile
    try:
        profile = request.user.patientprofile
        med_info_fields['Age'] = profile.age
    except PatientProfile.DoesNotExist:
        med_info_fields['Age'] = 'N/A'

    return render(request, 'core/medical_info.html', {
        'med_info_fields': med_info_fields,
        'med_info': med_info,
    })

@login_required
def medic_dashboard(request):
    query = request.GET.get('q', '').strip()
    all_patients = User.objects.filter(role='patient')

    if query:
        filtered_patients = all_patients.filter(imanis_code__icontains=query)
    else:
        filtered_patients = None

    your_patients = User.objects.filter(
        medical_forms__medic=request.user
    ).distinct()

    return render(request, 'core/medic_dashboard.html', {
        'patients': filtered_patients,
        'your_patients': your_patients,
        'query': query,
    })

@login_required
def patient_dashboard(request):
    return render(request, 'core/patient_dashboard.html')

@login_required
def view_patient(request, patient_id):
    # Ensures the medic is viewing a valid patient
    patient = get_object_or_404(User, id=patient_id, role='patient')

    profile = getattr(patient, 'patientprofile', None)
    profile_fields = {}

    if profile:
        for field in profile._meta.fields:
            if field.name in ['id', 'user']:
                continue
            field_name = field.verbose_name.title()
            field_value = getattr(profile, field.name)
            profile_fields[field_name] = field_value
        profile_fields['Age'] = profile.age
    else:
        profile_fields['Age'] = 'N/A'

    # Gets the latest medical info entry for the patient
    med_info = MedicalInfo.objects.filter(patient=patient).order_by('-date_created').first()
    med_info_fields = {}

    if med_info:
        for field in med_info._meta.fields:
            if field.name in ['id', 'patient', 'medic', 'date_created']:
                continue
            field_name = field.verbose_name.title()
            field_value = getattr(med_info, field.name)
            med_info_fields[field_name] = field_value

        med_info_fields['Entered By'] = f"Dr. {med_info.medic.last_name} ({med_info.medic.imanis_code})"
        med_info_fields['Date Created'] = med_info.date_created.strftime('%Y-%m-%d %H:%M')

    # Past medical exams
    past_exams = MedicalExam.objects.filter(patient=patient).order_by('-date')

    full_name = f"{patient.first_name} {patient.last_name}"

    return render(request, 'core/view_patient.html', {
        'patient': patient,
        'profile_fields': profile_fields,
        'med_info_fields': med_info_fields,
        'med_info': med_info,
        'past_exams': past_exams,
        'full_name': full_name,
    })

def view_past_exams(request):
    if request.user.role != 'patient':
        return redirect('some-error-or-homepage')

    past_exams = MedicalExam.objects.filter(patient=request.user).order_by('-date')

    return render(request, 'core/view_past_exams.html', {
        'past_exams': past_exams,
    })

@login_required
def create_medical_exam(request, patient_id):
    patient = get_object_or_404(User, id=patient_id)
    gender = getattr(patient.patientprofile, 'gender', None)

    if request.method == 'POST':
        form = MedicalForm(request.POST, gender=gender)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.medic = request.user
            exam.patient = patient
            exam.save()
            messages.success(request, "Medical exam successfully recorded.")
            return redirect('view_medical_exam', exam_id=exam.id)
    else:
        form = MedicalForm(gender=gender)

    return render(request, 'core/create_medical_exam.html', {
        'form': form,
        'patient': patient
    })

@login_required
def view_medical_exam(request, exam_id):
    exam = get_object_or_404(MedicalExam, id=exam_id)

    exam_data = {}
    for field in exam._meta.fields:
        if field.name != 'id':
            value = getattr(exam, field.name)
            if field.is_relation:
                value = getattr(value, 'username', str(value))
            exam_data[field.verbose_name.capitalize()] = value

    return render(request, 'core/view_medical_exam.html', {
        'exam': exam,
        'exam_data': exam_data,
        'patient': exam.patient,
        'user_role': request.user.role
    })

@login_required
def update_patient_medical_info(request, patient_id):
    if request.user.role != 'medic':
        return redirect('dashboard')

    try:
        patient = User.objects.get(id=patient_id, role='patient')
    except User.DoesNotExist:
        return redirect('medic_dashboard')

    medical_info, created = MedicalInfo.objects.get_or_create(
        patient=patient,
        medic=request.user
    )

    if request.method == 'POST':
        form = MedicalInfoForm(request.POST, instance=medical_info)
        if form.is_valid():
            info = form.save(commit=False)
            info.patient = patient
            info.medic = request.user
            info.save()
            messages.success(request, "Medical info updated successfully")
            return redirect('view_patient', patient_id=patient.id)
    else:
        form = MedicalInfoForm(instance=medical_info)

    return render(request, 'core/update_patient_medical_info.html', {
        'form': form,
        'patient': patient,
    })
