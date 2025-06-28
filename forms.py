# pulse/ui/forms.py

import tkinter as tk
from tkinter import ttk, END, messagebox
from tkcalendar import DateEntry
import sqlite3
import os
from datetime import datetime
from ui.photo_handler import load_image, take_picture, add_photo

def add_spacer(frame, row, col_span=4):
    """Add vertical spacing."""
    ttk.Label(frame, text="").grid(row=row, column=0, columnspan=col_span)
    return row + 1


class PatientForm:
    def __init__(self, parent, db_path, treeview, refresh_treeview, photo_label):
        self.parent = parent
        self.db_path = db_path
        self.treeview = treeview
        self.refresh_treeview = refresh_treeview
        self.photo_label = photo_label
        self.photos_folder = os.path.join(os.path.dirname(db_path), 'photos')
        self.create_widgets()

    def create_widgets(self):
        # Main widgets frame for patient info
        self.widgets_frame = ttk.LabelFrame(self.parent, text="DEMOGRAPHICS | CONSTANTS", padding=(10, 10))
        self.widgets_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

        current_row = 0

        # --- Demographics Section ---
        ttk.Label(self.widgets_frame, text="Name").grid(row=current_row, column=0, sticky='w')
        self.entry_name = ttk.Entry(self.widgets_frame)
        self.entry_name.grid(row=current_row, column=1, padx=5, sticky='w')
        current_row += 1

        ttk.Label(self.widgets_frame, text="Birth Date").grid(row=current_row, column=0, sticky='w')
        self.birth_date_entry = DateEntry(self.widgets_frame, date_pattern='dd-mm-yyyy')
        self.birth_date_entry.grid(row=current_row, column=1, padx=5, sticky='w')
        current_row += 1

        ttk.Label(self.widgets_frame, text="Gender").grid(row=current_row, column=0, sticky='w')
        self.gender_var = tk.StringVar(value="Male")
        self.gender_combo = ttk.Combobox(
            self.widgets_frame,
            textvariable=self.gender_var,
            values=["Male", "Female"],
            state="readonly",
            width=10
        )
        self.gender_combo.grid(row=current_row, column=1, padx=5, sticky='w')
        current_row += 1

        ttk.Label(self.widgets_frame, text="Last Menses").grid(row=current_row, column=0, sticky='w')
        self.last_menstrual_period_entry = DateEntry(self.widgets_frame, date_pattern='dd-mm-yyyy')
        self.last_menstrual_period_entry.config(state='disabled')
        self.last_menstrual_period_entry.grid(row=current_row, column=1, padx=5, sticky='w')
        current_row += 1

        current_row = add_spacer(self.widgets_frame, current_row)

        # --- Constants Section ---
        ttk.Label(self.widgets_frame, text="Weight (kg)").grid(row=current_row, column=0, sticky='w')
        self.entry_weight = ttk.Spinbox(self.widgets_frame, from_=20, to=300, increment=0.5, format="%.1f", width=10)
        self.entry_weight.insert(0, "70.0")
        self.entry_weight.grid(row=current_row, column=1, padx=5, sticky='w')
        current_row += 1

        ttk.Label(self.widgets_frame, text="Height (m)").grid(row=current_row, column=0, sticky='w')
        self.entry_height = ttk.Spinbox(self.widgets_frame, from_=0.8, to=2.5, increment=0.01, format="%.2f", width=10)
        self.entry_height.insert(0, "1.50")
        self.entry_height.grid(row=current_row, column=1, padx=5, sticky='w')
        current_row += 1

        ttk.Label(self.widgets_frame, text="Systolic BP").grid(row=current_row, column=0, sticky='w')
        self.entry_systolic = ttk.Spinbox(self.widgets_frame, from_=50, to=250, increment=1, width=10)
        self.entry_systolic.insert(0, "120")
        self.entry_systolic.grid(row=current_row, column=1, padx=5, sticky='w')
        current_row += 1

        ttk.Label(self.widgets_frame, text="Diastolic BP").grid(row=current_row, column=0, sticky='w')
        self.entry_diastolic = ttk.Spinbox(self.widgets_frame, from_=40, to=150, increment=1, width=10)
        self.entry_diastolic.insert(0, "80")
        self.entry_diastolic.grid(row=current_row, column=1, padx=5, sticky='w')
        current_row += 1

        ttk.Label(self.widgets_frame, text="Pulse").grid(row=current_row, column=0, sticky='w')
        self.entry_pulse = ttk.Spinbox(self.widgets_frame, from_=30, to=200, increment=1, width=10)
        self.entry_pulse.insert(0, "65")
        self.entry_pulse.grid(row=current_row, column=1, padx=5, sticky='w')
        current_row += 1

        ttk.Label(self.widgets_frame, text="Temperature (°C)").grid(row=current_row, column=0, sticky='w')
        self.entry_temperature = ttk.Spinbox(self.widgets_frame, from_=34.0, to=42.0, increment=0.1, format="%.1f", width=10)
        self.entry_temperature.insert(0, "37.0")
        self.entry_temperature.grid(row=current_row, column=1, padx=5, sticky='w')
        current_row += 1

        current_row = add_spacer(self.widgets_frame, current_row)

        # --- Contact & Personal Info Section ---
        ttk.Label(self.widgets_frame, text="Address").grid(row=current_row, column=0, sticky='w')
        self.entry_address = ttk.Entry(self.widgets_frame)
        self.entry_address.grid(row=current_row, column=1, padx=5, sticky='w')
        current_row += 1

        ttk.Label(self.widgets_frame, text="Email").grid(row=current_row, column=0, sticky='w')
        self.entry_email = ttk.Entry(self.widgets_frame)
        self.entry_email.grid(row=current_row, column=1, padx=5, sticky='w')
        current_row += 1

        ttk.Label(self.widgets_frame, text="Profession").grid(row=current_row, column=0, sticky='w')
        self.entry_profession = ttk.Entry(self.widgets_frame)
        self.entry_profession.grid(row=current_row, column=1, padx=5, sticky='w')
        current_row += 1

        ttk.Label(self.widgets_frame, text="Telephone").grid(row=current_row, column=0, sticky='w')
        self.entry_telephone = ttk.Entry(self.widgets_frame)
        self.entry_telephone.grid(row=current_row, column=1, padx=5, sticky='w')
        current_row += 1

        ttk.Label(self.widgets_frame, text="Marital Status").grid(row=current_row, column=0, sticky='w')
        self.marital_status_var = tk.StringVar(value="Single")
        marital_frame = ttk.Frame(self.widgets_frame)
        marital_frame.grid(row=current_row, column=1, padx=5, sticky='w')

        tk.Radiobutton(marital_frame, text="Single", variable=self.marital_status_var, value="Single").pack(side=tk.LEFT)
        tk.Radiobutton(marital_frame, text="Married", variable=self.marital_status_var, value="Married").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(marital_frame, text="Widowed", variable=self.marital_status_var, value="Widowed").pack(side=tk.LEFT)
        current_row += 1

        current_row = add_spacer(self.widgets_frame, current_row)

        # --- Output Fields ---
        ttk.Label(self.widgets_frame, text="Ideal Weight (kg)").grid(row=current_row, column=0, sticky='w')
        self.entry_ibw = ttk.Entry(self.widgets_frame)
        self.entry_ibw.grid(row=current_row, column=1, padx=5, sticky='w')
        current_row += 1

        # Buttons at bottom
        button_frame = ttk.Frame(self.widgets_frame)
        button_frame.grid(row=current_row, column=0, columnspan=4, pady=10, sticky='ew')

        self.register_button = ttk.Button(button_frame, text="Register Patient", command=self.on_register, state='disabled')
        self.register_button.pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Update Patient", command=self.on_update).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save to PDF", command=self.on_save_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.on_clear).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Take A Picture", command=self.capture_and_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Choose Photo", command=self.browse_and_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Patient", command=self.on_delete).pack(side=tk.LEFT, padx=5)

        # Event bindings
        self.gender_combo.bind("<<ComboboxSelected>>", lambda e: self.toggle_menstrual_period())
        for entry in [
            self.entry_name,
            self.entry_weight,
            self.entry_height,
            self.entry_systolic,
            self.entry_diastolic,
            self.entry_pulse,
            self.entry_temperature,
            self.entry_telephone
        ]:
            entry.bind("<KeyRelease>", lambda e: self.check_fields())

    def get_data(self):
        return {
            'name': self.entry_name.get(),
            'birth_date': self.birth_date_entry.get(),
            'gender': self.gender_var.get(),
            'weight': self.entry_weight.get(),
            'height': self.entry_height.get(),
            'systolic_bp': self.entry_systolic.get(),
            'diastolic_bp': self.entry_diastolic.get(),
            'pulse': self.entry_pulse.get(),
            'temperature': self.entry_temperature.get(),
            'address': self.entry_address.get(),
            'email': self.entry_email.get(),
            'profession': self.entry_profession.get(),
            'telephone': self.entry_telephone.get(),
            'marital_status': self.marital_status_var.get(),
            'menses': self.last_menstrual_period_entry.get() if self.gender_var.get() == "Female" else None
        }

    def check_fields(self):
        if (
            self.entry_name.get() and
            self.entry_weight.get() and
            self.entry_height.get() and
            self.entry_systolic.get() and
            self.entry_diastolic.get() and
            self.entry_pulse.get() and
            self.entry_temperature.get() and
            self.entry_telephone.get()
        ):
            self.register_button.config(state=tk.NORMAL)
        else:
            self.register_button.config(state=tk.DISABLED)
    
    def capture_and_preview(self):
        """Trigger camera and preview image in the form without saving yet."""
        global photo_path
        photo_path = take_picture(self.photo_label, self.photos_folder)

    def browse_and_preview(self):
        """Browse and preview a local image."""
        global photo_path
        photo_path = add_photo(self.photo_label, os.path.join(os.path.dirname(__file__), "..", "med_ico.png"))

    def toggle_menstrual_period(self):
        if self.gender_var.get() == "Female":
            self.last_menstrual_period_entry.config(state='enabled')
        else:
            self.last_menstrual_period_entry.set_date(datetime.now())
            self.last_menstrual_period_entry.config(state='disabled')

    def on_register(self):
        """Passes current form data to register_patient."""
        form_data = self.form.get_data()
        from database.patient_manager import register_patient
        register_patient(self.db_path, form_data)
        self.form.on_clear()
        self.refresh_treeview()

    def on_update(self):
        print("Updating selected patient...")

    def on_delete(self):
        print("Deleting selected patient...")

    def on_save_pdf(self):
        print("Saving patient report to PDF...")

    def on_clear(self):
        self.entry_name.delete(0, END)
        self.birth_date_entry.set_date(datetime.now())
        self.entry_weight.delete(0, END)
        self.entry_weight.insert(0, "70.0")
        self.entry_height.delete(0, END)
        self.entry_height.insert(0, "1.50")
        self.entry_systolic.delete(0, END)
        self.entry_systolic.insert(0, "120")
        self.entry_diastolic.delete(0, END)
        self.entry_diastolic.insert(0, "80")
        self.entry_pulse.delete(0, END)
        self.entry_pulse.insert(0, "65")
        self.entry_temperature.delete(0, END)
        self.entry_temperature.insert(0, "37.0")
        self.entry_address.delete(0, END)
        self.entry_email.delete(0, END)
        self.entry_profession.delete(0, END)
        self.entry_telephone.delete(0, END)
        self.gender_var.set("Male")
        self.last_menstrual_period_entry.set_date(datetime.now())
        self.last_menstrual_period_entry.config(state='disabled')
        self.marital_status_var.set("Single")

    def populate_form(self, item_values):
        if item_values:
            self.entry_name.delete(0, END)
            self.entry_name.insert(0, item_values[1])  # Name

            self.birth_date_entry.set_date(item_values[2])  # Birth Date

            gender = item_values[16]
            self.gender_var.set(gender)
            self.toggle_menstrual_period()

            self.entry_weight.delete(0, END)
            self.entry_weight.insert(0, item_values[5])  # Weight

            self.entry_height.delete(0, END)
            self.entry_height.insert(0, item_values[6])  # Height

            self.entry_systolic.delete(0, END)
            self.entry_systolic.insert(0, item_values[9])  # Systolic BP

            self.entry_diastolic.delete(0, END)
            self.entry_diastolic.insert(0, item_values[10])  # Diastolic BP

            self.entry_pulse.delete(0, END)
            self.entry_pulse.insert(0, item_values[11])  # Pulse

            self.entry_temperature.delete(0, END)
            self.entry_temperature.insert(0, item_values[12])  # Temperature

            self.entry_address.delete(0, END)
            self.entry_address.insert(0, item_values[19])  # Address

            self.entry_email.delete(0, END)
            self.entry_email.insert(0, item_values[20])  # Email

            self.entry_profession.delete(0, END)
            self.entry_profession.insert(0, item_values[21])  # Profession

            self.entry_telephone.delete(0, END)
            self.entry_telephone.insert(0, item_values[22])  # Telephone

            self.marital_status_var.set(item_values[23])  # Marital Status

            ibw = item_values[38] or "N/A"
            self.entry_ibw.delete(0, END)
            self.entry_ibw.insert(0, ibw)  # Ideal Body Weight

            # Load photo path and display image
            global photo_path
            photo_path = item_values[18]
            if photo_path and os.path.exists(photo_path):
                load_image(self.photo_label, photo_path)
            else:
                placeholder_path = os.path.join(os.path.dirname(__file__), "..", "med_ico.png")
                load_image(self.photo_label, placeholder_path)


