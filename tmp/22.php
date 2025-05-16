<?php 
if(isset($_POST['usr']) && isset($_POST['pw'])){ 
        $user = $_POST['usr']; 
        $pass = $_POST['pw']; 

        $db = new SQLite3('../fancy.db'); 
         
        $res = $db->query("SELECT id,name from Users where name='".$user."' and password='".sha1($pass."Salz!")."'"); 
    if($res){ 
        $row = $res->fetchArray(); 
    } 
    else{ 
        echo "<br>Some Error occourred!"; 
    } 

    if(isset($row['id'])){ 
            setcookie('name',' '.$row['name'], time() + 60, '/'); 
            header("Location: /"); 
            die(); 
    } 

} 

if(isset($_GET['debug'])) 
highlight_file('login.php'); 
?> 