import math
import time
import cv2
import numpy as np
import Preprocess as Preprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from flask import Flask, request
import os
from datetime import datetime
import requests
import json
from datetime import datetime

ADAPTIVE_THRESH_BLOCK_SIZE = 19
ADAPTIVE_THRESH_WEIGHT = 9
Min_char = 0.01
Max_char = 0.09
RESIZED_IMAGE_WIDTH = 20
RESIZED_IMAGE_HEIGHT = 30
#esp32_ip = "http://172.20.10.2"

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
            print(f"New image detected: {event.src_path}")
            time.sleep(1)
            process_license_plate(event.src_path)
def log_to_history(license_plate, status):
    """
    Ghi dữ liệu vào tệp history.json với biển số, thời gian và trạng thái.
    
    Args:
        license_plate (str): Biển số được nhận diện.
        status (str): Trạng thái, ví dụ: "Đã vào".
    """
    log_entry = {
        "license_plate": license_plate,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": status
    }
    
    history_file_path = "C:\\Users\\ACER\\Downloads\\doan2_2\\VIETNAMESE_LICENSE_PLATE-master\\history.json"
    
    try:
        # Đọc dữ liệu hiện tại trong tệp history.json nếu tồn tại
        if os.path.exists(history_file_path):
            with open(history_file_path, "r", encoding="utf-8") as file:
                history_data = json.load(file)
        else:
            history_data = []
        
        # Thêm bản ghi mới vào danh sách lịch sử
        history_data.append(log_entry)
        
        # Ghi lại dữ liệu vào tệp history.json
        with open(history_file_path, "w", encoding="utf-8") as file:
            json.dump(history_data, file, ensure_ascii=False, indent=4)
        
        print(f"Đã ghi vào history: {log_entry}")
    
    except Exception as e:
        print(f"Lỗi khi ghi vào history.json: {e}")
