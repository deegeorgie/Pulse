# pulse/utils/pdf_generator.py

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from tkinter import messagebox


def read_business_info(medease_folder):
    """
    Reads business information from 'business.txt' located in MedEase folder.
    
    Args:
        medease_folder (str): Path to the MedEase directory.
    
    Returns:
        dict: Dictionary containing business info like name, address, etc.
    """
    business_info_path = os.path.join(medease_folder, 'business.txt')
    business_info = {}

    try:
        with open(business_info_path, 'r') as file:
            for line in file:
                if ':' in line:
                    key, value = line.strip().split(':', 1)
                    business_info[key.strip()] = value.strip()
    except FileNotFoundError:
        raise FileNotFoundError(f"Business info file not found at {business_info_path}")
    except Exception as e:
        raise RuntimeError(f"Error reading business info: {e}")

    required_keys = ['Business Name', 'Business Address', 'Business Phone', 'Business Email', 'Logo Path']
    missing = [key for key in required_keys if key not in business_info]
    if missing:
        raise ValueError(f"Missing keys in business.txt: {', '.join(missing)}")

    return business_info


def create_invoice_pdf(medease_folder, invoice_list, customer_data):
    """
    Generates a PDF invoice for a patient visit or prescription.
    
    Args:
        medease_folder (str): Base path to MedEase folder.
        invoice_list (list): List of items in the invoice.
        customer_data (dict): Customer details like name, address, phone, etc.
    
    Returns:
        str: Path to the generated PDF file.
    """
    try:
        business_info = read_business_info(medease_folder)

        # Sanitize customer name for filename
        sanitized_name = sanitize_filename(customer_data['name'].split(' ')[0])

        # Define paths
        invoices_dir = os.path.join(medease_folder, 'invoices')
        os.makedirs(invoices_dir, exist_ok=True)
        doc_name = f"_BFINV_{sanitized_name}_{datetime.now().strftime('%d-%m-%Y-%H%M%S')}.pdf"
        doc_path = os.path.join(invoices_dir, doc_name)

        # Setup document
        pdf = SimpleDocTemplate(doc_path, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Add logo
        logo_path = business_info.get("Logo Path")
        if logo_path and os.path.exists(logo_path):
            logo = RLImage(logo_path, 2 * 48, 2 * 48)  # width, height in points
            elements.append(logo)
            elements.append(Spacer(1, 12))
        else:
            messagebox.showwarning("Warning", "Logo image not found. Skipping.")

        # Company info
        company_info = (
            f"<b>{business_info['Business Name']}</b><br/>"
            f"{business_info['Business Address']}<br/>"
            f"Phone: {business_info['Business Phone']}<br/>"
            f"Email: {business_info['Business Email']}"
        )
        elements.append(Paragraph(company_info, styles["Normal"]))
        elements.append(Spacer(1, 12))

        # Title
        elements.append(Paragraph("<b>INVOICE</b>", styles["Title"]))
        elements.append(Spacer(1, 14))

        # Customer info
        customer_info = (
            f"<b>Customer Information</b><br/>"
            f"Name: {customer_data['name']}<br/>"
            f"Address: {customer_data['address']}<br/>"
            f"Telephone: {customer_data['phone']}"
        )
        elements.append(Paragraph(customer_info, styles["Normal"]))
        elements.append(Spacer(1, 12))

        # Invoice table
        table_data = [['Item', 'Qty', 'Unit Price', 'Total']]
        for item in invoice_list:
            table_data.append(item)

        table = Table(table_data, colWidths=[3 * 72, 0.8 * 72, 1.5 * 72, 1.5 * 72])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))

        # Summary
        subtotal = sum(item[3] for item in invoice_list)
        salestax = 0.1
        total = subtotal * (1 + salestax)

        summary = (
            f"<b>Summary</b><br/>"
            f"Subtotal: CFA {subtotal}<br/>"
            f"VAT: {salestax * 100}%<br/>"
            f"Total: CFA {total}"
        )
        elements.append(Paragraph(summary, styles["Normal"]))

        # Build PDF
        pdf.build(elements)
        messagebox.showinfo("Success", f"Invoice generated successfully: {doc_name}")
        return doc_path

    except Exception as e:
        messagebox.showerror("PDF Error", f"Failed to generate invoice: {e}")
        return None


def generate_patient_report(patient_data, medease_folder, photo_path=None):
    """
    Generate a detailed PDF report for a specific patient.
    
    Args:
        patient_data (tuple): Raw data from the database for a patient.
        medease_folder (str): Base path to MedEase folder.
        photo_path (str): Optional path to patient photo.
    
    Returns:
        str: Path to the generated PDF file.
    """
    try:
        business_info = read_business_info(medease_folder)

        # File setup
        reports_dir = os.path.join(medease_folder, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        file_name = f"report_{patient_data[0]}_{int(datetime.now().timestamp())}.pdf"
        file_path = os.path.join(reports_dir, file_name)

        c = canvas.Canvas(file_path, pagesize=A4)
        width, height = A4

        def draw_text(x, y, text, bold=False):
            font = "Helvetica-Bold" if bold else "Helvetica"
            c.setFont(font, 10)
            c.drawString(x, y, text)

        # Header
        draw_text(50, height - 50, f"PATIENT REPORT - FILE ID: {patient_data[-2]}", bold=True)
        draw_text(50, height - 70, f"Date: {datetime.now().strftime('%Y-%m-%d')}", bold=True)
        c.line(50, height - 80, width - 50, height - 80)

        # Patient Info
        info = [
            ("Name", patient_data[1]), ("Birth Date", patient_data[2]), ("Age", patient_data[4]),
            ("Weight", f"{patient_data[5]} kg"), ("Height", f"{patient_data[6]} m"), ("BMI", patient_data[7]),
            ("Weight Status", patient_data[8]), ("Ideal Body Weight", patient_data[38]), ("Systolic BP", f"{patient_data[9]} mmHg"),
            ("Diastolic BP", f"{patient_data[10]} mmHg"), ("Pulse", f"{patient_data[11]} bpm"),
            ("Temperature", f"{patient_data[12]} °C"), ("Gender", patient_data[16]),
            ("Last Menses", patient_data[17]), ("Address", patient_data[19]),
            ("Email", patient_data[20]), ("Profession", patient_data[21]), ("Telephone", patient_data[22]),
            ("Marital Status", patient_data[23]), ("Alerts", patient_data[39]), ("Observations", patient_data[40])
        ]

        y_pos = height - 100
        for label, value in info:
            draw_text(50, y_pos, f"{label}: {value}")
            y_pos -= 15

        # Insert photo
        if photo_path and os.path.exists(photo_path):
            c.drawImage(photo_path, 400, height - 150, width=100, height=100)

        # Footer
        footer_text = f"{business_info['Business Name']}, {business_info['Business Address']}, {business_info['Business Phone']} | {business_info['Business Email']}"
        draw_text(50, 30, footer_text, bold=True)

        # Logo
        logo_path = business_info.get("Logo Path")
        if logo_path and os.path.exists(logo_path):
            c.drawImage(logo_path, width - 150, 40, width=150, height=150)

        c.save()
        messagebox.showinfo("Success", f"Patient report generated successfully:\n{file_path}")
        return file_path

    except Exception as e:
        messagebox.showerror("PDF Error", f"Failed to generate report: {e}")
        return None


def sanitize_filename(name):
    """Sanitize the filename by replacing invalid characters."""
    import re
    return re.sub(r'[^\w\s]', '_', name)