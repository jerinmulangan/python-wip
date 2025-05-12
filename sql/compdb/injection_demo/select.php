<?php
// select.php
$conn = new mysqli('localhost','xyzcompany','projectcode','XYZCOMPANY');
if($conn->connect_errno) die($conn->connect_error);

$pid   = $_GET['pid']   ?? '';
$first = $_GET['first'] ?? '';

$sql = "SELECT PERSONAL_ID, FIRST_NAME, LAST_NAME, EMAIL
        FROM PERSON
        WHERE PERSONAL_ID = '$pid'
          AND FIRST_NAME  = '$first'";

echo "<p><strong>Running:</strong> $sql</p>";

if($res = $conn->query($sql)) {
  echo "<table border=1>";
  while($row = $res->fetch_assoc()) {
    echo "<tr>";
    foreach($row as $c) echo "<td>".htmlspecialchars($c)."</td>";
    echo "</tr>";
  }
  echo "</table>";
}
$conn->close();
