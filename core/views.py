from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from .forms import PatientRegisterForm, MedicRegisterForm, LoginForm, PatientProfileForm, MedicalInfoForm, MedicalForm
from django.contrib.auth.decorators import login_required
from .models import PatientProfile, MedicalInfo, User, MedicalExam
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages


def home(request):
    return render(request, 'core/home.html')

def register_patient(request):
    if request.method == 'POST':
        form = PatientRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = PatientRegisterForm()
    return render(request, 'core/register.html', {'form': form, 'title': 'Patient Registration'})


def register_medic(request):
    if request.method == 'POST':
        form = MedicRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = MedicRegisterForm()
    return render(request, 'core/register.html', {'form': form, 'title': 'Medic Registration'})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if user.role == 'medic':
                return redirect('medic_dashboard')
            elif user.role == 'patient':
                return redirect('patient_dashboard')  # Create this if not done
            else:
                return redirect('home')

    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form})
    
@login_required
def patient_profile(request):
    try:
        profile = request.user.patientprofile
    except PatientProfile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        form = PatientProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('patient_dashboard')
    else:
        form = PatientProfileForm(instance=profile)

    return render(request, 'core/patient_profile.html', {'form': form})

@login_required
def medical_info(request):
    try:
        med_info = request.user.medicalinfo
        med_info_fields = {}
        if med_info:
            for field in med_info._meta.fields:
                if field.name in ['id', 'user']:
                    continue
                field_name = field.verbose_name.title()
                field_value = getattr(med_info, field.name)
                med_info_fields[field_name] = field_value

    except MedicalInfo.DoesNotExist:
        med_info = None
        med_info_fields = {}

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
    patients = User.objects.filter(role='patient')
    return render(request, 'core/medic_dashboard.html', {'patients': patients})

@login_required
def patient_dashboard(request):
    return render(request, 'core/patient_dashboard.html')

@login_required
def view_patient(request, patient_id):
    patient = User.objects.get(id=patient_id, role='patient')
    profile = getattr(patient, 'patientprofile', None)
    med_info = getattr(patient, 'medicalinfo', None)

    profile_fields = {}
    if profile:
        for field in profile._meta.fields:
            if field.name in ['id', 'user']:
                continue
            field_name = field.verbose_name.title()
            field_value = getattr(profile, field.name)
            profile_fields[field_name] = field_value
        profile_fields['Age'] = profile.age

    med_info_fields = {}
    if med_info:
        for field in med_info._meta.fields:
            if field.name in ['id', 'user']:
                continue
            field_name = field.verbose_name.title()
            field_value = getattr(med_info, field.name)
            med_info_fields[field_name] = field_value
    
    past_exams = MedicalExam.objects.filter(patient=patient).order_by('-date')

    return render(request, 'core/view_patient.html', {
        'patient': patient,
        'profile_fields': profile_fields,
        'med_info_fields': med_info_fields,
        'med_info': med_info,
        'past_exams': past_exams,
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
        if field.name != 'id':  # Skip ID if you don't want to display it
            value = getattr(exam, field.name)
            # For ForeignKey fields, show the related object's username if available
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

    medical_info, created = MedicalInfo.objects.get_or_create(user=patient)

    if request.method == 'POST':
        form = MedicalInfoForm(request.POST, instance=medical_info)
        if form.is_valid():
            form.save()
            return redirect('view_patient', patient_id=patient.id)

    else:
        form = MedicalInfoForm(instance=medical_info)

    return render(request, 'core/update_patient_medical_info.html', {
        'form': form,
        'patient': patient
    })

