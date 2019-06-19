# SQL Query
## Summary:
Module that queries an existing sqlite database <br>
script name: `sql_query.py` <br>

__What Does the Module do?:__ <br>

* Queries User Identified Database using the User Identified query
* Also can return list of available tables within the database

## Prerequisites:
Download Tool:<br>
[SQLite DB Browser](https://sqlitebrowser.org/)<br>

1. Must have `sql_query.py` module installed
1. Create an SQLite database (.db file)

__Example:__ <br>
Create a table named `Environments_<Project>`: <br>

* Table Columns: `Environment`, `URL`, `Type`, `IP`, `Hostname`, `Service Account`, `Password` <br>

Column       |     Type
------------ | -------------
Environment | TEXT
URL | TEXT
TYPE | TEXT
IP | TEXT
HostName | TEXT
Service Account | TEXT
Password | TEXT

* Ensure that the `Password` values in your table are encoded using the `encode_password` Module
* Populate Table data using SQLite DB Browser

## Arguments:
  Argument   |     CommandLine Flag   |   Description
------------ | ------------- | -------------
Database | --database, --db, -database, -db | Defines what database to perform queries on
Query | --query, --q, -query, -q | Defines what sqlite query will be done to provide a list of server information. This controls the # of Environments and servers to report on.