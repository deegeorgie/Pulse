# pulse/utils/validators.py

import re
from tkinter import messagebox, Entry, Text, END
from functools import partial
import tkinter as tk

# utils/validators.py

from datetime import datetime

def is_valid_date(date_str, date_format="%Y-%m-%d"):
    """
    Check if a string is a valid date.
    
    Args:
        date_str (str): The date string to validate.
        date_format (str): Expected format (default: YYYY-MM-DD)

    Returns:
        bool: True if valid date, False otherwise.
    """
    try:
        datetime.strptime(date_str, date_format)
        return True
    except ValueError:
        return False

def validate_email(content):
    """
    Validate an email address using regex.
    
    Args:
        content (str): Email string to check.
    
    Returns:
        bool: True if valid, False otherwise.
    """
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_pattern, content) is not None


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format.
    
    Args:
        phone (str): Phone number to validate.
    
    Returns:
        bool: True if valid, False otherwise.
    """
    phone_pattern = r'^\+?1?\d{9,15}$'
    return re.match(phone_pattern, phone) is not None


def validate_weight(weight: str) -> bool:
    """
    Check if weight is a positive float.
    
    Args:
        weight (str): Weight input as string.
    
    Returns:
        bool: True if valid, False otherwise.
    """
    try:
        value = float(weight)
        return value > 0
    except ValueError:
        return False


def validate_height(height: str) -> bool:
    """
    Check if height is within human range (0.5m - 2.5m).
    
    Args:
        height (str): Height in meters.
    
    Returns:
        bool: True if valid, False otherwise.
    """
    try:
        value = float(height)
        return 0.5 <= value <= 2.5
    except ValueError:
        return False


def validate_blood_pressure(systolic: str, diastolic: str) -> bool:
    """
    Validate systolic and diastolic blood pressure values.
    
    Args:
        systolic (str): Systolic BP value.
        diastolic (str): Diastolic BP value.
    
    Returns:
        bool: True if both are valid integers within normal ranges.
    """
    try:
        sys_val = int(systolic)
        dia_val = int(diastolic)
        return 50 <= sys_val <= 250 and 30 <= dia_val <= 180
    except ValueError:
        return False


def validate_pulse(pulse: str) -> bool:
    """
    Validate that pulse rate is a reasonable integer.
    
    Args:
        pulse (str): Pulse input as string.
    
    Returns:
        bool: True if valid, False otherwise.
    """
    try:
        value = int(pulse)
        return 30 <= value <= 200
    except ValueError:
        return False


def validate_temperature(temp: str) -> bool:
    """
    Validate body temperature is within a realistic range.
    
    Args:
        temp (str): Temperature input as string.
    
    Returns:
        bool: True if valid, False otherwise.
    """
    try:
        value = float(temp)
        return 34.0 <= value <= 42.0
    except ValueError:
        return False


def validate_age(age: str) -> bool:
    """
    Validate that age is a positive integer.
    
    Args:
        age (str): Age input as string.
    
    Returns:
        bool: True if valid, False otherwise.
    """
    try:
        value = int(age)
        return value > 0
    except ValueError:
        return False


def validate_name(name: str) -> bool:
    """
    Validate that name contains only letters and spaces.
    
    Args:
        name (str): Name input as string.
    
    Returns:
        bool: True if valid, False otherwise.
    """
    return bool(re.match(r'^[A-Za-z\s\-\' ]+$', name.strip()))


def validate_address(address: str) -> bool:
    """
    Validate that the address is non-empty and reasonably formatted.
    
    Args:
        address (str): Address input as string.
    
    Returns:
        bool: True if valid, False otherwise.
    """
    return len(address.strip()) >= 3


def validate_required_fields(fields: dict) -> list:
    """
    Ensure all required fields are filled.
    
    Args:
        fields (dict): Dictionary of field names and their values.
    
    Returns:
        list: List of missing field names.
    """
    missing = [field for field, value in fields.items() if not value or value.strip() == ""]
    return missing


def on_invalid():
    """
    Generic function to call when invalid input is detected.
    Can be used for logging or triggering UI feedback.
    """
    print("Invalid input detected.")


def highlight_invalid(entry: Entry):
    """
    Highlight an entry widget to indicate invalid input.
    
    Args:
        entry (Entry): Tkinter Entry widget.
    """
    entry.config(bg='orange')


def reset_highlight(entry: Entry):
    """
    Reset the background color of an entry widget.
    
    Args:
        entry (Entry): Tkinter Entry widget.
    """
    entry.config(bg='white')


def check_form_filled(*entries):
    """
    Check if all given entries have content.
    
    Args:
        *entries: Variable number of Tkinter Entry widgets.
    
    Returns:
        bool: True if all fields are filled, False otherwise.
    """
    for entry in entries:
        if isinstance(entry, Entry):
            if not entry.get().strip():
                return False
        elif isinstance(entry, Text):
            if not entry.get("1.0", "end").strip():
                return False
    return True


def show_validation_error(title="Validation Error", message="Please correct the highlighted fields."):
    """
    Show a validation error message box.
    
    Args:
        title (str): Title of the message box.
        message (str): Message text.
    """
    messagebox.showwarning(title, message)


def sanitize_input(text: str) -> str:
    """
    Sanitize input by stripping whitespace and escaping special characters.
    
    Args:
        text (str): Input string to sanitize.
    
    Returns:
        str: Cleaned string.
    """
    return text.strip()


def calculate_age(birth_date: str) -> int:
    """
    Calculate age from birth date.
    
    Args:
        birth_date (str): Birth date in 'dd-mm-yyyy' format.
    
    Returns:
        int: Calculated age.
    """
    from datetime import datetime
    today = datetime.today()
    birth_date = datetime.strptime(birth_date, "%d-%m-%Y")
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age


def calculate_bmi(weight: float, height: float) -> float:
    """
    Calculate BMI from weight and height.
    
    Args:
        weight (float): Weight in kg.
        height (float): Height in meters.
    
    Returns:
        float: BMI value rounded to two decimal places.
    """
    try:
        bmi = weight / (height ** 2)
        return round(bmi, 2)
    except ZeroDivisionError:
        return None


def assess_health(pulse: int, temperature: float, systolic_bp: int, diastolic_bp: int, gender: str, menses: str = None) -> list:
    """
    Assess health based on vital signs and gender-specific information.
    
    Args:
        pulse (int): Pulse rate.
        temperature (float): Body temperature.
        systolic_bp (int): Systolic blood pressure.
        diastolic_bp (int): Diastolic blood pressure.
        gender (str): Gender ('Male' or 'Female').
        menses (str): Last menstrual period in 'dd-mm-yyyy' format.
    
    Returns:
        list: List of health alerts.
    """
    alerts = []
    # Thresholds
    HIGH_SYSTOLIC_BP = 120
    HIGH_DIASTOLIC_BP = 80
    LOW_PULSE = 60
    HIGH_PULSE = 100
    LOW_TEMPERATURE = 36.1
    HIGH_TEMPERATURE = 37.2
    MENSTRUAL_CYCLE_DAYS = 28

    if systolic_bp > HIGH_SYSTOLIC_BP or diastolic_bp > HIGH_DIASTOLIC_BP:
        alerts.append("High blood pressure")

    if pulse < LOW_PULSE or pulse > HIGH_PULSE:
        alerts.append("Abnormal pulse rate")

    if temperature < LOW_TEMPERATURE or temperature > HIGH_TEMPERATURE:
        alerts.append("Abnormal body temperature")

    if gender.lower() == "female" and menses:
        try:
            from datetime import date
            current_date = date.today()
            lmp_date = datetime.strptime(menses, "%d-%m-%Y").date()
            days_since_lmp = (current_date - lmp_date).days
            if days_since_lmp > MENSTRUAL_CYCLE_DAYS:
                alerts.append("Consider pregnancy test")
        except ValueError:
            alerts.append("Invalid date parsing for last menses")
        except Exception as e:
            alerts.append(f"Error assessing menses: {e}")

    if alerts:
        messagebox.showinfo("Health Alerts", "\n".join(alerts))

    return alerts


def generate_patient_id(gender: str, birth_date: str) -> str:
    """
    Generate a unique patient ID based on gender, age, DOB, and random number.
    
    Args:
        gender (str): Gender of the patient.
        birth_date (str): Date of birth in 'dd-mm-yyyy' format.
    
    Returns:
        str: Generated patient ID.
    """
    from datetime import datetime
    import random

    sex_code = '1' if gender == 'Male' else '2'
    birth_date_obj = datetime.strptime(birth_date, '%d-%m-%Y')
    age = calculate_age(birth_date)
    age_code = f"{age:02d}"
    birth_date_code = birth_date_obj.strftime('%d%m%y')
    unique_id = f"{random.randint(1000, 9999):04d}"

    return f"{sex_code}{age_code}{birth_date_code}{unique_id}"


def calculate_ideal_body_weight(height: float, gender: str) -> float:
    """
    Calculate ideal body weight based on Devine formula.
    
    Args:
        height (float): Height in meters.
        gender (str): Gender ('Male' or 'Female').
    
    Returns:
        float: Ideal body weight in kg.
    """
    height_in_inches = height * 39.3701  # Convert height to inches
    if gender == "Male":
        ibw = 50 + 2.3 * (height_in_inches - 60)
    else:
        ibw = 45.5 + 2.3 * (height_in_inches - 60)
    return round(ibw, 2)


def validate_patient_registration_form(
    name_entry: Entry,
    birth_date_entry,
    weight_entry: Entry,
    height_entry: Entry,
    systolic_entry: Entry,
    diastolic_entry: Entry,
    pulse_entry: Entry,
    temperature_entry: Entry,
    telephone_entry: Entry,
    gender_var: tk.StringVar,
    marital_status_var: tk.StringVar
):
    """
    Validate the patient registration form fields.
    
    Args:
        name_entry (Entry): Name field.
        birth_date_entry (DateEntry): Birth date picker.
        weight_entry (Entry): Weight field.
        height_entry (Entry): Height field.
        systolic_entry (Entry): Systolic BP field.
        diastolic_entry (Entry): Diastolic BP field.
        pulse_entry (Entry): Pulse field.
        temperature_entry (Entry): Temperature field.
        telephone_entry (Entry): Telephone field.
        gender_var (StringVar): Gender selection.
        marital_status_var (StringVar): Marital status selection.
    
    Returns:
        bool: True if all fields are valid, False otherwise.
    """
    # Get values from UI elements
    name = name_entry.get()
    birth_date = birth_date_entry.get()
    weight = weight_entry.get()
    height = height_entry.get()
    systolic = systolic_entry.get()
    diastolic = diastolic_entry.get()
    pulse = pulse_entry.get()
    temperature = temperature_entry.get()
    telephone = telephone_entry.get()
    gender = gender_var.get()
    marital_status = marital_status_var.get()

    errors = []

    if not validate_name(name):
        highlight_invalid(name_entry)
        errors.append("Name")
    else:
        reset_highlight(name_entry)

    if not re.match(r'^\d{2}-\d{2}-\d{4}$', birth_date):
        highlight_invalid(birth_date_entry.entry)
        errors.append("Birth Date")
    else:
        reset_highlight(birth_date_entry.entry)

    if not validate_weight(weight):
        highlight_invalid(weight_entry)
        errors.append("Weight")
    else:
        reset_highlight(weight_entry)

    if not validate_height(height):
        highlight_invalid(height_entry)
        errors.append("Height")
    else:
        reset_highlight(height_entry)

    if not validate_blood_pressure(systolic, diastolic):
        highlight_invalid(systolic_entry)
        highlight_invalid(diastolic_entry)
        errors.append("Blood Pressure")
    else:
        reset_highlight(systolic_entry)
        reset_highlight(diastolic_entry)

    if not validate_pulse(pulse):
        highlight_invalid(pulse_entry)
        errors.append("Pulse")
    else:
        reset_highlight(pulse_entry)

    if not validate_temperature(temperature):
        highlight_invalid(temperature_entry)
        errors.append("Temperature")
    else:
        reset_highlight(temperature_entry)

    if not validate_phone(telephone):
        highlight_invalid(telephone_entry)
        errors.append("Telephone")
    else:
        reset_highlight(telephone_entry)

    if gender not in ("Male", "Female"):
        errors.append("Gender")

    if marital_status not in ("Single", "Married", "Widowed"):
        errors.append("Marital Status")

    if errors:
        messagebox.showerror('Input Validation Failed', f"The following fields are invalid: {', '.join(errors)}")
        return False

    return True