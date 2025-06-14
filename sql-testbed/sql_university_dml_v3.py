import random
from faker import Faker

fake = Faker()

# Number of records to generate
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
num_section = 5
num_current_section = 7
num_transcript = 50
num_registered = 90
num_majorminor = 105
num_belongs = 10

# Track generated IDs
person_ids = list(range(1, num_person + 1))
faculty_ids = random.sample(person_ids, num_faculty)
student_ids = list(set(person_ids) - set(faculty_ids))[:num_student]
grad_student_ids = random.sample(student_ids, num_grad_student)

# Predefined College & Department Names
college_names = ["Engineering", "Science", "Business"]
department_names = ["Computer Science", "Mathematics", "Physics", "Biology", "Finance"]

# Course and Section IDs
course_ids = list(range(1, num_course + 1))
section_ids = list(range(1, num_section + 1))
current_section_ids = list(range(1, num_current_section + 1))

# Insert PERSON records
print("-- INSERT INTO PERSON Table")
for personid in person_ids:
    fname = fake.first_name()
    minit = fake.random_letter().upper()
    lname = fake.last_name()
    bdate = fake.date_of_birth(minimum_age=18, maximum_age=70).strftime('%Y-%m-%d')
    sex = random.choice(['M', 'F'])
    street = fake.street_address()
    aptno = random.randint(100, 999)
    city = fake.city()
    state = fake.state_abbr()
    zip_code = fake.zipcode()

    print(f"INSERT INTO PERSON (PERSONID, FNAME, MINIT, LNAME, BDATE, SEX, STREET, APTNO, CITY, STATE, ZIP) "
          f"VALUES ({personid}, '{fname}', '{minit}', '{lname}', '{bdate}', '{sex}', '{street}', '{aptno}', '{city}', '{state}', '{zip_code}');")

# Insert FACULTY records
print("-- INSERT INTO FACULTY Table")
for faculty_id in faculty_ids:
    faculty_rank = random.choice(["Assistant Professor", "Associate Professor", "Professor"])
    faculty_office = fake.building_number()
    faculty_phone = fake.phone_number()
    salary = random.randint(50000, 300000)

    print(f"INSERT INTO FACULTY (FACULTYID, FACULTYRANK, FOFFICE, FPHONE, SALARY) "
          f"VALUES ({faculty_id}, '{faculty_rank}', '{faculty_office}', '{faculty_phone}', {salary});")

# Insert COLLEGE records
print("-- INSERT INTO COLLEGE Table")
for i in range(num_college):
    cname = college_names[i % len(college_names)]
    dean = fake.name()
    office = fake.building_number()

    print(f"INSERT INTO COLLEGE (CNAME, DEAN, COFFICE) "
          f"VALUES ('{cname}', '{dean}', '{office}');")

# Insert DEPARTMENT records
print("-- INSERT INTO DEPARTMENT Table")
for i in range(num_department):
    dname = department_names[i % len(department_names)]
    dphone = fake.phone_number()
    doffice = fake.building_number()
    chair = random.choice(faculty_ids)
    college = random.choice(college_names)

    print(f"INSERT INTO DEPARTMENT (DNAME, DPHONE, DOFFICE, CHAIR, COLLEGENAME) "
          f"VALUES ('{dname}', '{dphone}', '{doffice}', {chair}, '{college}');")

# Insert STUDENT records
print("-- INSERT INTO STUDENT Table")
for student_id in student_ids:
    student_class = random.randint(1, 4)
    major = random.choice(department_names)
    minor = random.choice(department_names) if random.random() > 0.5 else None

    print(f"INSERT INTO STUDENT (STUDENTID, CLASS, MAJOR, MINOR) "
          f"VALUES ({student_id}, {student_class}, '{major}', {f'NULL' if minor is None else f"'{minor}'"});")

