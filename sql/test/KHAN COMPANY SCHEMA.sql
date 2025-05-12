select * from information_schema.tables;
select distinct table_schema from information_schema.tables;
create database company;
create user 'company'@'localhost' identified by 'companyuser';
grant all on company.* to 'company'@'localhost';
flush privileges;
show databases;

alter user 'company'@'localhost' identified by 'password123';
create user 'companyuser'@'localhost' identified by 'password123';
grant all on company.* to 'companyuser'@'localhost';
flush privileges;