SET AUTOCOMMIT = 0;
SELECT @@AUTOCOMMIT;

START TRANSACTION;
DROP DATABASE IF EXISTS UNIVERSITY;
CREATE DATABASE UNIVERSITY;
COMMIT;
SHOW DATABASES;

USE UNIVERSITY;

CREATE TABLE PERSON (
    PERSONID INT AUTO_INCREMENT PRIMARY KEY,
    FNAME VARCHAR(50),
    MINIT CHAR(1),
    LNAME VARCHAR(50),
    BDATE DATE,
    GENDER CHAR(1),
    STREET VARCHAR(100),
    APT_NO VARCHAR(10),
    CITY VARCHAR(50),
    STATE CHAR(2),
    ZIP CHAR(10)
);

SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'UNIVERSITY';


SELECT * FROM PERSON;

CREATE TABLE FACULTY (
    FACULTYID INT PRIMARY KEY,
    TITLE VARCHAR(30) CHECK (TITLE IN ('PROFESSOR', 'ASSOCIATE PROFESSOR', 'ASSISTANT PROFESSOR')),
    FOFFICE VARCHAR(20) NOT NULL,
    FPHONE VARCHAR(30) UNIQUE,
    SALARY DECIMAL(10,2) CHECK (SALARY >= 40000 AND SALARY <= 200000),
    FOREIGN KEY (FACULTYID) REFERENCES PERSON(PERSONID) ON DELETE CASCADE
);

SELECT * FROM FACULTY;

CREATE TABLE STUDENT (
    STUDENTID INT PRIMARY KEY,
    CLASS INT,
    FOREIGN KEY (STUDENTID) REFERENCES PERSON(PERSONID) ON DELETE CASCADE
);

SELECT * FROM STUDENT;

CREATE TABLE GRAD_STUDENT (
    GRAD_STUDENTID INT,
	DEGREE VARCHAR(20) CHECK (DEGREE IN ('M.SC.', 'PH.D.', 'MBA')),
    COLLEGE VARCHAR(50) NOT NULL,
    YEAR INT,
	PRIMARY KEY (GRAD_STUDENTID, DEGREE),
    FOREIGN KEY (GRAD_STUDENTID) REFERENCES STUDENT(STUDENTID) ON DELETE CASCADE
);

SELECT * FROM GRAD_STUDENT;

DELIMITER $$

CREATE TRIGGER CHECK_GRAD_STUDENT_INSERT
BEFORE INSERT ON GRAD_STUDENT
FOR EACH ROW
BEGIN
    DECLARE STUDENT_CLASS INT;
    SELECT CLASS INTO STUDENT_CLASS FROM STUDENT WHERE STUDENTID = NEW.GRAD_STUDENTID;
    IF STUDENT_CLASS <> 5 OR STUDENT_CLASS IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'ONLY STUDENTS FROM CLASS 5 CAN BE INSERTED INTO GRAD_STUDENT';
    END IF;
END $$

DELIMITER ;

ALTER TABLE GRAD_STUDENT ADD UNIQUE KEY GRAD_STUDENT(GRAD_STUDENTID);

CREATE TABLE COMMITTEE (
    FACULTYID INT,
    GRAD_STUDENTID INT,
    PRIMARY KEY (FACULTYID, GRAD_STUDENTID),
    FOREIGN KEY (FACULTYID) REFERENCES FACULTY(FACULTYID),
    FOREIGN KEY (GRAD_STUDENTID) REFERENCES GRAD_STUDENT(GRAD_STUDENTID)
);

CREATE TABLE GRANT_INFO (
    GRANTID INT PRIMARY KEY AUTO_INCREMENT,
    PI_FACULTYID INT,
    TITLE VARCHAR(100),
    GRANTNUMBER VARCHAR(50) UNIQUE NOT NULL,
    AGENCY VARCHAR(50),
    STARTDATE DATE,
    ENDDATE DATE,
    FOREIGN KEY (PI_FACULTYID) REFERENCES FACULTY(FACULTYID)
);

CREATE TABLE INSTRUCTOR_RESEARCHER (
    INSTRUCT_RESEARCHID INT PRIMARY KEY,
    CATEGORYTYPE ENUM('FACULTY', 'GRAD_STUDENT') NOT NULL,
    FACULTYID INT,
    GRAD_STUDENTID INT,
    FOREIGN KEY (FACULTYID) REFERENCES FACULTY(FACULTYID) ON DELETE CASCADE,
    FOREIGN KEY (GRAD_STUDENTID) REFERENCES GRAD_STUDENT(GRAD_STUDENTID) ON DELETE CASCADE,
    CHECK (
        (CATEGORYTYPE = 'FACULTY' AND FACULTYID IS NOT NULL AND GRAD_STUDENTID IS NULL) OR
        (CATEGORYTYPE = 'GRAD_STUDENT' AND GRAD_STUDENTID IS NOT NULL AND FACULTYID IS NULL)
    )
);

CREATE TABLE SUPPORT (
	GRANTID INT,
    INSTRUCT_RESEARCHID INT,
    START_DATE DATE,
    END_DATE DATE,
    START_TIME TIME,
    END_TIME TIME,
    PRIMARY KEY (GRANTID, INSTRUCT_RESEARCHID),
    FOREIGN KEY (GRANTID) REFERENCES GRANT_INFO(GRANTID),
    FOREIGN KEY (INSTRUCT_RESEARCHID) REFERENCES INSTRUCTOR_RESEARCHER(INSTRUCT_RESEARCHID)
);

CREATE TABLE COLLEGE (
	COLLEGEID INT PRIMARY KEY AUTO_INCREMENT, 
    COLLEGENAME VARCHAR(100),
    COLLEGEOFFICE VARCHAR(50),
    DEAN VARCHAR(100)
);

CREATE TABLE DEPARTMENT (
    DEPTID INT PRIMARY KEY AUTO_INCREMENT,
    COLLEGEID INT,
    DEPTNAME VARCHAR(100) UNIQUE,
    DEPTPHONE VARCHAR(30),
    DEPTOFFICE VARCHAR(50),
    FOREIGN KEY (COLLEGEID) REFERENCES COLLEGE(COLLEGEID) ON DELETE CASCADE
);

