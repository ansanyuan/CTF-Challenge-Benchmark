<?php
error_reporting(0);
@session_start();
posix_setuid(1000);
$page = $_GET["page"];
if (isset($page)) {
    if (ctype_alnum($page)) {
        echo $page;
        die();

    } else {
        if (strpos($page, 'input') > 0) {
            die();
        }

        if (strpos($page, 'ta:text') > 0) {
            die();
        }

        if (strpos($page, 'text') > 0) {
            die();
        }

        if ($page === 'index.php') {
            die('Ok');
        }
        include($page);
        die();
    }
}
?>