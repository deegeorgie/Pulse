# pulse/database/patient_manager.py

import sqlite3
import os
from datetime import datetime
from tkinter import messagebox
import random
import tkinter as tk

def connect_db(db_path):
    """Connect to SQLite database."""
    try:
        return sqlite3.connect(db_path)
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Could not connect to database:\n{e}")
        raise

def calculate_age(birth_date_str):
    birth_date = datetime.strptime(birth_date_str, "%d-%m-%Y")
    today = datetime.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def calculate_bmi(weight, height):
    try:
        return round(float(weight) / (float(height) ** 2), 2)
    except ZeroDivisionError:
        return None

def calculate_ideal_body_weight(height, gender):
    height_in_inches = float(height) * 39.3701
    if gender == "Male":
        return round(50 + 2.3 * (height_in_inches - 60), 2)
    else:
        return round(45.5 + 2.3 * (height_in_inches - 60), 2)

def register_patient(db_path, form_data):
    conn = connect_db(db_path)
    cursor = conn.cursor()
    try:
        name = form_data['name']
        birth_date = form_data['birth_date']
        gender = form_data['gender']
        weight = float(form_data['weight'])
        height = float(form_data['height'])
        systolic_bp = int(form_data['systolic_bp'])
        diastolic_bp = int(form_data['diastolic_bp'])
        pulse = int(form_data['pulse'])
        temperature = float(form_data['temperature'])
        address = form_data['address']
        email = form_data['email']
        profession = form_data['profession']
        telephone = form_data['telephone']
        marital_status = form_data['marital_status']

        age = calculate_age(birth_date)
        bmi = calculate_bmi(weight, height)
        ideal_weight = calculate_ideal_body_weight(height, gender)
        weight_status = "Underweight" if bmi < 18.5 else "Normal" if 18.5 <= bmi < 24.9 else "Overweight" if 25 <= bmi < 29.9 else "Obese"

        cursor.execute('''
            INSERT INTO patients (
                name, birth_date, current_date, age, weight, height, 
                bmi, weight_status, systolic_bp, diastolic_bp, pulse, temperature, 
                glucose, cholesterol, uric_acid, gender, menses, photo_path, address, 
                email, profession, telephone, marital_status, diabetes, kidney, epilepsy, 
                allergy, asthma, heart, cancer, surgery, stroke, hypertension, hypotension, 
                smoking, sports, alcohol, ideal_weight, alerts, observations, file_UID, qrcode
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            name, birth_date, datetime.now().strftime("%d-%m-%Y"), age, weight, height,
            bmi, weight_status, systolic_bp, diastolic_bp, pulse, temperature,
            0, 0, 0, gender, None, "", address, email, profession,
            telephone, marital_status, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            ideal_weight, "", "", generate_patient_id(gender, birth_date), ""
        ))

        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Patient registered successfully.")
    except Exception as e:
        messagebox.showerror("Registration Error", f"Failed to register patient:\n{e}")

def update_patient(db_path, form_data, patient_id):
    conn = connect_db(db_path)
    cursor = conn.cursor()
    try:
        name = form_data['name']
        birth_date = form_data['birth_date']
        gender = form_data['gender']
        weight = float(form_data['weight'])
        height = float(form_data['height'])
        systolic_bp = int(form_data['systolic_bp'])
        diastolic_bp = int(form_data['diastolic_bp'])
        pulse = int(form_data['pulse'])
        temperature = float(form_data['temperature'])
        address = form_data['address']
        email = form_data['email']
        profession = form_data['profession']
        telephone = form_data['telephone']
        marital_status = form_data['marital_status']

        age = calculate_age(birth_date)
        bmi = calculate_bmi(weight, height)
        ideal_weight = calculate_ideal_body_weight(height, gender)
        weight_status = "Underweight" if bmi < 18.5 else "Normal" if 18.5 <= bmi < 24.9 else "Overweight" if 25 <= bmi < 29.9 else "Obese"

        cursor.execute('''
            UPDATE patients SET 
                name=?, birth_date=?, age=?, weight=?, height=?, bmi=?, weight_status=?, 
                systolic_bp=?, diastolic_bp=?, pulse=?, temperature=?, address=?, 
                email=?, profession=?, telephone=?, marital_status=?, ideal_weight=?
            WHERE id=?
        ''', (
            name, birth_date, age, weight, height, bmi, weight_status,
            systolic_bp, diastolic_bp, pulse, temperature, address,
            email, profession, telephone, marital_status, ideal_weight,
            patient_id
        ))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Patient updated successfully.")
    except Exception as e:
        messagebox.showerror("Update Error", f"Failed to update patient:\n{e}")

def delete_patient(db_path, patient_id):
    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this patient?")
    if not confirm:
        return

    conn = connect_db(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM patients WHERE id=?", (patient_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Patient deleted successfully.")
    except Exception as e:
        messagebox.showerror("Delete Error", f"Failed to delete patient:\n{e}")

def generate_patient_id(gender, birth_date):
    birth_date_obj = datetime.strptime(birth_date, "%d-%m-%Y")
    age = calculate_age(birth_date)
    sex_code = '1' if gender == "Male" else '2'
    age_code = f"{age:02d}"
    birth_date_code = birth_date_obj.strftime('%d%m%y')
    unique_id = f"{random.randint(1000, 9999)}"
    return f"{sex_code}{age_code}{birth_date_code}{unique_id}"

def refresh_treeview(treeview, db_path):
    for row in treeview.get_children():
        treeview.delete(row)

    conn = connect_db(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients")
    rows = cursor.fetchall()
    for row in rows:
        treeview.insert("", tk.END, values=row)
    conn.close()

def search_patient(treeview, db_path, search_term):
    conn = connect_db(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM patients WHERE
        name LIKE ? OR birth_date LIKE ? OR address LIKE ?
    ''', ('%' + search_term + '%', '%' + search_term + '%', '%' + search_term + '%'))
    rows = cursor.fetchall()
    for row in treeview.get_children():
        treeview.delete(row)
    for row in rows:
        treeview.insert("", tk.END, values=row)
    conn.close()