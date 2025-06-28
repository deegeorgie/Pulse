# pulse/config/business_config.py

import os
from tkinter import Toplevel, Label, Entry, Button, filedialog, messagebox, StringVar
from functools import partial


def get_business_info(medease_folder):
    """
    Read business information from 'business.txt' located in MedEase folder.
    
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

    # Ensure required fields are present
    required_keys = ['Business Name', 'Business Address', 'Business Phone', 'Business Email', 'Logo Path']
    missing = [key for key in required_keys if key not in business_info]
    if missing:
        raise ValueError(f"Missing keys in business.txt: {', '.join(missing)}")

    return business_info


def save_business_info(medease_folder, business_data):
    """
    Save business information back to 'business.txt'.
    
    Args:
        medease_folder (str): Path to the MedEase directory.
        business_data (dict): Dictionary containing updated business data.
    """
    business_info_path = os.path.join(medease_folder, 'business.txt')

    try:
        with open(business_info_path, 'w') as file:
            for key, value in business_data.items():
                file.write(f"{key}: {value}\n")
        messagebox.showinfo("Success", "Business settings saved successfully.")
    except Exception as e:
        messagebox.showerror("Save Error", f"Failed to save business settings: {e}")


def validate_required_fields(business_data):
    """
    Validate that all required fields are filled.
    
    Args:
        business_data (dict): Business info dictionary.
    
    Returns:
        list: List of missing field names.
    """
    required_fields = [
        "Business Name",
        "Business Address",
        "Business Email",
        "Business Phone"
    ]
    missing = [field for field in required_fields if not business_data.get(field)]
    return missing


def open_business_settings(root, medease_folder):
    """
    Open a new window to edit and save business information.
    
    Args:
        root: Tkinter root window.
        medease_folder: Path to the MedEase directory.
    """
    try:
        current_info = get_business_info(medease_folder)
    except Exception as e:
        messagebox.showerror("Configuration Error", str(e))
        return

    def on_save():
        updated_info = {
            "Business Name": business_name_entry.get(),
            "Business Address": business_address_entry.get(),
            "Business Website": business_website_entry.get(),
            "Business Email": business_email_entry.get(),
            "Business Phone": business_phone_entry.get(),
            "Business Tax ID": business_tax_id_entry.get(),
            "Logo Path": logo_path_var.get()
        }

        missing = validate_required_fields(updated_info)
        if missing:
            messagebox.showwarning("Validation Error", f"Please fill in all required fields: {', '.join(missing)}")
            return

        save_business_info(medease_folder, updated_info)
        settings_window.destroy()

    def select_logo():
        file_path = filedialog.askopenfilename(
            title="Select Logo File",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif"), ("All Files", "*.*")]
        )
        if file_path:
            logo_path_var.set(file_path)

    # Create settings window
    settings_window = Toplevel(root)
    settings_window.title("Edit Business Details")
    settings_window.geometry("500x350")
    settings_window.resizable(False, False)
    settings_window.transient(root)
    settings_window.grab_set()

    # Placeholder helper
    def create_placeholder_entry(parent, default_text):
        entry = Entry(parent, width=40)
        entry.insert(0, default_text)
        entry.bind("<FocusIn>", lambda e: entry.delete(0, 'end') if entry.get() == default_text else None)
        entry.bind("<FocusOut>", lambda e: entry.insert(0, default_text) if entry.get() == '' else None)
        return entry

    # Form fields
    Label(settings_window, text="Business Name *").grid(row=0, column=0, sticky='w', padx=10, pady=5)
    business_name_entry = create_placeholder_entry(settings_window, "Enter business name")
    business_name_entry.insert(0, current_info.get("Business Name", ""))
    business_name_entry.grid(row=0, column=1, padx=10, pady=5)

    Label(settings_window, text="Business Address *").grid(row=1, column=0, sticky='w', padx=10, pady=5)
    business_address_entry = create_placeholder_entry(settings_window, "Enter business address")
    business_address_entry.insert(0, current_info.get("Business Address", ""))
    business_address_entry.grid(row=1, column=1, padx=10, pady=5)

    Label(settings_window, text="Business Website").grid(row=2, column=0, sticky='w', padx=10, pady=5)
    business_website_entry = create_placeholder_entry(settings_window, "Enter website URL")
    business_website_entry.insert(0, current_info.get("Business Website", ""))
    business_website_entry.grid(row=2, column=1, padx=10, pady=5)

    Label(settings_window, text="Business Email *").grid(row=3, column=0, sticky='w', padx=10, pady=5)
    business_email_entry = create_placeholder_entry(settings_window, "Enter business email")
    business_email_entry.insert(0, current_info.get("Business Email", ""))
    business_email_entry.grid(row=3, column=1, padx=10, pady=5)

    Label(settings_window, text="Business Phone *").grid(row=4, column=0, sticky='w', padx=10, pady=5)
    business_phone_entry = create_placeholder_entry(settings_window, "Enter business phone")
    business_phone_entry.insert(0, current_info.get("Business Phone", ""))
    business_phone_entry.grid(row=4, column=1, padx=10, pady=5)

    Label(settings_window, text="Business Tax ID").grid(row=5, column=0, sticky='w', padx=10, pady=5)
    business_tax_id_entry = create_placeholder_entry(settings_window, "Enter tax ID")
    business_tax_id_entry.insert(0, current_info.get("Business Tax ID", ""))
    business_tax_id_entry.grid(row=5, column=1, padx=10, pady=5)

    Label(settings_window, text="Logo File").grid(row=6, column=0, sticky='w', padx=10, pady=5)

    logo_path_var = StringVar(value=current_info.get("Logo Path", ""))
    logo_entry = Entry(settings_window, textvariable=logo_path_var, width=30, state='readonly')
    logo_entry.grid(row=6, column=1, padx=10, pady=5)

    Button(settings_window, text="Browse", command=select_logo).grid(row=6, column=2, padx=5, pady=5)

    # Save button
    Button(settings_window, text="Save Settings", bg="#57a1f8", fg="white", command=on_save).grid(
        row=7, column=1, columnspan=2, pady=20
    )