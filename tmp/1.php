<?
$dir = $_GET["dir"];
if (isset($dir)) {
    if (preg_match("/echo/", $dir)) {
        die("nope");
    }
    system("ls -al" . $dir);
}
?>