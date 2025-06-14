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
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Karen', 'Y', 'Terry', '2004-08-31', 'F', '7359 Pierce Mills', '683', 'Jacobhaven', 'MN', '37893');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Edward', 'S', 'Smith', '1966-09-10', 'M', '6722 Hayes Pass', '184', 'West Melinda', 'LA', '53958');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Matthew', 'R', 'Little', '1993-11-29', 'F', '4785 Lisa Cliffs', '398', 'West Briantown', 'RI', '76470');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Amy', 'U', 'Griffith', '1963-05-17', 'F', '6681 Mikayla Mission', '462', 'Lake Taraton', 'VI', '32953');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Erica', 'Q', 'Rice', '1967-03-10', 'M', '90981 Virginia Plaza Apt. 996', '372', 'Emilyhaven', 'GA', '14968');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Zachary', 'A', 'Mitchell', '1974-06-24', 'F', '0911 Ramos Knoll', '303', 'Combsburgh', 'CA', '49008');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Joseph', 'M', 'Jenkins', '1959-09-06', 'F', '94985 Danielle Extensions Suite 511', '198', 'Valerieshire', 'ND', '67237');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('James', 'C', 'Berg', '1998-04-27', 'F', '236 Thompson Ramp Suite 752', '596', 'Morganmouth', 'SC', '19369');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Melissa', 'S', 'Smith', '1998-06-24', 'F', '44325 Fox Ferry', '876', 'Lewiston', 'DC', '42276');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Sarah', 'R', 'Green', '1964-08-11', 'F', '340 Becky Trace Apt. 796', '169', 'New Mariamouth', 'IA', '38956');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('James', 'R', 'Walters', '1969-04-01', 'M', '229 Anthony Coves Suite 298', '697', 'South Rebecca', 'NV', '70798');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Billy', 'I', 'English', '1985-02-04', 'F', '6033 John Overpass Apt. 851', '867', 'South Deniseport', 'ID', '72563');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Sarah', 'E', 'Bowman', '1984-01-17', 'M', '1460 Gardner Key Apt. 567', '632', 'East Kennethville', 'MS', '47370');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Shannon', 'P', 'Anderson', '1960-06-25', 'M', '76174 Kathryn Circles', '623', 'Smithburgh', 'WI', '83386');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Kristi', 'C', 'Wallace', '1965-10-16', 'M', '736 Williams Alley', '576', 'Leonardville', 'WV', '25716');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Rebecca', 'I', 'Rivera', '1965-07-23', 'M', '4501 Olson Point', '748', 'Thomasborough', 'IL', '73639');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Crystal', 'Q', 'Navarro', '1966-01-02', 'F', '28534 Hansen Brook', '980', 'Simpsonberg', 'WI', '39168');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Jackie', 'G', 'Smith', '1981-09-13', 'F', '52084 David Springs Suite 509', '535', 'East Timothy', 'ME', '30653');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Tyler', 'I', 'Fritz', '2005-11-21', 'M', '95352 Clark Forks Apt. 623', '399', 'Port Destiny', 'AS', '52861');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Wayne', 'I', 'Jacobs', '1959-12-17', 'F', '950 Joshua Village', '281', 'Elizabethport', 'IA', '95995');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Gary', 'H', 'Bryant', '1967-07-02', 'F', '8751 Michele Light', '784', 'Alexandermouth', 'MO', '99009');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Bruce', 'F', 'Krueger', '1988-02-11', 'M', '7152 Rebecca Garden Suite 497', '438', 'North Kristi', 'MH', '94654');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('John', 'C', 'Garza', '1955-07-14', 'M', '7408 Gibson Viaduct Suite 794', '200', 'Hillview', 'WY', '14021');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Christina', 'U', 'Nelson', '1975-01-23', 'F', '96709 Ayala Garden Suite 709', '745', 'Mariafort', 'HI', '91764');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Laura', 'D', 'Fisher', '1980-06-29', 'M', '2170 Bethany Ports Suite 377', '118', 'Youngtown', 'NH', '32832');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Amanda', 'O', 'Berger', '1992-03-04', 'M', '22604 White Crest', '449', 'Kennethtown', 'PA', '26019');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Joseph', 'W', 'Hutchinson', '1972-06-02', 'F', '9610 Clark Canyon', '539', 'Brittanymouth', 'RI', '98184');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Kellie', 'D', 'Doyle', '1962-03-10', 'F', '75230 Jennifer Overpass Apt. 498', '492', 'Lake Roberthaven', 'UT', '17436');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Erica', 'F', 'Smith', '1997-09-06', 'M', '676 Nash Unions', '363', 'East Andrewmouth', 'MI', '82426');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Chelsea', 'T', 'Wolfe', '1973-05-24', 'M', '117 Patrick Radial', '415', 'East Alyssa', 'MH', '31102');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Donna', 'C', 'Durham', '1993-09-12', 'M', '78356 Deleon Crest Apt. 030', '719', 'Mcbrideport', 'CT', '40655');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Christopher', 'L', 'Stokes', '1985-07-27', 'M', '513 Hannah Route Apt. 453', '296', 'North Darrenchester', 'ME', '36140');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('William', 'L', 'Clay', '1967-01-18', 'F', '327 Courtney Viaduct Apt. 659', '645', 'Michaelshire', 'RI', '23382');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Tina', 'L', 'Salazar', '2004-03-30', 'F', '37680 Walker Canyon', '584', 'Valentineland', 'MI', '93032');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Kimberly', 'G', 'Jenkins', '1989-08-01', 'F', '38042 Martin Drives', '479', 'North Kelly', 'GU', '73632');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('David', 'E', 'Patterson', '2003-07-05', 'M', '63558 Wright Lights', '580', 'Tranville', 'OK', '81961');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Elizabeth', 'I', 'Alexander', '1999-12-18', 'M', '64811 Hoffman Land Apt. 345', '298', 'New Cynthiahaven', 'FL', '49210');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Angelica', 'W', 'Frazier', '1985-05-16', 'F', '43685 Sullivan Inlet Suite 821', '408', 'North Erin', 'LA', '75364');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Kaitlyn', 'X', 'Maldonado', '1958-06-19', 'M', '04430 Linda Well Suite 248', '155', 'North Amanda', 'MT', '81420');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Paula', 'J', 'Schaefer', '1975-05-19', 'F', '5020 Thomas Freeway', '642', 'North Danaborough', 'OH', '71344');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Tracy', 'A', 'Rivas', '1995-03-23', 'F', '911 Janet Courts Suite 909', '888', 'Johnsonmouth', 'DE', '18259');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Eric', 'E', 'Williams', '1981-12-02', 'M', '124 Ryan Motorway Apt. 700', '534', 'Melissafurt', 'VT', '95761');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Heather', 'Z', 'Hunt', '1980-09-29', 'M', '6939 Miller Springs Apt. 314', '579', 'North Garyton', 'OK', '86434');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Sheri', 'M', 'Boyer', '1983-07-31', 'M', '762 Patterson Key Suite 758', '448', 'West Tommy', 'WV', '09052');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Kim', 'S', 'Greer', '1970-09-25', 'F', '571 Kevin Parks', '267', 'North Katherine', 'KY', '86896');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Christine', 'D', 'Porter', '1986-04-12', 'M', '77717 Brian Village Apt. 244', '181', 'Matthewsland', 'LA', '76232');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Nichole', 'D', 'Gonzales', '1958-07-17', 'F', '35119 Kevin Junction', '538', 'Lake Jameshaven', 'SD', '60969');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Dawn', 'R', 'Bass', '1992-06-17', 'M', '35060 Hughes Canyon', '574', 'Ramirezland', 'AK', '79995');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Eric', 'M', 'Hall', '1955-08-21', 'M', '265 Tyler Brook Apt. 623', '379', 'South Ronaldstad', 'NM', '59528');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Melissa', 'T', 'Lewis', '2007-01-12', 'M', '5027 Lewis Cliff', '226', 'Port Matthew', 'HI', '84333');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Darlene', 'G', 'Barnes', '1965-12-04', 'M', '25102 Lori Club', '879', 'New Kaylafort', 'UT', '62252');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Angela', 'P', 'Roberts', '1976-10-22', 'F', '898 Stephens Rest Apt. 534', '388', 'Lake Gerald', 'MI', '96210');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Nancy', 'O', 'Rodriguez', '1997-04-18', 'F', '82161 Christina Valley', '484', 'Onealtown', 'NV', '49288');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Gina', 'H', 'Griffin', '1985-06-16', 'M', '29090 Lee Ramp', '861', 'North Richardhaven', 'ID', '45334');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Melanie', 'K', 'Valenzuela', '1974-02-10', 'M', '8490 Callahan Spur Apt. 623', '949', 'Hansonland', 'NH', '10220');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Amber', 'L', 'Roach', '2006-09-22', 'F', '6205 Washington Lodge Suite 226', '782', 'Jacksonfurt', 'MA', '72610');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Brandon', 'U', 'Green', '1969-06-26', 'F', '76465 Ashley Neck Apt. 716', '161', 'Kimberlyborough', 'NC', '85148');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Kristina', 'L', 'Kidd', '1982-05-24', 'M', '18791 Andrew Radial Suite 888', '387', 'New Michellemouth', 'VI', '41599');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Wanda', 'U', 'Butler', '2001-03-25', 'M', '08326 Randy Summit Suite 509', '816', 'South Ryanmouth', 'IN', '10738');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Lynn', 'U', 'Perez', '1987-08-11', 'F', '3460 Hansen Gardens Apt. 620', '506', 'South Katherinechester', 'WI', '17524');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Barbara', 'T', 'Brown', '1996-04-11', 'M', '5763 Stacy Brooks Apt. 420', '302', 'North Patrick', 'NY', '95980');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Kristi', 'T', 'Warner', '1960-10-27', 'F', '08222 Sierra Stream Apt. 183', '619', 'Lake Julie', 'AZ', '02309');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Christopher', 'U', 'James', '1963-09-30', 'F', '6424 Melissa Expressway Apt. 357', '724', 'North Mary', 'MT', '12535');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Claudia', 'Y', 'Simpson', '1966-05-14', 'F', '3438 Aguirre Spurs Apt. 384', '485', 'Lake Christinefort', 'WY', '15321');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Christina', 'N', 'Jones', '1975-06-25', 'F', '6592 Colleen Green', '187', 'Gonzalezstad', 'MH', '58179');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Patrick', 'B', 'Escobar', '2001-11-22', 'M', '66279 William Crossing Suite 651', '630', 'Bennettfurt', 'RI', '37718');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Christine', 'K', 'Ward', '1962-03-21', 'F', '2370 Benton Gateway Suite 472', '513', 'Walkerview', 'MP', '84017');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Jon', 'T', 'Simmons', '1984-10-14', 'M', '6844 Ellen Isle Suite 357', '973', 'Jamesland', 'WV', '99346');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Jessica', 'G', 'Allen', '2001-07-26', 'F', '87839 Tonya Union', '503', 'Port Sheilaton', 'MN', '49507');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Allen', 'R', 'Stevens', '1978-10-25', 'M', '867 Jerry Islands Apt. 053', '785', 'New Daniel', 'WA', '57591');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Robert', 'W', 'Norton', '1960-05-12', 'M', '00525 Cameron River Apt. 493', '196', 'Richardberg', 'PW', '57746');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Kayla', 'T', 'Herrera', '1972-04-04', 'F', '869 Corey Terrace Suite 455', '845', 'South Laura', 'GA', '11833');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Timothy', 'E', 'Parker', '1966-12-30', 'M', '1917 Danielle Crescent', '703', 'Stevenburgh', 'AK', '45756');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Lauren', 'V', 'Rodriguez', '1978-02-15', 'F', '69698 Garcia Locks', '820', 'Debraland', 'PW', '61898');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Dennis', 'Y', 'Ellis', '1970-12-25', 'F', '36316 Martinez Walk', '745', 'North Jessicaville', 'MS', '97668');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Chelsea', 'D', 'Graham', '1957-02-05', 'F', '540 Craig Pine Suite 390', '417', 'Erinhaven', 'OH', '65275');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Rachel', 'E', 'Turner', '1978-10-24', 'F', '51248 Vargas Village', '419', 'Lake Shawnview', 'NY', '77879');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Jasmine', 'C', 'Garcia', '1964-04-25', 'M', '511 Kelly Village Suite 594', '881', 'North Tammy', 'AK', '76258');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Sarah', 'O', 'Prince', '1974-10-09', 'F', '8636 Oneill Court Apt. 774', '486', 'Lanefurt', 'TX', '77100');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Jackie', 'J', 'Mason', '1958-12-22', 'M', '054 Rogers Crossroad Apt. 965', '832', 'North Kevin', 'MH', '57882');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Richard', 'R', 'Hall', '1956-09-03', 'F', '4337 Brianna Vista Apt. 014', '848', 'Smithton', 'TN', '06378');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Manuel', 'G', 'Hart', '1999-10-17', 'F', '6646 Mosley Camp', '773', 'Wayneport', 'SD', '15251');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Denise', 'D', 'Newman', '1956-08-04', 'F', '706 Russo Vista', '374', 'Stewartton', 'IN', '23580');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Adriana', 'N', 'Smith', '1986-03-11', 'F', '233 Jerry Well', '578', 'Sandovalmouth', 'RI', '24460');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Maurice', 'F', 'Jordan', '1987-09-16', 'F', '65871 John Overpass', '957', 'Laurastad', 'MD', '16458');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Crystal', 'Y', 'Smith', '1979-04-08', 'F', '60400 Caroline Bypass Suite 479', '759', 'Rebeccaside', 'NE', '13558');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Leslie', 'E', 'Fuentes', '1987-02-20', 'F', '451 Devin Haven Apt. 209', '786', 'New Timothy', 'ND', '57086');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Jessica', 'O', 'Patel', '1998-01-05', 'F', '7712 Gregory Parkway Suite 132', '256', 'West Marcus', 'NY', '80014');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Jeremy', 'W', 'Mccarthy', '1961-12-05', 'F', '316 Elizabeth Field', '975', 'Williamsside', 'AK', '24347');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Laura', 'I', 'Gordon', '1975-01-29', 'M', '0352 Evans Vista', '838', 'West Bradley', 'VA', '34172');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Belinda', 'I', 'Baker', '2000-08-28', 'F', '62488 Evelyn Mill Apt. 843', '587', 'Westmouth', 'FL', '99265');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Stephen', 'E', 'Nelson', '1979-12-22', 'M', '69738 Danielle Bypass', '386', 'North Alexander', 'IN', '68947');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Sean', 'Y', 'Bright', '1956-11-22', 'F', '243 Suzanne Overpass', '986', 'Kevinhaven', 'CO', '65935');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Lisa', 'B', 'Miller', '1966-08-10', 'F', '4102 Angela Unions Suite 320', '613', 'Margaretland', 'OH', '02042');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Rebecca', 'J', 'Cobb', '1965-05-08', 'F', '9373 Lopez Ridge Apt. 378', '639', 'Hurstbury', 'OH', '26813');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Joseph', 'O', 'Townsend', '1980-03-24', 'F', '825 Williamson Greens', '197', 'North Laurenbury', 'KS', '53356');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Nicole', 'B', 'Mosley', '1997-02-13', 'M', '76794 Gary Mount', '189', 'Katelynland', 'ND', '42438');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Jacqueline', 'S', 'Garcia', '1961-11-18', 'M', '49237 Anna Mountains Suite 613', '958', 'Brownview', 'SD', '23313');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Evan', 'B', 'Lynch', '1963-02-03', 'M', '957 Rachel Course Suite 616', '242', 'Lake Arianaton', 'ID', '23143');
INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) VALUES ('Lonnie', 'Z', 'Campbell', '1998-08-28', 'F', '8900 Shelly Canyon Suite 546', '891', 'South Brandystad', 'MN', '95504');
-- INSERT INTO FACULTY Table
INSERT INTO FACULTY (FACULTYID, TITLE, FOFFICE, FPHONE, SALARY) VALUES (65, 'ASSOCIATE PROFESSOR', 'Room 505', '398-358-2268x4387', 163042.14);
INSERT INTO FACULTY (FACULTYID, TITLE, FOFFICE, FPHONE, SALARY) VALUES (34, 'PROFESSOR', 'Room 290', '295.231.0007x56162', 42990.22);
INSERT INTO FACULTY (FACULTYID, TITLE, FOFFICE, FPHONE, SALARY) VALUES (40, 'ASSOCIATE PROFESSOR', 'Room 728', '375.988.4030x8894', 125721.8);
INSERT INTO FACULTY (FACULTYID, TITLE, FOFFICE, FPHONE, SALARY) VALUES (8, 'ASSOCIATE PROFESSOR', 'Room 488', '+1-906-376-4961', 182353.55);
INSERT INTO FACULTY (FACULTYID, TITLE, FOFFICE, FPHONE, SALARY) VALUES (42, 'PROFESSOR', 'Room 547', '4624204427', 137644.11);
INSERT INTO FACULTY (FACULTYID, TITLE, FOFFICE, FPHONE, SALARY) VALUES (75, 'ASSISTANT PROFESSOR', 'Room 678', '434.546.3679x66909', 94039.87);
INSERT INTO FACULTY (FACULTYID, TITLE, FOFFICE, FPHONE, SALARY) VALUES (50, 'ASSOCIATE PROFESSOR', 'Room 692', '219.353.7025x436', 45642.85);
INSERT INTO FACULTY (FACULTYID, TITLE, FOFFICE, FPHONE, SALARY) VALUES (82, 'PROFESSOR', 'Room 180', '2169282951', 197355.25);
INSERT INTO FACULTY (FACULTYID, TITLE, FOFFICE, FPHONE, SALARY) VALUES (86, 'ASSOCIATE PROFESSOR', 'Room 926', '(964)909-1256x978', 119177.3);
INSERT INTO FACULTY (FACULTYID, TITLE, FOFFICE, FPHONE, SALARY) VALUES (24, 'PROFESSOR', 'Room 589', '+1-431-809-2345', 191470.29);
-- INSERT INTO STUDENT Table
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (1, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (2, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (3, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (4, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (5, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (6, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (7, 2);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (9, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (10, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (11, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (12, 2);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (13, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (14, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (15, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (16, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (17, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (18, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (19, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (20, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (21, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (22, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (23, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (25, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (26, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (27, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (28, 2);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (29, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (30, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (31, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (32, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (33, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (35, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (36, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (37, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (38, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (39, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (41, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (43, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (44, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (45, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (46, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (47, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (48, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (49, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (51, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (52, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (53, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (54, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (55, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (56, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (57, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (58, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (59, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (60, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (61, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (62, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (63, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (64, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (66, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (67, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (68, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (69, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (70, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (71, 2);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (72, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (73, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (74, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (76, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (77, 2);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (78, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (79, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (80, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (81, 2);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (83, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (84, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (85, 4);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (87, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (88, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (89, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (90, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (91, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (92, 2);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (93, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (94, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (95, 3);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (96, 2);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (97, 5);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (98, 1);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (99, 2);
INSERT INTO STUDENT (STUDENTID, CLASS) VALUES (100, 1);
-- INSERT INTO GRAD_STUDENT Table
INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) VALUES (44, 'M.SC.', 'Engineering College', 2024);
INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) VALUES (19, 'M.SC.', 'Engineering College', 2027);
INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) VALUES (93, 'M.SC.', 'Engineering College', 2025);
INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) VALUES (15, 'M.SC.', 'Business College', 2026);
INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) VALUES (70, 'PH.D.', 'Business College', 2024);
INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) VALUES (60, 'M.SC.', 'Business College', 2026);
INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) VALUES (10, 'MBA', 'Business College', 2025);
INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) VALUES (14, 'PH.D.', 'Science College', 2027);
INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) VALUES (30, 'M.SC.', 'Engineering College', 2025);
INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) VALUES (97, 'MBA', 'Science College', 2026);
INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) VALUES (23, 'M.SC.', 'Business College', 2025);
INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) VALUES (79, 'PH.D.', 'Science College', 2026);
INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) VALUES (55, 'MBA', 'Engineering College', 2026);
INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) VALUES (56, 'PH.D.', 'Engineering College', 2024);
INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) VALUES (64, 'MBA', 'Business College', 2026);
-- INSERT INTO COMMITTEE Table
INSERT INTO COMMITTEE (FACULTYID, GRAD_STUDENTID) VALUES (40, 93);
INSERT INTO COMMITTEE (FACULTYID, GRAD_STUDENTID) VALUES (34, 44);
INSERT INTO COMMITTEE (FACULTYID, GRAD_STUDENTID) VALUES (8, 97);
INSERT INTO COMMITTEE (FACULTYID, GRAD_STUDENTID) VALUES (50, 10);
INSERT INTO COMMITTEE (FACULTYID, GRAD_STUDENTID) VALUES (34, 70);
-- INSERT INTO GRANT_INFO Table
INSERT INTO GRANT_INFO (PI_FACULTYID, TITLE, GRANTNUMBER, AGENCY, STARTDATE, ENDDATE) VALUES (24, 'Lay decide section fight just down.', 'e7f48f55-2217', 'NIH', '2024-06-05', '2028-06-17');
INSERT INTO GRANT_INFO (PI_FACULTYID, TITLE, GRANTNUMBER, AGENCY, STARTDATE, ENDDATE) VALUES (50, 'Everything within fear both just church of region.', '841776bb-3c1b', 'NASA', '2021-07-25', '2029-05-25');
INSERT INTO GRANT_INFO (PI_FACULTYID, TITLE, GRANTNUMBER, AGENCY, STARTDATE, ENDDATE) VALUES (50, 'Price inside necessary wind audience today soldier.', '79cc78d2-bada', 'NIH', '2025-03-03', '2027-05-16');
-- INSERT INTO INSTRUCTOR_RESEARCHER Table
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, FACULTYID) VALUES (65, 'FACULTY', 65);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) VALUES (23, 'GRAD_STUDENT', 23);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) VALUES (30, 'GRAD_STUDENT', 30);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) VALUES (10, 'GRAD_STUDENT', 10);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, FACULTYID) VALUES (40, 'FACULTY', 40);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, FACULTYID) VALUES (8, 'FACULTY', 8);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, FACULTYID) VALUES (86, 'FACULTY', 86);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) VALUES (64, 'GRAD_STUDENT', 64);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) VALUES (60, 'GRAD_STUDENT', 60);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) VALUES (19, 'GRAD_STUDENT', 19);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, FACULTYID) VALUES (34, 'FACULTY', 34);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) VALUES (79, 'GRAD_STUDENT', 79);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, FACULTYID) VALUES (82, 'FACULTY', 82);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) VALUES (56, 'GRAD_STUDENT', 56);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) VALUES (55, 'GRAD_STUDENT', 55);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) VALUES (93, 'GRAD_STUDENT', 93);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) VALUES (14, 'GRAD_STUDENT', 14);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) VALUES (15, 'GRAD_STUDENT', 15);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) VALUES (97, 'GRAD_STUDENT', 97);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, FACULTYID) VALUES (75, 'FACULTY', 75);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) VALUES (44, 'GRAD_STUDENT', 44);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) VALUES (70, 'GRAD_STUDENT', 70);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, FACULTYID) VALUES (42, 'FACULTY', 42);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, FACULTYID) VALUES (50, 'FACULTY', 50);
INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, FACULTYID) VALUES (24, 'FACULTY', 24);
-- INSERT INTO SUPPORT Table
INSERT INTO SUPPORT (GRANTID, INSTRUCT_RESEARCHID, START_DATE, END_DATE, START_TIME, END_TIME) VALUES (1, 79, '2024-09-11', '2026-05-21', '11:50:00', '10:48:37');
INSERT INTO SUPPORT (GRANTID, INSTRUCT_RESEARCHID, START_DATE, END_DATE, START_TIME, END_TIME) VALUES (2, 75, '2024-07-14', '2026-02-04', '02:11:24', '13:39:51');
INSERT INTO SUPPORT (GRANTID, INSTRUCT_RESEARCHID, START_DATE, END_DATE, START_TIME, END_TIME) VALUES (1, 8, '2024-09-14', '2026-05-05', '18:25:55', '12:48:42');
INSERT INTO SUPPORT (GRANTID, INSTRUCT_RESEARCHID, START_DATE, END_DATE, START_TIME, END_TIME) VALUES (2, 79, '2023-07-13', '2025-01-02', '03:31:06', '20:56:50');
INSERT INTO SUPPORT (GRANTID, INSTRUCT_RESEARCHID, START_DATE, END_DATE, START_TIME, END_TIME) VALUES (2, 40, '2022-03-26', '2025-08-21', '07:41:41', '03:03:55');
-- INSERT INTO COLLEGE Table
INSERT INTO COLLEGE (COLLEGEID, COLLEGENAME, COLLEGEOFFICE, DEAN) VALUES (1, 'College of Arts & Humanities', 'Office 275', 'Michael Schneider');
INSERT INTO COLLEGE (COLLEGEID, COLLEGENAME, COLLEGEOFFICE, DEAN) VALUES (2, 'College of Science', 'Office 188', 'Jessica Brennan');
INSERT INTO COLLEGE (COLLEGEID, COLLEGENAME, COLLEGEOFFICE, DEAN) VALUES (3, 'College of Business', 'Office 114', 'Jennifer Chavez');
-- INSERT INTO DEPARTMENT Table
INSERT INTO DEPARTMENT (COLLEGEID, DEPTNAME, DEPTPHONE, DEPTOFFICE) VALUES (2, 'Mechanical Engineering', '415.706.4111', 'Office 290');
INSERT INTO DEPARTMENT (COLLEGEID, DEPTNAME, DEPTPHONE, DEPTOFFICE) VALUES (1, 'Mathematics', '530.235.9710x925', 'Office 336');
INSERT INTO DEPARTMENT (COLLEGEID, DEPTNAME, DEPTPHONE, DEPTOFFICE) VALUES (2, 'Business Administration', '491-789-5509x867', 'Office 473');
INSERT INTO DEPARTMENT (COLLEGEID, DEPTNAME, DEPTPHONE, DEPTOFFICE) VALUES (2, 'Biology', '+1-462-378-0915x184', 'Office 289');
INSERT INTO DEPARTMENT (COLLEGEID, DEPTNAME, DEPTPHONE, DEPTOFFICE) VALUES (1, 'Computer Science', '+1-358-626-5305x533', 'Office 260');
-- INSERT INTO COURSE Table
INSERT INTO COURSE (COURSEID, DEPTID, CNUM, CNAME, CDESC) VALUES (1, 4, 'CS101', 'Introduction to Computer Science', 'Collection fall matter each space leader. Spend executive old north card best high each. Property central establish certain food see no. Book away wear degree.');
INSERT INTO COURSE (COURSEID, DEPTID, CNUM, CNAME, CDESC) VALUES (2, 4, 'MATH201', 'Calculus I', 'Grow side entire campaign. Ahead face involve civil police environmental.');
INSERT INTO COURSE (COURSEID, DEPTID, CNUM, CNAME, CDESC) VALUES (3, 5, 'ME301', 'Thermodynamics', 'Raise customer human Democrat. Walk industry give buy car remain.');
INSERT INTO COURSE (COURSEID, DEPTID, CNUM, CNAME, CDESC) VALUES (4, 5, 'BUS102', 'Principles of Management', 'When require manager anything year run. Us religious budget first.');
INSERT INTO COURSE (COURSEID, DEPTID, CNUM, CNAME, CDESC) VALUES (5, 4, 'BIO202', 'Genetics', 'Move include occur they girl. The statement near. Space throughout ok.');
INSERT INTO COURSE (COURSEID, DEPTID, CNUM, CNAME, CDESC) VALUES (6, 1, 'CS202', 'Data Structures', 'Present hear product hit behind. Defense also near central. Begin simple quite family perform politics left.');
INSERT INTO COURSE (COURSEID, DEPTID, CNUM, CNAME, CDESC) VALUES (7, 2, 'MATH305', 'Linear Algebra', 'Leave debate ask difference. Future hold personal box. Require suddenly compare both.');
-- INSERT INTO SECTION Table
INSERT INTO SECTION (SECTIONID, COURSEID, INSTRUCT_RESEARCHID, SECNUMBER, YEAR, QTR) VALUES (1, 2, 50, 3, 2023, 'Spring');
INSERT INTO SECTION (SECTIONID, COURSEID, INSTRUCT_RESEARCHID, SECNUMBER, YEAR, QTR) VALUES (2, 4, 82, 5, 2023, 'Winter');
INSERT INTO SECTION (SECTIONID, COURSEID, INSTRUCT_RESEARCHID, SECNUMBER, YEAR, QTR) VALUES (3, 7, 75, 1, 2020, 'Fall');
INSERT INTO SECTION (SECTIONID, COURSEID, INSTRUCT_RESEARCHID, SECNUMBER, YEAR, QTR) VALUES (4, 2, 75, 3, 2021, 'Spring');
INSERT INTO SECTION (SECTIONID, COURSEID, INSTRUCT_RESEARCHID, SECNUMBER, YEAR, QTR) VALUES (5, 2, 40, 4, 2023, 'Summer');
INSERT INTO SECTION (SECTIONID, COURSEID, INSTRUCT_RESEARCHID, SECNUMBER, YEAR, QTR) VALUES (6, 1, 34, 2, 2021, 'Spring');
INSERT INTO SECTION (SECTIONID, COURSEID, INSTRUCT_RESEARCHID, SECNUMBER, YEAR, QTR) VALUES (7, 4, 70, 4, 2020, 'Winter');
-- INSERT INTO CURRENT_SECTION Table
INSERT INTO CURRENT_SECTION (SECTIONID, CURRENTQTR, CURRENTYEAR) VALUES (1, 'Spring', 2025);
INSERT INTO CURRENT_SECTION (SECTIONID, CURRENTQTR, CURRENTYEAR) VALUES (3, 'Spring', 2025);
INSERT INTO CURRENT_SECTION (SECTIONID, CURRENTQTR, CURRENTYEAR) VALUES (7, 'Spring', 2025);
INSERT INTO CURRENT_SECTION (SECTIONID, CURRENTQTR, CURRENTYEAR) VALUES (5, 'Spring', 2025);
INSERT INTO CURRENT_SECTION (SECTIONID, CURRENTQTR, CURRENTYEAR) VALUES (2, 'Spring', 2025);
INSERT INTO CURRENT_SECTION (SECTIONID, CURRENTQTR, CURRENTYEAR) VALUES (6, 'Spring', 2025);
INSERT INTO CURRENT_SECTION (SECTIONID, CURRENTQTR, CURRENTYEAR) VALUES (4, 'Spring', 2025);
-- INSERT INTO REGISTERED Table
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (29, 5);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (94, 3);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (49, 1);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (96, 1);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (89, 3);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (98, 5);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (51, 1);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (98, 2);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (14, 5);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (62, 5);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (68, 1);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (69, 7);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (88, 1);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (47, 1);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (1, 1);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (43, 7);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (80, 5);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (6, 7);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (55, 4);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (90, 6);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (67, 2);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (68, 2);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (66, 6);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (91, 2);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (18, 3);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (5, 7);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (63, 3);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (63, 5);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (48, 2);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (95, 6);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (93, 6);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (69, 5);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (48, 5);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (2, 6);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (53, 6);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (31, 7);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (6, 5);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (27, 2);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (93, 4);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (46, 3);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (41, 6);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (68, 3);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (33, 3);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (9, 7);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (27, 5);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (45, 1);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (38, 3);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (10, 4);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (35, 7);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (26, 6);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (87, 7);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (5, 6);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (11, 4);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (12, 5);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (59, 5);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (59, 4);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (22, 1);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (49, 7);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (83, 3);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (55, 2);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (37, 2);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (35, 3);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (25, 6);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (80, 3);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (39, 7);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (6, 1);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (91, 5);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (92, 1);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (95, 5);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (18, 6);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (94, 1);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (80, 2);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (89, 2);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (73, 7);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (41, 7);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (32, 3);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (51, 3);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (88, 4);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (46, 7);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (5, 4);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (67, 4);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (41, 5);
INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES (26, 3);
-- INSERT INTO TRANSCRIPT Table
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (87, 7, 'D+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (55, 2, 'D');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (67, 4, 'B');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (45, 1, 'F');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (93, 4, 'B+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (94, 3, 'B');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (83, 3, 'B');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (32, 3, 'C+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (68, 2, 'B+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (49, 7, 'B+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (55, 4, 'F');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (80, 3, 'D+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (93, 6, 'B-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (88, 1, 'A-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (98, 5, 'B-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (18, 3, 'D+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (95, 6, 'F');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (59, 4, 'C+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (91, 2, 'F');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (43, 7, 'B');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (35, 3, 'B+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (62, 5, 'F');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (5, 7, 'C+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (73, 7, 'C');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (9, 7, 'D');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (11, 4, 'A');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (41, 5, 'B-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (68, 1, 'C+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (98, 2, 'C');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (35, 7, 'F');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (25, 6, 'B');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (6, 1, 'A-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (39, 7, 'A-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (53, 6, 'B+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (14, 5, 'C');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (80, 5, 'A-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (69, 5, 'A-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (41, 7, 'B');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (66, 6, 'B+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (33, 3, 'B');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (26, 6, 'D');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (2, 6, 'C-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (47, 1, 'C+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (5, 4, 'C');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (69, 7, 'B');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (51, 1, 'B+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (48, 5, 'D+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (63, 3, 'B');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (31, 7, 'C');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (37, 2, 'B-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (89, 3, 'A-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (5, 6, 'C-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (51, 3, 'C+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (63, 5, 'A');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (12, 5, 'A-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (80, 2, 'A-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (94, 1, 'A-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (27, 5, 'C+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (90, 6, 'D');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (46, 3, 'A');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (68, 3, 'F');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (29, 5, 'C-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (95, 5, 'D+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (41, 6, 'B-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (48, 2, 'B-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (49, 1, 'C-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (6, 5, 'B-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (22, 1, 'A');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (59, 5, 'C-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (88, 4, 'D');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (46, 7, 'B-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (38, 3, 'F');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (6, 7, 'C+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (18, 6, 'C+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (67, 2, 'C+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (92, 1, 'B-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (89, 2, 'A-');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (27, 2, 'B');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (91, 5, 'C');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (96, 1, 'D+');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (10, 4, 'A');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (1, 1, 'A');
INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES (26, 3, 'D');
-- INSERT INTO MAJORMINOR Table
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (99, '4', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (61, '1', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (28, '4', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (91, '3', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (87, '3', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (93, '1', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (59, '3', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (11, '2', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (73, '1', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (70, '1', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (56, '5', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (67, '5', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (27, '1', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (22, '2', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (89, '5', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (54, '2', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (30, '1', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (57, '5', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (83, '1', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (52, '1', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (17, '5', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (44, '1', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (60, '2', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (78, '5', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (88, '4', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (20, '4', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (77, '1', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (78, '2', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (4, '1', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (41, '5', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (16, '2', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (1, '3', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (85, '5', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (71, '4', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (95, '1', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (4, '5', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (14, '3', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (80, '5', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (26, '2', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (44, '3', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (100, '1', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (44, '4', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (39, '5', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (62, '4', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (62, '5', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (73, '4', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (94, '2', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (2, '1', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (7, '4', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (20, '5', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (91, '4', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (9, '3', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (64, '2', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (2, '4', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (28, '5', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (4, '2', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (2, '5', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (46, '5', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (12, '3', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (47, '1', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (71, '5', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (53, '4', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (39, '1', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (43, '2', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (45, '2', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (46, '3', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (30, '1', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (12, '3', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (74, '4', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (68, '5', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (76, '4', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (79, '3', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (1, '4', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (31, '3', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (49, '4', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (25, '2', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (9, '5', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (92, '3', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (7, '2', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (23, '3', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (88, '3', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (90, '5', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (48, '3', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (92, '2', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (41, '5', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (60, '2', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (73, '3', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (38, '4', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (98, '5', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (95, '2', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (81, '4', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (37, '4', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (72, '2', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (70, '5', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (29, '4', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (64, '3', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (96, '5', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (96, '4', 'MAJOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (81, '1', 'MINOR');
INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES (67, '2', 'MAJOR');
-- INSERT INTO BELONGS Table
INSERT INTO BELONGS (FACULTYID, DEPTID) VALUES (86, '1');
INSERT INTO BELONGS (FACULTYID, DEPTID) VALUES (86, '3');
INSERT INTO BELONGS (FACULTYID, DEPTID) VALUES (65, '2');
INSERT INTO BELONGS (FACULTYID, DEPTID) VALUES (8, '2');
INSERT INTO BELONGS (FACULTYID, DEPTID) VALUES (86, '2');
INSERT INTO BELONGS (FACULTYID, DEPTID) VALUES (24, '4');
INSERT INTO BELONGS (FACULTYID, DEPTID) VALUES (50, '3');
INSERT INTO BELONGS (FACULTYID, DEPTID) VALUES (24, '1');
INSERT INTO BELONGS (FACULTYID, DEPTID) VALUES (42, '4');
INSERT INTO BELONGS (FACULTYID, DEPTID) VALUES (82, '5');

DROP USER IF EXISTS 'ASSIGN1PART2'@'LOCALHOST';
CREATE USER 'ASSIGN1PART2'@'LOCALHOST' IDENTIFIED BY 'UNIVERSITY123';
GRANT ALL ON UNIVERSITY.* TO 'ASSIGN1PART2'@'LOCALHOST';
FLUSH PRIVILEGES;

SELECT * FROM information_schema.tables WHERE table_schema = 'university'  ORDER BY create_time ASC;
SELECT * FROM information_schema.triggers WHERE trigger_schema = 'university';
SELECT * FROM information_schema.TABLE_CONSTRAINTS  WHERE table_schema = 'university'  ORDER BY table_name ASC;

SHOW TABLES;