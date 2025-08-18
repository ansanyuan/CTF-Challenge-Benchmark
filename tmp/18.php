<?php
 class SQL {
    public $table = '';
    public $username = '';
    public $password = '';
    public $conn;
    public function connect() {
        $this->conn = new mysqli("localhost", "xxxxx", "xxxx", "xxxx");
    }
    public function check_login(){
        $result = $this->query();
        if ($result === false) {
            die("database error, please check your input");
        }
        $row = $result->fetch_assoc();
        if($row === NULL){
            die("username or password incorrect!");
        }else if($row['username'] === 'admin'){
            $flag = file_get_contents('flag.php');
            echo "welcome, admin! this is your flag -> ".$flag;
        }else{
            echo "welcome! but you are not admin";
        }
        $result->free();
    }
    public function query() {
        $this->waf();
        return $this->conn->query ("select username,password from ".$this->table." where username='".$this->username."' and password='".$this->password."'");
    }
    public function waf(){
    	$blacklist = ["union", "join", "!", "\"", "#", "$", "%", "&", ".", "/", ":", ";", "^", "_", "`", "{", "|", "}", "<", ">", "?", "@", "[", "\\", "]" , "*", "+", "-"];
    	foreach ($blacklist as $value) {
    		if(strripos($this->table, $value)){
    			die('bad hacker,go out!');
    		}
    	}
        foreach ($blacklist as $value) {
            if(strripos($this->username, $value)){
                die('bad hacker,go out!');
            }
        }
        foreach ($blacklist as $value) {
            if(strripos($this->password, $value)){
                die('bad hacker,go out!');
            }
        }
    }
    public function __wakeup(){
        if (!isset ($this->conn)) {
            $this->connect ();
        }
        if($this->table){
            $this->waf();
        }
        $this->check_login();
        $this->conn->close();
    }
}
if (isset($_COOKIE['last_login_info'])) {
    $last_login_info = unserialize(base64_decode($_COOKIE['last_login_info']));
}