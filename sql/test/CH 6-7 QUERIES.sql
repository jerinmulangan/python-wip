## CHapter 6 - Basic SQL 
use company;
SELECT Fname, Lname, Address
  FROM EMPLOYEE, DEPARTMENT
 WHERE Dname = 'Research' AND Dnumber = Dno;
 
SELECT Pnumber, Dnum, Lname, Address, Bdate
  FROM PROJECT, DEPARTMENT, EMPLOYEE
 WHERE Dnum = Dnumber AND Mgr_ssn = Ssn AND Plocation = 'Stafford';
 
SELECT E.Fname, E.Lname, S.Fname, S.Lname
  FROM EMPLOYEE AS E, EMPLOYEE AS S
 WHERE E.Super_ssn = S.Ssn;
 
( SELECT DISTINCT Pnumber
FROM PROJECT, DEPARTMENT, EMPLOYEE
WHERE Dnum = Dnumber AND Mgr_ssn = Ssn
AND Lname = 'Smith' )
UNION
( SELECT DISTINCT Pnumber
FROM PROJECT, WORKS_ON, EMPLOYEE
WHERE Pnumber = Pno AND Essn = Ssn
AND Lname = 'Smith' );

SELECT Fname, Lname
  FROM EMPLOYEE
 WHERE Address LIKE '%Houston%';
 
SELECT Fname, Lname
  FROM EMPLOYEE
WHERE Bdate LIKE '__7%';

 
SELECT E.Fname, E.Lname, E.Salary AS Salary, 1.1 * E.Salary AS Increased_sal
  FROM EMPLOYEE AS E, WORKS_ON AS W, PROJECT AS P
 WHERE E.Ssn = W.Essn AND W.Pno = P.Pnumber AND P.Pname = 'ProductX';
 
SELECT *
  FROM EMPLOYEE
 WHERE (Salary BETWEEN 30000 AND 40000) AND Dno = 5;
 
SELECT D.Dname, E.Lname, E.Fname, P.Pname
  FROM DEPARTMENT AS D, EMPLOYEE AS E, WORKS_ON AS W, PROJECT AS P
 WHERE D.Dnumber = E.Dno AND E.Ssn = W.Essn AND W.Pno = P.Pnumber
ORDER BY D.Dname, E.Lname, E.Fname asc;

## Chapter 7
SELECT Fname, Lname
  FROM EMPLOYEE
 WHERE Super_ssn IS NULL;
 
SELECT DISTINCT Pnumber
  FROM PROJECT
 WHERE Pnumber IN (SELECT Pnumber
                     FROM PROJECT, DEPARTMENT, EMPLOYEE
                    WHERE Dnum = Dnumber AND Mgr_ssn = Ssn AND Lname = 'Smith' )
	OR
	   Pnumber IN ( SELECT Pno 
                      FROM WORKS_ON, EMPLOYEE 
					 WHERE Essn = Ssn AND Lname = 'Smith' );

SELECT DISTINCT Essn
  FROM WORKS_ON
 WHERE (Pno, Hours) IN ( SELECT Pno, Hours
                           FROM WORKS_ON
                          WHERE Essn = '123456789' );
                          
SELECT Lname, Fname
  FROM EMPLOYEE
 WHERE Salary > All ( SELECT Salary 
					    FROM EMPLOYEE
                       WHERE Dno = 5 );
   
SELECT E.Fname, E.Lname
  FROM EMPLOYEE AS E, DEPENDENT AS D
 WHERE E.Ssn = D.Essn AND E.Sex = D.Sex
   AND E.Fname = D.Dependent_name;

SELECT E.Fname, E.Lname
  FROM EMPLOYEE AS E
 WHERE EXISTS ( SELECT *
                  FROM DEPENDENT AS D
                 WHERE E.Ssn = D.Essn AND E.Sex = D.Sex
                   AND E.Fname = D.Dependent_name);

SELECT Fname, Lname
  FROM EMPLOYEE
 WHERE NOT EXISTS ( SELECT *
                      FROM DEPENDENT
                     WHERE Ssn = Essn );
                     
SELECT Fname, Lname
  FROM EMPLOYEE
 WHERE EXISTS ( SELECT *
                  FROM DEPENDENT
                 WHERE Ssn = Essn )
   AND EXISTS ( SELECT *
                  FROM DEPARTMENT
                 WHERE Ssn = Mgr_ssn );
                 
SELECT distinct Fname, Lname
  FROM EMPLOYEE e, DEPENDENT de, DEPARTMENT dp
 WHERE e.Ssn = de.Essn
   and e.Ssn = dp.Mgr_ssn;
   
## Retrieve the name of each employee who works on all the projects controlled by department number 5
SELECT Fname, Lname
  FROM EMPLOYEE
 WHERE NOT EXISTS ( ( SELECT Pnumber
                        FROM PROJECT
                       WHERE Dnum = 5)
           EXCEPT ( SELECT Pno
                      FROM WORKS_ON
                     WHERE Ssn = Essn) );

select * from project;
select * from works_on order by essn, pno;

SELECT Fname, Lname
   FROM EMPLOYEE E
  WHERE NOT EXISTS (SELECT Pnumber
                      FROM PROJECT P
                     WHERE P.Dnum = 5
                       AND NOT EXISTS (SELECT Pno
                                         FROM WORKS_ON W
                                        WHERE W.Essn = E.Ssn AND W.Pno = P.Pnumber
                                       )
                   );
                   
select * from works_on;
insert into works_on values (123456789,3,32.5);
delete from works_on where essn = 123456789 and pno = 3; 

SELECT E.Lname Employee_name, S.Lname Supervisor_name
   FROM (EMPLOYEE E LEFT OUTER JOIN EMPLOYEE S ON E.Super_ssn = S.Ssn);
   
SELECT E.Lname Employee_name, S.Lname Supervisor_name
   FROM EMPLOYEE E, EMPLOYEE S 
  where E.Super_ssn = S.Ssn;