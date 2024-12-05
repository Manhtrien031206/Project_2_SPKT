import cv2 
from pytesseract import pytesseract
from PIL import Image
from database import checkNp, checkNpStatus, insertNp, updateNp  # Ensure database.py is in the same directory

# Đọc biển số xe từ ảnh đã lưu vào thư mục "images"
def readnumberplate(image_path):
    path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    pytesseract.tesseract_cmd = path_to_tesseract
    image = Image.open(image_path)

    text = pytesseract.image_to_string(image, lang="eng")
    number_plate = ''.join(char for char in str(text) if not char.isspace())
    print("----------------------------------")
    print("Xe co bien so : " + number_plate)
    print("----------------------------------")

    if number_plate:
        check = checkNp(number_plate)
        if check == 0:
            insertNp(number_plate)
        else:
            check2 = checkNpStatus(number_plate)
            if check2[2] == 1:
                updateNp(check2[0])
            else:
                insertNp(number_plate)
    else:
        print("Bien so khong xac dinh !")

# Hardcode đường dẫn ảnh
image_path = r"C:\xampp\htdocs\project2\plate-recognition-main\image7.jpg"

# Kiểm tra đường dẫn ảnh
try:
    # Đọc ảnh từ đường dẫn đã nhập
    image = cv2.imread(image_path)
    
    if image is None:
        raise ValueError("Không thể mở ảnh. Vui lòng kiểm tra đường dẫn.")
    
    # Chuyển đổi ảnh sang màu xám để nhận diện
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imshow("Bien so xe", gray_image)
    
    # Gọi hàm xử lý biển số xe
    readnumberplate(image_path)

    cv2.waitKey(0)  # Chờ cho đến khi nhấn phím để đóng cửa sổ
    cv2.destroyAllWindows()

except Exception as e:
    print(f"Lỗi: {e}")
