import random
import pymysql
from faker import Faker

fake = Faker()

# Connect to the PLANESDB MySQL database
conn = pymysql.connect(
    host='127.0.0.1',
    user='exambonus',
    password='bonus123',
    database='planesdb'
)
cursor = conn.cursor()

#Insert into PERSON
num_person = 50
print("-- INSERT INTO PERSON TABLE")
for _ in range(num_person):
    ssn = fake.ssn()
    per_name = fake.name()
    #truncate address to 50 to fit in varchar(50)
    address = fake.address()[:50]
    #msisdn to fit into int value
    phone = fake.msisdn()
    sql = """
        INSERT INTO PERSON (SSN, PER_NAME, ADDRESS, PHONE) 
        VALUES (%s, %s, %s, %s)
    """
    values = (ssn, per_name, address, phone)
    cursor.execute(sql, values)
conn.commit()

#Insert into CORPORATION
num_corporation = 50
print("-- INSERT INTO CORPORATION TABLE")
for _ in range(num_corporation):
    #char limits for varchar(20)
    cor_name = fake.company()[:20]
    address = fake.address()[:50]
    phone = fake.msisdn()
    sql = """
        INSERT INTO CORPORATION (COR_NAME, ADDRESS, PHONE) 
        VALUES (%s, %s, %s)
    """
    values = (cor_name, address, phone)
    cursor.execute(sql, values)
conn.commit()

#Insert into OWNER
num_owner = 50
print("-- INSERT INTO OWNER_TABLE")
#get existing corporation names and person SSNs
cursor.execute("SELECT COR_NAME FROM CORPORATION")
cor_names = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT SSN FROM PERSON")
person_ssns = [row[0] for row in cursor.fetchall()]

owner_table_data = []
#OWNER_ID will be sequential from 1 to num_owner
for owner_id in range(1, num_owner + 1):
    #randomly decide if the owner is a corporation or a person
    if random.choice([True, False]) and cor_names:
        #for a corporation owner, COR_NAME must be not null and SSN must be null.
        category = "CORPORATION"
        cor_name_val = random.choice(cor_names)
        ssn_val = None
    else:
        category = "PERSON"
        cor_name_val = None
        ssn_val = random.choice(person_ssns)
    
    owner_table_data.append((owner_id, category, cor_name_val, ssn_val))

cursor.executemany(
    "INSERT INTO OWNER_TABLE (OWNER_ID, CATEGORYTYPE, COR_NAME, SSN) VALUES (%s, %s, %s, %s)",
    owner_table_data
)
conn.commit()

#Insert into EMPLOYEE
num_employees = 30
print("-- INSERT INTO EMPLOYEE TABLE")
#make sure unique SSNs by sampling from PERSON records
employee_ssns = random.sample(person_ssns, min(num_employees, len(person_ssns)))
employee_data = []
for ssn in employee_ssns:
    salary = random.randint(30000, 150000)
    shift = random.choice([1, 2, 3])
    employee_data.append((ssn, salary, shift))
    
cursor.executemany(
    "INSERT INTO EMPLOYEE (SSN, SALARY, SHIFT) VALUES (%s, %s, %s)",
    employee_data
)
conn.commit()

#Insert into PILOT
num_pilots = 15
print("-- INSERT INTO PILOT TABLE")
#choose pilot SSNs (they can overlap with employees)
pilot_ssns = random.sample(person_ssns, min(num_pilots, len(person_ssns)))
pilot_data = []
for ssn in pilot_ssns:
    #RESTR is a CHAR; use a flag ('Y' or 'N') to indicate restrictions.
    restr = random.choice(['Y', 'N'])
    lic_num = random.randint(1000, 9999)
    pilot_data.append((ssn, restr, lic_num))
    
cursor.executemany(
    "INSERT INTO PILOT (SSN, RESTR, LIC_NUM) VALUES (%s, %s, %s)",
    pilot_data
)
conn.commit()

#Insert into PLANE_TYPE
num_plane_types = 10
print("-- INSERT INTO PLANE_TYPE TABLE")
plane_type_data = []
for _ in range(num_plane_types):
    #create a unique model string; limit length to 20 chars.
    model = fake.unique.bothify(text='??-###')[:20]
    capacity = random.randint(50, 300)
    weight = random.randint(20000, 200000)
    plane_type_data.append((model, capacity, weight))
    
cursor.executemany(
    "INSERT INTO PLANE_TYPE (MODEL, CAPACITY, WEIGHT) VALUES (%s, %s, %s)",
    plane_type_data
)
conn.commit()

#Insert into HANGAR
num_hangars = 5
print("-- INSERT INTO HANGAR TABLE")
hangar_data = []
for i in range(1, num_hangars + 1):
    hangar_number = i  #use sequential numbers for simplicity.
    capacity = random.randint(1, 50)
    location = fake.city()[:50]
    hangar_data.append((hangar_number, capacity, location))
    
cursor.executemany(
    "INSERT INTO HANGAR (HANGAR_NUMBER, CAPACITY, LOCATION) VALUES (%s, %s, %s)",
    hangar_data
)
conn.commit()

