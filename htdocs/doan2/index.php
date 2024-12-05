<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quản lý chuỗi biển số</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <style>
        /* Navigation Bar */
        nav {
            background-color: black;
            padding: 10px;
            display: flex;
            justify-content: flex-start;
            align-items: center;
            width: 100%;
            position: fixed;
            top: 0;
            left: 0;
            z-index: 1000;
        }
        nav a {
            color: white;
            text-decoration: none;
            margin: 0 15px;
            font-size: 18px;
            font-weight: bold;
            padding: 5px 10px;
            border-radius: 5px;
        }
        nav a.active {
            background-color: white;
            color: black;
        }
        nav a:hover {
            background-color: white;
            color: black;
        }

        /* Background and Table */
        body {
            background-image: url('/doan2/2.jpg');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            padding-top: 60px;
            color: white;
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        /* Container for the entire table and form */
        .table-container {
            background-color: rgba(0, 0, 0, 0.7);  /* Darker background */
            color: white;
            padding: 20px;
            border-radius: 10px;
            width: 100%;  /* Full width */
            max-width: calc(1800px + 1000px);  /* Increase max width by 5cm (189px) */
            margin-top: 40px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5); /* Shadow effect */
            height: calc(100% + 189px); /* Increase height by 5cm (189px) */
        }

        h1, h2 {
            margin-top: 20px;
            padding: 10px;
            border: 2px solid #007BFF;
            background-color: rgba(0, 0, 0, 0.6);
            border-radius: 5px;
            color: white;
        }

        table {
            background-color: rgba(0, 0, 0, 0.8);
            color: white;
            border-collapse: collapse;
            width: 100%;
            margin-top: 20px;
            border: 2px solid #007BFF;
        }

        th, td {
            padding: 12px;
            text-align: center;
            border: 1px solid #444;
        }

        th {
            background-color: #333;
            font-weight: bold;
        }

        #add-plate-form {
            margin-top: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        input[type="text"] {
            padding: 10px;
            width: 300px;
            margin-bottom: 10px;
            background-color: rgba(255, 255, 255, 0.8);
            border-radius: 5px;
            border: 1px solid #007BFF;
        }

        input[type="date"] {
            padding: 10px;
            width: 300px;
            margin-bottom: 10px;
            background-color: rgba(255, 255, 255, 0.8);
            border-radius: 5px;
            border: 1px solid #007BFF;
        }

        input[type="email"] {
            padding: 10px;
            width: 300px;
            margin-bottom: 10px;
            background-color: rgba(255, 255, 255, 0.8);
            border-radius: 5px;
            border: 1px solid #007BFF;
        }
        button {
            padding: 10px;
            background-color: #007BFF;
            color: white;
            border: none;
            cursor: pointer;
            border-radius: 5px;
        }

        button:hover {
            background-color: #0056b3;
        }

        table tr:hover {
            background-color: white;
            color: black;
        }

        .content {
            display: none;
            margin-top: 20px;
        }

        .active-content {
            display: block;
        }
    </style>
</head>
<body>
    <nav>
        <a href="#list" id="list-tab" class="active">List</a>
        <a href="#history" id="history-tab">History</a>
    </nav>

    <div id="list" class="content active-content">
    <!-- Container for Table and Form -->
    <div class="table-container">
        <h1>DANH SÁCH BIỂN SỐ ĐÃ ĐĂNG KÝ</h1>

        <table>
            <thead>
                <tr>
                    <th>Biển số</th>
                    <th>Trạng thái</th>
                    <th>Thời gian hết hạn</th>
                    <th>Số điện thoại</th>
                    <th>Gmail</th>
                    <th>Xóa</th>
                </tr>
            </thead>
            <tbody id="plate-list">
                <!-- Rows will be populated by JSON data -->
            </tbody>
        </table>

        <h2>Thêm biển số mới</h2>
        <form id="add-plate-form">
            <input type="text" name="new_plate" id="new_plate" placeholder="Nhập biển số mới" required>
            <input type="date" name="expiration_date" id="expiration_date" required>
            <input type="text" name="phone_number" id="phone_number" placeholder="Nhập số điện thoại" required>
            <input type="email" name="gmail" id="gmail" placeholder="Nhập Gmail" required>
            <button type="submit">Thêm</button>
        </form>
    </div>
</div>

    <div id="history" class="content">
    <h1>Lịch sử biển số</h1>
    <table>
        <thead>
            <tr>
                <th>STT</th>
                <th>Biển số</th>
                <th>Thời gian</th>
                <th>Trạng thái</th>
            </tr>
        </thead>
        <tbody id="history-list">
            <!-- Rows will be populated by JSON data -->
        </tbody>
    </table>
</div>

<script>
    $(document).ready(function() {
    loadPlates();
    loadHistory();

    // Switch between List and History tabs
    $('nav a').click(function() {
        $('nav a').removeClass('active');
        $(this).addClass('active');
        $('.content').removeClass('active-content');
        var target = $(this).attr('href').substring(1);
        $('#' + target).addClass('active-content');
    });

    $('#add-plate-form').submit(function(e) {
        e.preventDefault();
        let newPlate = $('#new_plate').val();
        let expirationDate = $('#expiration_date').val();
        let phoneNumber = $('#phone_number').val();
        let gmail = $('#gmail').val(); // Lấy Gmail từ form

        $.post('update_plates.php', { action: 'add', plate: newPlate, expiration_date: expirationDate, phone_number: phoneNumber, gmail: gmail }, function(response) {
            $('#new_plate').val('');
            $('#expiration_date').val('');
            $('#phone_number').val('');
            $('#gmail').val('');
            loadPlates(); // Refresh the plate list after adding
        });
    });

    setInterval(function() {
        loadPlates();
        loadHistory();
    }, 3000); // Refresh every 3 seconds
});
// Gửi yêu cầu ra khỏi bãi xe
function requestExit(license_plate) {
    $.post("exit_request.php", { 
        action: "exit_request", 
        license_plate: license_plate
    }, function(response) {
        alert(response); // Hiển thị thông báo từ server
    });
}


function loadPlates() {
    $.getJSON('update_plates.php', function(data) {
        let rows = '';
        $.each(data, function(index, plate) {
            rows += `<tr>
                <td>${plate.license}</td>
                <td>${plate.status}</td>
                <td>${plate.expiration_time}</td>
                <td>${plate.phone_number}</td>
                <td>${plate.gmail}</td>
                <td><button onclick="deletePlate(${index})">Xóa</button></td>
            </tr>`;
        });
        $('#plate-list').html(rows);
    });
}

    function loadHistory() {
    $.getJSON('update_history.php', function(data) {
        let rows = '';
        $.each(data, function(index, entry) {
            rows += `<tr>
                <td>${index + 1}</td>  <!-- STT column -->
                <td>${entry.license_plate}</td>
                <td>${entry.time}</td>
                <td>${entry.status}</td>
            </tr>`;
        });
        $('#history-list').html(rows);
    });
    }

    function updatePlate(index) {
        let updatedPlate = $(`input[data-index="${index}"]`).val();
        $.post('update_plates.php', { action: 'edit', index: index, plate: updatedPlate }, function(response) {
            loadPlates(); // Refresh the plate list after updating
        });
    }

    function deletePlate(index) {
    $.post('update_plates.php', { action: 'delete', index: index }, function(response) {
        loadPlates(); // Refresh the plate list after deleting
    });
}
</script>
</body>
</html>
