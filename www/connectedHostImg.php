<?php
// Get database variables
include_once('connect.php');
$maxNameLength = 0;

function getHumanName($db) {
	$sql = "select * from ConnectedHosts;";
	$stmt = $db->prepare($sql);
	$stmt->execute();
	$rows = $stmt->fetchAll(PDO::FETCH_ASSOC);

	foreach($rows as $row) {
		$txt = $row["Name"] ." ".$row["Device"];
		$lengthTxt = strlen($txt);
		$humanName[$row["MAC"]] = $txt;
		if($lengthTxt > $maxNameLength) {
			$maxNameLength = $lengthTxt; 
		}
	}
	return $humanName;
}

$humanName = getHumanName($db);

$sql = "SELECT * FROM `ConnectedHostsTimeSeries` WHERE `Time` > DATE_SUB( NOW( ) , INTERVAL 1 DAY );";
$stmt = $db->prepare($sql);
$stmt->execute();
$rows = $stmt->fetchAll(PDO::FETCH_ASSOC);

$i=0;

foreach($rows as $row) {
	$json = json_decode($row["Data"], true);
	foreach ($json["Addresses"] as $value){
		if($value["mac"] != "") {
			$overview[$value["mac"]][$i] = "*";
		}
	}
	$timestamp[$i] = $json["TimeStamp"];
	$i++;
}

// Set the font
$fontSize = 5;
//Calculate the size of the font
$fontWidth = imagefontwidth($fontSize);
$fontHeight = imagefontheight($fontSize);

// imageWidthis 17*fontwidht (mac address) + number of database results
$maxMacLength = 17;
if($maxNameLength > $maxMacLength) {
	$textWidth = $maxNameLength*$fontWidth;
} else {
	$textWidth = $maxMacLength*$fontWidth;
}

// lineWidth: width of the line in the image in px
// imageHeight: number of results + 1 row for x axis labels
$lineWidth = 2;
$imageWidth = $textWidth+$lineWidth*$stmt->rowCount();
$plotHeight = count($overview)*$fontHeight;
$imageHeight = (count($overview)+1)*$fontHeight;

// Calculate the image size
$canvas = imagecreatetruecolor($imageWidth, $imageHeight);

$green = imagecolorallocate($canvas, 0, 255, 0);
$red = imagecolorallocate($canvas, 255, 0, 0);
$white = imagecolorallocate($canvas, 255, 255, 255);
$black = imagecolorallocate($canvas, 0, 0, 0);
//Set background color
imagefill($canvas, 0, 0, $white);

$textY = 0;

foreach ($overview as $key => $value) {
	$string = $key;

	if(isset($humanName[$key])) {
		$string = $humanName[$key];
	}
		
	imagestring($canvas, $fontSize, 0, $textY, $string, $black);
	
	for($i=0; $i <$stmt->rowCount(); $i++) {
		$color = $red;
		if($value[$i] == "*") {
			$color = $green;
		}
		
		$x = $textWidth+$lineWidth*$i;
		imagefilledrectangle ($canvas, $x, $textY, $x+$lineWidth, $textY+$fontHeight, $color);	
	}
	imageline($canvas, $textWidth,  $textY, $imageWidth, $textY, $white);
	$textY += $fontHeight;
}

// First one does not need to be marked
$prevHour = date("H", $timestamp[0]);
// Mark every hour in the plot

for($i=0; $i <$stmt->rowCount(); $i++) {
	$x = $textWidth+$lineWidth*$i;
	$currentHour = date("H", $timestamp[$i]);
	if($prevHour != $currentHour) {
		imageline($canvas, $x,  0, $x, $plotHeight, $black);
		imagestring($canvas, $fontSize, $x, $plotHeight, $currentHour, $black);
		$prevHour = $currentHour;
	}
}	
// Output and free from memory
header('Content-Type: image/png');

imagepng($canvas);
imagedestroy($canvas);
?>