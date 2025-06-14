import random
from faker import Faker
from datetime import datetime

fake = Faker()

num_person = 100
num_faculty = 10
num_student = 90
num_grad_student = 15
num_committee = 5
num_grant_info = 3
num_instructor_researcher = 25
num_support = 5
num_college = 3
num_department = 5
num_course = 7
num_section = 7
num_current_section = 7
num_transcript = 90
num_registered = 90
num_majorminor = 105
num_belongs = 10

person_ids = list(range(1, num_person + 1))  
random.shuffle(person_ids)  
print("-- INSERT INTO PERSON Table")
for personid in range(num_person):
    fname = fake.first_name()
    minit = fake.random_letter().upper()
    lname = fake.last_name()
    bdate = fake.date_of_birth(minimum_age=18, maximum_age=70)
    gender = random.choice(['M', 'F'])
    street = fake.street_address()
    apt_no = random.randint(100, 999)
    city = fake.city()
    state = fake.state_abbr()
    zip_code = fake.zipcode()
    
    print(f"INSERT INTO PERSON (Fname, Minit, Lname, Bdate, gender, Street, Apt_no, City, State, Zip) "
          f"VALUES ('{fname}', '{minit}', '{lname}', '{bdate}', '{gender}', '{street}', '{apt_no}', '{city}', '{state}', '{zip_code}');")
    

faculty_ids = set(random.sample(person_ids, num_faculty))  
remaining_ids = list(set(person_ids) - faculty_ids)  
student_ids = set(random.sample(remaining_ids, num_student))  

# Generate FACULTY records
print("-- INSERT INTO FACULTY Table")
for facultyid in faculty_ids:
    title = random.choice(['PROFESSOR', 'ASSOCIATE PROFESSOR', 'ASSISTANT PROFESSOR'])
    foffice = f"Room {random.randint(100, 999)}"
    fphone = fake.unique.phone_number()
    salary = round(random.uniform(40000, 200000), 2)
    
    print(f"INSERT INTO FACULTY (FACULTYID, TITLE, FOFFICE, FPHONE, SALARY) "
          f"VALUES ({facultyid}, '{title}', '{foffice}', '{fphone}', {salary});")

# Generate STUDENT records
print("-- INSERT INTO STUDENT Table")
student_classes = {}

for studentid in student_ids:
    student_class = random.randint(1, 5)  
    student_classes[studentid] = student_class 

    print(f"INSERT INTO STUDENT (STUDENTID, CLASS) "
          f"VALUES ({studentid}, {student_class});")

# Generate GRAD_STUDENT records (Only students from CLASS = 5)
print("-- INSERT INTO GRAD_STUDENT Table")
grad_student_candidates = [sid for sid in student_classes if student_classes[sid] == 5]

grad_student_ids = random.sample(grad_student_candidates, min(num_grad_student, len(grad_student_candidates)))

for grad_student_id in grad_student_ids:
    degree = random.choice(['M.SC.', 'PH.D.', 'MBA'])
    college = random.choice(['Engineering College', 'Science College', 'Business College'])
    year = random.randint(2024, 2027)  


    print(f"INSERT INTO GRAD_STUDENT (GRAD_STUDENTID, DEGREE, COLLEGE, YEAR) "
          f"VALUES ({grad_student_id}, '{degree}', '{college}', {year});")

# Generate COMMITTEE records
print("-- INSERT INTO COMMITTEE Table")
committee_records = set()

faculty_list = list(faculty_ids)  
grad_student_list = list(grad_student_ids)  

while len(committee_records) < num_committee:
    faculty_id = random.choice(faculty_list)  
    grad_student_id = random.choice(grad_student_list) 
    

    if (faculty_id, grad_student_id) not in committee_records:
        committee_records.add((faculty_id, grad_student_id))
        print(f"INSERT INTO COMMITTEE (FACULTYID, GRAD_STUDENTID) "
              f"VALUES ({faculty_id}, {grad_student_id});")

        
# Generate GRANT_INFO records
print("-- INSERT INTO GRANT_INFO Table")
grant_agencies = ['NSF', 'NIH', 'DOE', 'DARPA', 'NASA']
grant_records = set()


faculty_list = list(faculty_ids)

