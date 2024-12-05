<?php
// Đường dẫn tới tệp history.json
$historyFilePath = 'C:\\Users\\ACER\\Downloads\\doan2_2\\VIETNAMESE_LICENSE_PLATE-master\\history.json';

// Kiểm tra xem yêu cầu có phải là POST không
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Lấy dữ liệu từ yêu cầu POST
    $licensePlate = isset($_POST['license_plate']) ? $_POST['license_plate'] : '';
    $status = isset($_POST['status']) ? $_POST['status'] : '';

    // Kiểm tra xem các giá trị có hợp lệ không
    if (!empty($licensePlate) && !empty($status)) {
        // Tạo một mục lịch sử mới với biển số, thời gian hiện tại và trạng thái
        $logEntry = array(
            "license_plate" => $licensePlate,
            "time" => date("Y-m-d H:i:s"),
            "status" => $status
        );

        // Kiểm tra xem tệp history.json có tồn tại không và đọc dữ liệu hiện tại
        if (file_exists($historyFilePath)) {
            $historyData = json_decode(file_get_contents($historyFilePath), true);
            if ($historyData === null) {
                $historyData = array();
            }
        } else {
            $historyData = array();
        }

        // Thêm bản ghi mới vào lịch sử
        $historyData[] = $logEntry;

        // Ghi lại dữ liệu vào tệp history.json
        if (file_put_contents($historyFilePath, json_encode($historyData, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT))) {
            echo "Cập nhật lịch sử thành công.";
        } else {
            echo "Lỗi khi ghi vào tệp history.json.";
        }
    } else {
        echo "Dữ liệu không hợp lệ.";
    }
} else {
    echo "Chỉ hỗ trợ yêu cầu POST.";
}
?>
