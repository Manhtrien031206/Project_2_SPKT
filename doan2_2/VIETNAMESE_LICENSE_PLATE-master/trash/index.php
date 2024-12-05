<!DOCTYPE html>
<html>
<head>
  <title>TTL Status</title>
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
  <script type="text/javascript">
    $(document).ready(function(){
      setInterval(function(){
        $.ajax({
          url: "http://172.20.10.4:5000/get_status",
          method: "GET",
          success: function(data) {
            $('#status').text(data);
          }
        });
      }, 1000); // Check every 1 second
    });
  </script>
</head>
<body>
  <h1>TTL Sensor Status: <span id="status">KC</span></h1>
</body>
</html>
