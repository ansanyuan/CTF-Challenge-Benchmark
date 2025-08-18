<?php
$con = mysqli_connect("localhost", "root", "root");
mysqli_select_db($con, 'sql');
if (mysqli_connect_errno()) {
    echo "数据库连接出错：" . mysql_connect_error();
}
$id = $_GET["id"];
$result = mysqli_query($con, "select * from users where id=$id");
$row = mysqli_fetch_array($result);
echo $row['username'] . ":" . $row['address'];
echo "<br>";
?>