# pulse/utils/crypto.py

import os
import datetime
from cryptography.fernet import Fernet

TIME_LIMIT_DAYS = 15  # Trial period length in days
INSTALL_DATE_FILE = 'install_date.enc'
KEY_FILE = 'secret.key'

def generate_key():
    """Generate a new encryption key and save it to a file."""
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as key_file:
        key_file.write(key)

def load_key():
    """Load the previously generated encryption key."""
    return open(KEY_FILE, 'rb').read()

def encrypt_date(date_str):
    """Encrypt a date string using the stored key."""
    key = load_key()
    fernet = Fernet(key)
    encrypted_date = fernet.encrypt(date_str.encode())
    return encrypted_date

def decrypt_date(encrypted_date):
    """Decrypt an encrypted date string."""
    key = load_key()
    fernet = Fernet(key)
    decrypted_date = fernet.decrypt(encrypted_date).decode()
    return decrypted_date

def get_install_date():
    """Retrieve or set the installation date."""
    if not os.path.exists(KEY_FILE):
        generate_key()

    if not os.path.exists(INSTALL_DATE_FILE):
        install_date = datetime.datetime.now().isoformat()
        encrypted_date = encrypt_date(install_date)
        with open(INSTALL_DATE_FILE, 'wb') as f:
            f.write(encrypted_date)
        return datetime.datetime.fromisoformat(install_date)
    else:
        with open(INSTALL_DATE_FILE, 'rb') as f:
            encrypted_date = f.read()
        decrypted_date_str = decrypt_date(encrypted_date)
        return datetime.datetime.fromisoformat(decrypted_date_str)

def check_trial_status():
    """Check if the application is still within the trial period."""
    install_date = get_install_date()
    current_date = datetime.datetime.now()
    usage_duration = current_date - install_date

    return (current_date - install_date).days <= TIME_LIMIT_DAYS

def show_expiry_message():
    """Display a message indicating that the trial has expired."""
    import tkinter.messagebox as messagebox
    messagebox.showwarning("Time Limit Exceeded", "Your trial period has expired. Please contact support.")