CREATE TABLE COURSE (
    COURSEID INT PRIMARY KEY,
    DEPTID INT,
    CNUM VARCHAR(10),
    CNAME VARCHAR(100),
    CDESC TEXT,
    FOREIGN KEY (DEPTID) REFERENCES DEPARTMENT(DEPTID) ON DELETE CASCADE
);

CREATE TABLE SECTION (
    SECTIONID INT PRIMARY KEY AUTO_INCREMENT,
    COURSEID INT,
    INSTRUCT_RESEARCHID INT,
    SECNUMBER INT,
    YEAR INT,
    QTR VARCHAR(10),
    FOREIGN KEY (INSTRUCT_RESEARCHID) REFERENCES INSTRUCTOR_RESEARCHER(INSTRUCT_RESEARCHID) ON DELETE CASCADE,
    FOREIGN KEY (COURSEID) REFERENCES COURSE(COURSEID) ON DELETE CASCADE
);

CREATE TABLE CURRENT_SECTION (
    SECTIONID INT PRIMARY KEY,
    CURRENTQTR VARCHAR(10),
    CURRENTYEAR INT,
    FOREIGN KEY (SECTIONID) REFERENCES SECTION(SECTIONID) ON DELETE CASCADE
);

CREATE TABLE REGISTERED (
    STUDENTID INT,
    SECTIONID INT,
    PRIMARY KEY (STUDENTID, SECTIONID),
    FOREIGN KEY (STUDENTID) REFERENCES STUDENT(STUDENTID) ON DELETE CASCADE,
    FOREIGN KEY (SECTIONID) REFERENCES SECTION(SECTIONID) ON DELETE CASCADE
);

CREATE TABLE TRANSCRIPT (
    STUDENTID INT,
    SECTIONID INT,
    GRADE CHAR(2),
    PRIMARY KEY (STUDENTID, SECTIONID),
    FOREIGN KEY (STUDENTID) REFERENCES STUDENT(STUDENTID) ON DELETE CASCADE,
    FOREIGN KEY (SECTIONID) REFERENCES SECTION(SECTIONID) ON DELETE CASCADE
);

CREATE TABLE MAJORMINOR (
    MAJORMINORID INT PRIMARY KEY AUTO_INCREMENT,
    STUDENTID INT,
    DEPTID INT NOT NULL,
    CATEGORY ENUM('MAJOR', 'MINOR') NOT NULL,  -- RESTRICTS VALUES
    FOREIGN KEY (STUDENTID) REFERENCES STUDENT(STUDENTID) ON DELETE CASCADE,
    FOREIGN KEY (DEPTID) REFERENCES DEPARTMENT(DEPTID) ON DELETE CASCADE
);

CREATE TABLE BELONGS (
    FACULTYID INT,
    DEPTID INT,
    PRIMARY KEY (FACULTYID, DEPTID),
    FOREIGN KEY (FACULTYID) REFERENCES FACULTY(FACULTYID) ON DELETE CASCADE,
    FOREIGN KEY (DEPTID) REFERENCES DEPARTMENT(DEPTID) ON DELETE CASCADE
);

