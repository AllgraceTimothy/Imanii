ROLE_CHOICES = [
    ('patient', 'Patient'),
    ('medic', 'Medic'),
    ('admin', 'Admin'),
]

GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('non-binary', 'non-binary'),
]

FEMALE_SPECIFIC_FIELDS = {
    'is_pregnant': {
        'field_type': 'BooleanField',
        'label': 'Is the patient pregnant?',
        'required': False,
        'widget': 'CheckboxInput',
        'widget_attrs': {'class': 'form-check-input'}
    },
    'pregnancy_weeks': {
        'field_type': 'IntegerField',
        'label': 'Weeks of pregnancy',
        'required': False,
        'widget': 'NumberInput',
        'widget_attrs': {'class': 'form-control'}
    },
    'last_menstrual_period': {
        'field_type': 'DateField',
        'label': 'Last menstrual period',
        'required': False,
        'widget': 'DateInput',
        'widget_attrs': {'type': 'date', 'class': 'form-control'}
    },
    'menstrual_cycle_notes': {
        'field_type': 'CharField',
        'label': 'Menstrual cycle notes',
        'required': False,
        'widget': 'Textarea',
        'widget_attrs': {'class': 'form-control', 'rows': 3}
    }
}

BLOOD_GROUP_CHOICES = [
    ('A', 'A'),
    ('B', 'B'),
    ('AB', 'AB'),
    ('O', 'O'),
]

RH_FACTOR_CHOICES = [
    ('Positive', 'Positive'),
    ('Negative', 'Negative'),
]

LAB_TEST_CHOICES = [
    ('CBC', 'Complete Blood Count (CBC)'),
    ('CMP', 'Comprehensive Metabolic Panel (CMP)'),
    ('PT', 'Pregnancy Test (PT)'),
    ('LIPID', 'Lipid Panel'),
    ('GLUCOSE', 'Blood Glucose'),
    ('UA', 'Urinalysis (UA)'),
    ('TSH', 'Thyroid Stimulating Hormone (TSH)'),
    ('HBA1C', 'HbA1c'),
    ('VITD', 'Vitamin D Level'),
    ('CRP', 'C-Reactive Protein (CRP)'),
    ('LFT', 'Liver Function Tests (LFTs)'),
]

PROCEDURE_CHOICES = [
    ('EXAM', 'Physical Examination'),
    ('PHLEBOTOMY', 'Blood Draw (Phlebotomy)'),
    ('VACCINE', 'Vaccination/Immunization'),
    ('WOUND_CARE', 'Wound Dressing Change / Care'),
    ('SUTURE', 'Suture Placement / Removal'),
    ('IV', 'IV Line Insertion'),
    ('ECG', 'Electrocardiogram (ECG/EKG)'),
    ('XRAY', 'X-ray'),
    ('DRAINAGE', 'Minor Incision and Drainage (I&D)'),
    ('CONSULT', 'Consultation'),
]