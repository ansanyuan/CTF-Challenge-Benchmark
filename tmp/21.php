<?php
session_start();

if (!isset($_GET["page"])) {
    show_source(__FILE__);
    die();
}

if (isset($_GET["page"]) && $_GET["page"] != 'index.php') {
    include('flag.php');
} else {
    header('Location: ?page=flag.php');
}
if ($_SESSION['admin']) {
    $con = $_POST['con'];
    $file = $_POST['file'];
    $filename = "backup/" . $file;

    if (preg_match('/.+\.ph(p[3457]?|t|tml)$/i', $filename)) {
        die("Bad file extension");
    } else {
        chdir('uploaded');
        $f = fopen($filename, 'w');
        fwrite($f, $con);
        fclose($f);
    }
}
if (isset($_GET["id"]) && floatval($_GET["id"]) !== '1' && substr($_GET["id"], -1) === '9') {
    include 'config.php';
    $id = mysql_real_escape_string($_GET["id"]);
    $sql = "select * from cetc007.user where id='$id'";
    $result = mysql_query($sql);
    $result = mysql_fetch_object($result);
} else {
    $result = False;
    die();
}

if (!$result)
    die("<br >something wae wrong ! <br>");
if ($result) {
    echo "id: " . $result->id . "</br>";
    echo "name:" . $result->user . "</br>";
    $_SESSION['admin'] = True;
}