-- INSERT INTO PERSON Table
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Katelyn', 'K', 'Williams', '1969-04-14', 'M', '78712 Allison Row Suite 819', '494', 'East Nicholas', 'CT', '72312');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Nichole', 'G', 'Anderson', '1986-05-19', 'F', '766 Kelsey Shores', '370', 'Donnaville', 'AZ', '52067');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Travis', 'G', 'Delacruz', '1996-10-12', 'F', '965 Obrien Wall Suite 718', '142', 'Monroefurt', 'MA', '80535');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Matthew', 'D', 'Peterson', '1985-08-26', 'M', '508 Morgan Meadow Apt. 042', '382', 'New Dianachester', 'CT', '73599');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Emily', 'X', 'Massey', '2001-02-18', 'M', '7539 Cynthia Mews Apt. 328', '265', 'Port Jessica', 'TN', '83110');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Linda', 'I', 'Lawson', '1997-08-24', 'F', '711 Ryan Wells Suite 792', '468', 'Weissport', 'AL', '16824');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Isabella', 'N', 'Owens', '1962-02-19', 'M', '1375 Lauren Views Suite 656', '445', 'East Arielside', 'RI', '46520');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Adrian', 'X', 'Delacruz', '1990-05-24', 'M', '9872 Jeffrey Lake Suite 226', '688', 'Phillipshaven', 'AR', '79692');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Michelle', 'L', 'Wright', '1956-01-06', 'M', '50072 Jordan Meadow', '572', 'East Amanda', 'MH', '54001');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Sharon', 'O', 'Taylor', '1987-02-10', 'M', '344 Stephenson Groves Apt. 068', '175', 'Jamesmouth', 'CT', '38552');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Casey', 'L', 'Stephens', '1964-04-11', 'M', '771 Arthur Mews', '792', 'Perezfurt', 'MS', '04795');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Wendy', 'H', 'Villanueva', '1996-02-29', 'F', '19807 Tina Mews', '904', 'North Anthony', 'VT', '86968');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Christopher', 'Z', 'Franklin', '1999-06-22', 'F', '19226 Barker Villages', '651', 'Lake Justinbury', 'OR', '14275');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Brooke', 'O', 'Bradshaw', '1999-01-06', 'F', '4571 Mcconnell Crossroad Apt. 787', '441', 'North Yvetteville', 'IL', '30456');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Samantha', 'V', 'Fletcher', '1959-10-21', 'M', '8364 Jennifer Fort', '338', 'Port Tiffany', 'CO', '50499');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Penny', 'G', 'Richardson', '1995-03-01', 'M', '4132 Kramer Dale', '222', 'Velezview', 'MS', '30738');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Stephanie', 'U', 'Nelson', '1992-12-06', 'F', '76550 Gonzalez Circles', '804', 'Russoview', 'IN', '88401');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('William', 'T', 'Carney', '1976-08-08', 'M', '610 Michael Glen Suite 635', '420', 'Reevesberg', 'MO', '08836');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Joshua', 'B', 'Walter', '1981-04-05', 'M', '02201 David Burg', '191', 'Rogerstown', 'LA', '70641');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Robert', 'Y', 'Burgess', '1974-11-03', 'M', '781 Nelson Center', '627', 'Lake Ariel', 'AL', '36405');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Kyle', 'B', 'Johnson', '1977-09-14', 'M', '83676 Mendez Mountain Suite 328', '902', 'North Theodoreland', 'CO', '36569');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Cynthia', 'V', 'Wright', '1995-07-22', 'M', '58627 Tony Dam Apt. 426', '253', 'Bakerbury', 'WV', '35976');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Regina', 'U', 'Welch', '1971-01-18', 'F', '47436 Stephanie Ville Suite 844', '971', 'East Richard', 'TX', '97339');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Mason', 'J', 'Adams', '1964-09-25', 'F', '41096 Samantha Well', '340', 'North Adrianafurt', 'MD', '20665');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Jeffery', 'L', 'Williams', '1990-10-25', 'M', '87523 Jeremiah Stream Apt. 037', '724', 'East Robert', 'CA', '51365');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Michelle', 'Y', 'Small', '2005-08-02', 'F', '393 April Valleys Suite 366', '369', 'Stewarttown', 'IL', '58485');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Natalie', 'S', 'Barber', '1977-10-10', 'F', '878 Lynch Isle Apt. 173', '834', 'North Elizabethside', 'NM', '73948');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Nicole', 'L', 'Dorsey', '1997-07-16', 'F', '3631 Kimberly Corners', '297', 'New Charlenechester', 'ME', '83190');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Wyatt', 'A', 'Carter', '2006-03-16', 'F', '98789 Jessica Valleys Apt. 604', '957', 'New Jennaland', 'SD', '31693');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Kathryn', 'B', 'Sampson', '1973-07-26', 'M', '2116 Sierra Dale Suite 707', '119', 'South Vanessaberg', 'NV', '21202');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Thomas', 'N', 'Gray', '1999-11-17', 'M', '47087 Marquez Island Suite 737', '191', 'Cruzton', 'FL', '96044');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Christina', 'U', 'Mcdaniel', '1989-05-13', 'M', '06865 Wilson Divide Apt. 747', '381', 'Port Matthew', 'AZ', '65378');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Douglas', 'V', 'Myers', '1987-03-21', 'M', '7621 Courtney Parkways', '199', 'Armstrongburgh', 'CT', '19333');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Teresa', 'G', 'Morales', '1977-06-19', 'M', '155 Richardson Lane', '825', 'South Jeffrey', 'HI', '17049');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Stephanie', 'N', 'Poole', '1978-09-02', 'M', '978 David Extension Suite 895', '174', 'Port James', 'IN', '38285');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Heather', 'N', 'Montoya', '1980-03-07', 'M', '8960 Moody Alley', '347', 'Caseyhaven', 'VA', '08571');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Brenda', 'S', 'Johnson', '1985-05-31', 'F', '623 Robert Manor', '441', 'Cassieberg', 'PW', '75829');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Erica', 'R', 'Orr', '1998-01-23', 'F', '66558 Jennifer Falls Suite 810', '373', 'Bryanport', 'AR', '37023');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Donald', 'S', 'Shaw', '1968-02-15', 'M', '548 Theresa Locks', '773', 'Chaneyview', 'DE', '30495');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Eric', 'I', 'White', '1963-10-30', 'F', '89991 Matthews Bridge', '628', 'Port Suzanne', 'ND', '80192');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Sara', 'T', 'Becker', '1999-01-09', 'F', '473 Kimberly Mission Suite 181', '681', 'Marcusland', 'CO', '31468');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('David', 'A', 'Hutchinson', '1993-01-01', 'M', '6682 Gary Walks', '191', 'Carolineland', 'VA', '87003');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Lauren', 'T', 'Blake', '1955-05-26', 'F', '5688 Martinez Skyway', '260', 'Stephanieville', 'MN', '70727');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Amy', 'N', 'Avila', '1981-08-17', 'F', '18840 Cheryl Plaza Apt. 069', '175', 'Rodriguezview', 'PR', '11421');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Ralph', 'E', 'Stephens', '1984-11-22', 'M', '77432 Gibbs Fords Apt. 793', '983', 'Pattersonborough', 'MH', '29147');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Bill', 'D', 'Miller', '1979-07-17', 'F', '4785 Anderson Unions Suite 335', '228', 'South Carloston', 'MP', '96029');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Julia', 'L', 'Carr', '2005-12-06', 'F', '749 Young Curve', '874', 'Moralesland', 'IN', '55108');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('David', 'P', 'Pope', '1986-11-07', 'M', '36263 Garrett Coves Apt. 127', '280', 'Harristown', 'DC', '28021');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Diamond', 'R', 'Miller', '2002-05-08', 'F', '997 Jacqueline Terrace', '570', 'Port Thomasshire', 'VI', '37224');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Rachael', 'K', 'Arias', '2005-10-13', 'M', '8281 Alexis Prairie', '135', 'North Edwardland', 'KY', '54276');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Krista', 'L', 'Alexander', '1979-06-07', 'F', '2815 Shirley Mall', '917', 'Lake Samantha', 'DC', '60773');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Justin', 'H', 'Turner', '1959-06-11', 'F', '0324 Matthew Course', '428', 'South Mariamouth', 'SC', '21303');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Robin', 'D', 'Pace', '1974-12-09', 'M', '02072 Dean Corner Suite 251', '867', 'West Russellberg', 'DC', '46039');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Michelle', 'C', 'Thomas', '1972-05-22', 'F', '95550 Rachel Rapids Apt. 955', '246', 'Johnsonton', 'CT', '86149');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Teresa', 'F', 'Farmer', '1962-10-18', 'M', '157 Jennifer Trail', '616', 'Davisstad', 'CT', '93233');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Donald', 'I', 'Cruz', '1995-12-03', 'F', '91935 Delgado Ridge', '828', 'Christopherstad', 'KY', '25077');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Robert', 'P', 'Sharp', '1982-10-26', 'F', '78971 Hall Neck Apt. 970', '575', 'West Danielberg', 'IA', '69594');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('John', 'J', 'Rodriguez', '1998-10-12', 'M', '61902 Julie Ports', '357', 'Karenberg', 'WV', '09702');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Gina', 'S', 'Webb', '1972-08-07', 'M', '20611 Davis Expressway', '160', 'West Sherry', 'IA', '21316');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Heather', 'D', 'Hays', '1983-05-10', 'M', '464 James Street Suite 067', '364', 'Ochoaton', 'ND', '11766');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Edward', 'Z', 'Gonzalez', '1976-03-30', 'M', '40979 Green Road Suite 283', '769', 'Lake Davidland', 'CA', '13177');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Shannon', 'Y', 'Rodriguez', '2000-03-07', 'F', '8441 Smith Locks', '779', 'Kellybury', 'VA', '10892');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Emma', 'I', 'Ramirez', '1994-08-27', 'M', '4476 Carla Tunnel', '115', 'Lynchmouth', 'AR', '20739');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Megan', 'C', 'Stanton', '1994-10-12', 'M', '959 Carrillo Park', '402', 'East Jeremy', 'OH', '35574');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Ruben', 'M', 'Smith', '1989-05-31', 'F', '28266 Mason Field', '806', 'South Adam', 'TN', '72484');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Fred', 'A', 'Harrison', '1964-07-05', 'M', '059 Chase Terrace Apt. 505', '735', 'Pollardport', 'DE', '41496');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Joshua', 'I', 'Peterson', '1955-07-28', 'M', '080 Karen Glens', '381', 'Lake Kathyfort', 'SC', '04138');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('James', 'E', 'Riddle', '1980-11-08', 'F', '77830 Paul Falls Suite 221', '946', 'Scottville', 'IL', '70743');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Brian', 'H', 'Martinez', '1975-10-19', 'F', '6584 Gonzalez Walk Apt. 212', '260', 'Nunezville', 'IN', '83199');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Samantha', 'Q', 'Duncan', '2000-04-23', 'M', '8494 Sara Inlet Apt. 392', '922', 'West Amanda', 'TN', '27666');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Jennifer', 'O', 'Vega', '1985-05-02', 'F', '9401 John Centers', '530', 'Thompsonton', 'NE', '01694');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Jessica', 'N', 'Powers', '1992-06-14', 'F', '3875 Andrew Manors Suite 151', '697', 'North Richardberg', 'FM', '79387');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Jason', 'Z', 'Contreras', '1960-01-04', 'M', '9985 Leslie Corner', '496', 'Mariaside', 'OH', '08189');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Joyce', 'L', 'Thompson', '1977-06-14', 'M', '2721 Corey Canyon Suite 115', '992', 'Heatherborough', 'KY', '76519');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Justin', 'B', 'Bell', '1976-05-29', 'F', '07991 Harris Plains', '948', 'South Pamela', 'PW', '59161');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Shelly', 'H', 'Wells', '1987-03-23', 'M', '574 Brandon Hills Apt. 939', '589', 'Lake Eileenport', 'NM', '67835');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Christopher', 'J', 'Lewis', '1986-09-17', 'F', '308 Skinner Gardens', '344', 'Butlerburgh', 'AK', '55467');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Stacy', 'J', 'Ingram', '1982-06-20', 'M', '83037 Madeline Unions Suite 522', '403', 'West Wyatt', 'DE', '14211');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Angela', 'L', 'Carter', '1991-11-13', 'F', '58475 Smith Cape Suite 937', '420', 'West Jessicabury', 'AZ', '73918');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Edward', 'M', 'Moore', '1955-09-14', 'F', '30302 Williams Mountain', '206', 'North Timothyfurt', 'VA', '88109');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Lisa', 'O', 'Martin', '1985-11-23', 'M', '767 Jeffrey Park', '379', 'Crystalburgh', 'SD', '29600');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Allison', 'F', 'Chapman', '1964-03-21', 'M', '23451 Kevin Court Suite 541', '896', 'New Sarahburgh', 'ID', '81665');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Jessica', 'L', 'Lee', '1995-08-04', 'F', '74588 Walton Stream', '761', 'Ruthland', 'MA', '20414');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Martha', 'N', 'Taylor', '1966-02-09', 'M', '696 James Prairie Suite 283', '524', 'Lake Allenmouth', 'GU', '29840');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Reginald', 'Y', 'Gonzales', '1973-10-16', 'M', '70306 Jaime Run', '436', 'West James', 'AS', '31573');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Angela', 'P', 'Martin', '1972-07-31', 'F', '0829 Brock Fort', '900', 'Bradleyborough', 'NM', '17091');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Shelley', 'A', 'Reyes', '1985-08-27', 'F', '15585 Rocha Port Suite 900', '344', 'Jeffersonburgh', 'GU', '07439');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Jesse', 'O', 'Mcmillan', '1978-12-25', 'F', '53376 Steven Crest Suite 784', '802', 'New Heatherton', 'VT', '97012');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Samantha', 'X', 'Valdez', '1967-06-09', 'F', '01548 David Gardens', '137', 'Smithfurt', 'MH', '25014');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Russell', 'U', 'Little', '1986-08-03', 'F', '1891 Johnson Manors Suite 699', '715', 'West Kathleen', 'IN', '42960');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Allen', 'R', 'Walker', '1959-05-22', 'M', '6078 Felicia Creek', '526', 'Josephside', 'CO', '26419');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Adam', 'B', 'Medina', '1984-02-03', 'F', '2852 Shelby Landing', '241', 'New Emilyland', 'SC', '08192');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Dwayne', 'E', 'Ramirez', '1987-08-16', 'F', '257 Jill Flat', '460', 'Josephbury', 'AR', '78253');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Kari', 'H', 'Hunt', '1955-02-08', 'F', '9352 Richard Forges', '850', 'Smithfort', 'MT', '43436');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Jacob', 'V', 'Martinez', '1983-09-30', 'F', '79349 Cunningham Light', '519', 'Matthewport', 'PW', '79416');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Sean', 'I', 'Rose', '1970-02-24', 'F', '94829 Brady Avenue', '552', 'Powellshire', 'NV', '56506');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Michelle', 'X', 'Guzman', '1955-09-25', 'M', '20931 Garcia Spring', '354', 'Patelberg', 'NV', '16790');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Joseph', 'I', 'Ray', '1996-10-09', 'F', '875 Wallace Cape', '302', 'South Dawn', 'WA', '78702');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Amy', 'P', 'Rojas', '1958-10-13', 'F', '4411 Gonzalez Glens Apt. 760', '630', 'West Barbaraberg', 'PA', '57194');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Bradley', 'O', 'Parker', '1989-08-28', 'F', '066 Hernandez Knolls Apt. 551', '311', 'Port Traciberg', 'PW', '72222');
-- INSERT INTO FACULTY Table
INSERT INTO FACULTY (FACULTYID, TITLE, FOFFICE, FPHONE, SALARY) VALUES (67, 'ASSISTANT PROFESSOR', 'Room 570', '+1-537-712-3135', 113618.04);
INSERT INTO FACULTY (FACULTYID, TITLE, FOFFICE, FPHONE, SALARY) VALUES (3, 'PROFESSOR', 'Room 569', '(728)244-6956', 42437.27);
INSERT INTO FACULTY (FACULTYID, TITLE, FOFFICE, FPHONE, SALARY) VALUES (36, 'PROFESSOR', 'Room 882', '403.544.5905', 135421.15);
INSERT INTO FACULTY (FACULTYID, TITLE, FOFFICE, FPHONE, SALARY) VALUES (69, 'PROFESSOR', 'Room 207', '648.332.4776', 162458.01);
INSERT INTO FACULTY (FACULTYID, TITLE, FOFFICE, FPHONE, SALARY) VALUES (71, 'ASSOCIATE PROFESSOR', 'Room 948', '(674)480-5394', 163163.11);
INSERT INTO FACULTY (FACULTYID, TITLE, FOFFICE, FPHONE, SALARY) VALUES (8, 'ASSISTANT PROFESSOR', 'Room 387', '470-665-7545x327', 80310.34);
INSERT INTO FACULTY (FACULTYID, TITLE, FOFFICE, FPHONE, SALARY) VALUES (42, 'ASSOCIATE PROFESSOR', 'Room 935', '(367)596-7489', 80409.52);
INSERT INTO FACULTY (FACULTYID, TITLE, FOFFICE, FPHONE, SALARY) VALUES (22, 'PROFESSOR', 'Room 798', '+1-292-573-9294', 170504.1);
INSERT INTO FACULTY (FACULTYID, TITLE, FOFFICE, FPHONE, SALARY) VALUES (57, 'ASSISTANT PROFESSOR', 'Room 854', '475.309.8322x3827', 125518.16);
INSERT INTO FACULTY (FACULTYID, TITLE, FOFFICE, FPHONE, SALARY) VALUES (28, 'PROFESSOR', 'Room 926', '9032477179', 184694.35);
-- INSERT INTO STUDENT Table
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (1, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (2, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (4, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (5, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (6, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (7, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (9, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (10, 2);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (11, 2);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (12, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (13, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (14, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (15, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (16, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (17, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (18, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (19, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (20, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (21, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (23, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (24, 2);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (25, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (26, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (27, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (29, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (30, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (31, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (32, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (33, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (34, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (35, 2);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (37, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (38, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (39, 2);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (40, 2);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (41, 2);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (43, 2);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (44, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (45, 2);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (46, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (47, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (48, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (49, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (50, 2);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (51, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (52, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (53, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (54, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (55, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (56, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (58, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (59, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (60, 2);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (61, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (62, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (63, 2);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (64, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (65, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (66, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (68, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (70, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (72, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (73, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (74, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (75, 2);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (76, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (77, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (78, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (79, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (80, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (81, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (82, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (83, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (84, 2);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (85, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (86, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (87, 2);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (88, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (89, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (90, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (91, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (92, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (93, 2);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (94, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (95, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (96, 2);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (97, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (98, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (99, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (100, 4);
-- INSERT INTO GRAD_STUDENT Table
INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) VALUES (68, 'MBA', 'Science College', 2024);
INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) VALUES (98, 'M.SC.', 'Science College', 2027);
INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) VALUES (72, 'M.SC.', 'Engineering College', 2025);
INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) VALUES (94, 'PH.D.', 'Science College', 2025);
INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) VALUES (12, 'PH.D.', 'Engineering College', 2025);
INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) VALUES (25, 'M.SC.', 'Science College', 2027);
INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) VALUES (9, 'PH.D.', 'Business College', 2025);
INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) VALUES (29, 'M.SC.', 'Engineering College', 2024);
INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) VALUES (78, 'M.SC.', 'Business College', 2025);
INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) VALUES (52, 'MBA', 'Business College', 2026);
INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) VALUES (15, 'PH.D.', 'Engineering College', 2025);
INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) VALUES (33, 'M.SC.', 'Business College', 2026);
INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) VALUES (2, 'M.SC.', 'Engineering College', 2027);
INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) VALUES (30, 'MBA', 'Engineering College', 2024);
INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) VALUES (31, 'PH.D.', 'Engineering College', 2027);
-- INSERT INTO COMMITTEE Table
INSERT INTO COMMITTEE (FACULTYID, GRAD_STUDENTID) VALUES (36, 31);
INSERT INTO COMMITTEE (FACULTYID, GRAD_STUDENTID) VALUES (8, 30);
INSERT INTO COMMITTEE (FACULTYID, GRAD_STUDENTID) VALUES (8, 15);
INSERT INTO COMMITTEE (FACULTYID, GRAD_STUDENTID) VALUES (8, 31);
INSERT INTO COMMITTEE (FACULTYID, GRAD_STUDENTID) VALUES (69, 94);
-- INSERT INTO GRANT_INFO Table
INSERT INTO GRANT_INFO (PI_FACULTYID, TITLE, GRANTNUMBER, AGENCY, STARTDATE, ENDDATE) VALUES (42, 'Wide issue never government area level.', '4d30e54c-a36d', 'DOE', '2020-07-07', '2025-12-03');
INSERT INTO GRANT_INFO (PI_FACULTYID, TITLE, GRANTNUMBER, AGENCY, STARTDATE, ENDDATE) VALUES (8, 'Stage technology that home stop billion.', '9d1b0043-c2b7', 'NIH', '2024-06-20', '2026-03-25');
INSERT INTO GRANT_INFO (PI_FACULTYID, TITLE, GRANTNUMBER, AGENCY, STARTDATE, ENDDATE) VALUES (28, 'Short away officer small.', '5e1675af-49e6', 'DARPA', '2020-05-16', '2020-06-18');
-- INSERT INTO INSTRUCTOR_RESEARCHER Table
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, FACULTYID) VALUES (71, 'FACULTY', 71);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) VALUES (94, 'GRAD_STUDENT', 94);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, FACULTYID) VALUES (67, 'FACULTY', 67);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, FACULTYID) VALUES (57, 'FACULTY', 57);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, FACULTYID) VALUES (36, 'FACULTY', 36);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) VALUES (29, 'GRAD_STUDENT', 29);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, FACULTYID) VALUES (8, 'FACULTY', 8);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) VALUES (30, 'GRAD_STUDENT', 30);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, FACULTYID) VALUES (42, 'FACULTY', 42);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, FACULTYID) VALUES (28, 'FACULTY', 28);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) VALUES (78, 'GRAD_STUDENT', 78);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) VALUES (31, 'GRAD_STUDENT', 31);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, FACULTYID) VALUES (22, 'FACULTY', 22);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) VALUES (52, 'GRAD_STUDENT', 52);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) VALUES (12, 'GRAD_STUDENT', 12);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) VALUES (9, 'GRAD_STUDENT', 9);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) VALUES (15, 'GRAD_STUDENT', 15);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, FACULTYID) VALUES (69, 'FACULTY', 69);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) VALUES (2, 'GRAD_STUDENT', 2);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) VALUES (72, 'GRAD_STUDENT', 72);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) VALUES (68, 'GRAD_STUDENT', 68);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, FACULTYID) VALUES (3, 'FACULTY', 3);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) VALUES (98, 'GRAD_STUDENT', 98);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) VALUES (25, 'GRAD_STUDENT', 25);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) VALUES (33, 'GRAD_STUDENT', 33);
-- INSERT INTO SUPPORT Table
INSERT INTO SUPPORT (GRANTID, INSTRUCT_RESEARCHID, START_DATE, END_DATE, START_TIME, END_TIME) VALUES (1, 33, '2023-03-01', '2025-03-22', '20:20:25', '03:40:03');
INSERT INTO SUPPORT (GRANTID, INSTRUCT_RESEARCHID, START_DATE, END_DATE, START_TIME, END_TIME) VALUES (1, 28, '2022-04-20', '2022-08-25', '07:13:01', '19:44:27');
INSERT INTO SUPPORT (GRANTID, INSTRUCT_RESEARCHID, START_DATE, END_DATE, START_TIME, END_TIME) VALUES (3, 57, '2025-02-03', '2026-01-17', '16:10:52', '03:55:19');
INSERT INTO SUPPORT (GRANTID, INSTRUCT_RESEARCHID, START_DATE, END_DATE, START_TIME, END_TIME) VALUES (3, 31, '2022-09-05', '2024-08-18', '11:36:24', '04:49:48');
INSERT INTO SUPPORT (GRANTID, INSTRUCT_RESEARCHID, START_DATE, END_DATE, START_TIME, END_TIME) VALUES (3, 28, '2022-10-05', '2024-10-07', '00:36:43', '06:02:11');
-- INSERT INTO COLLEGE Table
INSERT INTO COLLEGE (COLLEGEID, COLLEGENAME, COLLEGEOFFICE, DEAN) VALUES (1, 'College of Business', 'Office 154', 'Peter Oneill');
INSERT INTO COLLEGE (COLLEGEID, COLLEGENAME, COLLEGEOFFICE, DEAN) VALUES (2, 'College of Arts & Humanities', 'Office 353', 'Joel Hernandez');
INSERT INTO COLLEGE (COLLEGEID, COLLEGENAME, COLLEGEOFFICE, DEAN) VALUES (3, 'College of Medicine', 'Office 346', 'Jason Chan');
-- INSERT INTO DEPARTMENT Table
INSERT INTO DEPARTMENT (COLLEGEID, DEPTNAME, DEPTPHONE, DEPTOFFICE) VALUES (1, 'Biology', '(699)401-1712x13313', 'Office 221');
INSERT INTO DEPARTMENT (COLLEGEID, DEPTNAME, DEPTPHONE, DEPTOFFICE) VALUES (2, 'Computer Science', '821.433.2326x48210', 'Office 496');
INSERT INTO DEPARTMENT (COLLEGEID, DEPTNAME, DEPTPHONE, DEPTOFFICE) VALUES (3, 'Mathematics', '+1-538-850-2382', 'Office 345');
INSERT INTO DEPARTMENT (COLLEGEID, DEPTNAME, DEPTPHONE, DEPTOFFICE) VALUES (3, 'Business Administration', '001-551-412-3184x741', 'Office 440');
INSERT INTO DEPARTMENT (COLLEGEID, DEPTNAME, DEPTPHONE, DEPTOFFICE) VALUES (3, 'Mechanical Engineering', '001-217-507-0967x874', 'Office 191');
-- INSERT INTO COURSE Table
INSERT INTO COURSE (COURSEID, DEPTID, CNUM, CNAME, CDESC) VALUES (1, 3, 'CS101', 'Introduction to Computer Science', 'Yes call none check wall not trade. Whole question real Democrat raise cultural remember.');
INSERT INTO COURSE (COURSEID, DEPTID, CNUM, CNAME, CDESC) VALUES (2, 2, 'MATH201', 'Calculus I', 'Image memory support development without another magazine. Those example have industry. Control growth reduce culture new hour interesting. Event maintain population cell expect.');
INSERT INTO COURSE (COURSEID, DEPTID, CNUM, CNAME, CDESC) VALUES (3, 1, 'ME301', 'Thermodynamics', 'Ready network image paper low. Control mind create between hot section good. Two interview little.');
INSERT INTO COURSE (COURSEID, DEPTID, CNUM, CNAME, CDESC) VALUES (4, 2, 'BUS102', 'Principles of Management', 'Either staff whom police. Able century likely time. Sport that red school to international. Box compare artist finally seat and purpose.');
INSERT INTO COURSE (COURSEID, DEPTID, CNUM, CNAME, CDESC) VALUES (5, 5, 'BIO202', 'Genetics', 'Week yeah put left short more free. Scene public technology direction.');
INSERT INTO COURSE (COURSEID, DEPTID, CNUM, CNAME, CDESC) VALUES (6, 4, 'CS202', 'Data Structures', 'Total final security into model she approach. Sense long top decide weight. Name current practice side story.');
INSERT INTO COURSE (COURSEID, DEPTID, CNUM, CNAME, CDESC) VALUES (7, 5, 'MATH305', 'Linear Algebra', 'Face number five town safe. Base last final grow become. Realize tax mother should challenge character data real. Kitchen own by road list method.');
-- INSERT INTO SECTION Table
INSERT INTO SECTION (SECTIONID, COURSEID, INSTRUCT_RESEARCHID, SECNUMBER, YEAR, QTR) VALUES (1, 6, 42, 3, 2025, 'Summer');
INSERT INTO SECTION (SECTIONID, COURSEID, INSTRUCT_RESEARCHID, SECNUMBER, YEAR, QTR) VALUES (2, 7, 98, 5, 2024, 'Winter');
INSERT INTO SECTION (SECTIONID, COURSEID, INSTRUCT_RESEARCHID, SECNUMBER, YEAR, QTR) VALUES (3, 3, 52, 5, 2024, 'Fall');
INSERT INTO SECTION (SECTIONID, COURSEID, INSTRUCT_RESEARCHID, SECNUMBER, YEAR, QTR) VALUES (4, 2, 33, 5, 2021, 'Spring');
INSERT INTO SECTION (SECTIONID, COURSEID, INSTRUCT_RESEARCHID, SECNUMBER, YEAR, QTR) VALUES (5, 7, 98, 2, 2023, 'Spring');
INSERT INTO SECTION (SECTIONID, COURSEID, INSTRUCT_RESEARCHID, SECNUMBER, YEAR, QTR) VALUES (6, 3, 12, 2, 2024, 'Winter');
INSERT INTO SECTION (SECTIONID, COURSEID, INSTRUCT_RESEARCHID, SECNUMBER, YEAR, QTR) VALUES (7, 2, 36, 4, 2024, 'Fall');
-- INSERT INTO CURRENT_SECTION Table
INSERT INTO CURRENT_SECTION (SECTIONID, CURRENTQTR, CURRENTYEAR) VALUES (6, 'Spring', 2025);
INSERT INTO CURRENT_SECTION (SECTIONID, CURRENTQTR, CURRENTYEAR) VALUES (7, 'Spring', 2025);
INSERT INTO CURRENT_SECTION (SECTIONID, CURRENTQTR, CURRENTYEAR) VALUES (3, 'Spring', 2025);
INSERT INTO CURRENT_SECTION (SECTIONID, CURRENTQTR, CURRENTYEAR) VALUES (2, 'Spring', 2025);
INSERT INTO CURRENT_SECTION (SECTIONID, CURRENTQTR, CURRENTYEAR) VALUES (5, 'Spring', 2025);
INSERT INTO CURRENT_SECTION (SECTIONID, CURRENTQTR, CURRENTYEAR) VALUES (1, 'Spring', 2025);
INSERT INTO CURRENT_SECTION (SECTIONID, CURRENTQTR, CURRENTYEAR) VALUES (4, 'Spring', 2025);
-- INSERT INTO REGISTERED Table
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (83, 4);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (72, 7);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (50, 6);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (87, 5);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (1, 3);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (7, 6);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (95, 3);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (68, 4);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (79, 5);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (48, 6);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (52, 6);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (83, 1);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (80, 5);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (58, 5);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (45, 3);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (78, 3);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (89, 3);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (31, 7);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (65, 5);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (26, 5);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (73, 1);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (32, 5);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (99, 6);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (49, 6);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (91, 2);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (35, 6);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (75, 2);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (17, 4);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (19, 2);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (79, 3);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (77, 4);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (68, 1);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (87, 7);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (79, 6);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (4, 4);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (13, 7);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (6, 6);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (27, 2);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (80, 7);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (66, 4);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (83, 2);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (92, 7);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (10, 4);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (89, 2);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (83, 6);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (92, 1);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (75, 7);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (94, 2);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (29, 7);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (35, 7);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (77, 6);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (53, 3);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (95, 4);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (73, 3);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (30, 3);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (40, 2);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (62, 1);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (25, 3);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (85, 6);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (11, 2);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (12, 7);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (31, 4);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (44, 2);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (97, 2);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (39, 6);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (96, 4);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (51, 2);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (13, 2);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (34, 2);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (17, 1);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (35, 2);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (45, 6);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (59, 4);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (86, 1);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (61, 4);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (27, 4);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (2, 6);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (100, 3);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (46, 6);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (54, 5);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (73, 7);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (16, 5);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (87, 2);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (51, 6);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (77, 1);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (61, 6);
-- INSERT INTO TRANSCRIPT Table
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (87, 7, 'B');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (50, 6, 'D');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (27, 4, 'C');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (61, 6, 'D+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (26, 5, 'B-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (95, 4, 'D');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (86, 1, 'F');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (45, 3, 'C-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (100, 3, 'C+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (19, 2, 'C');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (32, 5, 'F');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (68, 4, 'F');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (73, 3, 'B-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (87, 2, 'B-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (59, 4, 'B');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (91, 2, 'B+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (51, 2, 'B-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (46, 6, 'D');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (79, 3, 'D');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (6, 6, 'D+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (85, 6, 'B-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (11, 2, 'B');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (1, 3, 'D+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (79, 5, 'D');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (73, 7, 'A');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (83, 2, 'B-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (94, 2, 'A-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (51, 6, 'F');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (75, 7, 'C');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (66, 4, 'C-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (68, 1, 'B');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (13, 7, 'C+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (35, 7, 'F');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (54, 5, 'F');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (34, 2, 'B+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (17, 4, 'C');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (80, 5, 'B-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (83, 4, 'C+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (58, 5, 'C-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (4, 4, 'C');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (92, 7, 'D');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (2, 6, 'D+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (16, 5, 'C+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (80, 7, 'A-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (83, 6, 'B+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (75, 2, 'C-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (13, 2, 'B+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (35, 2, 'A-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (31, 7, 'C-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (45, 6, 'D+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (77, 4, 'C');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (78, 3, 'D+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (89, 3, 'B-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (65, 5, 'B+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (25, 3, 'C-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (49, 6, 'B');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (95, 3, 'D');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (77, 6, 'B');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (83, 1, 'B-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (96, 4, 'B');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (35, 6, 'B-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (79, 6, 'F');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (39, 6, 'B+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (97, 2, 'B-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (12, 7, 'A');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (52, 6, 'C');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (30, 3, 'A-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (44, 2, 'C');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (73, 1, 'C+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (62, 1, 'B');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (29, 7, 'B-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (31, 4, 'D');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (77, 1, 'B+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (72, 7, 'D+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (7, 6, 'C-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (87, 5, 'B');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (89, 2, 'C');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (92, 1, 'D+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (53, 3, 'A');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (61, 4, 'A-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (27, 2, 'D+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (17, 1, 'A-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (10, 4, 'F');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (99, 6, 'C-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (48, 6, 'C-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (40, 2, 'C+');
-- INSERT INTO MAJORMINOR Table
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (65, '4', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (13, '1', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (48, '3', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (53, '5', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (26, '2', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (54, '1', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (34, '5', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (89, '1', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (91, '3', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (51, '3', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (100, '3', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (59, '3', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (21, '4', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (46, '3', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (91, '5', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (15, '5', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (62, '4', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (17, '5', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (10, '4', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (1, '1', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (80, '2', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (83, '4', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (19, '3', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (4, '2', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (14, '1', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (38, '2', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (40, '1', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (20, '1', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (2, '2', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (63, '5', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (66, '2', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (41, '4', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (31, '5', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (83, '2', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (21, '1', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (24, '5', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (32, '3', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (46, '5', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (58, '5', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (99, '1', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (34, '1', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (23, '5', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (60, '5', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (81, '1', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (61, '4', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (72, '3', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (93, '3', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (92, '4', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (61, '2', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (95, '3', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (84, '5', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (98, '4', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (2, '4', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (14, '2', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (61, '5', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (27, '2', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (19, '2', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (47, '3', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (33, '1', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (55, '4', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (85, '4', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (19, '5', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (73, '1', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (45, '3', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (50, '3', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (68, '2', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (80, '3', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (95, '4', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (98, '5', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (47, '4', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (86, '2', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (52, '1', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (33, '4', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (78, '1', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (77, '4', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (12, '3', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (29, '1', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (79, '1', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (34, '3', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (81, '3', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (76, '4', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (7, '4', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (29, '3', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (96, '3', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (24, '5', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (61, '1', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (70, '1', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (24, '3', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (17, '2', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (52, '4', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (55, '3', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (86, '4', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (75, '1', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (18, '2', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (91, '3', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (33, '2', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (44, '4', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (81, '2', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (85, '3', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (68, '5', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (56, '3', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (4, '4', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (78, '5', 'MAJOR');
-- INSERT INTO BELONGS Table
INSERT INTO BELONGS (FACULTYID, DEPTID) VALUES (69, '5');
INSERT INTO BELONGS (FACULTYID, DEPTID) VALUES (57, '5');
INSERT INTO BELONGS (FACULTYID, DEPTID) VALUES (28, '3');
INSERT INTO BELONGS (FACULTYID, DEPTID) VALUES (8, '2');
INSERT INTO BELONGS (FACULTYID, DEPTID) VALUES (57, '1');
INSERT INTO BELONGS (FACULTYID, DEPTID) VALUES (42, '3');
INSERT INTO BELONGS (FACULTYID, DEPTID) VALUES (67, '4');
INSERT INTO BELONGS (FACULTYID, DEPTID) VALUES (69, '2');
INSERT INTO BELONGS (FACULTYID, DEPTID) VALUES (3, '1');
INSERT INTO BELONGS (FACULTYID, DEPTID) VALUES (71, '2');

DROP USER IF EXISTS 'ASSIGN1PART2'@'LOCALHOST';
CREATE USER 'ASSIGN1PART2'@'LOCALHOST' IDENTIFIED BY 'UNIVERSITY123';
GRANT ALL ON UNIVERSITY.* TO 'ASSIGN1PART2'@'LOCALHOST';
FLUSH PRIVILEGES;

SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'UNIVERSITY' ORDER BY CREATE_TIME ASC;
SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'UNIVERSITY' ORDER BY TABLE_NAME, COLUMN_NAME ASC;
SELECT * FROM INFORMATION_SCHEMA.TRIGGERS WHERE TRIGGER_SCHEMA = 'UNIVERSITY';
SELECT * FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS WHERE TABLE_SCHEMA = 'UNIVERSITY' ORDER BY TABLE_NAME ASC;

SHOW TABLES;