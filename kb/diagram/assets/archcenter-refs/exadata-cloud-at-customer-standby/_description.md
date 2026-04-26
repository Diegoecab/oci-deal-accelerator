# Configure a standby database for disaster recovery using Oracle Exadata Database Service on Cloud@Customer

- Source: https://docs.oracle.com/en/solutions/exadata-cloud-at-customer-standby/index.html
- Date: 2025-07
- Type: reference-architecture
- Services: exacs, adg
- Tags: database, ha-dr

## Summary (catalog)

Data Guard standby on ExaCS Cloud@Customer for hybrid DR. On-premises primary with cloud standby, or cloud primary with on-premises standby for data sovereignty requirements.

## Architecture (fetched from source)

Architecture

 

 
This architecture shows an Oracle Exadata Database Service
 on Cloud@Customer primary database that transmits data to a standby database using Oracle Data Guard . The standby database is remotely located from the primary database for disaster recovery.
 

 

 
 Description of the illustration exadata-database-cloud-customer-standby-database.png 

 

 
 
Before You Begin

 

 
Before you begin, ensure you are familiar with the following resources:

 
 
- "Use Oracle Data Guard with Oracle Exadata Database Service on
 Cloud@Customer" in Exadata Database Service on Cloud@Customer
 Administrator's Guide .
 
 
- Enabling Data Guard on Oracle Exadata Cloud@Customer Video .
 
 
- "Create
 Oracle Database Homes on an Oracle Exadata Database Service on Cloud@Customer
 System" " in Oracle Cloud Infrastructure Documentation 
 
 
This playbook is tested on the following software and hardware versions of Oracle Exadata Database Service
 on Cloud@Customer :
 

 
 
- Oracle Exadata Database Service
 on Cloud@Customer X8M-2
 
 
- Exaimage 23.1.23 
 
- Oracle Database 19.25 
 
 

 

 
 
Considerations for Configuration

 

 
Before you begin to configure your standby database, review these assumptions and considerations.

 
 
- The primary and standby Oracle Exadata Database Service
 on Cloud@Customer infrastructures must be managed in the same OCI tenancy, but they can be managed
 in different OCI regions to ensure high availability in the event of a
 disaster.
 
 
- The standby database is a physical standby. 
 
- The primary and standby databases can be in different compartments. 
 
- A primary database supports up to a maximum of six standby databases
 using the new Data Guard Group model (19c and later). If you have an existing
 standby database using the Data Guard Association model, you can change your
 configuration to a Data Guard Group. This model switch only changes the OCI tooling
 metadata, and does not affect the databases. See Change an Oracle Data Guard
 Association to an Oracle Data Guard Group section to learn more. 
 
 
- To ensure maximum fault isolation for production workloads, we
 recommend primary and standby databases are configured on different Exadata
 Infrastructures. The Data Guard Group model allows in-region and cross-region
 standbys. Configuring cascade standby databases is not supported. 
 
- The primary and standby databases can run different release updates of
 the same major database version, particularly when performing maintenance and update
 operations. Standby databases can run newer release updates than primary
 databases. 
 
- Oracle Database Home Software, DBaaS Tools, and Dbcs Agent versions must be identical between primary and standby VM Clusters. 
 
- Your Oracle Data Guard configuration can be Active Data Guard or Data Guard . Whether you use Active Data Guard or Data Guard for the standby databases, automatic backups can now be enabled for any type of
 standby database.
 
 
- You can configure Data Guard for databases using customer managed keys (Oracle Key Vault). If a database will
 be configured with Data Guard and customer managed keys, first migrate the Transparent Data Encryption (TDE) keys to customer managed keys, then configure Data Guard . 
 
 
- Intermediate storage is not required. Standby database instantiation will happen over the network. 
 
 

 

 
 
About Required Services and Roles

 

 
This solution requires the following service:

 
 
- 
 
 Oracle Exadata Database Service
 on Cloud@Customer 

 
 
 
These are the roles needed for each service.

 

 
 
 
 Service Name: Role 
 Required to... 
 
 
 
 
 Oracle Exadata Database Service
 on Cloud@Customer : sys 
 
 
 
- Create the standby database in Oracle Exadata Database Service
 on Cloud@Customer .
 
 
- Log in to primary database and create Data Guard association between the primary and standby databases.
 
 
 
 
 
 
 

 
See Learn how to get Oracle Cloud services for
 Oracle Solutions to get the cloud services you need.
 

 

 

 

 

 

 
 Title and Copyright Information 

 

 
Configure a standby database for disaster recovery using Oracle Exadata Database Service on Cloud@Customer

 
F75399-02

 
July 2025

 
 Copyright © 2023,2025, 

Oracle and/or its affiliates.
