# pulse/utils/__init__.py

# Import validators
from utils.validators import (
    validate_email,
    validate_phone,
    validate_weight,
    validate_height,
    validate_age,
    validate_pulse,
    validate_temperature,
    validate_blood_pressure,
    validate_name,
    validate_address,
    validate_required_fields,
    check_form_filled,
    highlight_invalid,
    reset_highlight,
    show_validation_error,
    sanitize_input,
    is_valid_date,
    calculate_age,
    calculate_bmi,
    assess_health,
    generate_patient_id,
    calculate_ideal_body_weight,
    validate_patient_registration_form
)

# Import PDF generation functions
from utils.pdf_generator import (
    read_business_info,
    create_invoice_pdf,
    generate_patient_report,
    sanitize_filename
)

# Import QR code generator
from utils.qr_code import create_patient_qr_code

# Import crypto utilities
from utils.crypto import check_trial_status, show_expiry_message

# Optional metadata
__version__ = "1.0.0"
__author__ = "GEORGES BODIONG"