#Insert into AIRPLANE
num_airplanes = 20
print("-- INSERT INTO AIRPLANE TABLE")
#retrieve plane types and hangar numbers
cursor.execute("SELECT MODEL FROM PLANE_TYPE")
models = [row[0] for row in cursor.fetchall()]
cursor.execute("SELECT HANGAR_NUMBER FROM HANGAR")
hangar_numbers = [row[0] for row in cursor.fetchall()]

airplane_data = []
#use sequential REG_NUM values starting at 1000
for reg_num in range(1000, 1000 + num_airplanes):
    model = random.choice(models)
    hangar_number = random.choice(hangar_numbers)
    airplane_data.append((reg_num, model, hangar_number))
    
cursor.executemany(
    "INSERT INTO AIRPLANE (REG_NUM, MODEL, HANGAR_NUMBER) VALUES (%s, %s, %s)",
    airplane_data
)
conn.commit()

#Insert into SERVICE
num_services = 30
print("-- INSERT INTO SERVICE TABLE")
cursor.execute("SELECT REG_NUM FROM AIRPLANE")
reg_nums = [row[0] for row in cursor.fetchall()]
service_data = []
for _ in range(num_services):
    reg_num = random.choice(reg_nums)
    service_date = fake.date_between(start_date="-5y", end_date="today")
    workcode = random.randint(1, 10)
    hours = random.randint(1, 8)
    service_data.append((reg_num, service_date, workcode, hours))
    
cursor.executemany(
    "INSERT INTO SERVICE (REG_NUM, SERVICE_DATE, WORKCODE, HOURS) VALUES (%s, %s, %s, %s)",
    service_data
)
conn.commit()

#Insert into WORKS_ON
num_works_on = 20
print("-- INSERT INTO WORKS_ON TABLE")
cursor.execute("SELECT SSN FROM EMPLOYEE")
employee_ssns = [row[0] for row in cursor.fetchall()]
cursor.execute("SELECT MODEL FROM PLANE_TYPE")
models = [row[0] for row in cursor.fetchall()]

works_on_pairs = set()
works_on_data = []
while len(works_on_data) < num_works_on:
    ssn = random.choice(employee_ssns)
    model = random.choice(models)
    if (ssn, model) not in works_on_pairs:
        works_on_pairs.add((ssn, model))
        works_on_data.append((ssn, model))
        
cursor.executemany(
    "INSERT INTO WORKS_ON (SSN, MODEL) VALUES (%s, %s)",
    works_on_data
)
conn.commit()

#Insert into FLIES
num_flies = 20
print("-- INSERT INTO FLIES TABLE")
cursor.execute("SELECT SSN FROM PILOT")
pilot_ssns = [row[0] for row in cursor.fetchall()]
cursor.execute("SELECT MODEL FROM PLANE_TYPE")
models = [row[0] for row in cursor.fetchall()]

flies_pairs = set()
flies_data = []
while len(flies_data) < num_flies:
    ssn = random.choice(pilot_ssns)
    model = random.choice(models)
    if (ssn, model) not in flies_pairs:
        flies_pairs.add((ssn, model))
        flies_data.append((ssn, model))
        
cursor.executemany(
    "INSERT INTO FLIES (SSN, MODEL) VALUES (%s, %s)",
    flies_data
)
conn.commit()

#Insert into MAINTAIN
num_maintain = 20
print("-- INSERT INTO MAINTAIN TABLE")
cursor.execute("SELECT SSN FROM EMPLOYEE")
employee_ssns = [row[0] for row in cursor.fetchall()]
cursor.execute("SELECT SERVICE_RECORD FROM SERVICE")
service_records = [row[0] for row in cursor.fetchall()]

maintain_pairs = set()
maintain_data = []
while len(maintain_data) < num_maintain:
    ssn = random.choice(employee_ssns)
    service_record = random.choice(service_records)
    if (ssn, service_record) not in maintain_pairs:
        maintain_pairs.add((ssn, service_record))
        maintain_data.append((ssn, service_record))
        
cursor.executemany(
    "INSERT INTO MAINTAIN (SSN, SERVICE_RECORD) VALUES (%s, %s)",
    maintain_data
)
conn.commit()

#Insert into OWNS
num_owns = 20
print("-- INSERT INTO OWNS TABLE")
cursor.execute("SELECT REG_NUM FROM AIRPLANE")
reg_nums = [row[0] for row in cursor.fetchall()]
cursor.execute("SELECT SSN FROM OWNER_TABLE WHERE CATEGORYTYPE = 'PERSON'")
owner_person_ssns = [row[0] for row in cursor.fetchall()]

owns_pairs = set()
owns_data = []
while len(owns_data) < num_owns:
    reg_num = random.choice(reg_nums)
    if owner_person_ssns:
        ssn = random.choice(owner_person_ssns)
    else:
        ssn = None
    if (ssn, reg_num) not in owns_pairs:
        owns_pairs.add((ssn, reg_num))
        pdate = fake.date_between(start_date="-5y", end_date="today")
        owns_data.append((reg_num, ssn, pdate))
        
cursor.executemany(
    "INSERT INTO OWNS (REG_NUM, SSN, PDATE) VALUES (%s, %s, %s)",
    owns_data
)
conn.commit()

cursor.close()
conn.close()

print("Finished Inserting Data")
