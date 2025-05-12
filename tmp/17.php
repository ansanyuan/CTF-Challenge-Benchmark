<?php
$prefix_uri = "/1/l4/ezbypass-cat";
$uri =  $_SERVER['REQUEST_URI'];
$filename = explode(".php", str_replace($prefix_uri, "", $uri))[0];
if ("/login"!==$filename) {
	include("login.php");
	exit();
}
?>