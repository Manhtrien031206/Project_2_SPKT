import math
import time
import cv2
import numpy as np
import Preprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from flask import Flask, request
import os
from datetime import datetime
import requests
import json

ADAPTIVE_THRESH_BLOCK_SIZE = 19
ADAPTIVE_THRESH_WEIGHT = 9
Min_char = 0.01
Max_char = 0.09
RESIZED_IMAGE_WIDTH = 20
RESIZED_IMAGE_HEIGHT = 30

# Function to check if contour has 90-degree angles
def is_rectangular(contour, angle_tolerance=10):
    if len(contour) != 4:
        return False

    (x1, y1) = contour[0, 0]
    (x2, y2) = contour[1, 0]
    (x3, y3) = contour[2, 0]
    (x4, y4) = contour[3, 0]

    vec1 = [x2 - x1, y2 - y1]
    vec2 = [x3 - x2, y3 - y2]
    vec3 = [x4 - x3, y4 - y3]
    vec4 = [x1 - x4, y1 - y4]

    def angle_between(v1, v2):
        dot_product = v1[0] * v2[0] + v1[1] * v2[1]
        norm_v1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
        norm_v2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)
        cos_angle = dot_product / (norm_v1 * norm_v2)
        angle = math.acos(cos_angle) * (180.0 / math.pi)
        return angle

    angle1 = angle_between(vec1, vec2)
    angle2 = angle_between(vec2, vec3)
    angle3 = angle_between(vec3, vec4)
    angle4 = angle_between(vec4, vec1)

    return (abs(angle1 - 90) <= angle_tolerance and
            abs(angle2 - 90) <= angle_tolerance and
            abs(angle3 - 90) <= angle_tolerance and
            abs(angle4 - 90) <= angle_tolerance)

# Handler to process new images
class ImageHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith('.jpg') or event.src_path.endswith('.png'):
            print(f"New image detected in uploads: {event.src_path}")
            time.sleep(1)
            process_license_plate(event.src_path)

