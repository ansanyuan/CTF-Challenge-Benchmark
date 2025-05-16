<?php
if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_FILES['file'])) {
    $file = $_FILES['file'];
    $finfo = finfo_open(FILEINFO_MIME_TYPE);
    $mimeType = finfo_file($finfo, $file['tmp_name']);
    finfo_close($finfo);
    $allowedTypes = ['text/plain', 'application/pdf'];
    if (!in_array($mimeType, $allowedTypes)) {
        die("不允许上传此类型的文件。");
    }
    $uploadDir = 'uploads/';
    $uploadFile = $uploadDir . basename($file['name']);
    if (move_uploaded_file($file['tmp_name'], $uploadFile)) {
        echo "文件上传成功！";
    } else {
        echo "文件上传失败。";
    }
} else {
    echo "没有文件上传。";
}
?>
