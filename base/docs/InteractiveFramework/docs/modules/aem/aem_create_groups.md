# AEM Create Groups
## Summary:
Module that creates AEM System Groups, AEM Tenant Groups, and AEM Application Groups. Then assigns the necessary group memberships. <br>
script name: `aem_create_groups.py` <br>
Log Output Path: `<UserHome>/aem_create_groups/logs`<br>

__What Does the Module do?:__ <br>

* Creates Predefined System Groups
* Creates Predefined Tenant Groups
* Creates Predefined App groups
* Logs all Output to `<UserHome>/aem_create_groups/logs`

## Prerequisites:
Download Tool:<br>
[SQLite DB Browser](https://sqlitebrowser.org/)<br>

1. Must have `sql_query.py` module installed
1. Must have `encode_password.py` module installed
1. Create an SQLite database (.db file)
1. Create a table named `Environments_<Project>`
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

1. Create a table named `Groups_<Project>`
    * Table Columns: `Type`, `Node_Type`, `Name`, `Member_Of`

    Column       |     Type     | Specific Supported Values
    ------------ | ------------- | -------------
    TYPE | TEXT | system, tenant, app
    Node_Type | TEXT | group, user
    Name | TEXT
    Member_Of | TEXT

    * Populate Groups Data data using SQLite DB Browser

1. Create a table named `Service_Accounts_<Project>`
    * Table Columns: `Environment`, `Password`

    Column       |     Type
    ------------ | -------------
    Environment | TEXT
    Password | TEXT

    * Ensure that the `Password` values in your table are encoded using the `encode_password` Module
    * Populate Service Account Data data using SQLite DB Browser


## Arguments:
  Argument   |     CommandLine Flag   |   Description
------------ | ------------- | -------------
Database | --database, --db, -database, -db | Defines what database to perform queries on
Query | --query, --q, -query, -q | Defines what sqlite query will be done to provide a list of server information. This controls the # of Environments and servers to report on.