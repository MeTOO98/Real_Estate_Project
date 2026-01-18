use Real_EState
GO
-- Create Core Schema 

create schema Core
GO

-- Create Table Dim_Date 

create table Core.Dim_Date (
date_id varchar(100) primary key ,
date varchar(150) ,
day int ,
Month int,
Year int)
GO

-- Create Table Dim_Location

create table Core.Dim_Location (
Location_id int primary key identity (1,1),
Location varchar(250),
Compound varchar(250),
City varchar(250),
Gov varchar(250))
GO


-- create middle table 
create table Core.midd_table (
property_id int primary key,
Price varchar(150),
NumOfRooms int,
NumofBathRooms int,
Size int,
Type varchar(150),
completion_status varchar(150),
Date_Id varchar(100),
location varchar(250))
GO

-- Create The Fact_Table 

create table Core.Fact_Table (
property_id int primary key,
Price varchar(150),
NumOfRooms int,
NumofBathRooms int,
Size int,
Type varchar(150),
completion_status varchar(150),
Date_Id varchar(100),
Location_id int,
constraint c1 foreign key (Date_id) references Core.dim_date (date_id),
constraint c2 foreign key (Location_id) references Core.dim_location (location_id) )


