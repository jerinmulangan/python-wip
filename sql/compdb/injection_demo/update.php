<?php
// update.php
$conn = new mysqli('localhost','xyzcompany','projectcode','XYZCOMPANY');
if($conn->connect_errno) die($conn->connect_error);

$pid  = $_POST['pid']  ?? '';
$city = $_POST['city'] ?? '';

$sql = "UPDATE PERSON
        SET CITY = '$city'
        WHERE PERSONAL_ID = '$pid'";

echo "<p><strong>Running:</strong> $sql</p>";
if($conn->query($sql)) {
  echo "<p>Rows affected: {$conn->affected_rows}</p>";
}
$conn->close();
