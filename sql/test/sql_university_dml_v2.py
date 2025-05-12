# !pip install faker
# !pip install pymysql
import random
import pymysql
from faker import Faker

fake = Faker()
# Connect to MySQL database
conn = pymysql.connect(
    host='127.0.0.1',
    user='assign1part2',
    password='university123',
    database='university123'
)
cursor = conn.cursor()
num_person = 100

# Generate PERSON records
print("-- INSERT INTO PERSON Table")

# Example: Insert fake students into 'student' table
for _ in range(num_person):  
    fname = fake.first_name()
    minit = fake.random_letter().upper()
    lname = fake.last_name()
    bdate = fake.date_of_birth(minimum_age=18, maximum_age=70).strftime('%Y-%m-%d')  # Convert date to string
    gender = random.choice(['M', 'F'])
    street = fake.street_address()
    apt_no = random.randint(100, 999)
    city = fake.city()
    state = fake.state_abbr()
    zip_code = fake.zipcode()

    sql = """
        INSERT INTO PERSON (Fname, Minit, Lname, Bdate, Gender, Street, Apt_no, City, State, Zip) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (fname, minit, lname, bdate, gender, street, apt_no, city, state, zip_code)

    cursor.execute(sql, values)

# Commit and close connection
conn.commit()
print("✅ Fake data inserted into Person table successfully!")


num_faculty = 10

# Generate PERSON records
print("-- INSERT INTO Faculty Table")

# Filter person_ids to only include values between 1 and 100
# Fetch valid PersonId values from PERSON that are not in FACULTY
cursor.execute("""
    SELECT PersonId FROM PERSON
    WHERE PersonId NOT IN (SELECT FacultyId FROM FACULTY) 
""")
valid_person_ids = [row[0] for row in cursor.fetchall()]

# Generate fake data for Faculty
faculty_data = []
for _ in range(num_faculty):  # Example: generate 5 faculty entries
    person_id = fake.random_element(valid_person_ids)  # Randomly select PersonId in range 1-100
    title = fake.random_element(['Professor', 'Associate Professor', 'Assistant Professor'])
    office = fake.building_number()  # Generate random office number
    phone = fake.phone_number()[:15]  # Generate random phone number
    salary = round(fake.random_int(min=40000, max=200000), 2)  # Random salary in valid range

    faculty_data.append((person_id, title, office, phone, salary))

# Insert generated data into FACULTY table
insert_query = """
    INSERT INTO FACULTY (FacultyId, Title, Foffice, Fphone, Salary)
    VALUES (%s, %s, %s, %s, %s)
"""

cursor.executemany(insert_query, faculty_data)
conn.commit()

print("Data inserted successfully.")

num_student = 90

# Generate PERSON records
print("-- INSERT INTO Student Table")

# Fetch all PersonId values from PERSON table
cursor.execute("SELECT PersonId FROM PERSON")
all_person_ids = [row[0] for row in cursor.fetchall()]

# Fetch all FacultyId values from FACULTY table
cursor.execute("SELECT FacultyId FROM FACULTY")
faculty_ids = [row[0] for row in cursor.fetchall()]

# Filter out PersonIds that are already in FACULTY (those are faculty members)
valid_person_ids = [pid for pid in all_person_ids if pid not in faculty_ids]

# Generate data for Student
student_data = []
for student_id in valid_person_ids:
    class_year = fake.random_int(min=1, max=5)  # Random class (1-5)
    student_data.append((student_id, class_year))

# Insert generated data into STUDENT table
insert_query = """
    INSERT INTO STUDENT (StudentId, Class)
    VALUES (%s, %s)
"""

cursor.executemany(insert_query, student_data)
conn.commit()

print("Data inserted successfully.")

num_grad_student = 15

# Generate PERSON records
print("-- INSERT INTO Grad_Student Table")

# Fetch all StudentIds where Class = 5 (graduating students)
cursor.execute("SELECT StudentId FROM STUDENT WHERE Class = 5")
grad_student_ids = [row[0] for row in cursor.fetchall()]

# Generate data for Grad_Student table
grad_student_data = []
for student_id in grad_student_ids:
    degree = fake.random_element(elements=('M.Sc.', 'Ph.D.', 'MBA'))  # Random degree
    college = fake.company()  # Random college name
    year = fake.random_int(min=2020, max=2024)  # Random year (adjust as needed)

    grad_student_data.append((student_id, degree, college, year))

# Insert generated data into GRAD_STUDENT table
insert_query = """
    INSERT INTO GRAD_STUDENT (Grad_StudentId, Degree, College, Year)
    VALUES (%s, %s, %s, %s)