grant_ids = list(range(1, num_grant_info + 1))  

for grant_id in grant_ids:
    pi_faculty_id = random.choice(faculty_list)  
    title = fake.sentence(nb_words=6).replace("'", "''")  
    grant_number = fake.unique.uuid4()[:13] 
    agency = random.choice(grant_agencies)
    start_date = fake.date_between(start_date='-5y', end_date='today') 
    end_date = fake.date_between(start_date=start_date, end_date='+5y') 

    print(f"INSERT INTO GRANT_INFO (PI_FACULTYID, TITLE, GRANTNUMBER, AGENCY, STARTDATE, ENDDATE) "
          f"VALUES ({pi_faculty_id}, '{title}', '{grant_number}', '{agency}', '{start_date}', '{end_date}');")


total_instructors = faculty_list + list(grad_student_ids)  
num_instructor_researcher = min(num_instructor_researcher, len(total_instructors))  
instructor_researcher_ids = random.sample(total_instructors, num_instructor_researcher)



# Generate `INSTRUCTOR_RESEARCHER` records
print("-- INSERT INTO INSTRUCTOR_RESEARCHER Table")
for instruct_research_id in instructor_researcher_ids:
    if instruct_research_id in faculty_list:

        print(f"INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, FACULTYID) "
              f"VALUES ({instruct_research_id}, 'FACULTY', {instruct_research_id});")
    else:

        print(f"INSERT INTO INSTRUCTOR_RESEARCHER (INSTRUCT_RESEARCHID, CATEGORYTYPE, GRAD_STUDENTID) "
              f"VALUES ({instruct_research_id}, 'GRAD_STUDENT', {instruct_research_id});")
    
# Generate SUPPORT records
print("-- INSERT INTO SUPPORT Table")
support_records = set()

while len(support_records) < num_support:
    grant_id = random.choice(grant_ids)
    instruct_research_id = random.choice(instructor_researcher_ids)
    

    if (grant_id, instruct_research_id) not in support_records:
        support_records.add((grant_id, instruct_research_id))
        start_date = fake.date_between(start_date='-3y', end_date='today')
        end_date = fake.date_between(start_date=start_date, end_date='+3y')
        start_time = fake.time()
        end_time = fake.time()
        
        print(f"INSERT INTO SUPPORT (GRANTID, INSTRUCT_RESEARCHID, START_DATE, END_DATE, START_TIME, END_TIME) "
              f"VALUES ({grant_id}, {instruct_research_id}, '{start_date}', '{end_date}', '{start_time}', '{end_time}');")

# Generate COLLEGE records
print("-- INSERT INTO COLLEGE Table")

college_names = [
    "College of Engineering",
    "College of Science",
    "College of Business",
    "College of Arts & Humanities",
    "College of Medicine"
]


selected_colleges = random.sample(college_names, num_college)

for college_id, college_name in enumerate(selected_colleges, start=1):
    college_office = f"Office {random.randint(100, 500)}"
    dean_name = f"{fake.first_name()} {fake.last_name()}"
    
    print(f"INSERT INTO COLLEGE (COLLEGEID, COLLEGENAME, COLLEGEOFFICE, DEAN) "
          f"VALUES ({college_id}, '{college_name}', '{college_office}', '{dean_name}');")

# Generate DEPARTMENT records
print("-- INSERT INTO DEPARTMENT Table")

department_names = [
    "Computer Science",
    "Mathematics",
    "Mechanical Engineering",
    "Business Administration",
    "Biology"
]


selected_departments = random.sample(department_names, num_department)


college_ids = list(range(1, num_college + 1))

for dept_id, dept_name in enumerate(selected_departments, start=1):
    college_id = random.choice(college_ids)  
    dept_phone = fake.unique.phone_number()
    dept_office = f"Office {random.randint(100, 500)}"
    
    print(f"INSERT INTO DEPARTMENT (COLLEGEID, DEPTNAME, DEPTPHONE, DEPTOFFICE) "
          f"VALUES ({college_id}, '{dept_name}', '{dept_phone}', '{dept_office}');")

# Generate COURSE records
print("-- INSERT INTO COURSE Table")

