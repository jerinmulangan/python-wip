<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Database connection
$servername = "localhost";
$username = "INPUT_TEST";
$password = "inputvalid";
$dbname = "INPUT_VALID_TEST";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Check for POST request
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $name = $_POST["name"] ?? '';
    $email = $_POST["email"] ?? '';

    // Prepare and bind
    $stmt = $conn->prepare("INSERT INTO users (name, email) VALUES (?, ?)");
    if (!$stmt) {
        die("Prepare failed: " . $conn->error);
    }

    $stmt->bind_param("ss", $name, $email);

    // Execute
    if ($stmt->execute()) {
        echo "Data inserted successfully!";
    } else {
        echo "Execution failed: " . $stmt->error;
    }

    $stmt->close();
}

$conn->close();
?>
