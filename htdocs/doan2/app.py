from flask import Flask, request, jsonify
import cv2
from datetime import datetime
import os
import threading
import time

app = Flask(__name__)

# Đường dẫn thư mục lưu ảnh
UPLOADS_DIR = "C:\\xampp\\htdocs\\doan2\\uploads"
UPLOADS_OUT_DIR = "C:\\xampp\\htdocs\\doan2\\uploads_out"

# Trạng thái cảm biến và thời gian chụp ảnh lần cuối
sensor_status = {"KC": False, "KC2": False}
last_captured_time = {"KC": None, "KC2": None}
capture_intervals = {"KC": 10, "KC2": 100}  # Chu kỳ chụp ảnh: KC (10s), KC2 (20s)
initial_delay = 3  # Thời gian chờ chụp ảnh đầu tiên (giây)


# Hàm chụp ảnh và lưu vào thư mục tương ứng
def capture_image(camera_id, label, save_dir):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)  # Tạo thư mục nếu chưa tồn tại
    
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        print(f"Cannot open camera {camera_id}")
        return {"status": "error", "message": f"Cannot open camera {camera_id}"}
    
    ret, frame = cap.read()
    if ret:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(save_dir, f"{label}_camera{camera_id}_{timestamp}.jpg")
        cv2.imwrite(filename, frame)
        print(f"Image captured and saved as {filename}")
        cap.release()
        return {"status": "success", "message": f"Image saved as {filename}"}
    else:
        cap.release()
        print(f"Failed to capture image from camera {camera_id}")
        return {"status": "error", "message": "Failed to capture image"}


# Hàm chạy kiểm tra trạng thái và chụp ảnh nếu cần
def monitor_capturing():
    while True:
        current_time = time.time()

        # Kiểm tra trạng thái KC
        if sensor_status["KC"]:
            if last_captured_time["KC"] is None:  # Nếu chưa chụp lần nào
                if current_time - sensor_status["KC_start_time"] >= initial_delay:
                    capture_image(4, "KC", UPLOADS_DIR)
                    last_captured_time["KC"] = current_time
            elif current_time - last_captured_time["KC"] >= capture_intervals["KC"]:
                capture_image(4, "KC", UPLOADS_DIR)
                last_captured_time["KC"] = current_time

        # Kiểm tra trạng thái KC2
        if sensor_status["KC2"]:
            if last_captured_time["KC2"] is None:  # Nếu chưa chụp lần nào
                if current_time - sensor_status["KC2_start_time"] >= initial_delay:
                    capture_image(0, "KC2", UPLOADS_OUT_DIR)
                    last_captured_time["KC2"] = current_time
            elif current_time - last_captured_time["KC2"] >= capture_intervals["KC2"]:
                capture_image(0, "KC2", UPLOADS_OUT_DIR)
                last_captured_time["KC2"] = current_time

        time.sleep(1)  # Kiểm tra mỗi giây


# Route nhận yêu cầu từ ESP32
@app.route('/update_status', methods=['GET'])
@app.route('/update_status.php', methods=['GET'])  # Hỗ trợ cả hai endpoint
def update_status():
    # Lấy tham số 'status' từ ESP32
    status = request.args.get('status')
    if not status:
        return jsonify({"status": "error", "message": "Missing status parameter"}), 400

    # Xử lý trạng thái
    if status == "KC":
        print("Received KC, starting capture sequence...")
        sensor_status["KC"] = True
        sensor_status["KC_start_time"] = time.time()  # Lưu thời điểm nhận tín hiệu
        last_captured_time["KC"] = None  # Reset thời gian chụp ảnh
    elif status == "KC2":
        print("Received KC2, starting capture sequence...")
        sensor_status["KC2"] = True
        sensor_status["KC2_start_time"] = time.time()  # Lưu thời điểm nhận tín hiệu
        last_captured_time["KC2"] = None  # Reset thời gian chụp ảnh
    elif status == "CC":
        print("Received CC, stopping KC capturing...")
        sensor_status["KC"] = False
    elif status == "CC2":
        print("Received CC2, stopping KC2 capturing...")
        sensor_status["KC2"] = False
    else:
        return jsonify({"status": "error", "message": "Unknown status"}), 400

    return jsonify({"status": "success", "message": f"Handled status {status}"})


# Chạy server và luồng kiểm tra trạng thái
if __name__ == '__main__':
    # Chạy luồng giám sát trạng thái
    threading.Thread(target=monitor_capturing, daemon=True).start()
    app.run(host='172.20.10.4', port=5000, debug=True)
