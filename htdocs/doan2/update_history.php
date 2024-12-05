<?php
// Đường dẫn tới tệp history.json
$historyFilePath = 'C:\\Users\\ACER\\Downloads\\doan2_2\\VIETNAMESE_LICENSE_PLATE-master\\history.json';

// Kiểm tra xem yêu cầu có phải là POST không
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $licensePlate = isset($_POST['license_plate']) ? $_POST['license_plate'] : '';
    $status = isset($_POST['status']) ? $_POST['status'] : '';

    if (!empty($licensePlate) && !empty($status)) {
        $logEntry = array(
            "license_plate" => $licensePlate,
            "time" => date("Y-m-d H:i:s"),
            "status" => $status
        );

        if (file_exists($historyFilePath)) {
            $historyData = json_decode(file_get_contents($historyFilePath), true);
            if ($historyData === null) {
                $historyData = array();
            }
        } else {
            $historyData = array();
        }

        $historyData[] = $logEntry;

        if (file_put_contents($historyFilePath, json_encode($historyData, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT))) {
            echo "Cập nhật lịch sử thành công.";
        } else {
            echo "Lỗi khi ghi vào tệp history.json.";
        }
    } else {
        echo "Dữ liệu không hợp lệ.";
    }
} elseif ($_SERVER['REQUEST_METHOD'] === 'GET') {
    if (file_exists($historyFilePath)) {
        header('Content-Type: application/json');
        $historyData = json_decode(file_get_contents($historyFilePath), true);

        // Đảo ngược thứ tự của mảng để bản ghi mới nhất lên trên cùng
        $historyData = array_reverse($historyData);

        echo json_encode($historyData);
    } else {
        echo json_encode([]);
    }
} else {
    echo "Yêu cầu không hợp lệ.";
}
?>
