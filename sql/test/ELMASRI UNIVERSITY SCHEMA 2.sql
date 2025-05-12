SET autocommit = 0;
SELECT @@autocommit;

drop database if exists university123;
START TRANSACTION;
create database university123;
COMMIT;
show databases;

use university123;

CREATE TABLE PERSON (
    PersonId INT AUTO_INCREMENT PRIMARY KEY,
    Fname VARCHAR(50),
    Minit CHAR(1),
    Lname VARCHAR(50),
    Bdate DATE,
    Gender CHAR(1),
    Street VARCHAR(100),
    Apt_no VARCHAR(10),
    City VARCHAR(50),
    State CHAR(2),
    Zip CHAR(10)
);

# execute Python code to insert rows into person table
select * from person;

CREATE TABLE FACULTY (
    FacultyId INT PRIMARY KEY,
    Title VARCHAR(30) CHECK (Title IN ('Professor', 'Associate Professor', 'Assistant Professor')),
    Foffice VARCHAR(20) NOT NULL,
    Fphone VARCHAR(15) UNIQUE,
    Salary DECIMAL(10,2) CHECK (Salary >= 40000 AND Salary <= 200000),
    FOREIGN KEY (FacultyId) REFERENCES PERSON(PersonId) ON DELETE CASCADE
);

# execute Python code to insert rows into person table
select * from faculty;

CREATE TABLE STUDENT (
    StudentId INT PRIMARY KEY,
    Class INT,
    FOREIGN KEY (StudentId) REFERENCES PERSON(PersonId) ON DELETE CASCADE
);

SELECT StudentId FROM STUDENT WHERE Class = 5;
# execute Python code to insert rows into person table
select * from student where studentid not in (Select facultyid from faculty);
select class, count(*) from student group by class order by class;

CREATE TABLE GRAD_STUDENT (
    Grad_StudentId INT,
	Degree VARCHAR(20) CHECK (Degree IN ('M.Sc.', 'Ph.D.', 'MBA')),
    College VARCHAR(50) NOT NULL,
    Year INT,
	PRIMARY KEY (Grad_StudentId, Degree),
    FOREIGN KEY (Grad_StudentId) REFERENCES STUDENT(StudentId) ON DELETE CASCADE
);

select * from grad_student;

DELIMITER $$

CREATE TRIGGER check_grad_student_insert
BEFORE INSERT ON grad_student
FOR EACH ROW
BEGIN
    DECLARE student_class INT;
    
    -- Retrieve the class of the student from the student table
    SELECT class INTO student_class FROM student WHERE studentid = NEW.grad_studentid;

    -- Check if the student's class is not 5
    IF student_class <> 5 OR student_class IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Only students from class 5 can be inserted into grad_student';
    END IF;
END $$

DELIMITER ;

CREATE TABLE COMMITTEE (
    FacultyId INT,
    Grad_StudentId INT,
    PRIMARY KEY (FacultyId, Grad_StudentId),
    FOREIGN KEY (FacultyId) REFERENCES FACULTY(FacultyId),
    FOREIGN KEY (Grad_StudentId) REFERENCES GRAD_STUDENT(Grad_StudentId)
);

select * from committee;
CREATE TABLE GRANT_INFO (
    GrantID INT PRIMARY KEY AUTO_INCREMENT,
    PI_FacultyId INT,
    Title VARCHAR(100),
    GrantNumber VARCHAR(50) UNIQUE NOT NULL,
    Agency VARCHAR(50),
    StartDate DATE,
    EndDate DATE,
    FOREIGN KEY (PI_FacultyId) REFERENCES FACULTY(FacultyId)
);

select * from grant_info;
CREATE TABLE INSTRUCTOR_RESEARCHER (
    Instruct_ResearchId INT PRIMARY KEY AUTO_INCREMENT,
    FacultyId INT NULL,
    Grad_StudentId INT NULL,
    CategoryType ENUM('Faculty', 'Grad_Student') NOT NULL,
    FOREIGN KEY (FacultyId) REFERENCES FACULTY(FacultyId) ON DELETE CASCADE,
    FOREIGN KEY (Grad_StudentId) REFERENCES GRAD_STUDENT(Grad_StudentId) ON DELETE CASCADE,
    CHECK ((FacultyId IS NOT NULL AND Grad_StudentId IS NULL) OR (FacultyId IS NULL AND Grad_StudentId IS NOT NULL)) 
    -- Ensures that only one of FacultyId or Grad_StudentId is set
);

select * from INSTRUCTOR_RESEARCHER;