# Handler to process new images from uploads_out folder
class ImageHandlerOut(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith('.jpg') or event.src_path.endswith('.png'):
            print(f"New image detected in uploads_out: {event.src_path}")
            time.sleep(1)
            process_license_plate_out(event.src_path)
def extract_license_plate(screenCnt, img, imgThreshplate):
    mask = np.zeros(img.shape[:2], np.uint8)
    new_image = cv2.drawContours(mask, [screenCnt], 0, 255, -1)
    (x, y) = np.where(mask == 255)
    (topx, topy) = (np.min(x), np.min(y))
    (bottomx, bottomy) = (np.max(x), np.max(y))
    roi = img[topx:bottomx, topy:bottomy]
    imgThresh = imgThreshplate[topx:bottomx, topy:bottomy]
    return roi, imgThresh
def recognize_characters(roi, imgThresh, kNearest):
    thre_mor = cv2.morphologyEx(imgThresh, cv2.MORPH_DILATE, np.ones((3, 3), np.uint8))
    cont, _ = cv2.findContours(thre_mor, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    rows = []
    char_bboxes = []
    
    for cnt in cont:
        (x, y, w, h) = cv2.boundingRect(cnt)
        char_area = w * h
        height, width, _ = roi.shape
        roiarea = height * width
        if (Min_char * roiarea < char_area < Max_char * roiarea) and (0.25 < w / h < 0.7):
            char_bboxes.append((x, y, w, h, cnt))
    
    char_bboxes = sorted(char_bboxes, key=lambda b: (b[1], b[0]))

    current_row = []
    prev_y = -1
    threshold_y = 10

    for (x, y, w, h, cnt) in char_bboxes:
        if prev_y == -1 or abs(prev_y - y) < threshold_y:
            current_row.append((x, y, w, h, cnt))
        else:
            rows.append(sorted(current_row, key=lambda b: b[0]))
            current_row = [(x, y, w, h, cnt)]
        prev_y = y

    if current_row:
        rows.append(sorted(current_row, key=lambda b: b[0]))

    strFinalString = ""
    for row in rows:
        for (x, y, w, h, cnt) in row:
            imgROI = thre_mor[y:y + h, x:x + w]
            imgROIResized = cv2.resize(imgROI, (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT))
            npaROIResized = imgROIResized.reshape((1, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))
            _, npaResults, _, _ = kNearest.findNearest(np.float32(npaROIResized), k=3)
            strFinalString += str(chr(int(npaResults[0][0])))
    
    return strFinalString
def update_status_in_json(license_plate, new_status):
    try:
        # Đọc dữ liệu từ tệp JSON với mã hóa UTF-8
        with open("C:\\Users\\ACER\\Downloads\\doan2_2\\VIETNAMESE_LICENSE_PLATE-master\\plates.json", "r", encoding="utf-8") as file:
            plates_data = json.load(file)

        # Tìm biển số và cập nhật trạng thái
        for plate in plates_data:
            if plate["license"] == license_plate:
                plate["status"] = new_status
                break

        # Ghi lại dữ liệu đã cập nhật vào tệp JSON với mã hóa UTF-8 và giữ nguyên ký tự Unicode
        with open("C:\\Users\\ACER\\Downloads\\doan2_2\\VIETNAMESE_LICENSE_PLATE-master\\plates.json", "w", encoding="utf-8") as file:
            json.dump(plates_data, file, ensure_ascii=False, indent=4)
        print(f"Đã cập nhật trạng thái cho biển số {license_plate} thành '{new_status}'")

    except FileNotFoundError:
        print("File plates.json không tồn tại.")
    except json.JSONDecodeError:
        print("Lỗi định dạng trong file plates.json.")
    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")

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
        print(f"Logged to history: {log_entry}")
    except Exception as e:
        print(f"Error logging to history.json: {e}")
def send_email_php(plate_number, recipient_email):
    """
    Gửi yêu cầu POST đến endpoint PHP để gửi email.
    """
    try:
        php_endpoint = "http://localhost/doan2/send_email.php"  # Endpoint PHP

        response = requests.post(
            php_endpoint,
            data={"plate_number": plate_number, "recipient_email": recipient_email},
        )
        if response.status_code == 200:
            print(f"Email sent successfully to {recipient_email} for plate {plate_number}")
        else:
            print(f"Failed to send email. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {e}")
def process_license_plate(image_path):            
    img = cv2.imread(image_path)
    try:
        with open("C:\\Users\\ACER\\Downloads\\doan2_2\\VIETNAMESE_LICENSE_PLATE-master\\plates.json", "r", encoding="utf-8") as file:
            valid_plates_data = json.load(file)
            valid_plates = [plate['license'] for plate in valid_plates_data]
    except FileNotFoundError:
        print("File plates.json not found.")
        return
    except json.JSONDecodeError:
        print("Error decoding plates.json.")
        return

    npaClassifications = np.loadtxt("classifications.txt", np.float32)
    npaFlattenedImages = np.loadtxt("flattened_images.txt", np.float32)
    npaClassifications = npaClassifications.reshape((npaClassifications.size, 1))
    kNearest = cv2.ml.KNearest_create()
    kNearest.train(npaFlattenedImages, cv2.ml.ROW_SAMPLE, npaClassifications)

    imgGrayscaleplate, imgThreshplate = Preprocess.preprocess(img)
    canny_image = cv2.Canny(imgThreshplate, 250, 255)
    kernel = np.ones((3, 3), np.uint8)
    dilated_image = cv2.dilate(canny_image, kernel, iterations=1)
    contours, _ = cv2.findContours(dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:4]

    screenCnt = []
    recognized_plates = set()  # To store unique recognized plates

    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.06 * peri, True)
        if len(approx) == 4 and is_rectangular(approx):
            screenCnt.append(approx)

    if screenCnt:
        for screenCnt in screenCnt:
            roi, imgThresh = extract_license_plate(screenCnt, img, imgThreshplate)
            strFinalString = recognize_characters(roi, imgThresh, kNearest)
            print(f"\nLicense Plate detected: {strFinalString}\n")
            if strFinalString in valid_plates:
                recognized_plates.add(strFinalString)  # Add to the set of recognized plates

    # Process the unique recognized plates
    if recognized_plates:
        for plate in recognized_plates:
            update_status_in_json(plate, "Đã vào")
            log_to_history(plate, "Đã vào")
        # Only send data once
        send_data_to_esp32("Congvao")

def process_license_plate_out(image_path):
    img = cv2.imread(image_path)
    try:
        # Đọc từ tệp plates.json
        with open("C:\\Users\\ACER\\Downloads\\doan2_2\\VIETNAMESE_LICENSE_PLATE-master\\plates.json", "r", encoding="utf-8") as file:
            valid_plates_data = json.load(file)
            # Tạo từ điển biển số và email từ plates.json
            valid_plates = {plate['license']: plate['gmail'] for plate in valid_plates_data}
    except FileNotFoundError:
        print("File plates.json not found.")
        return
    except json.JSONDecodeError:
        print("Error decoding plates.json.")
        return

    # Load dữ liệu training
    npaClassifications = np.loadtxt("classifications.txt", np.float32)
    npaFlattenedImages = np.loadtxt("flattened_images.txt", np.float32)
    npaClassifications = npaClassifications.reshape((npaClassifications.size, 1))
    kNearest = cv2.ml.KNearest_create()
    kNearest.train(npaFlattenedImages, cv2.ml.ROW_SAMPLE, npaClassifications)

    imgGrayscaleplate, imgThreshplate = Preprocess.preprocess(img)
    canny_image = cv2.Canny(imgThreshplate, 250, 255)
    kernel = np.ones((3, 3), np.uint8)
    dilated_image = cv2.dilate(canny_image, kernel, iterations=1)
    contours, _ = cv2.findContours(dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:4]

    screenCnt = []
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.06 * peri, True)
        if len(approx) == 4:  # Nếu là hình chữ nhật
            screenCnt.append(approx)

    if screenCnt:
        for screenCnt in screenCnt:
            roi, imgThresh = extract_license_plate(screenCnt, img, imgThreshplate)
            strFinalString = recognize_characters(roi, imgThresh, kNearest)
            print(f"\nLicense Plate is: {strFinalString}\n")
            if strFinalString in valid_plates:
                recipient_email = valid_plates[strFinalString]
                send_email_php(strFinalString, recipient_email)


def send_data_to_esp32(data):
    esp32_data_endpoint = "http://172.20.10.3/receive_data"
    try:
        response = requests.post(esp32_data_endpoint, data={"data": data})
        if response.status_code == 200:
            print(f"{data} - Sent successfully to ESP32")
        else:
            print("Failed to send. Status code:", response.status_code)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    folder_to_track = r"C:\xampp\htdocs\doan2\uploads"
    folder_to_track_out = r"C:\xampp\htdocs\doan2\uploads_out"
    event_handler = ImageHandler()
    event_handler_out = ImageHandlerOut()
    observer = Observer()
    observer_out = Observer()

    observer.schedule(event_handler, folder_to_track, recursive=False)
    observer_out.schedule(event_handler_out, folder_to_track_out, recursive=False)

    observer.start()
    observer_out.start()
    print(f"Monitoring folder: {folder_to_track}")
    print(f"Monitoring folder: {folder_to_track_out}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer_out.stop()
    observer.join()
    observer_out.join()
