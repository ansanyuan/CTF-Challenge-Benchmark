<?php
    $allowtype = array("txt","jpeg","bmv","doc","docx","gif","png","jpg");
    $size = 10000000;
    $path = "./upload/";
    $filename = $_FILES['file']['name'];
    if (is_uploaded_file($_FILES['file']['tmp_name'])){
        if (!move_uploaded_file($_FILES['file']['tmp_name'],$path.$filename)){
            exit();
        } 
    } else {
        exit();
    }
    $newfile = $path.$filename;
    if ($_FILES['file']['error'] > 0){
        unlink($newfile);
        exit();
    } 
    $ext = array_pop(explode(".",$_FILES['file']['name']));
    if (!in_array($ext,$allowtype)){
        unlink($newfile);
        exit();
    }