course_names = [
    ("CS101", "Introduction to Computer Science"),
    ("MATH201", "Calculus I"),
    ("ME301", "Thermodynamics"),
    ("BUS102", "Principles of Management"),
    ("BIO202", "Genetics"),
    ("CS202", "Data Structures"),
    ("MATH305", "Linear Algebra")
]


department_ids = list(range(1, num_department + 1))

course_ids = []  

for course_id, (cnum, cname) in enumerate(course_names, start=1):
    dept_id = random.choice(department_ids)  
    cdesc = fake.paragraph(nb_sentences=3).replace("'", "''")  
    
    print(f"INSERT INTO COURSE (COURSEID, DEPTID, CNUM, CNAME, CDESC) "
          f"VALUES ({course_id}, {dept_id}, '{cnum}', '{cname}', '{cdesc}');")

    course_ids.append(course_id)  


# Generate SECTION records (Only if num_section > 0)
print("-- INSERT INTO SECTION Table")
existing_section_ids = []  

if num_section > 0:
    for section_id in range(1, num_section + 1):
        course_id = random.choice(course_ids) 
        instruct_research_id = random.choice(instructor_researcher_ids)  
        sec_number = random.randint(1, 5)  
        year = random.randint(2020, 2025)  
        qtr = random.choice(["Fall", "Winter", "Spring", "Summer"])

        print(f"INSERT INTO SECTION (SECTIONID, COURSEID, INSTRUCT_RESEARCHID, SECNUMBER, YEAR, QTR) "
              f"VALUES ({section_id}, {course_id}, {instruct_research_id}, {sec_number}, {year}, '{qtr}');")
        existing_section_ids.append(section_id)

# Generate CURRENT_SECTION records (Only if there are existing sections)
if existing_section_ids:
    print("-- INSERT INTO CURRENT_SECTION Table")
    current_year = datetime.now().year
    current_quarter = random.choice(["Winter", "Spring", "Summer", "Fall"])  

    num_current_section = min(len(existing_section_ids), num_current_section)

    selected_sections = random.sample(existing_section_ids, num_current_section) if existing_section_ids else []

    for section_id in selected_sections:
        print(f"INSERT INTO CURRENT_SECTION (SECTIONID, CURRENTQTR, CURRENTYEAR) "
              f"VALUES ({section_id}, '{current_quarter}', {current_year});")


student_list = list(student_ids)


registered_students = set()

# Generate REGISTERED records
print("-- INSERT INTO REGISTERED Table")
for _ in range(num_registered):
    student_id = random.choice(student_list)  
    section_id = random.choice(existing_section_ids)
    

    if (student_id, section_id) not in registered_students:
        registered_students.add((student_id, section_id))
        print(f"INSERT INTO REGISTERED (STUDENTID, SECTIONID) VALUES ({student_id}, {section_id});")


grades = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'F']

# Generate TRANSCRIPT records (only for registered students)
print("-- INSERT INTO TRANSCRIPT Table")
for student_id, section_id in registered_students:
    grade = random.choice(grades) 
    print(f"INSERT INTO TRANSCRIPT (STUDENTID, SECTIONID, GRADE) VALUES ({student_id}, {section_id}, '{grade}');")



student_list = list(student_ids)


student_majors_minors = set()

# Generate MAJORMINOR records
print("-- INSERT INTO MAJORMINOR Table")
for _ in range(num_majorminor):
    student_id = random.choice(student_list) 
    dept_id = random.choice(department_ids)
    category = random.choice(['MAJOR', 'MINOR'])
    

    if (student_id, dept_id, category) not in student_majors_minors:
        student_majors_minors.add((student_id, dept_id, category))
        print(f"INSERT INTO MAJORMINOR (STUDENTID, DEPTID, CATEGORY) VALUES ({student_id}, '{dept_id}', '{category}');")


faculty_departments = set()

faculty_list = list(faculty_ids)

# Generate BELONGS records
print("-- INSERT INTO BELONGS Table")
for _ in range(num_belongs):
    faculty_id = random.choice(faculty_list)  
    dept_id = random.choice(department_ids)
    

    if (faculty_id, dept_id) not in faculty_departments:
        faculty_departments.add((faculty_id, dept_id))
        print(f"INSERT INTO BELONGS (FACULTYID, DEPTID) VALUES ({faculty_id}, '{dept_id}');")
