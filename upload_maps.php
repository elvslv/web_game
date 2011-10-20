<?php
	$arr = array("thmb", "pict");
	for($i = 0; $i < sizeof($arr); ++$i)
	{
		$inputName = $arr[$i];
		if ($_FILES[$arr[$i]]["type"] != "image/jpeg")
		{
			$result = array('result' => 'error', 'msg' => 'Invalid file type');
			echo json_encode($result);
		}
		else if ($_FILES[$arr[$i]]["size"] > 5 * 1024 * 1024)
		{
			$result = array('result' => 'error', 'msg' => 'Too large file');
			echo json_encode($result);
		}
		else
		{
			if ($_FILES[$arr[$i]]["error"] > 0)
			{
				$result = array('result' => 'error', 'msg' => $_FILES[$arr[$i]]["error"]);
				echo json_encode($result);
			}
			else
			{
				if (file_exists("C:\wamp\www\smallworlds\maps\\" . basename($_FILES[$arr[$i]]["tmp_name"])))
				{
					$result = array('result' => 'error', 'msg' => basename($_FILES[$arr[$i]]["tmp_name"]) . " already exists. ");
					echo json_encode($result);
				}
				else
				{
					move_uploaded_file($_FILES[$arr[$i]]["tmp_name"],
					"C:\wamp\www\smallworlds\maps\\" . basename($_FILES[$arr[$i]]["tmp_name"]));
					$result = array('result' => 'ok', 'filename' => basename($_FILES[$arr[$i]]["tmp_name"]));
					echo json_encode($result);
				}
			}
		}
	}
	
?> 