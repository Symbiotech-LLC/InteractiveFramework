# AEM Access Report
## Summary:
creates multiple AEM user, group, and membership reports. <br>
script name: `aem_access_report.py` <br>
Report Output Path: `<UserHome>/aem_permission_reports`<br>

__What Does the Module do?:__ <br>

* Collects all User Info
    * Report on users without UUID
    * Repot on users missing Profiles
* Collects all Group Info
* Report on all users and what groups they belong to

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

## Arguments:
  Argument   |     CommandLine Flag   |   Description
------------ | ------------- | -------------
Database | --database, --db, -database, -db | Defines what database to perform queries on
Query | --query, --q, -query, -q | Defines what sqlite query will be done to provide a list of server information. This controls the # of Environments and servers to report on.