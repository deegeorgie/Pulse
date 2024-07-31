import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox, filedialog
import tkcalendar
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import sqlite3
import os
import cv2
from reportlab.lib.pagesizes import A4, letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import fonts
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.units import cm, inch
import time
from datetime import datetime, date
import random
import re
import qrcode
from typing import List
from cryptography.fernet import Fernet

############################################################# FOLDERS SET UP ######################################################
# Define the paths for the MedEase folder and subfolders
documents_folder = os.path.join(os.path.expanduser('~'), 'Documents')
medease_folder = os.path.join(documents_folder, 'Pulse')
invoices_folder = os.path.join(medease_folder, 'invoices')
photos_folder = os.path.join(medease_folder, 'photos')
reports_folder = os.path.join(medease_folder, 'reports')

# Create the MedEase folder and subfolders if they don't exist
if not os.path.exists(medease_folder):
    os.makedirs(medease_folder)
    os.makedirs(invoices_folder)
    os.makedirs(photos_folder)
    os.makedirs(reports_folder)

############################################################# FIRST PART ##############################################################

# Constants
TIME_LIMIT_DAYS = 30  # Usage time limit in days
INSTALL_DATE_FILE = 'install_date.enc'
KEY_FILE = 'secret.key'

def generate_key():
    """Generate a key for encryption and save it into a file."""
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as key_file:
        key_file.write(key)

def load_key():
    """Load the previously generated key."""
    return open(KEY_FILE, 'rb').read()

def encrypt_date(date_str):
    """Encrypt the given date string."""
    key = load_key()
    fernet = Fernet(key)
    encrypted_date = fernet.encrypt(date_str.encode())
    return encrypted_date

def decrypt_date(encrypted_date):
    """Decrypt the given encrypted date."""
    key = load_key()
    fernet = Fernet(key)
    decrypted_date = fernet.decrypt(encrypted_date).decode()
    return decrypted_date

def get_install_date():
    """Retrieve the installation date from the encrypted file or set it if it doesn't exist."""
    if not os.path.exists(KEY_FILE):
        generate_key()
    if not os.path.exists(INSTALL_DATE_FILE):
        # Set the installation date if the file doesn't exist
        install_date = datetime.now().isoformat()
        encrypted_date = encrypt_date(install_date)
        with open(INSTALL_DATE_FILE, 'wb') as f:
            f.write(encrypted_date)
    else:
        # Read the encrypted installation date from the file
        with open(INSTALL_DATE_FILE, 'rb') as f:
            encrypted_date = f.read()
        install_date = decrypt_date(encrypted_date)
    return datetime.fromisoformat(install_date)

def check_time_limit():
    global days_used
    """Check if the usage period has exceeded the time limit."""
    install_date = get_install_date()
    current_date = datetime.now()
    usage_duration = current_date - install_date
    try:
        # Check if 'days' is in the string representation of usage_duration
        if 'days' in str(usage_duration):
            days_used = int(str(usage_duration).split('days')[0])
        else:
            # If 'days' is not present, it means usage_duration is less than a day
            days_used = 0
    except ValueError:
        # Handle other potential value errors
        return "Invalid usage duration format"
    
    days_remaining = TIME_LIMIT_DAYS - days_used

    if usage_duration.days > TIME_LIMIT_DAYS:
        return False
    return True

def check_days_remaining():
    global days_remaining
    install_date = get_install_date()
    current_date = datetime.now()
    usage_duration = current_date - install_date
    days_remaining = TIME_LIMIT_DAYS - days_used
    return days_remaining


def show_expiry_message():
    """Show a message indicating that the time limit has expired."""
    messagebox.showwarning("Time Limit Exceeded", "Your trial period has expired. Please purchase the full version.")

###################################################### END OF FIRST PART ############################################################

################################################## MAIN APPLICATION LOGIC ##########################################################
def about():
    messagebox.showinfo("About", "MedEase App\nVersion 1.0. This is a beta version of\n the patient profiling software.")

