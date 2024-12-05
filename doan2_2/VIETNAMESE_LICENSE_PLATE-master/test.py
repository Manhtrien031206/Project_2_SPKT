import cv2
import os
import time

# Đường dẫn thư mục lưu ảnh
upload_path = r'C:\xampp\htdocs\doan2\uploads'

# Tên ảnh lưu trữ
image_name = 'image.jpg'
image_path = os.path.join(upload_path, image_name)

# Kiểm tra thư mục upload có tồn tại không, nếu không thì tạo
if not os.path.exists(upload_path):
    os.makedirs(upload_path)

# Hàm chụp ảnh
def capture_image():
    # Mở camera
    cap = cv2.VideoCapture(0)  # Camera mặc định, thay số 0 nếu dùng camera khác
    if not cap.isOpened():
        print("Không thể mở camera.")
        return

    ret, frame = cap.read()
    if ret:
        # Lưu ảnh
        cv2.imwrite(image_path, frame)
        print(f"Đã lưu ảnh tại {image_path}")
    else:
        print("Không thể chụp ảnh.")
    
    # Giải phóng camera
    cap.release()

# Chụp ảnh mỗi 5 giây
try:
    while True:
        capture_image()
        time.sleep(5)  # Dừng 5 giây
except KeyboardInterrupt:
    print("Dừng chương trình.")
