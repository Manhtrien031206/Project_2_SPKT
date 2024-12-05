import requests

esp32_ip = "http://172.20.10.3/receive_data"  # Thay bằng IP ESP32 của bạn
data = {"data": "Hello ESP32!"}  # Dữ liệu bạn muốn gửi

try:
    response = requests.post(esp32_ip, data=data)
    if response.status_code == 200:
        print("Data sent successfully to ESP32")
    else:
        print("Failed to send data. Status code:", response.status_code)
except Exception as e:
    print("An error occurred:", e)
