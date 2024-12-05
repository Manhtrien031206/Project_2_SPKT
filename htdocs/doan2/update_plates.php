<?php
$dataFile = 'C:\\Users\\ACER\\Downloads\\doan2_2\\VIETNAMESE_LICENSE_PLATE-master\\plates.json';
$plates = json_decode(file_get_contents($dataFile), true) ?: [];

// Function to check if the expiration date has passed
function checkExpiration($expirationDate) {
    $currentDate = date('Y-m-d');
    return $currentDate > $expirationDate;
}

// Clean up expired plates
$plates = array_filter($plates, function($plate) {
    return !checkExpiration($plate['expiration_time']);
});

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = $_POST['action'];

    if ($action === 'add') {
        $newPlate = $_POST['plate'];
        $expirationDate = $_POST['expiration_date'];
        $phoneNumber = $_POST['phone_number'];
        $gmail = $_POST['gmail'];

        // Add the new plate with phone number and gmail
        $plates[] = [
            'license' => $newPlate,
            'status' => 'Chưa vào',
            'expiration_time' => $expirationDate,
            'phone_number' => $phoneNumber,
            'gmail' => $gmail
        ];
    } elseif ($action === 'edit') {
        $index = $_POST['index'];
        $updatedPlate = $_POST['plate'];
        if (isset($plates[$index])) {
            $plates[$index]['license'] = $updatedPlate;
        }
    } elseif ($action === 'delete') {
        $index = $_POST['index'];
        if (isset($plates[$index])) {
            array_splice($plates, $index, 1);
        }
    }

    // Write the updated plates back to the JSON file
    file_put_contents($dataFile, json_encode(array_values($plates), JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT));
}

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    // Return the plates as JSON
    echo json_encode(array_values($plates), JSON_UNESCAPED_UNICODE);
}
?>
