import random
import pymysql
import datetime
from faker import Faker
from datetime import timedelta, date

fake = Faker()

conn = pymysql.connect(
    host='127.0.0.1',
    user='xyzcompany',
    password='projectcode',
    database='XYZCOMPANY'
)
cursor = conn.cursor()

num_person = 500
num_employee = 150
num_potential_employee = 100
num_customer = 250
num_department = 10
num_job = 15
num_applicant = 150
num_selected_for_interview = 80
num_interviewer = 15
num_product = 50
num_marketing_site = 15
num_sale = 750
num_vendor = 20
num_part = 75

person_ids = []
employee_ids = []
customer_ids = []
potential_employee_ids = []
department_ids = []
job_ids = []
applicant_ids = []
selected_applicant_ids = []
interviewer_ids = []
product_ids = []
marketing_site_ids = []
sale_ids = []
vendor_ids = []
part_ids = []

def random_date(start_date, end_date):
    days = (end_date - start_date).days
    return start_date + timedelta(days=random.randrange(days))

def generate_birth_date(min_age, max_age):
    today = date.today()
    return random_date(today - timedelta(days=max_age*365),
                       today - timedelta(days=min_age*365))

# 1) PERSON
print("Populating PERSON table...")
for i in range(1, num_person + 1):
    if i == 1:
        pid = 11111        
    else:
        pid = i - 1              
    first  = fake.first_name()
    last   = fake.last_name()
    bd     = generate_birth_date(18, 65)
    gender = random.choice(['M','F'])
    addr1  = fake.street_address()
    addr2  = fake.secondary_address() if random.random()>0.7 else None
    email  = fake.email()
    city   = fake.city()
    state  = fake.state_abbr()
    zipc   = fake.zipcode()
    cursor.execute("""
        INSERT INTO PERSON
          (PERSONAL_ID, FIRST_NAME, LAST_NAME, BIRTH_DATE, GENDER,
           ADDRESS_LINE_1, ADDRESS_LINE_2, EMAIL, CITY, STATE, ZIP_CODE)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (pid, first, last, bd, gender,
          addr1, addr2, email, city, state, zipc))
    person_ids.append(pid)
conn.commit()

cursor.execute("""
    UPDATE PERSON SET FIRST_NAME='Hellen', LAST_NAME='Cole'
    WHERE PERSONAL_ID=%s
""", (person_ids[0],))
conn.commit()

# 2) DEPARTMENT
print("Populating DEPARTMENT table...")
dept_names = ["Marketing","IT","HR","Sales","Finance","Operations",
              "R&D","Legal","Customer Service","Logistics"]
for idx, name in enumerate(dept_names, start=1):
    cursor.execute("INSERT INTO DEPARTMENT (DEPARTMENT_ID, DEPARTMENT_NAME) VALUES (%s,%s)",
                   (idx, name))
    department_ids.append(idx)
conn.commit()

# 3) EMPLOYEE
print("Populating EMPLOYEE table...")
for i in range(num_employee):
    eid = person_ids[i]
    dept = random.choice(department_ids)
    rank = random.choice(["Junior","Mid","Senior","Lead"])
    title = random.choice(["Engineer","Analyst","Manager","Sales Representative"])
    sup = random.choice(employee_ids) if (employee_ids and random.random()>0.3) else None
    cursor.execute("""
        INSERT INTO EMPLOYEE
          (EMPLOYEE_ID, EMPLOYEE_RANK, EMPLOYEE_TITLE, DEPARTMENT_ID, EMPLOYEE_SUPERVISOR)
        VALUES (%s,%s,%s,%s,%s)
    """, (eid, rank, title, dept, sup))
    employee_ids.append(eid)
conn.commit()

# 4) POTENTIAL_EMPLOYEE
print("Populating POTENTIAL_EMPLOYEE table...")
for i in range(num_employee, num_employee+num_potential_employee):
    pid = person_ids[i]
    cursor.execute("INSERT INTO POTENTIAL_EMPLOYEE (POTENTIAL_EMPLOYEE_ID) VALUES (%s)", (pid,))
    potential_employee_ids.append(pid)
conn.commit()

# 5) CUSTOMER
print("Populating CUSTOMER table...")
for i in range(num_employee+num_potential_employee,
               num_employee+num_potential_employee+num_customer):
    pid = person_ids[i]
    cursor.execute("INSERT INTO CUSTOMER (CUSTOMER_ID) VALUES (%s)", (pid,))
    customer_ids.append(pid)
conn.commit()

# 6) SHIFTS & WORKS_AT_DEPARTMENT
print("Populating SHIFT and EMPLOYEE_WORKS_AT_DEPARTMENT...")

for eid in employee_ids:
    for _ in range(random.randint(1,3)):
        start_dt = datetime.datetime(
            random.randint(2009,2011),
            random.randint(1,12),
            random.randint(1,28),
            random.randint(6,9),
            0
        )
        end_dt = start_dt + timedelta(hours=8)
        dept = random.choice(department_ids)
        cursor.execute("""
            INSERT INTO SHIFT
              (EMPLOYEE_ID, DEPARTMENT_ID, SHIFT_START_TIME, SHIFT_END_TIME)
            VALUES (%s,%s,%s,%s)
        """, (eid, dept, start_dt, end_dt))
conn.commit()

emp_all = employee_ids[1]
for dept in department_ids:
    sd = date(2009, 1, 1)
    ed = sd + timedelta(days=30)
    cursor.execute("""
        INSERT INTO EMPLOYEE_WORKS_AT_DEPARTMENT
          (EMPLOYEE_ID, DEPARTMENT_ID, START_DATE, END_DATE)
        VALUES (%s,%s,%s,%s)
    """, (emp_all, dept, sd, ed))
conn.commit()

for eid in employee_ids:
    for _ in range(random.randint(1,2)):
        dept = random.choice(department_ids)
        sd = random_date(date(2009,1,1), date(2011,12,31))
        ed = sd + timedelta(days=random.randint(30,365))
        cursor.execute("""
            INSERT INTO EMPLOYEE_WORKS_AT_DEPARTMENT
              (EMPLOYEE_ID, DEPARTMENT_ID, START_DATE, END_DATE)
            VALUES (%s,%s,%s,%s)
        """, (eid, dept, sd, ed))
conn.commit()


# 7) JOB
print("Populating JOB table...")

fixed_jobs = [11111, 12345]

while len(job_ids) < num_job:
    jid = random.randint(10000, 99999)
    if jid not in fixed_jobs and jid not in job_ids:
        job_ids.append(jid)
job_ids = fixed_jobs + job_ids[:num_job-len(fixed_jobs)]

for jid in job_ids:
    desc = fake.sentence(nb_words=6)

    pd = random_date(date(2009,1,1), date(2011,12,31))

    if jid == 11111:
        pd = random_date(date(2011,1,1), date(2011,1,31))
        dept = department_ids[0] 
    elif jid == 12345:
        dept = random.choice(department_ids)
    else:
        dept = random.choice(department_ids)
    cursor.execute("""
        INSERT INTO JOB (JOB_ID, JOB_DESCRIPTION, POSTED_DATE, DEPARTMENT_POST)
        VALUES (%s,%s,%s,%s)
    """, (jid, desc, pd, dept))
conn.commit()

# 8) APPLICANT & APPLIED
print("Populating APPLICANT and APPLIED...")
cursor.execute("""
    INSERT INTO APPLICANT (APPLICANT_CATEGORY, POTENTIAL_EMPLOYEE_ID)
    VALUES ('POTENTIAL_EMPLOYEE', %s)
""", (potential_employee_ids[0],))
app_hc = cursor.lastrowid
applicant_ids.append(app_hc)
cursor.execute("INSERT INTO APPLIED (JOB_ID, APPLICANT_ID) VALUES (%s,%s)", (11111, app_hc))
conn.commit()

for eid in random.sample(employee_ids, k=5):
    cursor.execute("""
        INSERT INTO APPLICANT (APPLICANT_CATEGORY, EMPLOYEE_ID)
        VALUES ('EMPLOYEE', %s)
    """, (eid,))
    aid = cursor.lastrowid
    applicant_ids.append(aid)
    cursor.execute("INSERT INTO APPLIED (JOB_ID, APPLICANT_ID) VALUES (%s,%s)", (12345, aid))
conn.commit()

for _ in range(num_applicant - len(applicant_ids)):
    if random.random()>0.5:
        eid = random.choice(employee_ids)
        cursor.execute("INSERT INTO APPLICANT (APPLICANT_CATEGORY, EMPLOYEE_ID) VALUES ('EMPLOYEE',%s)", (eid,))
    else:
        pid = random.choice(potential_employee_ids)
        cursor.execute("INSERT INTO APPLICANT (APPLICANT_CATEGORY, POTENTIAL_EMPLOYEE_ID) VALUES ('POTENTIAL_EMPLOYEE',%s)", (pid,))
    aid = cursor.lastrowid
    applicant_ids.append(aid)
    jid = random.choice(job_ids)
    cursor.execute("INSERT INTO APPLIED (JOB_ID, APPLICANT_ID) VALUES (%s,%s)", (jid, aid))
conn.commit()

# 9) SELECTED_FOR_INTERVIEW & INTERVIEWER & INTERVIEW
print("Populating SELECTED_FOR_INTERVIEW and INTERVIEW...")
for aid in random.sample(applicant_ids, k=num_selected_for_interview):

    cursor.execute(
      "INSERT INTO SELECTED_FOR_INTERVIEW (JOB_ID, APPLICANT_ID) VALUES (%s,%s)",
      (random.choice(job_ids), aid)
    )
    sa = cursor.lastrowid
    selected_applicant_ids.append(sa)

    emp = random.choice(employee_ids)
    cursor.execute("INSERT INTO INTERVIEWER (EMPLOYEE_ID) VALUES (%s)", (emp,))
    ir = cursor.lastrowid
    interviewer_ids.append(ir)
    for _ in range(random.randint(1,3)):
        itime = datetime.datetime(
            random.randint(2010,2011),
            random.randint(1,12),
            random.randint(1,28),
            random.randint(9,16), 0
        )
        rnd   = random.randint(1,3)
        grade = random.randint(50,100)
        jid   = random.choice(job_ids)
        cursor.execute("""
            INSERT INTO INTERVIEW
              (CANDIDATE_ID, INTERVIEWER_ID, JOB_POSITION,
               INTERVIEW_TIME, INTERVIEW_ROUND, INTERVIEW_GRADE)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (sa, ir, jid, itime, rnd, grade))

