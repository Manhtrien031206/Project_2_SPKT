import os
from flask import Flask, request
import cv2

app = Flask(__name__)

# Biến toàn cục để lưu trữ trạng thái
status = "KC"  # Trạng thái ban đầu
upload_folder = r"D:\DO_AN_2\VIETNAMESE_LICENSE_PLATE-master\VIETNAMESE_LICENSE_PLATE-master\data\image"

@app.route('/update_status.php', methods=['GET'])
def update_status():
    global status
    new_status = request.args.get('status')
    print(f"Received request to update status to: {new_status}")  # Debug message
    if new_status:
        status = new_status
        if status == "KC":
            capture_image()  # Gọi hàm chụp ảnh khi trạng thái là KC
        return "Status updated", 200
    return "No status received", 400

@app.route('/get_status', methods=['GET'])
def get_status():
    return status, 200

def capture_image():
    # Mở camera
    cap = cv2.VideoCapture(1)  # 0 cho camera mặc định
    ret, frame = cap.read()
    if ret:
        # Đường dẫn tới file ảnh
        image_path = os.path.join(upload_folder, "image.jpg")

        # Kiểm tra nếu ảnh cũ đã tồn tại thì xóa
        if os.path.exists(image_path):
            os.remove(image_path)

        # Lưu ảnh mới
        cv2.imwrite(image_path, frame)
        print(f"Image captured and saved to {image_path}")

    cap.release()  # Giải phóng camera

if __name__ == "__main__":
    app.run(host="172.20.10.4", port=5000)