"""

cursor.executemany(insert_query, grad_student_data)
conn.commit()

print("Data inserted successfully.")

num_grad_student = 15

# Generate PERSON records
print("-- INSERT INTO Committee Table")

# Fetch FacultyIds and Grad_StudentIds
cursor.execute("SELECT FacultyId FROM FACULTY")
faculty_ids = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT Grad_StudentId FROM GRAD_STUDENT")
grad_student_ids = [row[0] for row in cursor.fetchall()]

# Insert data into COMMITTEE table
committee_data = [
    (random.choice(faculty_ids), random.choice(grad_student_ids))
    for _ in range(10)  # Insert 10 random records
]

cursor.executemany("INSERT INTO COMMITTEE (FacultyId, Grad_StudentId) VALUES (%s, %s)", committee_data)
conn.commit()
print("Inserted data into COMMITTEE table.")



num_grant_info = 5

# Generate PERSON records
print("-- INSERT INTO Grant_Info Table")

# Insert data into GRANT_INFO table
grant_data = [
    (
        random.choice(faculty_ids),
        fake.sentence(nb_words=3),  # Random short title
        fake.uuid4()[:8],  # Generate a random unique grant number
        fake.company(),  # Agency name
        fake.date_between(start_date="-5y", end_date="today"),  # Start date within last 5 years
        fake.date_between(start_date="today", end_date="+5y")  # End date within next 5 years
    )
    for _ in range(num_grant_info)  # Insert 5 random grants
]

cursor.executemany(
    "INSERT INTO GRANT_INFO (PI_FacultyId, Title, GrantNumber, Agency, StartDate, EndDate) VALUES (%s, %s, %s, %s, %s, %s)",
    grant_data
)
conn.commit()
print("Inserted data into GRANT_INFO table.")



num_instructor_researcher = 25

# Generate PERSON records
print("-- INSERT INTO INSTRUCTOR_RESEARCHER Table")

# Fetch FacultyIds and Grad_StudentIds
cursor.execute("SELECT FacultyId FROM FACULTY")
faculty_ids = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT Grad_StudentId FROM GRAD_STUDENT")
grad_student_ids = [row[0] for row in cursor.fetchall()]

# Insert data into INSTRUCTOR_RESEARCHER table
instructor_researcher_data = []
for _ in range(num_instructor_researcher):  # Insert 10 random records
    if random.choice([True, False]):  # Randomly assign Faculty or Grad_Student
        faculty_id = random.choice(faculty_ids)
        grad_student_id = None
        category = "Faculty"
    else:
        faculty_id = None
        grad_student_id = random.choice(grad_student_ids)
        category = "Grad_Student"

    instructor_researcher_data.append((faculty_id, grad_student_id, category))

cursor.executemany(
    "INSERT INTO INSTRUCTOR_RESEARCHER (FacultyId, Grad_StudentId, CategoryType) VALUES (%s, %s, %s)",
    instructor_researcher_data
)
conn.commit()
print("Inserted data into INSTRUCTOR_RESEARCHER table.")



### 14. Insert into GRANT_INFO ###
grant_data = [(random.choice(faculty_ids), fake.sentence(), fake.uuid4(), fake.company(), fake.date_this_decade(), fake.date_between(start_date='+1y', end_date='+5y')) for _ in range(10)]
cursor.executemany("INSERT INTO GRANT_INFO (PI_FacultyId, Title, GrantNumber, Agency, StartDate, EndDate) VALUES (%s, %s, %s, %s, %s, %s)", grant_data)
conn.commit()

print("Data inserted successfully.")



cursor.execute("SELECT Instruct_ResearchId FROM INSTRUCTOR_RESEARCHER")
instructor_ids = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT GrantID FROM GRANT_INFO")
grant_ids = [row[0] for row in cursor.fetchall()]

### 15. Insert into SUPPORT ###
support_data = [(random.choice(grant_ids), random.choice(instructor_ids), fake.date_this_year(), fake.date_between(start_date='+1y', end_date='+3y'), fake.time(), fake.time()) for _ in range(10)]
cursor.executemany("INSERT INTO SUPPORT (GrantID, Instruct_ResearchId, Start_Date, End_Date, Start_Time, End_Time) VALUES (%s, %s, %s, %s, %s, %s)", support_data)
conn.commit()

print("Data inserted successfully.")



### 1. Insert into COLLEGE ###
college_data = [(fake.company(), fake.address()[:50], fake.name()) for _ in range(5)]
cursor.executemany("INSERT INTO COLLEGE (CollegeName, CollegeOffice, Dean) VALUES (%s, %s, %s)", college_data)
conn.commit()

print("Data inserted successfully.")



cursor.execute("SELECT CollegeId FROM COLLEGE")
college_ids = [row[0] for row in cursor.fetchall()]

### 2. Insert into DEPARTMENT ###
dept_data = [(random.choice(college_ids), fake.word(), fake.phone_number()[:20], fake.address()[:50]) for _ in range(10)]
cursor.executemany("INSERT INTO DEPARTMENT (CollegeId, DeptName, DeptPhone, DeptOffice) VALUES (%s, %s, %s, %s)", dept_data)
conn.commit()

print("Data inserted successfully.")



cursor.execute("SELECT DeptID FROM DEPARTMENT")
dept_ids = [row[0] for row in cursor.fetchall()]

### 3. Insert into COURSE ###
course_data = [(random.choice(dept_ids), fake.unique.word().upper(), fake.sentence(), fake.paragraph()) for _ in range(20)]
cursor.executemany("INSERT INTO COURSE (DeptID, CNum, CName, CDesc) VALUES (%s, %s, %s, %s)", course_data)
conn.commit()

print("Data inserted successfully.")



cursor.execute("SELECT CourseID FROM COURSE")
course_ids = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT Instruct_ResearchId FROM INSTRUCTOR_RESEARCHER")
instructor_ids = [row[0] for row in cursor.fetchall()]

### 7. Insert into SECTION ###
section_data = [(random.choice(course_ids), random.choice(instructor_ids), fake.random_int(min=1, max=5), fake.random_int(min=2020, max=2025), fake.random_element(elements=['Fall', 'Winter', 'Spring', 'Summer'])) for _ in range(20)]
cursor.executemany("INSERT INTO SECTION (CourseID, Instruct_ResearchId, SecNumber, Year, Qtr) VALUES (%s, %s, %s, %s, %s)", section_data)
conn.commit()

print("Data inserted successfully.")



cursor.execute("SELECT SectionID FROM SECTION")
section_ids = [row[0] for row in cursor.fetchall()]

### 8. Insert into CURRENT_SECTION ###
current_section_data = [(random.choice(section_ids), "Spring", 2024) for _ in range(5)]
cursor.executemany("INSERT INTO CURRENT_SECTION (SectionID, CurrentQtr, CurrentYear) VALUES (%s, %s, %s)", current_section_data)
conn.commit()

print("Data inserted successfully.")



cursor.execute("SELECT StudentID FROM STUDENT")
student_ids = [row[0] for row in cursor.fetchall()]

### 10. Insert into REGISTERED ###
registered_data = [(random.choice(student_ids), random.choice(section_ids)) for _ in range(30)]
cursor.executemany("INSERT INTO REGISTERED (StudentID, SectionID) VALUES (%s, %s)", registered_data)
conn.commit()

### 11. Insert into TRANSCRIPT ###
grades = ['A', 'B', 'C', 'D', 'F', 'P', 'NP']
transcript_data = [(random.choice(student_ids), random.choice(section_ids), random.choice(grades)) for _ in range(30)]
cursor.executemany("INSERT INTO TRANSCRIPT (StudentID, SectionID, Grade) VALUES (%s, %s, %s)", transcript_data)
conn.commit()

### 12. Insert into MAJORMINOR ###
major_minor_data = [(random.choice(student_ids), random.choice(dept_ids), random.choice(['Major', 'Minor'])) for _ in range(20)]
cursor.executemany("INSERT INTO MAJORMINOR (StudentID, DeptId, Category) VALUES (%s, %s, %s)", major_minor_data)
conn.commit()
print("Data inserted successfully.")



cursor.execute("SELECT FacultyId FROM FACULTY")
faculty_ids = [row[0] for row in cursor.fetchall()]

### 13. Insert into BELONGS ###
belongs_data = [(random.choice(faculty_ids), random.choice(dept_ids)) for _ in range(10)]
cursor.executemany("INSERT INTO BELONGS (FacultyId, DeptID) VALUES (%s, %s)", belongs_data)
conn.commit()

print("Data inserted successfully.")

cursor.close()
conn.close()