conn.commit()

if selected_applicant_ids and interviewer_ids:
    vip_app = selected_applicant_ids[0]
    vip_int = interviewer_ids[0]
    for rnd in range(1, 6):
        itime = datetime.datetime(2011, 4, rnd+1, 9, 0)
        cursor.execute("""
            INSERT INTO INTERVIEW
              (CANDIDATE_ID, INTERVIEWER_ID, JOB_POSITION,
               INTERVIEW_TIME, INTERVIEW_ROUND, INTERVIEW_GRADE)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (vip_app, vip_int, 11111, itime, rnd, 80))
    conn.commit()

# 10) PRODUCT
print("Populating PRODUCT table...")
for _ in range(num_product):
    pid = len(product_ids) + 1
    ptype = random.choice(["Widget","Gadget","Cup","Tool","Device","Instrument"])
    size = random.choice(["Small","Medium","Large"])
    price = round(random.uniform(50,500),2)
    weight = round(random.uniform(0.5,10.0),2)
    style = fake.word()
    cursor.execute("""
        INSERT INTO PRODUCT (PRODUCT_ID, PRODUCT_TYPE, PRODUCT_SIZE,
                             PRODUCT_LIST_PRICE, PRODUCT_WEIGHT, PRODUCT_STYLE)
        VALUES (%s,%s,%s,%s,%s,%s)
    """, (pid, ptype, size, price, weight, style))
    product_ids.append(pid)
conn.commit()

# 11) MARKETING_SITE
print("Populating MARKETING_SITE...")
for i in range(1, num_marketing_site+1):
    name = f"Site-{i}"
    loc = fake.city()
    cursor.execute("INSERT INTO MARKETING_SITE (SITE_ID,SITE_NAME,SITE_LOCATION) VALUES (%s,%s,%s)",
                   (i, name, loc))
    marketing_site_ids.append(i)
conn.commit()

# 12) EMPLOYEE_WORKS_FOR_SITE & PRODUCT_SOLD_AT_SITE
print("Populating EMPLOYEE_WORKS_FOR_SITE and PRODUCT_SOLD_AT_SITE...")
for eid in employee_ids:
    for site in random.sample(marketing_site_ids, k=random.randint(1,3)):
        cursor.execute("INSERT INTO EMPLOYEE_WORKS_FOR_SITE VALUES (%s,%s)", (eid,site))
for pid in product_ids:
    for site in random.sample(marketing_site_ids, k=random.randint(1,4)):
        cursor.execute("INSERT INTO PRODUCT_SOLD_AT_SITE VALUES (%s,%s)", (pid,site))
conn.commit()

# 13) VENDOR, PART, PART_SUPPLIED_BY_VENDOR, PART_USED_IN_PRODUCT
print("Populating VENDOR, PART, PART_SUPPLIED_BY_VENDOR, PART_USED_IN_PRODUCT...")
for i in range(1, num_vendor+1):
    name = fake.company()
    a1 = fake.street_address()
    a2 = None
    city = fake.city()
    st = fake.state_abbr()
    zipc = fake.zipcode()
    acct = random.randint(1000,9999)
    cr = random.randint(300,850)
    url = fake.url()
    cursor.execute("""
        INSERT INTO VENDOR
          (VENDOR_ID,VENDOR_NAME,VENDOR_ADDRESS_LINE_1,
           VENDOR_ADDRESS_LINE_2,VENDOR_CITY,VENDOR_STATE,
           VENDOR_ZIP_CODE,VENDOR_ACCOUNT_NO,VENDOR_CREDIT_RATING,
           VENDOR_WEBSERVICE_URL)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (i,name,a1,a2,city,st,zipc,acct,cr,url))
    vendor_ids.append(i)
