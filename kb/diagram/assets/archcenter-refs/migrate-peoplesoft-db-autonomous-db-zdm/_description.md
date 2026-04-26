# Migrate a PeopleSoft database to Oracle Autonomous Database

- Source: https://docs.oracle.com/en/solutions/migrate-peoplesoft-db-autonomous-db-zdm/index.html
- Date: 2025-02
- Type: reference-architecture
- Services: adb-s, compute
- Tags: database, migration, autonomous, peoplesoft

## Summary (catalog)

PeopleSoft database migration to ADB-S using Zero Downtime Migration. Logical migration with Data Pump, ZDM for orchestration. PeopleTools compatibility verification required before migration.

## Architecture (fetched from source)

About Migrating a PeopleSoft Database to Oracle Autonomous Database Using Oracle Zero Downtime Migration 
 
 
 
 
- 
 
- 
 
 
 
 
 
- 
 
 
 
 
 
 
 
 
 
- 
 
 
 
 
 
 
 
 
 
- 
 
- 
 
- 
 
- 
 
- 
 
- 
 
- 
 
- 
 
- 
 
- 
 
- 
 
- 
 
 
 
 

 Previous 
 Next 
 JavaScript must be enabled to correctly display this content
 
 

 

 
 
 
- Migrate a PeopleSoft database to Oracle Autonomous Database 
 
- About Migrating a PeopleSoft
 Database to Oracle Autonomous Database Using Oracle Zero Downtime Migration 
 
 
 
 
About Migrating a PeopleSoft
 Database to Oracle Autonomous Database Using Oracle Zero Downtime Migration 

 
 

 

 

 Migrate your full-tier PeopleSoft environment to a self-driving,
 self-securing, and self-repairing capable database, without having to worry about
 downtime during migration. 
 
 

 
Data migration is moving data with or without its schema from one system,
 location, or application to another. When migrating to Oracle Autonomous Database , you can use Oracle Zero Downtime Migration to ensure a secure migration to Oracle Autonomous Database .
 

 
 Oracle Autonomous Database is a private database service within the Oracle Public Cloud, which helps customers
 exercise stronger security measures for enterprise applications, and to comply to the
 regulations of their industry pertaining to using cloud database management
 services.
 

 
In this solution playbook, we walkthrough how to migrate a full-tier
 PeopleSoft HCM environment running on an Oracle Linux virtual machine to Oracle Autonomous Database on Dedicated Exadata Infrastructure for online transaction processing, provisioned on Oracle Cloud
 Infrastructure (OCI). Zero Downtime Migration Logical Offline Migration is used for the
 migration.
 

 

 
 
Before You Begin

 

 

 Before you begin, review the requirements and download the required
 software packages. 
 
 

 

 
 
Review Requirements

 

 
Here are the minimum requirements for PeopleTools to support Oracle Autonomous Database on Dedicated Exadata Infrastructure .
 

 
 
- PeopleTools 
 
- For version 8.57, 8.57.16 and above. 
 
- For version 8.58, 8.58.05 and above. 
 
- For version 8.59, 8.59.01 and above. 
 
 
 
- Oracle Database Client 
To obtain required Oracle
 Client levels, update the client on the middle tier by applying a database
 release update patch on the mid tiers. The minimum level required is 19.13. See
 Oracle Database 19c Release Update & Release Update in Download Software
 Packages for details.

 
Oracle Call Interface clients support
 TLS authentication without a wallet if you are using the following client
 versions:

 
 
- Oracle Instant Client/Oracle Database Client 19.13 - only on
 Linux x64. 
 
- Oracle Instant Client/Oracle Database Client 19.14 (or later)
 and 21.5 (or later) - only on Linux x64 and Windows. 
 
 
 
 

 

 
 
Download Software Packages

 

 

 Download the following software packages, to be installed later in
 this solution playbook. 
 
 

 
 
- Oracle Database 19c Release Update & Release Update 
Update the
 client on the middle tier by applying a database release update patch on the mid
 tiers. The minimum level required is 19.13.

 
 
- Oracle Instant Client Downloads for
 Linux x86-64 (64-bit) 
 
