<?php
use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

require 'PHPMailer/src/Exception.php';
require 'PHPMailer/src/PHPMailer.php';
require 'PHPMailer/src/SMTP.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $plate_number = $_POST['plate_number'];
    $recipient_email = $_POST['recipient_email'];

    $mail = new PHPMailer(true);

    try {
        // Cấu hình SMTP
        $mail->isSMTP();
        $mail->Host = 'smtp.gmail.com'; // Hoặc mail server của bạn
        $mail->SMTPAuth = true;
        $mail->Username   = 'phmt612@gmail.com';   //SMTP write your email
        $mail->Password   = 'nayipvzrnrzzulnp';      //SMTP password
        $mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS;
        $mail->Port = 587;

        // Cấu hình người gửi và người nhận
        $mail->setFrom('phmt612@gmail.com', 'System');
        $mail->addAddress($recipient_email);

        // Nội dung mail
        $mail->isHTML(true);
        $mail->Subject = 'Xac nhan bien so xe: ' . $plate_number;
        $mail->Body = "
    <p>Biển số xe: <b>$plate_number</b> đã được phát hiện.</p>
    <p>Bạn có cho phép xe ra khỏi bãi không:</p>
    <a href='http://172.20.10.4/doan2/handle_accept.php?plate_number=$plate_number' style='padding:10px 15px; background-color:green; color:white; text-decoration:none;'>Chấp nhận</a>
    <a href='http://172.20.10.4/doan2/handle_reject.php?plate_number=$plate_number' style='padding:10px 15px; background-color:red; color:white; text-decoration:none;'>Không chấp nhận</a>
";

        $mail->send();
        echo "Email sent successfully to $recipient_email";
    } catch (Exception $e) {
        echo "Error sending email: {$mail->ErrorInfo}";
    }
}
?>h