for _ in range(num_part):
    pid = len(part_ids)+1
    ptype = random.choice(["Bolt","Nut","Cup","Gear","Panel","Screw"])
    cursor.execute("INSERT INTO PART (PART_ID, PART_TYPE) VALUES (%s,%s)", (pid,ptype))
    part_ids.append(pid)
conn.commit()

for pid in part_ids:
    vid = random.choice(vendor_ids)
    price = round(random.uniform(1,50),2)
    cursor.execute("INSERT INTO PART_SUPPLIED_BY_VENDOR VALUES (%s,%s,%s)", (vid,pid,price))
for pid in product_ids:
    used = random.randint(1,10)
    part = random.choice(part_ids)
    cursor.execute("INSERT INTO PART_USED_IN_PRODUCT VALUES (%s,%s,%s)", (part,pid,used))
conn.commit()

# ─── 14) SALE & CUSTOMER_BUYS_SALE ─────────────────────────────────────────────
cursor.execute("SELECT EMPLOYEE_ID, SITE_ID FROM EMPLOYEE_WORKS_FOR_SITE")
employee_sites = {}
for emp_id, site_id in cursor.fetchall():
    employee_sites.setdefault(emp_id, set()).add(site_id)

cursor.execute("SELECT PRODUCT_ID, SITE_ID FROM PRODUCT_SOLD_AT_SITE")
product_sites = {}
for prod_id, site_id in cursor.fetchall():
    product_sites.setdefault(prod_id, []).append(site_id)

