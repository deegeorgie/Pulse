# pulse/utils/qr_code.py

import os
import qrcode
from PIL import Image, ImageDraw
from tkinter import messagebox


def create_patient_qr_code(name, uid, birth_date, gender, telephone, marital_status,
                            allergy_status, surgery_status, cancer_status,
                            hypertension_status, output_dir="photos"):
    """
    Generate and save a QR code containing patient information.

    Args:
        name (str): Patient's full name.
        uid (str): Unique ID for the patient.
        birth_date (str): Birth date in 'dd-mm-yyyy' format.
        gender (str): Gender ('Male' or 'Female').
        telephone (str): Contact number.
        marital_status (str): Marital status (e.g., 'Single', 'Married').
        allergy_status (int): 0 or 1 indicating presence of allergies.
        surgery_status (int): 0 or 1 indicating history of surgery.
        cancer_status (int): 0 or 1 indicating family/personal cancer history.
        hypertension_status (int): 0 or 1 indicating hypertension.
        output_dir (str): Directory where the QR code should be saved.

    Returns:
        str: Path to the generated QR code image.
    """
    try:
        # Format patient info into a string
        info_str = (
            f"Name: {name}\n"
            f"ID: {uid}\n"
            f"Birth Date: {birth_date}\n"
            f"Gender: {gender}\n"
            f"Telephone: {telephone}\n"
            f"Marital Status: {marital_status}\n"
            f"Allergies: {'Yes' if allergy_status else 'No'}\n"
            f"Surgeries: {'Yes' if surgery_status else 'No'}\n"
            f"Cancer: {'Yes' if cancer_status else 'No'}\n"
            f"Hypertension: {'Yes' if hypertension_status else 'No'}"
        )

        # Create base QR code
        qr = qrcode.QRCode(
            version=3,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(info_str)
        qr.make(fit=True)

        # Create image from QR Code instance
        img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

        # Ensure output directory exists
        full_output_path = os.path.join(output_dir, uid)
        os.makedirs(full_output_path, exist_ok=True)

        # Define the filename using the patient's UID
        filename = f"{uid}_qr.png"
        filepath = os.path.join(full_output_path, filename)

        # Save the image
        img.save(filepath)

        return filepath

    except Exception as e:
        messagebox.showerror("QR Code Error", f"Failed to generate QR code:\n{e}")
        return None