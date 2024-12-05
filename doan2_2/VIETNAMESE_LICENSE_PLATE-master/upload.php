<?php
$target_dir = "uploads/";  // Thư mục uploads
$target_file = $target_dir . "image.jpg";  // Lưu ảnh với tên cố định là image.jpg

if (move_uploaded_file($_FILES["image"]["tmp_name"], $target_file)) {
    echo "The file has been uploaded.";
} else {
    echo "Sorry, there was an error uploading your file.";
}
?>