expensive = []
for pid in product_ids:
    cursor.execute(
        "SELECT PRODUCT_LIST_PRICE FROM PRODUCT WHERE PRODUCT_ID=%s",
        (pid,)
    )
    price = cursor.fetchone()[0]
    if price > 200.0:
        expensive.append(pid)

print("Populating SALE table ...")
for _ in range(num_sale):
    prod = random.choice(product_ids)
    cust = random.choice(customer_ids)
    sold_date = random_date(date(2009,1,1), date(2011,12,31))
    sold_dt   = datetime.datetime.combine(sold_date,
                                          datetime.time(random.randint(8,18), 0))

    valid_pairs = []
    for site in product_sites.get(prod, []):
        for emp, sites in employee_sites.items():
            if site in sites:
                valid_pairs.append((emp, site))

    if not valid_pairs:
        continue

    salesman, site = random.choice(valid_pairs)
    cursor.execute("""
        INSERT INTO SALE
          (SALESMAN_ID, CUSTOMER_ID, PRODUCT_ID, SITE_ID, SALES_TIME)
        VALUES (%s,%s,%s,%s,%s)
    """, (salesman, cust, prod, site, sold_dt))
    sale_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO CUSTOMER_BUYS_SALE (SALE_ID, CUSTOMER_ID) VALUES (%s,%s)",
        (sale_id, cust)
    )

