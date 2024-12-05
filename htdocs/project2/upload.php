<?php
if (isset($_FILES['image'])) {
    // Tạo thư mục uploads nếu chưa tồn tại
    if (!is_dir('uploads')) {
        mkdir('uploads');
    }

    // Đường dẫn lưu file ảnh được upload
    $target_dir = "uploads/";
    $target_file = $target_dir . basename($_FILES["image"]["name"]);

    // Lưu ảnh vào thư mục uploads
    if (move_uploaded_file($_FILES["image"]["tmp_name"], $target_file)) {
        // Gọi Python script để xử lý ảnh
        $output = shell_exec("python process_image.py " . escapeshellarg($target_file));

        // In kết quả
        echo "<h3>Kết quả nhận diện biển số:</h3>";
        echo "<p>" . $output . "</p>";
    } else {
        echo "Lỗi khi tải ảnh lên.";
    }
} else {
    echo "Vui lòng chọn một ảnh để upload.";
}
?>
