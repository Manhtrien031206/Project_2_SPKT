#include <WiFi.h>
#include <WebServer.h>
#include <ESP32Servo.h> // Thư viện điều khiển Servo cho ESP32

const char* ssid = "iPhone";
const char* password = "khongnho0169";
WebServer server(80);

Servo myServo; // Tạo đối tượng servo
int servoPin = 18; // Chân GPIO nối với chân điều khiển servo

void handleData() {
  if (server.hasArg("data")) {
    String receivedData = server.arg("data");
    Serial.println("Received data: " + receivedData);
    
    // Điều khiển servo xoay 90 độ rồi trở lại vị trí ban đầu
    myServo.write(90);     // Xoay servo đến góc 90 độ
    delay(1000);           // Giữ ở 90 độ trong 1 giây
    myServo.write(0);      // Trở lại vị trí ban đầu (0 độ)
  }
  server.send(200, "text/plain", "Data received");
}

void setup() {
  Serial.begin(115200);

  // Kết nối WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // Cấu hình server và servo
  server.on("/receive_data", handleData);
  server.begin();
  myServo.attach(servoPin); // Kết nối servo với chân GPIO
}

void loop() {
  server.handleClient(); // Xử lý các yêu cầu từ client
}