# Insert GRADSTUDENT records
print("-- INSERT INTO GRADSTUDENT Table")
for grad_student_id in grad_student_ids:
    student_class = random.randint(1, 4)
    fac_advisor = random.choice(faculty_ids)

    print(f"INSERT INTO GRADSTUDENT (GRADSTUDENTID, CLASS, FAC_ADVISOR) "
          f"VALUES ({grad_student_id}, {student_class}, {fac_advisor});")

# Insert COMMITTEE records
print("-- INSERT INTO COMMITTEE Table")

# Use a set to track assigned (faculty, grad student) pairs
existing_pairs = set()

for _ in range(num_committee):
    while True:
        fac_id = random.choice(faculty_ids)
        gs_id = random.choice(grad_student_ids)

        # Check if this pair is already assigned
        if (fac_id, gs_id) not in existing_pairs:
            existing_pairs.add((fac_id, gs_id))
            break  # Valid unique pair found

    print(f"INSERT INTO COMMITTEE (COM_FAC_ID, COM_GS_ID) VALUES ({fac_id}, {gs_id});")


# Insert RESEARCH GRANTS
print("-- INSERT INTO RESEARCHGRANT Table")
for grant_no in range(1, num_grant_info + 1):
    title = fake.word()
    agency = fake.company()
    startdate = fake.date_between(start_date='-5y', end_date='today')
    fac_id = random.choice(faculty_ids)

    print(f"INSERT INTO RESEARCHGRANT (GRANTNO, TITLE, AGENCY, STARTDATE, FAC_GRANT_ID) "
          f"VALUES ({grant_no}, '{title}', '{agency}', '{startdate}', {fac_id});")

# Track assigned faculty and grad students
assigned_faculty = set()
assigned_grad_students = set()

print("-- INSERT INTO INSTRUCTORRESEARCHER Table")
for ir_id in range(1, num_instructor_researcher + 1):
    if random.random() > 0.5 and len(assigned_grad_students) < len(grad_student_ids):  
        # Assign a grad student if available
        available_grad_students = list(set(grad_student_ids) - assigned_grad_students)
        if available_grad_students:
            ir_gs_id = random.choice(available_grad_students)
            assigned_grad_students.add(ir_gs_id)
            ir_fac_id = "NULL"
    else:
        # Assign a faculty member if available
        available_faculty = list(set(faculty_ids) - assigned_faculty)
        if available_faculty:
            ir_fac_id = random.choice(available_faculty)
            assigned_faculty.add(ir_fac_id)
            ir_gs_id = "NULL"
        else:
            continue  # Skip iteration if no faculty left

    print(f"INSERT INTO INSTRUCTORRESEARCHER (INSTRUCTRESEARCH_ID, IR_GRADSTUDENT_ID, IR_FAC_ID) "
          f"VALUES ({ir_id}, {ir_gs_id}, {ir_fac_id});")


# Insert SUPPORT records
# Get valid instructor-researcher IDs from the database
existing_ir_ids = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 23, 24, 25}  # Replace with actual DB query result

print("-- INSERT INTO SUPPORT Table")

existing_support_pairs = set()

for _ in range(num_support):
    while True:
        support_grant_no = random.randint(1, num_grant_info)
        support_ir_id = random.choice(list(existing_ir_ids))  # Pick only valid IDs

        if (support_grant_no, support_ir_id) not in existing_support_pairs:
            existing_support_pairs.add((support_grant_no, support_ir_id))
            break  # Unique valid pair found

    start_date = fake.date_between(start_date='-2y', end_date='today')
    time_period = random.randint(6, 24)
    end_date = fake.date_between(start_date=start_date, end_date='+2y')

    print(f"INSERT INTO SUPPORT (SUPPORT_GRANT_NO, SUPPORT_INSTRUCTRESEARCH_ID, STARTDATE, TIMEPERIOD, ENDDATE) "
          f"VALUES ({support_grant_no}, {support_ir_id}, '{start_date}', {time_period}, '{end_date}');")

