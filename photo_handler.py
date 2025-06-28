import time
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2


def load_image(photo_label, path, use_resize=True):
    """
    Load and display an image in the given label.
    
    Args:
        photo_label (tk.Label): Label where the image will be displayed.
        path (str): Path to the image file.
        use_resize (bool): Whether to resize the image or just thumbnail it.
    """
    try:
        img = Image.open(path)
        if use_resize:
            img = img.resize((200, 200), Image.LANCZOS)
        else:
            img.thumbnail((200, 200))
        img = ImageTk.PhotoImage(img)
        photo_label.configure(image=img)
        photo_label.image = img  # Keep reference to prevent garbage collection
    except Exception as e:
        messagebox.showerror("Image Error", f"Could not load image:\n{e}")


def add_photo(photo_label, placeholder_path):
    """
    Open a dialog to select a photo from the local drive and display it.
    
    Args:
        photo_label (tk.Label): Label where the image will be displayed.
        placeholder_path (str): Default image to show if no image is selected.
        
    Returns:
        str: Path to the selected image.
    """
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
    if file_path:
        load_image(photo_label, file_path)
        return file_path
    else:
        messagebox.showwarning("Warning", "No image selected")
        load_image(photo_label, placeholder_path)
        return ""

def take_picture(photo_label, photos_folder):
    """
    Open a camera window to take a picture of the patient.
    
    Args:
        photo_label (tk.Label): Label where the image will be displayed.
        photos_folder (str): Folder where captured images are saved.
        
    Returns:
        str: Path to the captured image.
    """
    photo_path = None
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        messagebox.showerror("Camera Error", "Failed to open the camera.")
        return ""

    def update_frame():
        nonlocal frame, photo_image
        ret, frame = cap.read()
        if ret:
            cv2_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2_image)
            photo_image = ImageTk.PhotoImage(image=img)
            canvas.create_image(0, 0, anchor=tk.NW, image=photo_image)
            camera_window.after(10, update_frame)

    def capture_image():
        nonlocal frame, captured_frame, photo_path
        if frame is not None:
            captured_frame = frame.copy()
            save_captured_image()

    def save_captured_image():
        nonlocal photo_path
        if captured_frame is not None:
            filename = f"captured_{int(time.time())}.jpg"
            photo_path = os.path.join(photos_folder, filename)
            cv2.imwrite(photo_path, captured_frame)
            print(f"Image saved to: {photo_path}")
            camera_window.destroy()
            cap.release()
            # Load captured image in main form
            load_image(photo_label, photo_path)
        else:
            messagebox.showerror("Save Error", "No image was captured.")

    def close_camera():
        cap.release()
        camera_window.destroy()

    camera_window = tk.Toplevel()
    camera_window.title("Webcam - Take Patient Photo")
    camera_window.geometry("640x480")
    camera_window.wm_attributes("-topmost", True)

    canvas = tk.Canvas(camera_window, width=640, height=400)
    canvas.pack()

    button_frame = tk.Frame(camera_window)
    button_frame.pack(fill=tk.X, pady=10)

    tk.Button(button_frame, text="Capture", command=capture_image).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Close", command=close_camera).pack(side=tk.RIGHT, padx=10)

    frame = None
    captured_frame = None
    photo_image = None

    update_frame()  # Start updating the canvas with video feed

    camera_window.wait_window()  # Wait until closed

    return photo_path