def process_license_plate(image_path):            
    n = 1
    img = cv2.imread(image_path)
    
    try:
        with open("C:\\Users\\ACER\\Downloads\\doan2_2\\VIETNAMESE_LICENSE_PLATE-master\\plates.json", "r", encoding="utf-8") as file:
            valid_plates_data = json.load(file)
            valid_plates = [plate['license'] for plate in valid_plates_data]  # Extract just the license plate numbers
    except FileNotFoundError:
        print("File plates.json không tồn tại.")
        return
    except json.JSONDecodeError:
        print("Lỗi định dạng trong file plates.json.")
        return

    # Load và huấn luyện mô hình nhận dạng ký tự
    npaClassifications = np.loadtxt("classifications.txt", np.float32)
    npaFlattenedImages = np.loadtxt("flattened_images.txt", np.float32)
    npaClassifications = npaClassifications.reshape((npaClassifications.size, 1))
    kNearest = cv2.ml.KNearest_create()
    kNearest.train(npaFlattenedImages, cv2.ml.ROW_SAMPLE, npaClassifications)
    
    # Xử lý ảnh
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
        if len(approx) == 4 and is_rectangular(approx):
            screenCnt.append(approx)
            [x, y, w, h] = cv2.boundingRect(approx.copy())
            cv2.putText(img, str(len(approx.copy())), (x, y), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 255, 0), 3)

    if screenCnt:
        for screenCnt in screenCnt:
            cv2.drawContours(img, [screenCnt], -1, (0, 255, 0), 3)
            roi, imgThresh = extract_license_plate(screenCnt, img, imgThreshplate)
            strFinalString = recognize_characters(roi, imgThresh, kNearest)
            print(f"\nLicense Plate {n} is: {strFinalString}\n")
            n += 1

            # Kiểm tra biển số nhận dạng
            if strFinalString in valid_plates:
                #-------------------------------------------------------------------------------------------------
                send_data_to_esp32("Congvao")
                #-------------------------------------------------------------------------------------------------
                # Cập nhật trạng thái biển số từ "Chưa vào" thành "Đã vào"
                update_status_in_json(strFinalString, "Đã vào")
                log_to_history(strFinalString, "Đã vào")

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
    
    # Danh sách chứa các nhóm (hàng) các ký tự
    rows = []

    # Lưu trữ các bounding box (x, y, w, h) của các ký tự
    char_bboxes = []
    
    for cnt in cont:
        (x, y, w, h) = cv2.boundingRect(cnt)
        char_area = w * h
        height, width, _ = roi.shape
        roiarea = height * width
        if (Min_char * roiarea < char_area < Max_char * roiarea) and (0.25 < w / h < 0.7):
            char_bboxes.append((x, y, w, h, cnt))
    
    # Sắp xếp các bounding box theo y (từ trên xuống dưới), nếu y trùng thì sắp xếp theo x (từ trái sang phải)
    char_bboxes = sorted(char_bboxes, key=lambda b: (b[1], b[0]))

    # Nhóm các bounding box thành các hàng (rows)
    current_row = []
    prev_y = -1
    threshold_y = 10  # Ngưỡng để phân biệt các hàng, có thể điều chỉnh

    for (x, y, w, h, cnt) in char_bboxes:
        if prev_y == -1 or abs(prev_y - y) < threshold_y:  # Còn trong cùng một hàng
            current_row.append((x, y, w, h, cnt))
        else:  # Một hàng mới bắt đầu
            rows.append(sorted(current_row, key=lambda b: b[0]))  # Sắp xếp theo x trong hàng
            current_row = [(x, y, w, h, cnt)]  # Khởi tạo hàng mới
        prev_y = y

    # Thêm hàng cuối cùng vào
    if current_row:
        rows.append(sorted(current_row, key=lambda b: b[0]))

    # Nhận diện ký tự theo từng hàng và từ trái sang phải trong mỗi hàng
    strFinalString = ""
    for row in rows:
        for (x, y, w, h, cnt) in row:
            imgROI = thre_mor[y:y + h, x:x + w]
            imgROIResized = cv2.resize(imgROI, (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT))
            npaROIResized = imgROIResized.reshape((1, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))
            _, npaResults, _, _ = kNearest.findNearest(np.float32(npaROIResized), k=3)
            strFinalString += str(chr(int(npaResults[0][0])))
    
    return strFinalString

def update_history(license_plate, status="Đã vào"):
    history_file = "C:\\Users\\ACER\\Downloads\\doan2_2\\VIETNAMESE_LICENSE_PLATE-master\\history.json"
    
    # Create a new entry with the current time, license plate, and status
    entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "plate": license_plate,
        "status": status
    }
    
    # Load existing history data, if any
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as file:
            try:
                history_data = json.load(file)
            except json.JSONDecodeError:
                # If the file is empty or corrupted, initialize an empty list
                history_data = []
    else:
        history_data = []

    # Append the new entry to the history data
    history_data.append(entry)

    # Write the updated history data back to the file
    with open(history_file, "w", encoding="utf-8") as file:
        json.dump(history_data, file, ensure_ascii=False, indent=4)
    
    print(f"Lịch sử đã được cập nhật cho biển số {license_plate}")

def send_data_to_esp32(data):
    esp32_data_endpoint = "http://172.20.10.2/receive_data"  # Cập nhật IP ESP32 nếu cần
    try:
        response = requests.post(esp32_data_endpoint, data={"data": data})
        if response.status_code == 200:
            print(f"{data} - Đã gửi thành công đến ESP32")
        else:
            print("Gửi thất bại. Mã trạng thái:", response.status_code)
    except Exception as e:
        print("Có lỗi xảy ra:", e)

if __name__ == "__main__":
    folder_to_track = r"C:\xampp\htdocs\doan2\uploads"
    event_handler = ImageHandler()
    observer = Observer()
    observer.schedule(event_handler, folder_to_track, recursive=False)
    observer.start()
    print(f"Đang theo dõi tệp: {folder_to_track}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()