# Insert MAJOR_MINOR records
print("-- INSERT INTO MAJOR_MINOR Table")

for student_id in student_ids:
    major = random.choice(department_names)

    # Ensure minor is different from major
    available_minors = [dept for dept in department_names if dept != major]
    minor = random.choice(available_minors) if available_minors and random.random() > 0.5 else None

    # Insert major
    print(f"INSERT INTO MAJOR_MINOR (MAJOR_MINOR_FLAG, MM_STU_ID, MM_DEPT_NAME) "
          f"VALUES (1, {student_id}, '{major}');")

    # Insert minor if available
    if minor:
        print(f"INSERT INTO MAJOR_MINOR (MAJOR_MINOR_FLAG, MM_STU_ID, MM_DEPT_NAME) "
              f"VALUES (0, {student_id}, '{minor}');")


# Insert FAC_BELONGS_DEP records
print("-- INSERT INTO FAC_BELONGS_DEP Table")
for faculty_id in faculty_ids:
    department = random.choice(department_names)
    print(f"INSERT INTO FAC_BELONGS_DEP (BELONGS_FAC_ID, BELONGS_DEP_DNAME) "
          f"VALUES ({faculty_id}, '{department}');")

# Insert COURSE records
print("-- INSERT INTO COURSE Table")
for course_no in course_ids:
    cname = fake.word()
    cdesc = fake.sentence(nb_words=6)
    dept = random.choice(department_names)
    print(f"INSERT INTO COURSE (COURSENO, CNAME, CDESC, DEPTNAME) "
          f"VALUES ({course_no}, '{cname}', '{cdesc}', '{dept}');")

# Insert SECTION records
# Use only valid instructor IDs based on the database query
existing_instructor_ids = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 23, 24, 25}

for section_no in section_ids:
    year = random.randint(2020, 2025)
    quarter = random.randint(1, 4)
    course_no = random.choice(course_ids)

    if existing_instructor_ids:
        teacher = random.choice(list(existing_instructor_ids))
    else:
        continue  # Skip if no valid instructors

    print(f"INSERT INTO SECTION (SECTIONNO, SECTIONYEAR, SECQTR, COURSENUM, TEACHER) "
          f"VALUES ({section_no}, {year}, {quarter}, {course_no}, {teacher});")




# Insert CURRENTSECTION records
# Get valid SECTIONNOs from the database
existing_section_ids = {1, 2, 3, 4, 5}  # Replace with actual query results

print("-- INSERT INTO CURRENTSECTION Table")
for section_no in current_section_ids:
    if section_no not in existing_section_ids:
        continue  # Skip if SECTIONNO does not exist in SECTION

    cur_year = 2025
    cur_qtr = random.randint(1, 4)
    print(f"INSERT INTO CURRENTSECTION (CUR_YR, CUR_QTR, CUR_SECTIONNO) "
          f"VALUES ({cur_year}, {cur_qtr}, {section_no});")
    current_section_ids = existing_section_ids


# Insert REGISTERED records
print("-- INSERT INTO REGISTERED Table")

valid_cur_section_ids = set(existing_section_ids)  # Ensure only valid section numbers are chosen

for student_id in student_ids:
    if valid_cur_section_ids:  # Ensure valid sections exist
        cur_sec_no = random.choice(list(valid_cur_section_ids))
        print(f"INSERT INTO REGISTERED (STU_ID, CUR_SECNO) VALUES ({student_id}, {cur_sec_no});")


# Insert TRANSCRIPT records
print("-- INSERT INTO TRANSCRIPT Table")
for _ in range(num_transcript):
    student_id = random.choice(student_ids)
    sec_no = random.choice(section_ids)
    grade = random.randint(60, 100)
    print(f"INSERT INTO TRANSCRIPT (STU_ID, SEC_NO, GRADE) VALUES ({student_id}, {sec_no}, {grade});")