class HealthHistoryForm:
    def __init__(self, parent, observations_callback=None):
        self.parent = parent
        self.observations_callback = observations_callback
        self.check_vars = {}
        self.create_widgets()

    def create_widgets(self):
        # Frame for health history
        self.health_frame = ttk.LabelFrame(self.parent, text="ADDITIONAL HEALTH RELATED DETAILS", padding=(10, 10))
        self.health_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

        conditions = [
            ("Diabetes", "diabetes"),
            ("Kidney Disease", "kidney"),
            ("Epilepsy", "epilepsy"),
            ("Allergy", "allergy"),
            ("Asthma", "asthma"),
            ("Heart Disease", "heart"),
            ("Cancer", "cancer"),
            ("Surgery", "surgery"),
            ("Stroke", "stroke"),
            ("Hypertension", "hypertension"),
            ("Hypotension", "hypotension"),
            ("Smoking", "smoking"),
            ("Sports", "sports"),
            ("Alcohol", "alcohol")
        ]

        row = 0
        col = 0
        for label, key in conditions:
            var = tk.IntVar()
            ttk.Checkbutton(self.health_frame, text=label, variable=var).grid(
                row=row, column=col, sticky='w', padx=5, pady=2
            )
            self.check_vars[key] = var
            col += 1
            if col > 2:
                col = 0
                row += 1

        row += 1
        col = 0

        # Observations Text Field inside Health History
        ttk.Label(self.health_frame, text="Observations", font=("Helvetica", 10, "bold")).grid(
            row=row, column=0, sticky='w', pady=(10, 0), columnspan=3
        )
        self.observations = tk.Text(self.health_frame, width=81, height=5)
        self.observations.grid(row=row+1, column=0, columnspan=3, sticky='ew', padx=5, pady=5)

        # Bind to callback if provided
        if self.observations_callback:
            self.observations.bind("<KeyRelease>", lambda e: self.observations_callback())

    def get_data(self):
        data = {key: var.get() for key, var in self.check_vars.items()}
        data['observations'] = self.observations.get("1.0", tk.END).strip()
        return data

    def set_observations(self, text=""):
        self.observations.delete("1.0", tk.END)
        self.observations.insert("1.0", text)

    def populate_health_form(self, values):
        if values:
            self.check_vars['diabetes'].set(values[24])
            self.check_vars['kidney'].set(values[25])
            self.check_vars['epilepsy'].set(values[26])
            self.check_vars['allergy'].set(values[27])
            self.check_vars['asthma'].set(values[28])
            self.check_vars['heart'].set(values[29])
            self.check_vars['cancer'].set(values[30])
            self.check_vars['surgery'].set(values[31])
            self.check_vars['stroke'].set(values[32])
            self.check_vars['hypertension'].set(values[33])
            self.check_vars['hypotension'].set(values[34])
            self.check_vars['alcohol'].set(values[35])
            self.check_vars['sports'].set(values[36])
            self.check_vars['smoking'].set(values[37])

            self.set_observations(values[40])  # Observations