CREATE TABLE SUPPORT (
	GrantID INT,
    Instruct_ResearchId INT,
    Start_Date DATE,
    End_Date DATE,
    Start_Time TIME,
    End_Time TIME,
    PRIMARY KEY (GrantID, Instruct_ResearchId),
    FOREIGN KEY (GrantID) REFERENCES GRANT_INFO(GrantID),
    FOREIGN KEY (Instruct_ResearchId) REFERENCES INSTRUCTOR_RESEARCHER(Instruct_ResearchId)
);

CREATE TABLE COLLEGE (
	CollegeId INT PRIMARY KEY AUTO_INCREMENT, 
    CollegeName VARCHAR(100),
    CollegeOffice VARCHAR(50),
    Dean VARCHAR(100)
);

select * from college;
CREATE TABLE DEPARTMENT (
    DeptID INT PRIMARY KEY AUTO_INCREMENT,
    CollegeId INT,
    DeptName VARCHAR(100) UNIQUE,
    DeptPhone VARCHAR(20),
    DeptOffice VARCHAR(50),
    FOREIGN KEY (CollegeId) REFERENCES COLLEGE(CollegeId) ON DELETE CASCADE
);

select * from department;

CREATE TABLE COURSE (
    CourseID INT PRIMARY KEY AUTO_INCREMENT,
    DeptID INT,
    CNum VARCHAR(10),
    CName VARCHAR(100),
    CDesc TEXT,
    FOREIGN KEY (DeptID) REFERENCES DEPARTMENT(DeptID) ON DELETE CASCADE
);

CREATE TABLE SECTION (
    SectionID INT PRIMARY KEY AUTO_INCREMENT,
    CourseID INT,
    Instruct_ResearchId INT,
    SecNumber INT,
    Year INT,
    Qtr VARCHAR(10),
    FOREIGN KEY (Instruct_ResearchId) REFERENCES INSTRUCTOR_RESEARCHER(Instruct_ResearchId) ON DELETE CASCADE,
    FOREIGN KEY (CourseID) REFERENCES COURSE(CourseID) ON DELETE CASCADE
);

select * from SECTION;
CREATE TABLE CURRENT_SECTION (
    SectionID INT PRIMARY KEY,
    CurrentQtr VARCHAR(10),
    CurrentYear INT,
    FOREIGN KEY (SectionID) REFERENCES SECTION(SectionID) ON DELETE CASCADE
);

CREATE TABLE REGISTERED (
    StudentID INT,
    SectionID INT,
    PRIMARY KEY (StudentID, SectionID),
    FOREIGN KEY (StudentID) REFERENCES STUDENT(StudentID) ON DELETE CASCADE,
    FOREIGN KEY (SectionID) REFERENCES SECTION(SectionID) ON DELETE CASCADE
);

select * from registered;

CREATE TABLE TRANSCRIPT (
    StudentID INT,
    SectionID INT,
    Grade CHAR(2),
    PRIMARY KEY (StudentID, SectionID),
    FOREIGN KEY (StudentID) REFERENCES STUDENT(StudentID) ON DELETE CASCADE,
    FOREIGN KEY (SectionID) REFERENCES SECTION(SectionID) ON DELETE CASCADE
);

select * from transcript;

CREATE TABLE MAJORMINOR (
    MajorMinorId INT PRIMARY KEY AUTO_INCREMENT,
    StudentID INT,
    DeptId INT NOT NULL,
    Category ENUM('Major', 'Minor') NOT NULL,  -- Restricts values
    FOREIGN KEY (StudentID) REFERENCES STUDENT(StudentID) ON DELETE CASCADE,
    FOREIGN KEY (DeptId) REFERENCES DEPARTMENT(DeptId) ON DELETE CASCADE
);

select * from majorminor;
CREATE TABLE BELONGS (
    FacultyId INT,
    DeptID INT,
    PRIMARY KEY (FacultyId, DeptID),
    FOREIGN KEY (FacultyId) REFERENCES FACULTY(FacultyId) ON DELETE CASCADE,
    FOREIGN KEY (DeptID) REFERENCES DEPARTMENT(DeptID) ON DELETE CASCADE
);

DROP USER IF EXISTS 'assign1part2'@'localhost';
create user 'assign1part2'@'localhost' identified by 'university123';
grant all on university123.* to 'assign1part2'@'localhost';
flush privileges;
commit;
select * from information_schema.tables where table_schema = 'university123' order by create_time asc;
select distinct table_name, create_time from information_schema.tables where table_schema = 'university123' order by create_time asc;
select * from information_schema.columns where table_schema = 'university123' order by table_name, column_name asc;
select * from information_schema.triggers where trigger_schema = 'university123';
select * from information_schema.TABLE_CONSTRAINTS where table_schema = 'university123' order by table_name asc;




