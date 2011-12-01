<?php
	foreach($_POST as $key=>$value ) ${$key}=$value;
	foreach($_GET as $key=>$value ) ${$key}=$value;

	function GenPostQuery($path, $serv, $data)
	{
		$result = "POST " . $path . " HTTP/1.1\r\n";
		$result .= "Host: ". $serv . "\r\n";
		$result .= "Connection: Close\r\n";
		$result .= "Referer: " . $serv . "\r\n";
		$result .= "Content-Length: " . strlen($data). "\r\n\r\n";
		$result .= $data;
		return $result;
	}

	$query = GenPostQuery($path, $serv, $data);

	$fp = fsockopen($serv, 80);
	if (!$fp)
		die("Can't open socket.");

	fputs($fp, $query);

	while($gets = fgets($fp))
	{
		echo $gets;
	}

	fclose($fp);
?>
