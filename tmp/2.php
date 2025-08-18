<?
$dir = $_GET["dir"];
if(isset($dir))
{
system("ls -al".$dir);
}
 
?>