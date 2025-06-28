# pulse/main.py

import os
import sys
from tkinter import messagebox
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog
import cv2

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import core modules
from database.db_manager import initialize_database
from utils.crypto import check_trial_status, show_expiry_message
from ui.app_window import run_app
from ui.photo_handler import load_image

def main():
    """Main entry point for the Pulse Patient Profiling Application."""
    try:
        # Check trial limit before launching the app
        if not check_trial_status():
            show_expiry_message()
            return

        # Initialize database
        db_path = initialize_database()

        # Run the application UI
        run_app(db_path)

    except Exception as e:
        messagebox.showerror("Startup Error", f"An error occurred while starting the application:\n{e}")
        raise

if __name__ == "__main__":
    main()