<?php
// prepared_select.php
$conn = new mysqli('localhost','xyzcompany','projectcode','XYZCOMPANY');
if($conn->connect_errno) die($conn->connect_error);

$stmt = $conn->prepare(
  "SELECT PERSONAL_ID, FIRST_NAME, LAST_NAME, EMAIL
     FROM PERSON
    WHERE PERSONAL_ID = ?
      AND FIRST_NAME  = ?"
);

$pid   = $_GET['pid']   ?? '';
$first = $_GET['first'] ?? '';

$stmt->bind_param('is', $pid, $first);
$stmt->execute();
$res = $stmt->get_result();

echo "<p><strong>Safe prepared:</strong></p>";
echo "<table border=1>";
while($row = $res->fetch_assoc()) {
  echo "<tr>";
  foreach($row as $c) echo "<td>".htmlspecialchars($c)."</td>";
  echo "</tr>";
}
echo "</table>";

$stmt->close();
$conn->close();