class SearchAndActionButtons:
    """
    A reusable UI component containing:
    - A search field
    - Action buttons (Register, Update, Delete, Clear, PDF)
    """

    def __init__(self, parent, form, observations, db_path, treeview):
        self.parent = parent
        self.form = form
        self.observations = observations
        self.db_path = db_path
        self.treeview = treeview
        self.create_widgets()

    def create_widgets(self):
        # Frame for buttons and search
        button_frame = ttk.Frame(self.parent)
        button_frame.pack(fill='x', pady=10)

        # Search section
        ttk.Label(button_frame, text="Search").grid(row=0, column=0, padx=5, sticky='w')
        self.search_entry = ttk.Entry(button_frame, width=40)
        self.search_entry.grid(row=0, column=1, padx=5, sticky='w')

        self.search_button = ttk.Button(button_frame, text="Search", command=self.on_search)
        self.search_button.grid(row=0, column=2, padx=5)

        self.refresh_button = ttk.Button(button_frame, text="Refresh", command=self.on_refresh)
        self.refresh_button.grid(row=0, column=3, padx=5)

        # Action buttons
        action_frame = ttk.Frame(self.parent)
        action_frame.pack(fill='x', pady=5)

        self.register_button = ttk.Button(action_frame, text="Register", style="TButton", command=self.on_register)
        self.register_button.grid(row=0, column=0, padx=5)

        self.update_button = ttk.Button(action_frame, text="Update", style="TButton", command=self.on_update)
        self.update_button.grid(row=0, column=1, padx=5)

        self.delete_button = ttk.Button(action_frame, text="Delete", style="TButton", command=self.on_delete)
        self.delete_button.grid(row=0, column=2, padx=5)

        self.pdf_button = ttk.Button(action_frame, text="Save PDF", style="TButton", command=self.on_save_pdf)
        self.pdf_button.grid(row=0, column=3, padx=5)

        self.clear_button = ttk.Button(action_frame, text="Clear", style="TButton", command=self.on_clear)
        self.clear_button.grid(row=0, column=4, padx=5)

        # Scrollbars for Treeview
        self.scrollbar_y = ttk.Scrollbar(self.parent)
        self.scrollbar_x = ttk.Scrollbar(self.parent, orient='horizontal')

    def on_register(self):
        """Handle register button click."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            data = self.form.get_data()
            name = data['name']
            birth_date = data['birth_date']
            gender = data['gender']
            weight = float(data['weight'])
            height = float(data['height'])
            systolic_bp = int(data['systolic_bp'])
            diastolic_bp = int(data['diastolic_bp'])
            pulse = int(data['pulse'])
            temperature = float(data['temperature'])

            # Calculate derived values
            bmi = round(weight / (height ** 2), 2)
            age = calculate_age(birth_date)  # Make sure this function is imported or defined here
            ideal_weight = calculate_ideal_body_weight(height, gender)
            alerts = assess_health(pulse, temperature, systolic_bp, diastolic_bp, gender)

            # Insert into DB
            cursor.execute('''
                INSERT INTO patients (
                    name, birth_date, gender, weight, height, systolic_bp, diastolic_bp,
                    pulse, temperature, bmi, age, ideal_weight, alerts, observations
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                name, birth_date, gender, weight, height, systolic_bp, diastolic_bp,
                pulse, temperature, bmi, age, ideal_weight, alerts, self.observations.get("1.0", END).strip()
            ))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Patient registered successfully!")
            self.on_refresh()

        except Exception as e:
            messagebox.showerror("Registration Error", f"Could not register patient:\n{e}")

    def on_update(self):
        """Handle update button click."""
        selected_item = self.treeview.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "No patient selected to update.")
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            item_values = self.treeview.item(selected_item, 'values')
            patient_id = item_values[0]

            data = self.form.get_data()
            name = data['name']
            birth_date = data['birth_date']
            gender = data['gender']
            weight = float(data['weight'])
            height = float(data['height'])
            systolic_bp = int(data['systolic_bp'])
            diastolic_bp = int(data['diastolic_bp'])
            pulse = int(data['pulse'])
            temperature = float(data['temperature'])

            # Recalculate derived fields
            bmi = round(weight / (height ** 2), 2)
            age = calculate_age(birth_date)
            ideal_weight = calculate_ideal_body_weight(height, gender)
            alerts = assess_health(pulse, temperature, systolic_bp, diastolic_bp, gender)

            cursor.execute('''
                UPDATE patients SET 
                    name=?, birth_date=?, gender=?, weight=?, height=?, systolic_bp=?, diastolic_bp=?,
                    pulse=?, temperature=?, bmi=?, age=?, ideal_weight=?, alerts=?, observations=?
                WHERE id=?
            ''', (
                name, birth_date, gender, weight, height, systolic_bp, diastolic_bp,
                pulse, temperature, bmi, age, ideal_weight, alerts,
                self.observations.get("1.0", END).strip(),
                patient_id
            ))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Patient updated successfully!")
            self.on_refresh()

        except ValueError as ve:
            messagebox.showerror("Validation Error", f"Please enter valid numbers.\n{ve}")
        except Exception as e:
            messagebox.showerror("Update Error", f"Could not update patient:\n{e}")

    def on_delete(self):
        """Handle delete button click."""
        selected_item = self.treeview.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "No patient selected to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this patient?")
        if not confirm:
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            patient_id = self.treeview.item(selected_item)['values'][0]
            cursor.execute("DELETE FROM patients WHERE id=?", (patient_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Patient deleted successfully!")
            self.on_refresh()

        except Exception as e:
            messagebox.showerror("Delete Error", f"Could not delete patient:\n{e}")

    def on_save_pdf(self):
        """Handle save to PDF button click."""
        from utils.pdf_generator import generate_patient_report

        selected_item = self.treeview.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "No patient selected to save as PDF.")
            return

        try:
            item_values = self.treeview.item(selected_item, 'values')
            medease_folder = os.path.dirname(self.db_path)  # Assuming MedEase folder structure
            generate_patient_report(item_values, medease_folder)

        except Exception as e:
            messagebox.showerror("PDF Error", f"Failed to generate PDF:\n{e}")

    def on_search(self):
        """Handle search functionality."""
        search_term = self.search_entry.get().strip()
        if not search_term:
            self.on_refresh()
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM patients WHERE
                name LIKE ? OR birth_date LIKE ? OR address LIKE ?
            ''', ('%' + search_term + '%', '%' + search_term + '%', '%' + search_term + '%'))

            rows = cursor.fetchall()
            conn.close()

            for row in self.treeview.get_children():
                self.treeview.delete(row)

            for row in rows:
                self.treeview.insert("", tk.END, values=row)

        except Exception as e:
            messagebox.showerror("Search Error", f"An error occurred during search:\n{e}")

    def on_refresh(self):
        """Refresh the patient list."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patients")
            rows = cursor.fetchall()
            conn.close()

            for row in self.treeview.get_children():
                self.treeview.delete(row)

            for row in rows:
                self.treeview.insert("", tk.END, values=row)

            self.form.reset_form()  # If implemented in PatientForm
            self.observations.delete("1.0", tk.END)

        except Exception as e:
            messagebox.showerror("Refresh Error", f"Could not refresh patient list:\n{e}")

    def on_clear(self):
        """Clear all form fields."""
        self.form.entry_name.delete(0, tk.END)
        self.form.entry_weight.delete(0, tk.END)
        self.form.entry_height.delete(0, tk.END)
        self.form.entry_systolic.delete(0, tk.END)
        self.form.entry_diastolic.delete(0, tk.END)
        self.form.entry_pulse.delete(0, tk.END)
        self.form.entry_temperature.delete(0, tk.END)
        self.form.gender_var.set("Male")
        self.observations.delete("1.0", tk.END)

def calculate_age(birth_date_str):
    birth_date = datetime.strptime(birth_date_str, "%d-%m-%Y")
    today = datetime.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def calculate_ideal_body_weight(height_m, gender):
    height_inches = height_m * 39.3701  # Convert meters to inches
    if gender == "Male":
        return round(50 + 2.3 * (height_inches - 60), 2)
    else:
        return round(45.5 + 2.3 * (height_inches - 60), 2)

def assess_health(pulse, temperature, systolic_bp, diastolic_bp, gender, menses=None):
    alerts = []

    if pulse < 60 or pulse > 100:
        alerts.append("Abnormal Pulse")

    if temperature < 36.1 or temperature > 37.2:
        alerts.append("Abnormal Temperature")

    if systolic_bp > 120 or diastolic_bp > 80:
        alerts.append("High Blood Pressure")

    if gender == "Female" and menses:
        lmp = datetime.strptime(menses, "%d-%m-%Y")
        days_since_lmp = (datetime.today() - lmp).days
        if days_since_lmp > 28:
            alerts.append("Consider Pregnancy Test")

    return "\n".join(alerts)