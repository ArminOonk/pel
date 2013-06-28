<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Connected Host</title>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<link rel="stylesheet" type="text/css" href="layout.css" />
</head>
<body>
<?php
include_once('connect.php');

$result = $mysqli->query("select * from ConnectedHosts;");

if($result->num_rows > 0)
{
	echo "<table id=\"demo\">\n";
	echo "<tr class=\"header\"><td class=\"header\">Name</td><td class=\"header\">Device</td><td class=\"header\">MAC</td><td class=\"header\">Last Seen</td><td class=\"header\">Last Left</td><td class=\"header\">Status</td></tr>\n";
	
	while($row = mysqli_fetch_array($result, MYSQLI_ASSOC))
	{
		$humanReadable[$row["MAC"]] = array($row["Name"], $row["Device"]);
		echo "<tr><td>".$row["Name"]."</td><td>".$row["Device"]."</td><td>".$row["MAC"]."</td><td>".$row["LastSeen"]."</td><td>".$row["LastLeft"]."</td><td>".$row["Status"]."</td></tr>\n";
	}
	echo "</table>\n";
}

echo "<p><img src=connectedHostImg.php/></p>";
?>
</body>
</html>