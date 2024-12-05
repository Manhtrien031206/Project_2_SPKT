#include <WiFi.h>
#include <HTTPClient.h>
#include <WebServer.h>
#include <LiquidCrystal_I2C.h>
#include <ESP32Servo.h> // Thư viện điều khiển servo cho ESP32

LiquidCrystal_I2C lcd(0x27, 20, 4);
const char* ssid = "iPhone"; // Tên Wi-Fi
const char* password = "khongnho0169"; // Mật khẩu Wi-Fi
const char* serverIP = "172.20.10.4"; // IP của server để gửi yêu cầu HTTP

WebServer server(80); // Web server trên cổng 80
Servo servo1;         // Servo cho động cơ thứ nhất
Servo servo2;         // Servo cho động cơ thứ hai
const int irSensor1 = 34;
const int irSensor2 = 35;
const int irSensor3 = 32;
const int irSensor4 = 33;
const int irSensor5 = 25;
const int irSensor6 = 26;
const int sensorPin1 = 27; // Cảm biến 1
const int sensorPin2 = 14; // Cảm biến 2
const int servoPin1 = 18;  // GPIO để điều khiển servo thứ nhất
const int servoPin2 = 19;  // GPIO để điều khiển servo thứ hai

int sensorValue1 = 0;
int sensorValue2 = 0;
String status1 = "KC"; // Trạng thái mặc định của cảm biến 1
String status2 = "KC"; // Trạng thái mặc định của cảm biến 2

void setup() {
  Serial.begin(115200);
  pinMode(irSensor1, INPUT);
  pinMode(irSensor2, INPUT);
  pinMode(irSensor3, INPUT);
  pinMode(irSensor4, INPUT);
  pinMode(irSensor5, INPUT);
  pinMode(irSensor6, INPUT);
  pinMode(sensorPin1, INPUT);
  pinMode(sensorPin2, INPUT);
  
  lcd.init();
  lcd.backlight();
  // Kết nối Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // In địa chỉ IP của ESP32
  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());

  // Khởi tạo server HTTP và các servo
  server.on("/receive_data", handleData);
  server.begin();
  
  servo1.attach(servoPin1); // Gắn servo thứ nhất vào GPIO được chỉ định
  servo2.attach(servoPin2); // Gắn servo thứ hai vào GPIO được chỉ định

;
}

void loop() {
  // Xử lý các yêu cầu từ client
  server.handleClient();
  irSensor_lcd();
  // Đọc giá trị cảm biến và cập nhật trạng thái nếu thay đổi
  sensorValue1 = digitalRead(sensorPin1);
  sensorValue2 = digitalRead(sensorPin2);

  String newStatus1 = (sensorValue1 == HIGH) ? "CC" : "KC";
  String newStatus2 = (sensorValue2 == HIGH) ? "CC2" : "KC2";

  Serial.print("Sensor 1 Value: ");
  Serial.println(sensorValue1);
  Serial.print("Sensor 2 Value: ");
  Serial.println(sensorValue2);

  // Gửi trạng thái đến server nếu có thay đổi
  if (status1 != newStatus1) {
    status1 = newStatus1;
    sendStatusToServer(status1);
  }

  if (status2 != newStatus2) {
    status2 = newStatus2;
    sendStatusToServer(status2);
  }

  delay(2000); // Kiểm tra mỗi giây
}

// Hàm gửi trạng thái đến server bên ngoài
void sendStatusToServer(String status) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String serverPath = "http://" + String(serverIP) + ":5000/update_status.php?status=" + status;

    http.begin(serverPath);
    int httpResponseCode = http.GET();

    if (httpResponseCode > 0) {
      Serial.println("Status updated: " + status);
    } else {
      Serial.print("Error in sending request: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  } else {
    Serial.println("WiFi not connected");
  }
}

// Hàm xử lý yêu cầu nhận dữ liệu và điều khiển servo
void handleData() {
  if (server.hasArg("data")) {
    String receivedData = server.arg("data");
    Serial.println("Received data: " + receivedData);

    // Điều khiển servo dựa trên dữ liệu nhận được
    if (receivedData == "Congvao") {
      servo1.write(90);     // Xoay servo thứ nhất đến 90 độ
      delay(6000);          // Giữ ở 90 độ trong 6 giây
      servo1.write(-90);      // Quay về 0 độ ngay sau đó
    } else if (receivedData == "Congra") {
      servo2.write(90);     // Xoay servo thứ hai đến 90 độ
      delay(6000);          // Giữ ở 90 độ trong 6 giây
      servo2.write(-90);      // Quay về 0 độ ngay sau đó
    }
  }
  server.send(200, "text/plain", "Data received");
}
void irSensor_lcd()
{
  int sensorValue1 = digitalRead(irSensor1);
  int sensorValue2 = digitalRead(irSensor2);
  int sensorValue3 = digitalRead(irSensor3);
  int sensorValue4 = digitalRead(irSensor4);
  int sensorValue5 = digitalRead(irSensor5);
  int sensorValue6 = digitalRead(irSensor6);

  // Kiểm tra trạng thái cảm biến và chuyển đổi sang "NA" hoặc "A"
  String s1 = sensorValue1 == LOW ? "NA" : "A";
  String s2 = sensorValue2 == LOW ? "NA" : "A";
  String s3 = sensorValue3 == LOW ? "NA" : "A";
  String s4 = sensorValue4 == LOW ? "NA" : "A";
  String s5 = sensorValue5 == LOW ? "NA" : "A";
  String s6 = sensorValue6 == LOW ? "NA" : "A";

  // Xóa màn hình LCD trước khi in mới
  lcd.clear();

  // Kiểm tra nếu tất cả cảm biến đều là "NA"
  if (s1 == "NA" && s2 == "NA" && s3 == "NA" && s4 == "NA" && s5 == "NA" && s6 == "NA") 
  {
    // Hiển thị thông báo không còn chỗ trống
    lcd.setCursor(0, 0); // Vị trí dòng 1, cột 1
    lcd.print("Xin loi, bai giu xe");
    lcd.setCursor(0, 1); // Vị trí dòng 2, cột 1
    lcd.print("hien khong con cho");
    lcd.setCursor(0, 2); // Vị trí dòng 3, cột 1
    lcd.print("trong!");
  } 
  else 
  {
    // In các giá trị cảm biến lên màn hình LCD 
    lcd.setCursor(0, 0); // Vị trí dòng 1, cột 1
    lcd.print("S1: "); lcd.print(s1); 
    lcd.print("   S2: "); lcd.print(s2);
  
    lcd.setCursor(0, 1); // Vị trí dòng 2, cột 1
    lcd.print("S3: "); lcd.print(s3);
    lcd.print("   S4: "); lcd.print(s4);
    
    lcd.setCursor(0, 2);
    lcd.print("S5: "); lcd.print(s5);
    lcd.print("   S6: "); lcd.print(s6);
  }
  delay(1000);
}