-- first i will create a database and this database will be its name Real_State
create database Real_EState
GO

-- change to this database
use Real_EState
GO

-- create schema 'raw_data'

create schema  raw_data
GO

-- create the table that i will put the raw data in it 

create table raw_data.data (
url varchar(600),
Price varchar(150),
NumofRooms varchar(100),
NumofBathroom varchar(100),
Size varchar(150),
Type varchar(150),
created_date varchar(150),
completion_status varchar(150),
location varchar(250))
