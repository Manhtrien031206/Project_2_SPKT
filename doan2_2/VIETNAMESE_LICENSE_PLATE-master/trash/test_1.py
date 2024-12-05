import math
import time
import cv2
import numpy as np
import Preprocess as Preprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
from datetime import datetime
import json

# Constants for image processing
ADAPTIVE_THRESH_BLOCK_SIZE = 19
ADAPTIVE_THRESH_WEIGHT = 9
Min_char = 0.01
Max_char = 0.09
RESIZED_IMAGE_WIDTH = 20
RESIZED_IMAGE_HEIGHT = 30

# Function to log history
def log_to_history(license_plate, status):
    log_entry = {
        "license_plate": license_plate,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": status
    }
    history_file_path = "C:\\Users\\ACER\\Downloads\\doan2_2\\VIETNAMESE_LICENSE_PLATE-master\\history.json"

    try:
        if os.path.exists(history_file_path):
            with open(history_file_path, "r", encoding="utf-8") as file:
                history_data = json.load(file)
        else:
            history_data = []
        
        history_data.append(log_entry)

        with open(history_file_path, "w", encoding="utf-8") as file:
            json.dump(history_data, file, ensure_ascii=False, indent=4)
        
        print(f"Đã ghi vào history: {log_entry}")
    except Exception as e:
        print(f"Lỗi khi ghi vào history.json: {e}")

# Function to update status in plates.json
def update_status_in_json(license_plate, new_status):
    try:
        with open("C:\\Users\\ACER\\Downloads\\doan2_2\\VIETNAMESE_LICENSE_PLATE-master\\plates.json", "r", encoding="utf-8") as file:
            plates_data = json.load(file)

        for plate in plates_data:
            if plate["license"] == license_plate:
                plate["status"] = new_status
                break

        with open("C:\\Users\\ACER\\Downloads\\doan2_2\\VIETNAMESE_LICENSE_PLATE-master\\plates.json", "w", encoding="utf-8") as file:
            json.dump(plates_data, file, ensure_ascii=False, indent=4)
        print(f"Đã cập nhật trạng thái cho biển số {license_plate} thành '{new_status}'")

    except FileNotFoundError:
        print("File plates.json không tồn tại.")
    except json.JSONDecodeError:
        print("Lỗi định dạng trong file plates.json.")
    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")

# Handler to process new images
class ImageHandler(FileSystemEventHandler):
    def __init__(self, folder_type):
        super().__init__()
        self.folder_type = folder_type

    def on_created(self, event):
        if event.src_path.endswith('.jpg') or event.src_path.endswith('.png'):
            print(f"New image detected in {self.folder_type}: {event.src_path}")
            time.sleep(1)  # Ensure the image is completely saved
            
            # Check which folder triggered the event and update the status accordingly
            if self.folder_type == "uploads":
                process_license_plate(event.src_path, "Đã vào")
            elif self.folder_type == "uploads_out":
                process_license_plate(event.src_path, "Đã ra")

def process_license_plate(image_path, status):
    recognized_plate = "79F153004"  # Simulate recognition for this example
    update_status_in_json(recognized_plate, status)
    log_to_history(recognized_plate, status)

if __name__ == "__main__":
    # Initialize observers for both directories
    uploads_folder = r"C:\xampp\htdocs\doan2\uploads"
    uploads_out_folder = r"C:\xampp\htdocs\doan2\uploads_out"

    uploads_handler = ImageHandler("uploads")
    uploads_out_handler = ImageHandler("uploads_out")

    observer_uploads = Observer()
    observer_uploads.schedule(uploads_handler, uploads_folder, recursive=False)

    observer_uploads_out = Observer()
    observer_uploads_out.schedule(uploads_out_handler, uploads_out_folder, recursive=False)

    # Start both observers
    observer_uploads.start()
    observer_uploads_out.start()
    
    print(f"Đang theo dõi tệp: {uploads_folder} và {uploads_out_folder}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer_uploads.stop()
        observer_uploads_out.stop()

    observer_uploads.join()
    observer_uploads_out.join()
