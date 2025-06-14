import random
import pymysql
from faker import Faker

fake = Faker()

conn = pymysql.connect(
    host='127.0.0.1',
    user='exambonus',
    password='bonus123',
    database='planesdb'
)
cursor = conn.cursor()
num_person = 50
num_corporation = 50
print("-- INSERT INTO PERSON TABLE")
for _ in range(num_person):  
    ssn = fake.ssn()
    per_name = fake.name()
    address = fake.address()
    phone = fake.msisdn()
    sql = """
        INSERT INTO PERSON (SSN, PER_NAME, ADDRESS, PHONE) 
        VALUES (%s, %s, %s, %s)
    """
    values = (ssn, per_name, address, phone)

    cursor.execute(sql, values)

conn.commit()

print("-- INSERT INTO CORPORATION TABLE")
for _ in range(num_corporation):  
    cor_name = fake.company()
    address = fake.address()
    phone = fake.msisdn()
    sql = """
        INSERT INTO PERSON (COR_NAME, ADDRESS, PHONE) 
        VALUES (%s, %s, %s)
    """
    values = (cor_name, address, phone)

    cursor.execute(sql, values)

conn.commit()

num_owner = 50

print("-- INSERT INTO OWNER_TABLE TABLE")

cursor.execute("SELECT COR_NAME FROM CORPORATION")
cor_names = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT SSN FROM PERSON")
ssns = [row[0] for row in cursor.fetchall()]

owner_table_data = []
for _ in range(num_owner): 
    if random.choice([True, False]):  
        cor_name = random.choice(cor_names)
        ssn = None
        category = "CORPORATION"
    else:
        cor_name = None
        ssn = random.choice(ssns)
        category = "PERSON"

    owner_table_data.append((category, cor_name, ssn))

cursor.executemany(
    "INSERT INTO OWNER_TABLE (CATEGORYTYPE, COR_NAME, SSN) VALUES (%s, %s, %s)",
    owner_table_data
)
conn.commit()

print("-- INSERT INTO EMPLOYEE Table")

cursor.execute("SELECT SSN FROM PERSON")
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