# pulse/database/db_manager.py

import os
import sqlite3
from datetime import datetime

# Constants for folder structure
DOCUMENTS_FOLDER = os.path.join(os.path.expanduser('~'), 'Documents')
MEDEASE_FOLDER = os.path.join(DOCUMENTS_FOLDER, 'Pulse')
INVOICES_FOLDER = os.path.join(MEDEASE_FOLDER, 'invoices')
PHOTOS_FOLDER = os.path.join(MEDEASE_FOLDER, 'photos')
REPORTS_FOLDER = os.path.join(MEDEASE_FOLDER, 'reports')

def create_folders():
    """Create necessary directories if they don't exist."""
    os.makedirs(MEDEASE_FOLDER, exist_ok=True)
    os.makedirs(INVOICES_FOLDER, exist_ok=True)
    os.makedirs(PHOTOS_FOLDER, exist_ok=True)
    os.makedirs(REPORTS_FOLDER, exist_ok=True)

def get_db_path():
    """Return the path to the SQLite database file."""
    return os.path.join(MEDEASE_FOLDER, 'patients.db')

def connect_db(db_path):
    """Connect to the SQLite database."""
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.Error as e:
        raise RuntimeError(f"Failed to connect to database: {e}")

def create_tables(conn):
    """Create database tables if they do not exist."""
    cursor = conn.cursor()

    # Patients table
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

    # Visits table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS visits (
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
        telephone TEXT,
        address TEXT,
        file_UID TEXT,
        qrcode TEXT,
        FOREIGN KEY(patient_id) REFERENCES patients(id)
    )
    ''')

    conn.commit()

def initialize_database():
    """Initialize folders and database, then return the database path."""
    create_folders()
    db_path = get_db_path()
    conn = connect_db(db_path)
    create_tables(conn)
    conn.close()
    return db_path

if __name__ == "__main__":
    # This block is for testing only
    db_file = initialize_database()
    print(f"Database initialized at: {db_file}")