conn.commit()

top_salesman = employee_ids[0]
for prod in expensive:
    valid_sites = [
      s for s in product_sites.get(prod, [])
      if s in employee_sites.get(top_salesman, ())
    ]
    if not valid_sites:
        fallback = product_sites.get(prod, [])[:1]
        if not fallback:
            continue
        site = fallback[0]
        if site not in employee_sites.setdefault(top_salesman, set()):
            cursor.execute("""
                INSERT INTO EMPLOYEE_WORKS_FOR_SITE (EMPLOYEE_ID, SITE_ID)
                VALUES (%s,%s)
            """, (top_salesman, site))
            employee_sites[top_salesman].add(site)
    else:
        site = random.choice(valid_sites)

    sold_dt = datetime.datetime(2011, 3, 1, 10, 0)
    cursor.execute("""
        INSERT INTO SALE
          (SALESMAN_ID, CUSTOMER_ID, PRODUCT_ID, SITE_ID, SALES_TIME)
        VALUES (%s,%s,%s,%s,%s)
    """, (top_salesman, random.choice(customer_ids), prod, site, sold_dt))
    sale_id = cursor.lastrowid
    cursor.execute(
       "INSERT INTO CUSTOMER_BUYS_SALE (SALE_ID, CUSTOMER_ID) VALUES (%s,%s)",
       (sale_id, random.choice(customer_ids))
    )
conn.commit()


# 15) SALARY
print("Populating SALARY table...")
for eid in employee_ids:
    for txn in range(1, random.randint(2,6)):
        payd = random_date(date(2009,1,1), date(2011,12,31))
        amt = round(random.uniform(3000,10000),2)
        cursor.execute("""
            INSERT INTO SALARY (EMPLOYEE_ID,TRANSACTION_NO,PAY_DATE,PAY_AMOUNT)
            VALUES (%s,%s,%s,%s)
        """, (eid, txn, payd, amt))
conn.commit()

print("Populating PERSON_PHONE_NO table...")
for pid in person_ids:
    for _ in range(random.randint(1, 3)):
        phone_no = random.randint(1000000000, 1999999999)
        cursor.execute("""
            INSERT INTO PERSON_PHONE_NO (PERSONAL_ID, PHONE_NO)
            VALUES (%s, %s)
        """, (pid, phone_no))
conn.commit()

cursor.execute("""
    INSERT IGNORE INTO POTENTIAL_EMPLOYEE (POTENTIAL_EMPLOYEE_ID)
    VALUES (%s)
""", (11111,))

cursor.execute("""
    INSERT INTO APPLICANT (APPLICANT_CATEGORY, POTENTIAL_EMPLOYEE_ID)
    VALUES ('POTENTIAL_EMPLOYEE', 11111)
""")
new_aid = cursor.lastrowid

cursor.execute(
    "INSERT INTO APPLIED (JOB_ID, APPLICANT_ID) VALUES (11111, %s)",
    (new_aid,)
)

cursor.execute("""
    INSERT INTO SELECTED_FOR_INTERVIEW (JOB_ID, APPLICANT_ID)
    VALUES (11111, %s)
""", (new_aid,))
sel_app_id = cursor.lastrowid

top_emp = random.choice(employee_ids)
cursor.execute("INSERT INTO INTERVIEWER (EMPLOYEE_ID) VALUES (%s)", (top_emp,))
intv_id = cursor.lastrowid

for rnd in range(1, 6):
    cursor.execute("""
        INSERT INTO INTERVIEW
          (CANDIDATE_ID, INTERVIEWER_ID, JOB_POSITION,
           INTERVIEW_TIME, INTERVIEW_ROUND, INTERVIEW_GRADE)
        VALUES (%s, %s, 11111, NOW(), %s, 80)
    """, (sel_app_id, intv_id, rnd))

conn.commit()


print("Done populating all tables.")
conn.close()
