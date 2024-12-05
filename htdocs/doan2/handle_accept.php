<?php
if (isset($_GET['plate_number'])) {
    $plate_number = $_GET['plate_number'];
    date_default_timezone_set('Asia/Ho_Chi_Minh');

    // Đường dẫn file trạng thái đã gửi
    $sent_status_path = "C:/Users/ACER/Downloads/doan2_2/VIETNAMESE_LICENSE_PLATE-master/sent_status.json";

    // 1. Kiểm tra trạng thái đã gửi
    if (file_exists($sent_status_path)) {
        $sent_status = json_decode(file_get_contents($sent_status_path), true);
    } else {
        $sent_status = [];
    }


    // 2. Gửi mã về ESP32
    $esp32_url = 'http://172.20.10.3/receive_data';
    $data = ['data' => 'Congra'];

    $options = [
        'http' => [
            'header'  => "Content-type: application/x-www-form-urlencoded\r\n",
            'method'  => 'POST',
            'content' => http_build_query($data),
        ],
    ];

    $context = stream_context_create($options);
    $result = file_get_contents($esp32_url, false, $context);

    if ($result === FALSE) {
        echo "Error sending data to ESP32.<br>";
        exit();
    } else {
        echo "Data sent to ESP32 successfully.<br>";
    }

    // 3. Cập nhật trạng thái trong plates.json
    $plates_file_path = "C:/Users/ACER/Downloads/doan2_2/VIETNAMESE_LICENSE_PLATE-master/plates.json";

    if (file_exists($plates_file_path)) {
        $plates_data = json_decode(file_get_contents($plates_file_path), true);

        $plate_found = false;
        foreach ($plates_data as &$plate) {
            if ($plate['license'] === $plate_number) {
                $plate['status'] = "Đã ra"; // Cập nhật trạng thái
                $plate_found = true;
                break;
            }
        }

        if ($plate_found) {
            file_put_contents($plates_file_path, json_encode($plates_data, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT));
            echo "Cập nhật trạng thái cho biển số $plate_number thành 'Đã ra'.<br>";
        } else {
            echo "Không tìm thấy biển số $plate_number trong plates.json.<br>";
        }
    } else {
        echo "File plates.json không tồn tại.<br>";
    }

    // 4. Ghi log vào history.json
    $history_file_path = "C:/Users/ACER/Downloads/doan2_2/VIETNAMESE_LICENSE_PLATE-master/history.json";

    $log_entry = [
        "license_plate" => $plate_number,
        "time" => date("Y-m-d H:i:s"),
        "status" => "Đã ra"
    ];

    if (file_exists($history_file_path)) {
        $history_data = json_decode(file_get_contents($history_file_path), true);
    } else {
        $history_data = [];
    }

    $history_data[] = $log_entry;

    if (file_put_contents($history_file_path, json_encode($history_data, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT))) {
        echo "Logged to history: " . json_encode($log_entry) . "<br>";
    } else {
        echo "Error logging to history.json.<br>";
    }

    // 5. Đánh dấu biển số là đã gửi
    $sent_status[$plate_number] = true;
    if (file_put_contents($sent_status_path, json_encode($sent_status, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT))) {
        echo "Cập nhật trạng thái gửi thành công cho biển số $plate_number.<br>";
    } else {
        echo "Lỗi khi cập nhật trạng thái gửi.<br>";
    }
} else {
    echo "Biển số không được cung cấp.<br>";
}
?>