def main_app():
    # Connect to SQLite database

    db_path = os.path.join(medease_folder, 'patients.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table if it does not exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY,
        name TEXT,
        birth_date TEXT,
        current_date TEXT,
        age INTEGER,
        weight REAL,
        height REAL,
        bmi REAL,
        weight_status TEXT,
        systolic_bp INTEGER,
        diastolic_bp INTEGER,
        pulse INTEGER,
        temperature REAL,
        glucose REAL,
        cholesterol REAL,
        uric_acid REAL,
        gender TEXT,
        menses TEXT,
        photo_path TEXT,
        address TEXT,
        email TEXT,
        profession TEXT,
        telephone TEXT,
        marital_status TEXT,
        diabetes INTEGER,
        kidney INTEGER,
        epilepsy INTEGER,
        allergy INTEGER,
        asthma INTEGER,
        heart INTEGER,
        cancer INTEGER,
        surgery INTEGER,
        stroke INTEGER,
        hypertension INTEGER,
        hypotension INTEGER,
        alcohol INTEGER,
        sports INTEGER,
        smoking INTEGER,
        ideal_weight REAL,
        alerts TEXT,
        observations TEXT,
        file_UID TEXT,
        qrcode TEXT
    )
    ''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS visits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    name TEXT,
    visit_date TEXT,
    reason TEXT,
    diagnosis TEXT,
    treatment TEXT,
    systolic_bp INTEGER,
    diastolic_bp INTEGER,
    weight REAL,
    telephone INTEGER,
    address TEXT,
    file_UID TEXT,
    qrcode TEXT,
    FOREIGN KEY(patient_id) REFERENCES patients(id)
)''')

    ################################################## PRESCRIPTION AND BILLING ########################################################
    def create_invoice_pdf():
        #Get file path
        f_path = os.path.join(medease_folder, 'business.txt')

        # Read business information from 'business.txt'
        business_info = {}
        try:
            with open(f_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        business_info[key.strip()] = value.strip()

            # Ensure required keys are present in the business info
            required_keys = ['Business Name', 'Business Address', 'Business Phone', 'Business Email', 'Logo Path']
            for key in required_keys:
                if key not in business_info:
                    messagebox.showerror("File Error", f"Missing '{key}' in business.txt")
                    return

            # Extract company info and logo path
            company_info = f"""<b>{business_info['Business Name']}</b><br/>
                            {business_info['Business Address']}<br/>
                            Phone: {business_info['Business Phone']}<br/>
                            Email: {business_info['Business Email']}"""
            logo_path = business_info['Logo Path']

        except IOError as io_err:
            messagebox.showerror("File Error", f"File error occurred: {io_err}")
            return
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while reading business.txt: {e}")
            return

        name = customer_name_entry.get()
        address = address_entry.get()
        phone = tel_entry.get()

        # Calculate the subtotal
        try:
            subtotal = sum(item[3] for item in invoice_list)
        except IndexError as e:
            print(f"Index error while calculating subtotal: {e}")
            return

        salestax = 0.1
        total = subtotal * (1 + salestax)

        # Define the context
        context = {
            "name": name,
            "address": address,
            "phone": phone,
            "invoice_list": invoice_list,
            "subtotal": subtotal,
            "salestax": str(salestax * 100),
            "total": total
        }

        # Sanitize the name for the file name
        sanitized_name = sanitize_filename(context['name'].split(' ')[0])

        # Create 'MedEase/invoices' directory if it doesn't exist
        invoices_dir = os.path.join(medease_folder, 'invoices')
        os.makedirs(invoices_dir, exist_ok=True)

        # Generate the document name
        doc_name = "_BF" + "INV" + "_" + sanitized_name + "_" + datetime.now().strftime("%d-%m-%Y-%H%M%S") + ".pdf"
        doc_path = os.path.join(invoices_dir, doc_name)

        # Create the PDF document
        pdf = SimpleDocTemplate(doc_path, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Add the company logo
        if os.path.exists(logo_path):
            logo = RLImage(logo_path, 2 * inch, 2 * inch)
            elements.append(logo)
        else:
            messagebox.showerror("File Error", f"Logo image not found at path: {logo_path}")
            return
        
        elements.append(Spacer(1, 12))

        # Add company name and contact info
        company_info_paragraph = Paragraph(company_info, styles['Normal'])
        centered_company_info = Table([[company_info_paragraph]], colWidths=[6.5 * inch])
        centered_company_info.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER')
        ]))
        elements.append(centered_company_info)
        elements.append(Spacer(1, 12))

        # Add the title
        title = '<b>INVOICE</b>'
        elements.append(Paragraph(title, styles['Title']))
        elements.append(Spacer(1, 14))

        # Add customer information
        customer_info = f"""<b>ABOUT THE CLIENT</b><br/>
                            Name: {context['name']}<br/>
                            Address: {context['address']}<br/>
                            Telephone: {context['phone']}"""
        elements.append(Paragraph(customer_info, styles['Normal']))
        elements.append(Spacer(1, 12))

        # Add invoice details table
        table_data = [['Item', 'Quantity', 'Unit Price', 'Total']]
        for item in context['invoice_list']:
            table_data.append(item)

        table = Table(table_data, colWidths=[2.5 * inch, 1 * inch, 1.5 * inch, 1.5 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))

        # Add summary
        summary = f"""<b>Summary</b><br/>
                    Subtotal: CFA {context['subtotal']}<br/>
                    VAT: {context['salestax']}%<br/>
                    Total: CFA {context['total']}"""
        elements.append(Paragraph(summary, styles['Normal']))
        elements.append(Spacer(1, 12))

        # Add QR code image if available
        if 'qr' in globals():  # Ensure qr is defined globally
            qr_code_image = RLImage(qr, 2 * inch, 2 * inch)
            elements.append(Spacer(1, 12))
            elements.append(qr_code_image)
        else:
            messagebox.showerror("File Error", "QR code image not defined.")

        # Build the PDF
        pdf.build(elements)

        # Display success message with document name
        messagebox.showinfo("Success", f"Invoice generated successfully: {doc_name}")

        # Return the document name
        return doc_name

    def sanitize_filename(name):
    # Replace any character that is not a letter, digit, or underscore with an underscore
        return re.sub(r'[^\w\s]', '_', name)

    def validate_invoice_list(invoice_list):
        for item in invoice_list:
            if len(item) < 4:
                raise ValueError("Each item in invoice_list must have at least 4 elements.")

    invoice_list = []

    def add_invoice_item(item):
        invoice_list.append(item)

    def add_product():
        item_description = item_description_entry.get()
        quantity = quantity_entry.get()
        price = price_entry.get()
        total = float(quantity) * float(price)
        invoice_item = [item_description, quantity, price, total]
        add_invoice_item(invoice_item)

        #debugging print statement
        print(invoice_item)
        tree.insert('', 'end', values=(item_description, quantity, price, total))
        entry_treatment.insert(END, item_description + '\n')
        clear_entry()

    def clear_entry():
        item_description_entry.delete(0, tk.END)
        quantity_entry.delete(0, tk.END)
        quantity_entry.insert(0, "1")
        price_entry.delete(0, tk.END)

    def search_visit():
        search_term = entry_name.get()
        cursor.execute('''
        SELECT * FROM visits WHERE
        name LIKE ? OR
        file_UID LIKE ?
        ''', ('%'+search_term+'%', '%'+search_term+'%'))
        rows = cursor.fetchall()
        update_visit_tree(rows)

    def update_visit_tree(rows):
        for row in visit_tree.get_children():
            visit_tree.delete(row)
        for row in rows:
            visit_tree.insert("", "end", values=row)

    # FUNCTION TO INSERT NEW VISIT
    def insert_visit(patient_id, visit_date, reason, diagnosis, treatment, systolic_bp, diastolic_bp, weight, telephone, address, file_uid):
        # Query the patients table for current values
        cursor.execute('''
        SELECT name, systolic_bp, diastolic_bp, weight, telephone, address, file_UID FROM patients WHERE id = ?
        ''', (patient_id,))
        patient_data = cursor.fetchone()
        if patient_data:
            name, systolic_bp, diastolic_bp, weight, telephone, address, uid = patient_data

            # Insert into visits table
            cursor.execute('''
            INSERT INTO visits(patient_id, name, visit_date, reason, diagnosis, treatment, systolic_bp, diastolic_bp, weight, telephone, address, file_UID)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (patient_id, name, visit_date, reason, diagnosis, treatment, systolic_bp, diastolic_bp, weight, telephone, address, uid))

            # Commit changes
            conn.commit()
            messagebox.showinfo("Success", "Visit added successfully")
        else:
            messagebox.showerror("Error", "Patient not found!")

    # Function to handle visit form submission
    def submit_visit(event=None):
        try:
            patient_id = int(id_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid patient ID")
            return

        visit_date = entry_visit_date.get()
        reason = entry_reason.get("1.0", tk.END).strip()
        diagnosis = entry_diagnosis.get("1.0", tk.END).strip()
        treatment = entry_treatment.get("1.0", tk.END).strip()
        systolic_bp = syst_entry.get()
        diastolic_bp = diast_entry.get()
        weight = w_entry.get()
        telephone = tel_entry.get()
        address = address_entry.get()
        file_uid = entry_patient_id.get()

        insert_visit(patient_id, visit_date, reason, diagnosis, treatment, systolic_bp, diastolic_bp, weight, telephone, address, file_uid)
        search_visit()

    def display_previous_visit(event):
        selected_item = visit_tree.focus()
        if selected_item:
            visit_values = visit_tree.item(selected_item, 'values')
            name = visit_values[2]
            visit_date = visit_values[3]
            reason = visit_values[4]
            diagnosis = visit_values[5]
            treatment = visit_values[6]
            syst = visit_values[7]
            diast = visit_values[8]
            qr = visit_values[-1]

            lbl_BP.config(text= "Blood Pressure: " + syst + '/' + diast)

            diag_entry.config(state='normal')
            diag_entry.delete("1.0", tk.END)
            diag_entry.insert("1.0", diagnosis)
            diag_entry.config(state='disabled')

            treat_entry.config(state='normal')
            treat_entry.delete("1.0", tk.END)
            treat_entry.insert("1.0", treatment)
            treat_entry.config(state='disabled')

    def display_previous_details():
        global qr
        selected_item = treeview.focus()

        if selected_item:
            item_values = treeview.item(selected_item, 'values')

            patient_id = item_values[0]
            name = item_values[1]
            w = item_values[5]
            syst = item_values[9]
            diast = item_values[10]
            telephone = item_values[22]
            address = item_values[19]
            uid = item_values[-2]
            qr = item_values[-1]
            al = item_values[-4]

            entry_patient_id.config(state='normal')
            entry_patient_id.delete(0, 'end')
            entry_patient_id.insert(0, uid)
            entry_patient_id.config(state='readonly')

            customer_name_entry.config(state='normal')
            customer_name_entry.delete(0, 'end')
            customer_name_entry.insert(0, name)
            customer_name_entry.config(state='readonly')

            address_entry.config(state='normal')
            address_entry.delete(0, 'end')
            address_entry.insert(0, address)
            address_entry.config(state='readonly')

            tel_entry.config(state='normal')
            tel_entry.delete(0, 'end')
            tel_entry.insert(0, telephone)
            tel_entry.config(state='readonly')

            syst_entry.config(state='normal')
            syst_entry.delete(0, 'end')
            syst_entry.insert(0, syst)
            syst_entry.config(state='readonly')

            diast_entry.config(state='normal')
            diast_entry.delete(0, 'end')
            diast_entry.insert(0, diast)
            diast_entry.config(state='readonly')

            w_entry.config(state='normal')
            w_entry.delete(0, 'end')
            w_entry.insert(0, w)
            w_entry.config(state='readonly')

            id_entry.config(state='normal')
            id_entry.delete(0, 'end')
            id_entry.insert(0, patient_id)
            id_entry.config(state='readonly')

            entry_reason.insert("1.0", al)

    def open_billing():
        new_window1 = tk.Toplevel(root)
        new_window1.title("Pulse v_1.0 | Prescription & Billing for " + entry_name.get())
        new_window1.resizable(False, False)
        new_window1.geometry("1250x570")
        # Ensure the new window stays on top
        new_window1.transient(root)
        new_window1.grab_set()
        
        global customer_name_entry, visit_tree, diag_entry, treat_entry, entry_patient_id, lbl_BP, entry_visit_date, qr_label, entry_diagnosis, entry_treatment, entry_reason, address_entry, id_entry, item_description_entry, syst_entry, diast_entry, w_entry, quantity_entry, price_entry, total_entry, tel_entry, tree

        p_frame = tk.LabelFrame(new_window1, padx=10, pady=5)
        p_frame.grid(row=0, column=0, sticky='e')

        right_frame = tk.LabelFrame(new_window1, text='All visits for ' + entry_name.get() + ' appear here', padx=10, pady=5)
        right_frame.grid(row=0, column=6, sticky='n')

        lbl_BP = ttk.Label(right_frame)
        lbl_BP.grid(row=1, column=0, columnspan=3, sticky='w')

        diag_entry = tk.Text(right_frame, width=25, height=4, bg='lightgreen')
        diag_entry.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky='w')

        treat_entry = tk.Text(right_frame, width=25, height=4, bg='lightgreen')
        treat_entry.grid(row=3, column=0, columnspan=4, padx=10, pady=5, sticky='w')

        products = [
            '999 Weitai', 'Amoxillin', 'Anchanjian', 'Axiluowei', 'Banlanguen Keli', 'Baoji Wan', 'Bi Yang Lin', 'Bishushi Pian',
            'Biyankang Wan', 'Buluofen', 'Chao ren tui', 'Cusuan Lujidin', 'Cusuan Ponisong', 'Dabaidu', 'Diyanying', 'Ear Drops',
            'Ejiao Keli', 'Famotiding', 'Feng Shi Ling', 'Wei Kang Ling', 'Fentai Han Pian', 'Antonding', 'Fufang Danshen', 'Weishengsu B',
            'Weishengsu B12', 'Weishengsu AD', 'Weishengsu E', 'Fuyankang', 'Glibenclamide', 'Hantaoye Pian', 'Huangbingshaxing', 'Jia Gaotong',
            'Jingsuo Gujing Wan', 'Jinwei Pian', 'Kamaxiping', 'Keteling', 'Leinitiding', 'Li Yang Ying', 'Libaweilin', 'Linkemeisu',
            'Liuwei Dihuang Wan', 'Lo Han Kuo', 'Lompicin', 'Luoxuanmeisu', 'Lymphshamei', 'Malaisuan', 'Maodongking', 'Nanbao Jiaonang', 'Nubao Jiaonang',
            'Nifediping', 'Niuhuang Jiedu Pian', 'Nuofushaxing', 'Po Wo Tong', 'Pulean Pian', 'Qiangli Tianma'
        ]

        ttk.Label(p_frame, text="Patient Name").grid(row=0, column=0, padx=10, pady=5, sticky='w')
        customer_name_entry = ttk.Entry(p_frame)
        customer_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky='w')

        ttk.Label(p_frame, text="File ID:").grid(row=0, column=2, padx=10, pady=5, sticky='w')
        entry_patient_id = ttk.Entry(p_frame)
        entry_patient_id.grid(row=0, column=3, padx=10, pady=5, sticky='w')

        ttk.Label(p_frame, text="Visit Date:").grid(row=0, column=4, padx=10, pady=5, sticky='w')
        entry_visit_date = DateEntry(p_frame)
        entry_visit_date.grid(row=0, column=5, padx=10, pady=5, sticky='w')
        
        ttk.Label(p_frame, text="Address").grid(row=1, column=0, padx=10, pady=5, sticky='w')
        address_entry = ttk.Entry(p_frame)
        address_entry.grid(row=1, column=1, padx=10, pady=5, sticky='w')

        ttk.Label(p_frame, text="Telephone").grid(row=1, column=2, padx=10, pady=5, sticky='w')
        tel_entry = ttk.Entry(p_frame)
        tel_entry.grid(row=1, column=3, padx=10, pady=5, sticky='w')

        ttk.Label(p_frame, text="Syst. BP").grid(row=1, column=4, padx=10, pady=5, sticky="w")
        syst_entry = ttk.Entry(p_frame)
        syst_entry.grid(row=1, column=5, padx=10, pady=5, sticky='w')

        ttk.Label(p_frame, text="Diast. BP").grid(row=2, column=0, padx=10, pady=5, sticky='w')
        diast_entry = ttk.Entry(p_frame)
        diast_entry.grid(row=2, column=1, padx=10, pady=5, sticky='w')

        ttk.Label(p_frame, text="Weight").grid(row=2, column=2, padx=10, pady=5, sticky='w')
        w_entry = ttk.Entry(p_frame)
        w_entry.grid(row=2, column=3, padx=10, pady=5, sticky='w')

        ttk.Label(p_frame, text='Patient ID').grid(row=2, column=4, padx=10, pady=5, sticky='w')
        id_entry = ttk.Entry(p_frame)
        id_entry.grid(row=2, column=5, padx=10, pady=5, sticky='w')

        ttk.Label(p_frame, text="Reason:").grid(row=3, column=0, padx=10, pady=5, sticky='w')
        entry_reason = tk.Text(p_frame, width=17, height=3)
        entry_reason.grid(row=3, column=1, rowspan=2, columnspan=2, padx=10, pady=5, sticky='w')

        ttk.Label(p_frame, text="Diagnosis:").grid(row=3, column=2, padx=10, pady=5, sticky='w')
        entry_diagnosis = tk.Text(p_frame, width=17, height=3)
        entry_diagnosis.grid(row=3, column=3, rowspan=2, columnspan=2, padx=10, pady=5, sticky='w')

        ttk.Label(p_frame, text="Treatment:").grid(row=3, column=4, padx=10, pady=5, sticky='w')
        entry_treatment = tk.Text(p_frame, width=17, height=3)
        entry_treatment.grid(row=3, column=5, rowspan=2, columnspan=2, padx=10, pady=5, sticky='w')
        
        ttk.Label(p_frame, text="Product").grid(row=6, column=0, padx=10, pady=5, sticky='w')
        prod_var = tk.StringVar()
        item_description_entry = ttk.Combobox(p_frame, textvariable=prod_var, values=products, width=15)
        item_description_entry.grid(row=6, column=1, padx=10, pady=5, sticky='w')
        
        ttk.Label(p_frame, text="Quantity").grid(row=7, column=0, padx=10, pady=5, sticky='w')
        quantity_entry = tk.Spinbox(p_frame, width=5, from_=1, to=20, increment=1)
        quantity_entry.grid(row=7, column=1, padx=10, pady=5, sticky='w')
        
        ttk.Label(p_frame, text="Price").grid(row=8, column=0, padx=10, pady=5, sticky='w')
        price_entry = ttk.Entry(p_frame, width=7)
        price_entry.grid(row=8, column=1, padx=10, pady=5, sticky='w')
        
        tk.Button(p_frame, text="Add New Visit", border=0, bg='#57a1f8', fg='white', cursor='hand2', command=submit_visit).grid(row=8, column=5, pady=10)
        tk.Button(p_frame, text="Add A Product", border=0, bg='#57a1f8', fg='white', cursor='hand2', command=add_product).grid(row=8, column=1, columnspan=2, pady=10, sticky='e')
        
        # Add Treeview widget
        columns = ('Description', 'Quantity', 'Price', 'Total')
        tree = ttk.Treeview(p_frame, columns=columns, show='headings')
        tree.heading('Description', text='Description')
        tree.heading('Quantity', text='Quantity')
        tree.heading('Price', text='Price')
        tree.heading('Total', text='Total')
        tree.grid(row=9, column=0, columnspan=6, padx=10, pady=5)
        
        ttk.Label(p_frame, text="Total").grid(row=10, column=4, padx=10, pady=5, sticky='w')
        total_entry = ttk.Entry(p_frame)
        total_entry.grid(row=10, column=5, padx=10, pady=5, sticky='w')
        
        # Add buttons to save the invoice
        save_pdf_button = tk.Button(p_frame, text="Generate Invoice", border=0, bg='#57a1f8', fg='white', cursor='hand2', command=create_invoice_pdf)
        save_pdf_button.grid(row=10, column=0, padx=10, pady=10)

        tree_columns = ("v_id", "Id", "Name", "v_date")
        visit_tree = ttk.Treeview(right_frame, columns=tree_columns, show='headings')
        visit_tree.heading('v_id', text='v_id')
        visit_tree.heading('Id', text='Id')
        visit_tree.heading('Name', text='Name')
        visit_tree.heading('v_date', text='v_date')
        visit_tree.grid(row=0, column=0, columnspan=4, padx=10, pady=5)

        # Set the headings and column widths
        for col in tree_columns:
            visit_tree.heading(col, text=col)
            visit_tree.column(col, width=85)

        visit_tree.bind("<<TreeviewSelect>>", display_previous_visit)

        display_previous_details()
        search_visit()
        
