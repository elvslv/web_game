<?php 
	foreach($_POST as $key=>$value ) ${$key}=$value;
	foreach($_GET as $key=>$value ) ${$key}=$value;
	include('curl.php');

	$cc = new cURL();
	echo $cc->post($url, $data); 

?>
