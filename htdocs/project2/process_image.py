import cv2
import pytesseract

# Cấu hình đường dẫn đến tệp thực thi Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


image_path = r'C:\xampp\htdocs\project2\uploads\quy-trinh-bam-bien-so-xe-may-cu.jpeg'

# Đ
# Đọc ảnh
image = cv2.imread(image_path)

# Chuyển đổi ảnh sang xám
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Áp dụng GaussianBlur để giảm nhiễu
blurred = cv2.GaussianBlur(gray, (5, 5), 0)

# Sử dụng phương pháp Canny để phát hiện biên
edges = cv2.Canny(blurred, 50, 150)

# Tìm các đường viền trong ảnh
contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# Lọc các đường viền để tìm biển số xe
license_plate = None
for contour in contours:
    # Tính toán diện tích của đường viền
    area = cv2.contourArea(contour)
    if area > 500:  # Lọc diện tích để loại bỏ các đường viền nhỏ
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / h
        # Giả định rằng biển số xe có tỷ lệ khung hình nhất định
        if 2 < aspect_ratio < 5:
            license_plate = image[y:y + h, x:x + w]
            break

if license_plate is not None:
    # Chuyển đổi biển số xe thành văn bản
    license_plate_text = pytesseract.image_to_string(license_plate, config='--psm 8')
    print("Biển số xe nhận dạng được:", license_plate_text.strip())
else:
    print("Không tìm thấy biển số xe.")
