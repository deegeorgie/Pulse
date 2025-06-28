# pulse/ui/app_window.py
import os
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox
from ui.forms import PatientForm
from database.patient_manager import refresh_treeview, search_patient
from ui.photo_handler import load_image, take_picture, add_photo
from utils.crypto import check_trial_status, show_expiry_message
from functools import partial
from ui.forms import HealthHistoryForm

def run_app(db_path):
    """Launch the main application window."""
    if not check_trial_status():
        show_expiry_message()
        return

    root = tk.Tk()
    root.title("Pulse v_1.0")
    root.geometry("1200x800")
    root.resizable(True, True)

    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Left side - Form area
    form_area = ttk.Frame(main_frame)
    form_area.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

    # Frame for patient form
    form_frame = ttk.Frame(form_area)
    form_frame.grid(row=1, column=0, sticky='nsew')

    # Right side - Data view area
    data_area = ttk.LabelFrame(main_frame, text="Patients Database", padding=(10, 10))
    data_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

    # Load placeholder image
    placeholder_path = os.path.join(os.path.dirname(__file__), "..", "med_ico.png")

    # Photo Label (Inside form_area)
    photo_label = tk.Label(form_area)
    photo_label.grid(row=0, column=0, rowspan=5, sticky='e', padx=10, pady=10)
    load_image(photo_label, placeholder_path)

    # Create Treeview inside data_area
    columns = (
        "ID", "Name", "Birth Date", "Visit Date", "Age", "Weight", "Height", "BMI", "Weight Status",
        "Systolic BP", "Diastolic BP", "Pulse", "Temp.", "Gender", "Photo Path", "Address",
        "Email", "Profession", "Telephone", "Marital Status"
    )

    treeview = ttk.Treeview(data_area, columns=columns, show="headings",
                            yscrollcommand=None, xscrollcommand=None)
    for col in columns:
        treeview.heading(col, text=col)
        treeview.column(col, width=100)
    treeview.pack(fill=tk.BOTH, expand=True)

    # Initialize PatientForm
    patient_form = PatientForm(form_frame, db_path, treeview, lambda: refresh_treeview(treeview, db_path), photo_label)

    # Initialize HealthHistoryForm below the patient form
    health_form = HealthHistoryForm(form_area)
    health_form.populate_health_form([])  # Default empty values

    # Search field section
    search_frame = ttk.Frame(data_area)
    search_frame.pack(fill=tk.X, pady=5)

    ttk.Label(search_frame, text="Search").pack(side=tk.LEFT, padx=5)
    search_entry = ttk.Entry(search_frame)
    search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    ttk.Button(search_frame, text="Search", command=lambda: search_patient(treeview, db_path, search_entry.get())).pack(
        side=tk.LEFT, padx=5)
    ttk.Button(search_frame, text="Refresh", command=lambda: refresh_treeview(treeview, db_path)).pack(
        side=tk.LEFT, padx=5)

    # Populate existing data
    refresh_treeview(treeview, db_path)

    # Bind selection to populate forms
    def on_select(event):
        selected_item = treeview.focus()
        if selected_item:
            item_values = treeview.item(selected_item, 'values')
            health_form.populate_health_form(item_values)
            patient_form.populate_form(item_values)

    treeview.bind("<<TreeviewSelect>>", on_select)

    # Start main loop
    root.mainloop()