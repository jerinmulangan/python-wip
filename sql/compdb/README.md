## Prerequisites

- **Java** (JDK 17+ tested; JDK 24 also works)
    
- **MySQL** server (v8-compatible)
    
- **Python 3.8+** with `pymysql` & `faker`
    
- **MySQL Connector/J** (tested with `mysql-connector-j-9.3.0.jar`)
    

---

## 1. Set up the MySQL schema

1. Start your MySQL server.
    
2. From a MySQL client (Workbench / CLI), run the provided `schema.sql` file to create **XYZCOMPANY** and all tables/views/triggers:
    
    sql
    
    CopyEdit
    
    `SOURCE path/to/schema.sql;`
    

---

## 2. Populate the database (Python DML)

1. Create & activate a Python 3 virtual environment:
    
    bash
    
    CopyEdit
    
    `python -m venv venv source venv/bin/activate      # Linux/macOS venv\Scripts\activate.bat     # Windows`
    
2. Install dependencies:
    
    bash
    
    CopyEdit
    
    `pip install pymysql faker`
    
3. Edit the database-connection parameters in `sql_project_initial_dml.py` if needed.
    
4. Run the DML script:
    
    bash
    
    CopyEdit
    
    `python sql_project_initial_dml.py`
    
    This will generate sample data, enforce business-rule triggers, and seed all tables.
    

---

## 3. Build & Run the Java Query Console

1. Place the MySQL Connector/J JAR in `lib/mysql-connector-j-9.3.0.jar`.
    
2. Compile:
    
    bash
    
    CopyEdit
    
    `javac -d bin -cp "lib/mysql-connector-j-9.3.0.jar" src/QueryConsole.java`
    
3. Run:
    
    bash
    
    CopyEdit
    
    `java -cp "bin;lib/mysql-connector-j-9.3.0.jar" QueryConsole`
    
    - On **Linux/macOS**, replace `;` with `:` in the classpath:
        
        bash
        
        CopyEdit
        
        `java -cp "bin:lib/mysql-connector-j-9.3.0.jar" QueryConsole`
        

The Swing UI will launch, presenting a dropdown of “SELECT *” for every table plus your 15 project queries and views. You can also choose “Custom SQL…” to type and execute arbitrary queries.

---

## 4. Troubleshooting

- **Driver not found**: Ensure `com.mysql.cj.jdbc.Driver` is on the classpath (the Connector/J JAR).
    
- **Connection errors**: Check your JDBC URL, username/password, and that the MySQL server is running and listening on port 3306.
    
- **Python errors**: Verify that the MySQL user `xyzcompany` with password `projectcode` has privileges on `XYZCOMPANY`, and that `pymysql` is installed in your virtualenv.


















# SQL-Injection Demo for XYZCOMPANY

This mini-project shows:
1. A **vulnerable** SELECT form (`select.php`)
2. A **safe** SELECT form using prepared statements (`safe_select.php`)
3. A **vulnerable** UPDATE form (`update.php`) and its safe counterpart (`safe_update.php`)

---

##  Prerequisites

1. **MySQL Server**  
   - Database: `XYZCOMPANY`  
   - User: `xyzcompany` / Password: `projectcode`  
   - Make sure you’ve loaded and populated the schema with `sql_project_initial_dml.py` (or via Workbench) before running the PHP demo.

2. **PHP 8.4+** (Windows installer from [php.net](https://windows.php.net/download/))  
   - During install, select **Thread-Safe** build for CLI and enable the **mysqli** and **pdo_mysql** extensions in your `php.ini`:
	ini
    extension=mysqli
    extension=pdo_mysql
     ```
   - Make sure `C:\php` (or wherever you installed) is on your **PATH**, or always call `C:\php\php.exe`.

---

## Directory Layout

3p2/
├── index.html ← form UI (points to select.php & update.php)
├── select.php ← vulnerable SELECT demo
├── safe_select.php ← prepared-stmt SELECT
├── update.php ← vulnerable UPDATE demo
├── safe_update.php ← prepared-stmt UPDATE
└── README.md ← this file


---

## Running Locally

1. **Start your MySQL server** and confirm you can connect with:
bash
mysql -u xyzcompany -pXYZCOMPANY
Fire up PHP’s built-in webserver in the 3p2/ directory:

cd C:\sql\3p2
php -S localhost:8000
If php isn’t recognized, use the full path:

& "C:\php\php.exe" -S localhost:8000
Browse to:
http://localhost:8000/index.html

Try the forms:

Vulnerable SELECT

Enter e.g. 1234' OR '1'='1 in the Personal ID field to see all rows.

Safe SELECT

Enter a real PERSONAL_ID + first name (e.g. 11111 + Hellen) to retrieve exactly that row.

Vulnerable UPDATE / Safe UPDATE similarly demonstrate injection vs. parameterization.

Preventing SQL Injection
Vulnerable versions directly interpolate `$_GET` into `"$sql = '…$pid…'"`.

Safe versions use mysqli->prepare() and bind parameters:

$stmt = $conn->prepare(
  "SELECT PERSONAL_ID, FIRST_NAME, LAST_NAME, EMAIL
     FROM PERSON
    WHERE PERSONAL_ID = ?
      AND FIRST_NAME  = ?"
);
$stmt->bind_param("is", $pid, $first);
$stmt->execute();

Troubleshooting
Class "mysqli" not found
Make sure extension=mysqli is enabled in your php.ini, then restart any running PHP servers.

Permission errors
Ensure your MySQL user has SELECT/UPDATE rights on XYZCOMPANY.

Port conflicts
If port 8000 is in use, choose another:

php -S localhost:9000
