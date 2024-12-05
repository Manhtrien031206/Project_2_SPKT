import cv2

# Khởi tạo camera (0 là chỉ số camera, có thể thay đổi nếu có nhiều camera)
cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("Không thể mở camera")
    exit()

# Đọc video từ camera
while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Không thể đọc video")
        break

    cv2.imshow('Webcam', frame)

    # Nhấn 'q' để thoát và chụp ảnh
    if cv2.waitKey(1) & 0xFF == ord('q'):
        # Lưu ảnh
        cv2.imwrite('image.jpg', frame)
        print("Ảnh đã được lưu!")
        break

# Giải phóng camera và đóng cửa sổ
cap.release()
cv2.destroyAllWindows()