############################################################# END OF PRESCRIPTION AND BILLING LOGIC #############################
    # Function to load and display the placeholder image
    def load_image(path, use_resize=True):
        img = Image.open(path)
        if use_resize:
            img = img.resize((200, 200), Image.LANCZOS)
        else:
            img.thumbnail((200, 200))
        img = ImageTk.PhotoImage(img)
        photo_label.configure(image=img)
        photo_label.image = img

    placeholder_path = 'med_ico.png'
    #photo_path = placeholder_path

    def create_patient_qr_code(name, uid, birth_date, gender, telephone, marital_status, allergy_status, surgery_status, cancer_status, hypertension_status):
        """
        Create a QR code containing patient information and save it to a file named after the patient's ID.

        Parameters:
        patient_info (dict): Dictionary containing patient information.
                            Expected keys: 'name', 'id', 'birth_date', 'gender', 'telephone', 'systolic_bp', 'diastolic_bp', 'pulse', 'temperature'

        Example of patient_info dictionary:
        patient_info = {
            'name': 'John Doe',
            'id': '123456',
            'birth_date': '1990-01-01',
            'gender': 'Male',
            'telephone': '555-1234'
        }
        """
        # Convert patient info dictionary to a formatted string
        info_str = (
            f"Name: {name}\n"
            f"ID: {uid}\n"
            f"Birth Date: {birth_date}\n"
            f"Gender: {gender}\n"
            f"Telephone: {telephone}\n"
            f"Marital Status: {marital_status}\n" 
            f"Any Allergies?: {allergy_status}\n"
            f"Surgeries: {surgery_status}\n"
            f"Cancer: {cancer_status}\n"
            f"Hypertension: {hypertension_status}\n"
        )

        # Create a QR code object
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        # Add data to the QR code
        qr.add_data(info_str)
        qr.make(fit=True)

        # Create an image from the QR code
        img = qr.make_image(fill='black', back_color='white')

        # Create 'MedEase/photos' directory if it doesn't exist
        photos_dir = os.path.join(medease_folder, 'photos')
        os.makedirs(photos_dir, exist_ok=True)

        # Define the filename using the patient's ID
        filename = f"{uid}.png"
        filepath = os.path.join(photos_dir, filename)

        # Save the image to a file
        img.save(filepath)

        return filepath

    def calculate_bmi(weight, height):
        try:
            bmi = weight / (height ** 2)
            return round(bmi, 2)
        except ZeroDivisionError:
            return None

    def calculate_age(birth_date):
        today = datetime.today()
        birth_date = datetime.strptime(birth_date, "%d-%m-%Y")
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age

    def assess_health(pulse: int, temperature: float, systolic_bp: int, diastolic_bp: int, gender: str, menses: str = None) -> List[str]:
        """
        Assess health based on vital signs and gender-specific information.

        Parameters:
        - systolic_bp (int): Systolic blood pressure.
        - diastolic_bp (int): Diastolic blood pressure.
        - pulse (int): Pulse rate.
        - temperature (float): Body temperature in Celsius.
        - gender (str): Gender of the person ("Male" or "Female").
        - menses (str, optional): Date of the last menstrual period in YYYY-MM-DD format.

        Returns:
        - List[str]: List of health alerts.
        """
        alerts = []

        # Constants for thresholds
        HIGH_SYSTOLIC_BP = 120
        HIGH_DIASTOLIC_BP = 80
        LOW_PULSE = 60
        HIGH_PULSE = 100
        LOW_TEMPERATURE = 36.1
        HIGH_TEMPERATURE = 37.2
        MENSTRUAL_CYCLE_DAYS = 28

        # Debug prints
        print(f"Inputs - Systolic BP: {systolic_bp}, Diastolic BP: {diastolic_bp}, Pulse: {pulse}, Temperature: {temperature}, Gender: {gender}, Menses: {menses}")

        # Check for high blood pressure
        if systolic_bp > HIGH_SYSTOLIC_BP or diastolic_bp > HIGH_DIASTOLIC_BP:
            alerts.append("High blood pressure")

        # Check for abnormal pulse rate
        if pulse < LOW_PULSE or pulse > HIGH_PULSE:
            alerts.append("Abnormal pulse rate")

        # Check for abnormal body temperature
        if temperature < LOW_TEMPERATURE or temperature > HIGH_TEMPERATURE:
            alerts.append("Abnormal body temperature")

        # Check for menses related alert for females
        if gender.lower() == "female" and menses:
            # Validate date format
            if re.match(r'^\d{2}-\d{2}-\d{4}$', menses):
                try:
                    current_date = date.today()
                    lmp_date = datetime.strptime(menses, "%d-%m-%Y").date()
                    days_since_lmp = (current_date - lmp_date).days
                    print(f"Days since last menstrual period: {days_since_lmp}")
                    if days_since_lmp > MENSTRUAL_CYCLE_DAYS:
                        alerts.append("Consider pregnancy test")
                except ValueError:
                    alerts.append("Invalid date parsing for last menses")
            else:
                alerts.append("Invalid date format for last menses")

            if alerts:
                messagebox.showinfo("Health Alerts", "\n".join(alerts))
        return alerts

    def generate_patient_id(gender, birth_date):
        # Encode gender
        if gender == 'Male':
            sex_code = '1'
        else:
            sex_code = '2'
        
        # Calculate age
        age = calculate_age(birth_date)
        age_code = f'{age:02d}'
        
        # Encode date of birth as YYMMDD
        birth_date_code = datetime.strptime(birth_date, '%d-%m-%Y').strftime('%d%m%y')
        
        # Generate a unique identifier
        unique_id = f'{random.randint(1000, 9999):04d}'
        
        # Generate unique patient ID
        patient_id = f'{sex_code}{age_code}{birth_date_code}{unique_id}'
        
        return patient_id

    def check_fields():
        if entry_name.get() and entry_weight.get() and entry_height.get() and entry_systolic.get() and entry_diastolic.get() and entry_pulse.get() and entry_temperature.get() and entry_telephone.get():
            register_button.config(state=tk.NORMAL) 
        else:
            register_button.config(state=tk.DISABLED)

    def register_patient():
        global qr
        try:
            name = entry_name.get()
            birth_date = birth_date_entry.get()
            current_date = datetime.today().strftime('%d-%m-%Y')
            weight = entry_weight.get()
            height = entry_height.get()
            systolic_bp = entry_systolic.get()
            diastolic_bp = entry_diastolic.get()
            pulse = entry_pulse.get()
            temperature = entry_temperature.get()
            glucose = entry_glucose.get()
            cholesterol = entry_cholesterol.get()
            uric = entry_uricemia.get()
            gender = gender_var.get()
            menses = None if gender_var.get() == "Male" else last_menstrual_period_entry.get()
            address = entry_address.get()
            email = entry_email.get()
            profession = entry_profession.get()
            telephone = entry_telephone.get()
            marital_status = marital_status_var.get()
        
            if not name or not weight or not height or not systolic_bp or not diastolic_bp or not pulse or not temperature or not gender or not telephone or not marital_status:
                messagebox.showerror('Error', 'Please fill all required fields')
                return

            weight = float(weight)
            height = float(height)
            systolic_bp = int(systolic_bp)
            diastolic_bp = int(diastolic_bp)
            pulse = int(pulse)
            temperature = float(temperature)
            bmi = calculate_bmi(weight, height)
            weight_status = weight_status = "Underweight" if bmi < 18.5 else "Normal" if 18.5 <= bmi < 24.9 else "Overweight" if 25 <= bmi < 29.9 else "Obese"
            age = calculate_age(birth_date)
            ideal_weight = calculate_ideal_body_weight(height, gender)
            uid = generate_patient_id(gender, birth_date)

            # Additional health-related details
            diabetes_status = a.get()
            kidney_status = renal.get()
            epilepsy_status = epilepsy.get()
            allergy_status = allergy.get()
            asthma_status = asthma.get()
            heart_status = heart.get()
            cancer_status = cancer.get()
            surgery_status = surgery.get()
            stroke_status = stroke.get()
            hypertension_status = hypertension.get()
            hypotension_status = hypotension.get()
            smoking_status = smoking.get()
            physical_activity = sports.get()
            alcohol_consumption = alcohol.get()
            observation_notes = observations.get("1.0", tk.END).strip()
            qr = create_patient_qr_code(name, uid, birth_date, gender, telephone, marital_status, allergy_status, surgery_status, cancer_status, hypertension_status)
            alerts = ' '.join(assess_health(pulse, temperature, systolic_bp, diastolic_bp, gender, menses))

            cursor.execute('''
            INSERT INTO patients (name, birth_date, current_date, age, weight, height, bmi, weight_status, 
                                systolic_bp, diastolic_bp, pulse, temperature, glucose, cholesterol, uric_acid, gender, menses, photo_path, address, 
                                email, profession, telephone, marital_status, diabetes, kidney, epilepsy, 
                                allergy, asthma, heart, cancer, surgery, stroke, hypertension, hypotension, 
                                smoking, sports, alcohol, ideal_weight, alerts, observations, file_UID, qrcode)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, birth_date, current_date, age, weight, height, bmi, weight_status, systolic_bp, diastolic_bp, 
                pulse, temperature, glucose, cholesterol, uric, gender, menses, photo_path, address, email, profession, telephone, marital_status,
                diabetes_status, kidney_status, epilepsy_status, allergy_status, asthma_status, heart_status,
                cancer_status, surgery_status, stroke_status, hypertension_status, hypotension_status,
                smoking_status, physical_activity, alcohol_consumption, ideal_weight, alerts, observation_notes, uid, qr))
        
            conn.commit()
            clear_fields()
            refresh_treeview()
            messagebox.showinfo("Success", "Patient registered successfully!")

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    # Function to clear all input fields
    def clear_fields():
        entry_name.delete(0, tk.END)
        birth_date_entry.set_date(datetime.now())
        entry_weight.delete(0, tk.END)

        entry_height.delete(0, tk.END)
        entry_height.insert(0, "1.50")

        entry_systolic.delete(0, tk.END)
        entry_systolic.insert(0, "120")

        entry_diastolic.delete(0, tk.END)
        entry_diastolic.insert(0, "80")

        entry_pulse.delete(0, tk.END)
        entry_pulse.insert(0, "65")

        entry_temperature.delete(0, tk.END)
        entry_temperature.insert(0, "37.0")

        entry_ibw.delete(0, tk.END)

        entry_glucose.delete(0, tk.END)
        entry_cholesterol.delete(0, tk.END)
        entry_uricemia.delete(0, tk.END)
        entry_address.delete(0, tk.END)
        entry_email.delete(0, tk.END)
        entry_profession.delete(0, tk.END)
        entry_telephone.delete(0, tk.END)
        gender_var.set("Male")
        last_menstrual_period_entry.set_date(datetime.now())
        marital_status_var.set("Single")
        a.set(0)
        renal.set(0)
        epilepsy.set(0)
        allergy.set(0)
        asthma.set(0)
        heart.set(0)
        cancer.set(0)
        surgery.set(0)
        stroke.set(0)
        hypertension.set(0)
        hypotension.set(0)
        smoking.set(0)
        sports.set(0)
        alcohol.set(0)
        observations.delete("1.0", tk.END)
        load_image(placeholder_path)
        check_fields()
        toggle_menstrual_period_entry("Male")
        # Global variable to store the photo path

    def take_picture():
        global photo_path

        def update_frame():
            nonlocal frame, photo_image
            ret, frame = cap.read()
            if ret:
                cv2_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2_image)
                photo_image = ImageTk.PhotoImage(image=img)
                canvas.create_image(0, 0, anchor=tk.NW, image=photo_image)
                camera_window.after(10, update_frame)  # Schedule the next frame update

        def capture_image():
            nonlocal frame, captured_frame
            if frame is not None:
                captured_frame = frame.copy()
                save_image()  # Save the image immediately after capture

        def save_image():
            nonlocal captured_frame
            if captured_frame is not None:
                # Generate a unique file name
                file_name = f"photo_{int(time.time())}.jpg"
                photo_path = os.path.join(photos_folder, file_name)
                
                # Save the captured image
                cv2.imwrite(photo_path, captured_frame)
                print(f"Image saved to: {photo_path}")  # Debugging statement
                load_image(photo_path)
                camera_window.destroy()
                cap.release()
            else:
                messagebox.showerror("Save Error", "No image to save.")

        def reset_image():
            nonlocal captured_frame
            captured_frame = None
            print("Camera reset. Capture a new image.")  # Debugging statement

        def close_camera():
            cap.release()
            cv2.destroyAllWindows()
            camera_window.destroy()

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Camera Error", "Failed to open the camera.")
            return

        camera_window = tk.Toplevel()
        camera_window.title("Camera")
        camera_window.geometry("640x480")  # Set the dimensions of the camera window
        camera_window.wm_attributes("-topmost", True)  # Set the window to stay on top

        canvas = tk.Canvas(camera_window, width=640, height=400)
        canvas.pack()

        button_frame = tk.Frame(camera_window)
        button_frame.pack(fill=tk.X, pady=10)

        capture_button = tk.Button(button_frame, text="Capture", command=capture_image)
        capture_button.pack(side=tk.LEFT, padx=10)

        reset_button = tk.Button(button_frame, text="Reset", command=reset_image)
        reset_button.pack(side=tk.LEFT, padx=10)

        close_button = tk.Button(button_frame, text="Close", command=close_camera)
        close_button.pack(side=tk.RIGHT, padx=10)

        frame = None
        captured_frame = None
        photo_image = None

        update_frame()  # Start the frame update loop

        camera_window.mainloop()
    
    def add_photo():
        global photo_path
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        if file_path:
            photo_path = file_path
            load_image(file_path)
        else:
            messagebox.showwarning("Warning", "No image selected")
        return photo_path
    
    def update_patient():
        global photo_path
        try:
            selected_item = treeview.focus()
            if not selected_item:
                messagebox.showerror("Selection Error", "No patient selected to update.")
                return

            item_values = treeview.item(selected_item, 'values')
            patient_id = item_values[0]
            name = entry_name.get()
            birth_date = birth_date_entry.get()
            current_date = datetime.today().strftime('%d-%m-%Y')
            weight = entry_weight.get()
            height = entry_height.get()
            systolic_bp = entry_systolic.get()
            diastolic_bp = entry_diastolic.get()
            pulse = entry_pulse.get()
            temperature = entry_temperature.get()
            glucose = entry_glucose.get()
            cholesterol = entry_cholesterol.get()
            uric = entry_uricemia.get()
            gender = gender_var.get()
            menses = None if gender_var.get() == "Male" else last_menstrual_period_entry.get()
            address = entry_address.get()
            email = entry_email.get()
            profession = entry_profession.get()
            telephone = entry_telephone.get()
            marital_status = marital_status_var.get()
            
            if not name or not weight or not height or not systolic_bp or not diastolic_bp or not pulse or not temperature or not gender or not telephone or not marital_status:
                messagebox.showerror('Error', 'Please fill all required fields')
                return

            weight = float(weight)
            height = float(height)
            systolic_bp = int(systolic_bp)
            diastolic_bp = int(diastolic_bp)
            pulse = int(pulse)
            temperature = float(temperature)
            bmi = calculate_bmi(weight, height)
            weight_status = "Underweight" if bmi < 18.5 else "Normal" if 18.5 <= bmi < 24.9 else "Overweight" if 25 <= bmi < 29.9 else "Obese"
            age = calculate_age(birth_date)

            # Additional health-related details
            diabetes_status = a.get()
            kidney_status = renal.get()
            epilepsy_status = epilepsy.get()
            allergy_status = allergy.get()
            asthma_status = asthma.get()
            heart_status = heart.get()
            cancer_status = cancer.get()
            surgery_status = surgery.get()
            stroke_status = stroke.get()
            hypertension_status = hypertension.get()
            hypotension_status = hypotension.get()
            smoking_status = smoking.get()
            physical_activity = sports.get()
            alcohol_consumption = alcohol.get()
            observation_notes = observations.get("1.0", tk.END).strip()
            uid = generate_patient_id(gender, birth_date)
            alerts = ' '.join(assess_health(pulse, temperature, systolic_bp, diastolic_bp, gender, menses))

            cursor.execute('''
            UPDATE patients SET name=?, birth_date=?, age=?, weight=?, height=?, bmi=?, weight_status=?, 
                            systolic_bp=?, diastolic_bp=?, pulse=?, temperature=?, glucose=?, cholesterol=?, uric_acid=?, 
                            gender=?, menses=?, photo_path=?, address=?, 
                            email=?, profession=?, telephone=?, marital_status=?, diabetes=?, kidney=?, epilepsy=?, 
                            allergy=?, asthma=?, heart=?, cancer=?, surgery=?, stroke=?, hypertension=?, hypotension=?, 
                            smoking=?, sports=?, alcohol=?, alerts=?, observations=?, file_UID=?
            WHERE id=?
            ''', (name, birth_date, age, weight, height, bmi, weight_status, systolic_bp, diastolic_bp, 
                pulse, temperature, glucose, cholesterol, uric, gender, menses, photo_path, address, email, 
                profession, telephone, marital_status, diabetes_status, kidney_status, epilepsy_status, 
                allergy_status, asthma_status, heart_status,
                cancer_status, surgery_status, stroke_status, hypertension_status, hypotension_status, 
                smoking_status, physical_activity, alcohol_consumption, alerts, observation_notes, uid, patient_id))
            
            conn.commit()
            clear_fields()
            refresh_treeview()
            messagebox.showinfo("Success", "Patient updated successfully!")

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    def search_patient():
        search_term = search_entry.get()
        cursor.execute('''
        SELECT * FROM patients WHERE
        name LIKE ? OR
        birth_date LIKE ? OR
        address LIKE ? OR
        email LIKE ? OR
        profession LIKE ? OR
        telephone LIKE ? OR
        marital_status LIKE ? OR
        gender LIKE ? OR
        file_UID LIKE ?
        ''', ('%'+search_term+'%', '%'+search_term+'%', '%'+search_term+'%', '%'+search_term+'%', '%'+search_term+'%', '%'+search_term+'%', '%'+search_term+'%', '%'+search_term+'%', '%'+search_term+'%'))
        rows = cursor.fetchall()
        update_treeview(rows)

    def display_selected_item(event):
        global photo_path
        selected_item = treeview.focus()

        if selected_item:
            billing_button.config(state=tk.NORMAL)

            item_values = treeview.item(selected_item, 'values')
            entry_name.delete(0, tk.END)
            entry_name.insert(0, item_values[1])

            birth_date_entry.set_date(item_values[2])

            entry_weight.delete(0, tk.END)
            entry_weight.insert(0, item_values[5])

            entry_height.delete(0, tk.END)
            entry_height.insert(0, item_values[6])

            entry_ibw.delete(0, tk.END)
            entry_ibw.insert(0, item_values[38])

            entry_systolic.delete(0, tk.END)
            entry_systolic.insert(0, item_values[9])

            entry_diastolic.delete(0, tk.END)
            entry_diastolic.insert(0, item_values[10])

            entry_pulse.delete(0, tk.END)
            entry_pulse.insert(0, item_values[11])

            entry_temperature.delete(0, tk.END)
            entry_temperature.insert(0, item_values[12])

            entry_glucose.delete(0, tk.END)
            entry_glucose.insert(0, item_values[13])

            entry_cholesterol.delete(0, tk.END)
            entry_cholesterol.insert(0, item_values[14])

            entry_uricemia.delete(0, tk.END)
            entry_uricemia.insert(0, item_values[15])

            gender_var.set(item_values[16])

            toggle_menstrual_period_entry(item_values[16])

            if item_values[17] is None or item_values[17] == "":
                last_menstrual_period_entry.set_date(date.today())
            else:
                try:
                    last_menstrual_period_entry.set_date(item_values[17])
                except ValueError:
                    # Handle invalid date format
                    last_menstrual_period_entry.set_date(date.today())

            entry_address.delete(0, tk.END)
            entry_address.insert(0, item_values[19])

            entry_email.delete(0, tk.END)
            entry_email.insert(0, item_values[20])

            entry_profession.delete(0, tk.END)
            entry_profession.insert(0, item_values[21])

            entry_telephone.delete(0, tk.END)
            entry_telephone.insert(0, item_values[22])

            marital_status_var.set(item_values[23])
            
            # Additional health-related details
            a.set(item_values[24])
            renal.set(item_values[25])
            epilepsy.set(item_values[26])
            allergy.set(item_values[27])
            asthma.set(item_values[28])
            heart.set(item_values[29])
            cancer.set(item_values[30])
            surgery.set(item_values[31])
            stroke.set(item_values[32])
            hypertension.set(item_values[33])
            hypotension.set(item_values[34])
            alcohol.set(item_values[35])
            sports.set(item_values[36])
            smoking.set(item_values[37])
            observations.delete("1.0", tk.END)
            observations.insert("1.0", item_values[40])
  
            photo_path = item_values[18]
            if photo_path and os.path.exists(photo_path):
                load_image(photo_path)
            else:
                load_image(placeholder_path)

    def delete_patient():
        selected_item = treeview.focus()
        if not selected_item:
            messagebox.showerror("Selection Error", "No patient selected to delete.")
            return

        item_values = treeview.item(selected_item, 'values')
        patient_id = item_values[0]
        
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this patient?")
        if confirm:
            cursor.execute("DELETE FROM patients WHERE id=?", (patient_id,))
            conn.commit()
            clear_fields()
            refresh_treeview()
            messagebox.showinfo("Success", "Patient deleted successfully!")

    def refresh_treeview():

        for row in treeview.get_children():
            treeview.delete(row)

        cursor.execute("SELECT * FROM patients")

        for row in cursor.fetchall():
            treeview.insert("", tk.END, values=row)

        clear_fields()

        billing_button.config(state=tk.DISABLED)

        if search_entry.get():
            search_entry.delete(0, tk.END)

    def update_treeview(rows):
        for row in treeview.get_children():
            treeview.delete(row)
        for row in rows:
            treeview.insert("", "end", values=row)

    def calculate_ideal_body_weight(height, gender):
        height_in_inches = height * 39.3701 # Convert height from meters to inches
        if gender == "Male":
            ibw = 50 + 2.3 * (height_in_inches - 60)
        else:
            ibw = 45.5 + 2.3 * (height_in_inches - 60)
        return round(ibw, 2)
    
    def calculate_fat_percentage(age, gender, bmi):
        pass


    def generate_pdf(patient_id, file_path, db_path, photo_path=None):
        conn = None

        try:
            # Get file 
            f_path = os.path.join(medease_folder, 'business.txt')
            # Read business information from 'business.txt'
            business_info = {}
            with open(f_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        business_info[key.strip()] = value.strip()

            # Ensure required keys are present in the business info
            required_keys = ['Business Name', 'Business Address', 'Business Phone', 'Business Email', 'Logo Path']
            for key in required_keys:
                if key not in business_info:
                    messagebox.showerror("File Error", f"Missing '{key}' in business.txt")
                    return

            # Extract footer text and logo path from business information
            footer_text = f"{business_info['Business Name']}, {business_info['Business Address']}, {business_info['Business Phone']} | {business_info['Business Email']}"
            logo_path = business_info['Logo Path']

            # Connect to the database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Fetch patient data
            cursor.execute("SELECT * FROM patients WHERE id=?", (patient_id,))
            patient_data = cursor.fetchone()
            if not patient_data:
                messagebox.showerror("Error", "Patient data not found.")
                return

            # Create a new PDF file with A4 page size
            c = canvas.Canvas(file_path, pagesize=A4)
            width, height = A4

            # Helper function to draw text
            def draw_text(x, y, text, bold=False):
                if bold:
                    c.setFont("Helvetica-Bold", 9)
                else:
                    c.setFont("Helvetica", 9)
                c.drawString(x, y, text)

            # Document header
            draw_text(50, height - 50, f"PATIENT REPORT - FILE ID: {patient_data[-2]}", bold=True)
            draw_text(50, height - 80, f"Date: {datetime.today().strftime('%Y-%m-%d')}", bold=True)
            c.line(50, height - 90, width - 50, height - 90)

            # Basic patient information
            info = [
                ("Name", patient_data[1]), ("Birth Date", patient_data[2]), ("Age", patient_data[4]),
                ("Weight", f"{patient_data[5]} kg"), ("Height", f"{patient_data[6]} m"), ("BMI", patient_data[7]),
                ("Weight Status", patient_data[8]), ("Ideal Body Weight", patient_data[38]), ("Systolic BP", f"{patient_data[9]} mmHg"),
                ("Diastolic BP", f"{patient_data[10]} mmHg"), ("Pulse", f"{patient_data[11]} bpm"),
                ("Temperature", f"{patient_data[12]} °C"), ("Gender", patient_data[16]),
                ("Last Menstrual Period", patient_data[17]), ("Address", patient_data[19]),
                ("Email", patient_data[20]), ("Profession", patient_data[21]), ("Telephone", patient_data[22]),
                ("Marital Status", patient_data[23]), ("Alerts", patient_data[39]), ("Observations", patient_data[40])
            ]

            y_pos = height - 120
            for label, value in info:
                draw_text(50, y_pos, f"{label}: {value}")
                y_pos -= 20

            # Patient photo
            if photo_path and os.path.exists(photo_path):
                c.drawImage(photo_path, 400, height - 150, width=100, height=100)

            # Draw QR code image
            qr_path = patient_data[-1]
            if os.path.exists(qr_path):
                c.drawImage(qr_path, 50, 50, width=100, height=100)
            else:
                messagebox.showerror("File Error", f"QR code image not found at path: {qr_path}")

            # Footer
            #footer_text = "CABINET NATURAL WELLNESS, Bobo Dioulasso, +226 74911538 | 60354400 | deebodiong@gmail.com"
            draw_text(50, 30, footer_text, bold=True)

            # Footer logo
            #logo_path = 'well.jpg'
            if os.path.exists(logo_path):
                c.drawImage(logo_path, width - 150, 40, width=150, height=150)
            else:
                messagebox.showerror("File Error", f"Logo image not found at path: {logo_path}")

            # Finalize PDF
            c.showPage()
            c.save()

        except sqlite3.Error as db_err:
            messagebox.showerror("Database Error", f"Database error occurred: {db_err}")
        except IOError as io_err:
            messagebox.showerror("File Error", f"File error occurred: {io_err}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        finally:
            # Ensure the database connection is closed if it was opened
            if conn:
                conn.close()
    
    def on_generate_pdf(treeview, db_path):
        selected_item = treeview.focus()
        if not selected_item:
            messagebox.showerror("Selection Error", "No patient selected to generate PDF.")
            return

        item_values = treeview.item(selected_item, 'values')
        patient_id = item_values[0]
        
        # Generate a unique file name
        file_name = f"report_{patient_id}_{int(time.time())}.pdf"
        file_path = os.path.join(reports_folder, file_name)
        
        generate_pdf(patient_id, file_path, db_path, photo_path)
        messagebox.showinfo("Success", f"Patient report generated successfully!\nSaved to: {file_path}")

    # Function to enable/disable menstrual period entry based on gender selection
    def toggle_menstrual_period_entry(event):
        if gender_var.get() == "Female":
            last_menstrual_period_entry.configure(state='enabled')
        else:
            last_menstrual_period_entry.set_date(date.today())
            last_menstrual_period_entry.configure(state='disabled')

    # Initialize camera
    cap = cv2.VideoCapture(0)

    def close_app():
        cap.release()
        root.destroy()

    def validate_email(content):
        # Regular expression for validating an email
        email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if re.match(email_pattern, content):
            entry_email.config(bg='lightgreen')  # Valid email
            return True
        else:
            entry_email.config(bg='orange')  # Invalid email
            return False
        
    def on_invalid():
        print("Invalid email address!")

    def exit_app():
        root.quit()

######################################### EDITING BUSINESS DETAILS ###########################################################

    def on_entry_click(event, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, "end")
            entry.config(fg='black')

    def on_focusout(event, entry, placeholder):
        if entry.get() == '':
            entry.insert(0, placeholder)
            entry.config(fg='grey')

    def create_placeholder_entry(parent, placeholder):
        entry = tk.Entry(parent, width=40, fg='grey')
        entry.insert(0, placeholder)
        entry.bind('<FocusIn>', lambda event: on_entry_click(event, entry, placeholder))
        entry.bind('<FocusOut>', lambda event: on_focusout(event, entry, placeholder))
        return entry

    def open_new_window():
        def save_business_details():
            business_name = business_name_entry.get()
            business_address = business_address_entry.get()
            business_web = business_web_entry.get()
            business_mail = business_mail_entry.get()
            business_phone = business_phone_entry.get()
            business_id = business_id_entry.get()
            logo_path = logo_path_var.get()

            # Check for required fields
            if (business_name == 'Enter Business name' or not business_name.strip() or
                business_address == 'Enter Business address' or not business_address.strip() or
                business_mail == 'Enter Business email' or not business_mail.strip() or
                business_phone == 'Enter Business phone' or not business_phone.strip()):
                messagebox.showerror("Error", "Please fill in all required fields.")
                return

            # Define the file name and path
            file_name = "business.txt"
            file_path = os.path.join(medease_folder, file_name)

            # Write the business details to the file
            try:
                with open(file_path, "w") as file:
                    file.write(f"Business Name: {business_name}\n")
                    file.write(f"Business Address: {business_address}\n")
                    file.write(f"Business Website: {business_web}\n")
                    file.write(f"Business Email: {business_mail}\n")
                    file.write(f"Business Phone: {business_phone}\n")
                    file.write(f"Business Tax ID: {business_id}\n")
                    file.write(f"Logo Path: {logo_path}\n")
                    file.write("\n")
                messagebox.showinfo("Success", f"Business details saved successfully to: {file_path}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save business details: {str(e)}")

        def select_logo():
            file_path = filedialog.askopenfilename(
                title="Select a logo file",
                filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif"), ("All files", "*.*")]
            )
            if file_path:
                logo_path_var.set(file_path)

        new_window = tk.Toplevel(root)
        new_window.title("Pulse v_1.0| Add your business details")
        new_window.geometry("550x350")
        new_window.resizable(False, False)

        # Ensure the new window stays on top
        new_window.transient(root)
        new_window.grab_set()

        img = tk.PhotoImage(file='med_ico.png')
        tk.Label(new_window, image=img).grid(row=0, column=0, padx=50, pady=50, sticky="nw")

        # Keep a reference to the image to prevent garbage collection
        new_window.img = img

        p_frame = tk.Frame(new_window)
        p_frame.grid(row=0, column=1, padx=20, pady=30, sticky="ne")

        heading = tk.Label(p_frame, text="Edit Business Details", fg='#57a1f8')
        heading.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        business_name_entry = create_placeholder_entry(p_frame, 'Enter Business name')
        business_name_entry.grid(row=1, column=0, columnspan=2, pady=5)

        business_address_entry = create_placeholder_entry(p_frame, 'Enter Business address')
        business_address_entry.grid(row=2, column=0, columnspan=2, pady=5)

        business_web_entry = create_placeholder_entry(p_frame, 'Enter Business website')
        business_web_entry.grid(row=3, column=0, columnspan=2, pady=5)

        business_mail_entry = create_placeholder_entry(p_frame, 'Enter Business email')
        business_mail_entry.grid(row=4, column=0, columnspan=2, pady=5)

        business_phone_entry = create_placeholder_entry(p_frame, 'Enter Business phone')
        business_phone_entry.grid(row=5, column=0, columnspan=2, pady=5)

        business_id_entry = create_placeholder_entry(p_frame, 'Enter Tax ID')
        business_id_entry.grid(row=6, column=0, columnspan=2, pady=5)

        logo_path_var = tk.StringVar()
        tk.Label(p_frame, text="Logo File:", bg='white').grid(row=7, column=0, sticky='e', pady=5)
        tk.Entry(p_frame, textvariable=logo_path_var, width=40, state='readonly', fg='black', border=0, bg='white').grid(row=7, column=1, pady=5)
        tk.Button(p_frame, text="Browse", command=select_logo, bg='#57a1f8', fg='white').grid(row=8, column=0, padx=5, pady=5, sticky='e')


        tk.Button(p_frame, text='Register Business', bg='#57a1f8', fg='white', border=0, command=save_business_details).grid(row=8, column=1, columnspan=2, pady=20)
################################################## END OF EDITING BUSINESS DETAILS #####################################################
   
    """Main application logic."""
    root = tk.Tk()
    root.title("Pulse v_1.0")
    root.state('zoomed')
    root.resizable(False, False)

    usage_label = tk.Label(root, text= str(check_days_remaining()) + " days remaining before the end of your trial period.", font=("Helvetica", 9, "bold"), bg="lightgreen")
    usage_label.pack(side=tk.TOP, padx=5, pady=5)

    h_label = tk.Label(root, text="This is a basic, test version of Pulse, your patient profiling software. The full-fledged version is coming soon. | Developer: Georges BODIONG | https://deebodiong.quarto.pub | deebodiong@gmail.com", font=("Helvetica", 9, "bold"), bg="lightblue")
    h_label.pack(side=tk.BOTTOM, padx=5, pady=5)

    # Create the menu
    menu_bar = tk.Menu(root)

    # Create the File menu
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="New Patient", command=clear_fields)
    file_menu.add_command(label="Billing", state=DISABLED, command=open_billing)
    file_menu.add_command(label="Pharmacy", state=DISABLED)
    file_menu.add_command(label="Dashboard", state=DISABLED)
    file_menu.add_command(label="Settings", command=open_new_window)
    file_menu.add_command(label="Exit", command=exit_app)
    menu_bar.add_cascade(label="File", menu=file_menu)

    #create the Edit menu
    edit_menu = tk.Menu(menu_bar, tearoff=0)
    edit_menu.add_command(label="Copy", state=DISABLED)
    edit_menu.add_command(label="Paste", state=DISABLED)
    menu_bar.add_cascade(label="Edit", menu=edit_menu)

    # Create the Help menu
    help_menu = tk.Menu(menu_bar, tearoff=0)
    help_menu.add_command(label="About", command=about)
    menu_bar.add_cascade(label="Help", menu=help_menu)

    # Attach the menu to the root window
    root.config(menu=menu_bar)

    #Create a style object
    style = ttk.Style()

    # Add icon image for application
    photo = ImageTk.PhotoImage(file = "med_ico.png")
    root.iconphoto(True, photo)

    validate_command = root.register(validate_email)
    invalid_command = root.register(on_invalid)

    # Left frame for form
    frame_form = tk.Frame(root)
    frame_form.pack(side=tk.LEFT, padx=10, pady=10)

    #Frame to contain patient infos
    widgets_frame = tk.LabelFrame(frame_form, text="DEMOGRAPHICS | CONSTANTS", padx=10, pady=10)
    widgets_frame.grid(row=0, column=0, columnspan=4, sticky=tk.NS)

    # New frame for displaying patient data
    data_frame = ttk.LabelFrame(frame_form, text="PATIENTS DATABASE", padding=(10, 10))
    data_frame.grid(row=0, column=5, sticky='s')

    # Health history frame
    health_history_frame = ttk.LabelFrame(frame_form, text="ADDITIONAL HEALTH RELATED DETAILS", padding=(10, 10))
    health_history_frame.grid(row=0, column=5, sticky='nw')

    # Name
    tk.Label(widgets_frame, text="Name:").grid(row=0, column=2, sticky=tk.W, pady=5)
    entry_name = tk.Entry(widgets_frame)
    entry_name.grid(row=0, column=3, pady=5, sticky='w')

    # Birth Date
    tk.Label(widgets_frame, text="Birth Date:").grid(row=1, column=2, sticky=tk.W, pady=5)
    birth_date_entry = DateEntry(widgets_frame, date_pattern='dd-mm-y')
    birth_date_entry.grid(row=1, column=3, pady=5, sticky='w')

    # Gender
    tk.Label(widgets_frame, text="Gender:").grid(row=2, column=2, sticky=tk.W, pady=5)
    gender_var = tk.StringVar(value="Male")
    gender_combo = ttk.Combobox(widgets_frame, textvariable=gender_var, values=["Male", "Female"], width=12)
    gender_combo.grid(row=2, column=3, sticky=tk.W)

    #Last Menses (for ladies only)
    tk.Label(widgets_frame, text="Last Menses:").grid(row=3, column=2, sticky=tk.W, pady=5)
    last_menstrual_period_entry = DateEntry(widgets_frame, date_pattern='dd-mm-y')
    last_menstrual_period_entry.configure(state='disabled')
    last_menstrual_period_entry.grid(row=3, column=3, pady=5, sticky='w')

    # Weight
    tk.Label(widgets_frame, text="Weight (kg):").grid(row=4, column=2, sticky=tk.W, pady=5)
    entry_weight = tk.Entry(widgets_frame, width=7)
    entry_weight.grid(row=4, column=3, pady=5, sticky='w')

    # Height
    tk.Label(widgets_frame, text="Height (m):").grid(row=5, column=2, sticky=tk.W, pady=5)
    default_height = tk.StringVar()
    default_height.set("1.50")
    entry_height = tk.Spinbox(widgets_frame, from_=0.8, to=3.0, increment=0.01, format='%.2f', width=5, textvariable=default_height)
    entry_height.grid(row=5, column=3, pady=5, sticky='w')

    # Ideal body weight
    tk.Label(widgets_frame, text="Ideal Weight (kgs):").grid(row=6, column=2, sticky=tk.W, pady=5)
    entry_ibw =tk.Entry(widgets_frame, width=7)
    entry_ibw.grid(row=6, column=3, padx=5, sticky='w')
    #entry_ibw.configure(state='readonly')

    # Systolic BP
    tk.Label(widgets_frame, text="Systolic BP:").grid(row=7, column=0, sticky=tk.W, pady=5)
    default_syst = tk.StringVar()
    default_syst.set("120")
    entry_systolic = tk.Spinbox(widgets_frame, from_= 50, to=250, increment=1, width=5, textvariable=default_syst)
    entry_systolic.grid(row=7, column=1, pady=5, sticky='w')

    # Diastolic BP
    tk.Label(widgets_frame, text="Diastolic BP:").grid(row=7, column=2, sticky=tk.W, pady=5)
    default_diast = tk.StringVar()
    default_diast.set("80")
    entry_diastolic = tk.Spinbox(widgets_frame, from_=40, to=200, increment=1, width=5, textvariable=default_diast)
    entry_diastolic.grid(row=7, column=3, pady=5, sticky='w')

    # Pulse
    tk.Label(widgets_frame, text="Pulse:").grid(row=8, column=0, sticky=tk.W, pady=5)
    default_pulse = tk.StringVar()
    default_pulse.set("65")
    entry_pulse = tk.Spinbox(widgets_frame, from_=40, to=150, increment=1, width=5, textvariable=default_pulse)
    entry_pulse.grid(row=8, column=1, pady=5, sticky='w')

    # Temperature
    default_temperature = tk.StringVar()
    default_temperature.set("37.0")
    tk.Label(widgets_frame, text="Temperature (°C):").grid(row=8, column=2, sticky=tk.W, pady=5)
    entry_temperature = tk.Spinbox(widgets_frame, width=5, from_=30.0, to=45.0, increment=0.1, format='%.1f', textvariable=default_temperature)
    entry_temperature.grid(row=8, column=3, pady=5, sticky='w')

    # Address
    tk.Label(widgets_frame, text="Address:").grid(row=9, column=0, sticky=tk.W, pady=5)
    entry_address = tk.Entry(widgets_frame)
    entry_address.grid(row=9, column=1, pady=5)

    #Blood Glucose
    tk.Label(widgets_frame, text="Glucose(umol/L):").grid(row=9, column=2, sticky=tk.W, pady=5)
    entry_glucose = tk.Entry(widgets_frame, width=7)
    entry_glucose.grid(row=9, column=3, pady=5, sticky='w')

    # Email
    tk.Label(widgets_frame, text="Email:").grid(row=10, column=0, sticky=tk.W, pady=5)
    entry_email = tk.Entry(widgets_frame, validate='focusout', validatecommand=(validate_command, '%P'), invalidcommand=invalid_command)
    entry_email.grid(row=10, column=1, pady=5)

    #Cholesterol
    tk.Label(widgets_frame, text="Cholesterol(umol/L):").grid(row=10, column=2, sticky=tk.W, pady=5)
    entry_cholesterol = tk.Entry(widgets_frame, width=7)
    entry_cholesterol.grid(row=10, column=3, pady=5, sticky='w')

    # Profession
    tk.Label(widgets_frame, text="Profession:").grid(row=11, column=0, sticky=tk.W, pady=5)
    entry_profession = tk.Entry(widgets_frame)
    entry_profession.grid(row=11, column=1, pady=5, sticky='w')

    #Uricemia
    tk.Label(widgets_frame, text="Uric Acid(mmol/L):").grid(row=11, column=2, sticky=tk.W, pady=5)
    entry_uricemia = tk.Entry(widgets_frame, width=7)
    entry_uricemia.grid(row=11, column=3, pady=5, sticky='w')

    # Telephone
    tk.Label(widgets_frame, text="Telephone:").grid(row=12, column=0, sticky=tk.W, pady=5)
    entry_telephone = tk.Entry(widgets_frame)
    entry_telephone.grid(row=12, column=1, pady=5)

    # Marital Status
    tk.Label(widgets_frame, text="Marital Status:").grid(row=13, column=0, sticky=tk.W, pady=5)
    marital_status_var = tk.StringVar(value="Single")
    tk.Radiobutton(widgets_frame, text="Single", variable=marital_status_var, value="Single").grid(row=13, column=1, sticky=tk.W)
    tk.Radiobutton(widgets_frame, text="Married", variable=marital_status_var, value="Married").grid(row=13, column=1, sticky=tk.E)
    tk.Radiobutton(widgets_frame, text="Widowed", variable=marital_status_var, value="Widowed").grid(row=13, column=2, sticky=tk.W)

    # Add search button

    tk.Label(health_history_frame, text="Filter Database").grid(row=7, column=0, sticky=tk.W, pady=5)
    search_entry = tk.Entry(health_history_frame)
    search_entry.grid(row=7, column=1, padx=5)
    search_button = tk.Button(health_history_frame, text='Search DB', border=0, bg='#57a1f8', fg='white', cursor='hand2', command=search_patient)
    search_button.grid(row=7, column=2, pady=5, sticky='w')

    # Create a custom button by configuring a Label widget with the image
    refresh_button = tk.Button(health_history_frame, text="Refresh DB", border=0, bg='#57a1f8', fg='white', cursor='hand2', command=refresh_treeview)
    refresh_button.grid(row=7, column=3, pady=10, sticky='e')

    # Open prescription and billing
    billing_button = tk.Button(health_history_frame, text="Prescription & Billing", border=0, bg='#57a1f8', fg='white', cursor='hand2', state=tk.DISABLED, command=open_billing)
    billing_button.grid(row=7, column=7, pady=10, sticky='e', columnspan=2)

    # Photo

    photo_button = tk.Button(widgets_frame, text="Choose Photo", border=0, bg='#57a1f8', fg='white', cursor='hand2', command=add_photo)
    photo_button.grid(row=6, column=0, pady=5)

    shoot_button = tk.Button(widgets_frame, text="Take A Picture", border=0, bg='#57a1f8', fg='white', cursor='hand2', command=take_picture)
    shoot_button.grid(row=6, column=1, pady=5)

    # Photo label
    photo_label = tk.Label(widgets_frame)
    photo_label.grid(row=0, column=0, rowspan=6, columnspan=2, pady=5)
    #photo_path = tk.StringVar()
    load_image(placeholder_path)

    # Buttons
    button_frame = tk.Frame(widgets_frame)
    button_frame.grid(row=16, column=0, columnspan=5, pady=10, sticky='w')

    register_button = tk.Button(button_frame, text="Register Patient", border=0, bg='#57a1f8', fg='white', cursor='hand2', command=register_patient, state=tk.DISABLED)
    register_button.grid(row=0, column=1, padx=5, sticky='w')

    update_button = tk.Button(button_frame, text="Update Patient", border=0, bg='#57a1f8', fg='white', cursor='hand2', command=update_patient)
    update_button.grid(row=0, column=2, padx=5, sticky='w')

    pdf_button = tk.Button(button_frame, text="Save to PDF", border=0, bg='#57a1f8', fg='white', cursor='hand2', command=lambda: on_generate_pdf(treeview, db_path))
    pdf_button.grid(row=0, column=3, padx=5, sticky='w')

    clear_button = tk.Button(button_frame, text="Clear Form", border=0, bg='#57a1f8', fg='white', cursor='hand2', command=clear_fields)
    clear_button.grid(row=0, column=4, padx=5, sticky='w')

    delete_button = tk.Button(button_frame, text="Delete Patient", border=0, bg='#57a1f8', fg='white', cursor='hand2', command=delete_patient)
    delete_button.grid(row=0, column=5, padx=5, sticky='w')

    # Health Conditions Section
    ttk.Label(health_history_frame, text="Health Conditions [Check all that apply]", font=("Helvetica", 13, "bold")).grid(row=0, column=0, columnspan=5, pady=10, sticky=tk.W)

    a = tk.IntVar()
    ttk.Checkbutton(health_history_frame, text="Diabetes", variable=a).grid(row=1, column=0, sticky=tk.W, pady=2)

    renal = tk.IntVar()
    ttk.Checkbutton(health_history_frame, text="Kidney Disease", variable=renal).grid(row=1, column=1, sticky=tk.W, pady=2)

    epilepsy = tk.IntVar()
    ttk.Checkbutton(health_history_frame, text="Epilepsy", variable=epilepsy).grid(row=1, column=2, sticky=tk.W, pady=2)

    allergy = tk.IntVar()
    ttk.Checkbutton(health_history_frame, text="Allergy", variable=allergy).grid(row=1, column=3, sticky=tk.W, pady=2)

    asthma = tk.IntVar()
    ttk.Checkbutton(health_history_frame, text="Asthma", variable=asthma).grid(row=1, column=4, sticky=tk.W, pady=2)

    heart = tk.IntVar()
    ttk.Checkbutton(health_history_frame, text="Heart Disease", variable=heart).grid(row=2, column=0, sticky=tk.W, pady=2)

    cancer = tk.IntVar()
    ttk.Checkbutton(health_history_frame, text="Cancer", variable=cancer).grid(row=2, column=1, sticky=tk.W, pady=2)

    surgery = tk.IntVar()
    ttk.Checkbutton(health_history_frame, text="Surgery", variable=surgery).grid(row=2, column=2, sticky=tk.W, pady=2)

    stroke = tk.IntVar()
    ttk.Checkbutton(health_history_frame, text="Stroke", variable=stroke).grid(row=2, column=3, sticky=tk.W, pady=2)

    smoking = tk.IntVar()
    ttk.Checkbutton(health_history_frame, text="Smoking", variable=smoking).grid(row=2, column=4, sticky=tk.W, pady=2)

    hypotension = tk.IntVar()
    ttk.Checkbutton(health_history_frame, text="Hypotension", variable=hypotension).grid(row=3, column=0, sticky=tk.W, pady=2)

    hypertension = tk.IntVar()
    ttk.Checkbutton(health_history_frame, text="Hypertension", variable=hypertension).grid(row=3, column=1, sticky=tk.W, pady=2)

    sports = tk.IntVar()
    ttk.Checkbutton(health_history_frame, text="Sports", variable=sports).grid(row=3, column=2, sticky=tk.W, pady=2)

    alcohol = tk.IntVar()
    ttk.Checkbutton(health_history_frame, text="Alcohol", variable=alcohol).grid(row=3, column=3, sticky=tk.W, pady=2)

    # Observation Notes
    ttk.Label(health_history_frame, text="Observations:").grid(column=6, row=0, sticky=tk.W)
    observations = tk.Text(health_history_frame, width=41, height=8)
    observations.grid(column=6, row=1, rowspan=3, columnspan=3, sticky=tk.E)

    # Define the columns for the Treeview
    columns = (
        "ID", "Name", "Birth Date", "Visit Date", "Age", "Weight", "Height", "BMI", "Weight Status",
        "Systolic BP", "Diastolic BP", "Pulse", "Temp.", "Gender", "Photo Path", "Address",
        "Email", "Profession", "Telephone", "Marital Status"
    )

    # Create the Treeview widget
    treeview = ttk.Treeview(data_frame, columns=columns, show="headings")

    # Set the headings and column widths
    for col in columns:
        treeview.heading(col, text=col)
        treeview.column(col, width=60)

    # Create the horizontal scrollbar
    scrollbar_x = ttk.Scrollbar(data_frame, orient=tk.HORIZONTAL, command=treeview.xview)

    # Create the vertical scrollbar
    scrollbar_y = ttk.Scrollbar(data_frame, orient=tk.VERTICAL, command=treeview.yview)

    # Configure the scrollbars
    treeview.configure(xscrollcommand=scrollbar_x.set, yscrollcommand=scrollbar_y.set)

    # Pack the Treeview and scrollbars
    scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    treeview.pack(fill=tk.BOTH, expand=True)

    # Bind the gender selection to the toggle function
    gender_combo.bind("<<ComboboxSelected>>", toggle_menstrual_period_entry)

    treeview.bind("<<TreeviewSelect>>", display_selected_item)

    entry_name.bind("<KeyRelease>", lambda event: check_fields())
    entry_weight.bind("<KeyRelease>", lambda event: check_fields())
    entry_height.bind("<KeyRelease>", lambda event: check_fields())
    entry_systolic.bind("<KeyRelease>", lambda event: check_fields())
    entry_diastolic.bind("<KeyRelease>", lambda event: check_fields())
    entry_pulse.bind("<KeyRelease>", lambda event: check_fields())
    entry_temperature.bind("<KeyRelease>", lambda event: check_fields())
    entry_telephone.bind("<KeyRelease>", lambda event: check_fields())

    refresh_treeview()  # Populate the treeview with data from the database

    # Run the application
    root.mainloop()

if __name__ == "__main__":
    if check_time_limit():
        main_app()
    else:
        show_expiry_message()