- Oracle Zero
 Downtime Migration Software 
 
 

 

 

 
 
Considerations for Architecture
 Changes in Oracle Autonomous Database 

 

 

 
 Database account 

 
The predefined administrative user is ADMIN . Because Oracle Autonomous Database on Dedicated Exadata Infrastructure imposes security controls and performs administrative database tasks for the
 customer, the ADMIN user does not have as many privileges as the
 SYS user. See The ADMIN User and the SYS User in Explore More for
 details.
 

 
 Database character set 

 
 Oracle Autonomous Database on Dedicated Exadata Infrastructure uses AL32UTF8 as the default database character set and AL16UTF16 as the default
 national character set. As part of Zero Downtime Migration's prerequisites, the
 character set on the source database must be the same as the target database. However,
 for on-premises customers, with existing applications (and databases) using other
 character sets, migrating to a Unicode character set can be a convoluted process with
 complex data analysis to avoid data truncation and corruption due to replacement
 characters. For enterprise customers using PeopleSoft, for instance, the prerequisite to
 converting their data to the AL32UTF8 character set as part of their migration to an
 autonomous database is quite complex. For this playbook, the source database character
 set is Unicode AL32UTF8. See the My Oracle Support article Doc ID 788156.1 in Explore
 More for details.
 

 
 Database initialization parameters 

 
See Database Initialization Parameters in Explore More for the initialization
 parameters, which can be modified. PeopleSoft recommends database patch and parameters
 from the My Oracle Support (Doc ID 1100831.1) article in Explore More for details.

 
 Database time zone 

 
The default autonomous database time zone is driven by the Autonomous VM
 Cluster OS Timezone. In this solution playbook, this is Coordinated Universal Time (UTC)
 and by default calls to SYSDATE . SYSTIMESTAMP returns
 the date and time in UTC.
 

 
 Database service 

 
 Oracle Autonomous Database provides multiple sets of database services to use when connecting a database to
 support different kinds of database operations. In each set, one service provides a
 secure TCP (TCPS) connection using the TLS protocol, and another provides a TCP
 connection. Oracle Autonomous Transaction
 Processing supports all connection services as tpurgent, tp, high, medium, and low. Although
 connection services those are designed for typical transaction processing operations
 are: tp_tls, tp, tp_ro_tls, tp_ro, tp_ss_tls, and tp_ss.
 

 
 Database user password policy 

 
 Oracle Autonomous Database requires strong passwords that must meet the following default complexity rules:
 

 
 
- The password must be between 12 and 30 characters long and must include at least one
 uppercase letter, one lowercase letter, and one numeric character. 
 
- The password cannot contain the username. 
 
- The password cannot be one of the last four passwords used for the same
 username. 
 
- The password cannot contain the double quote (") character. 
 
- The password must not be the same password that was set within the last 24
 hours. 
 
 
To change the password complexity rules and password parameter values, you
 can alter the default profile, or create a new profile and assign it to users. See
 Create Database Users in Explore More for details.

 

 
Note:
You can also create a password verify
 function (PVF) and associate it with a profile to manage the complexity of user
 passwords. See Manage Password Complexity on Autonomous Database in Explore More for
 details.
 

 
Data Pump can import a database user with a weak password to ease migration.
 For security purposes, it provides a 30-days time window to reset the password as per
 the Oracle Autonomous Database on Dedicated Exadata Infrastructure password policy.
 

 
 Automatic indexing 

 
Automatic indexing automates the index management tasks in Autonomous Database. Auto
 indexing is disabled by default in Autonomous Database. For PeopleSoft, it is
 recommended to rely upon application-provided indexes.

 
 Optimizer hints 

 
Optimizer hints are special comments in a SQL statement that pass instructions to the
 optimizer. Autonomous Database honors optimizer hints and parallel hints in SQL
 statements by default.

 
 Optimizer statistics 

 
Autonomous Database gathers optimizer statistics automatically so that users don't need
 to perform this task manually, helping to ensure database statistics are current.

 
 Data encryption 

 
Autonomous Database uses always-on encryption that protects data at rest and in transit.
 All data stored in and all network communications with Oracle Cl
