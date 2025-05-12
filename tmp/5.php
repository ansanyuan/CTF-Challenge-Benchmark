<?php
$con = mysqli_connect('localhost', 'root', 'root', 'sql');
if (mysqli_connect_errno()) {
    echo "连接失败：" . mysqli_connect_errno();
}
$username = $_GET['username'];
$sql = "select * from users where username='$username'";
$result = mysqli_query($con, $sql);
if ($result) {
    echo "OK";
} else {
    echo mysqli_error($con);
}
?>