# Configure Data Guard for Oracle Exadata Database Service on Dedicated Infrastructure

- Source: https://docs.oracle.com/en/solutions/dataguard-exadata-dedicated-infrastructure/index.html
- Date: 2025-07
- Type: reference-architecture
- Services: exacs, adg
- Tags: database, ha-dr

## Summary (catalog)

Data Guard configuration for ExaCS Dedicated. Active Data Guard for read offload and automatic failover. Cross-region standby for DR with Fast-Start Failover for automated switchover.

## Architecture (fetched from source)

Architecture

 

 
This architecture shows two Oracle Exadata Database Service on Dedicated
 Infrastructure databases located in different regions, with Oracle Data Guard configured between the databases to keep them both in sync.
 

 
The following diagram illustrates this architecture.

 

 
 Description of the illustration exadata-dedicated-cross-region-dataguard.png 

 
 exadata-dedicated-cross-region-dataguard.zip 

 
Alternatively, your Oracle Exadata Database Service on Dedicated
 Infrastructure databases can be located within the same region.
 

 
The following diagram illustrates this architecture.

 

 
 Description of the illustration exadata-dedicated-region-dataguard.png 

 
 exadata-dedicated-region-dataguard.zip 

 
When configuring Oracle Data Guard , we recommend configuring your Oracle Exadata Database Service on Dedicated
 Infrastructure primary and standby databases accordingly to ensure maximum availability:
 

 
 
- Maximum availability: Primary and standby databases in different OCI regions. 
 
- Higher availability: Primary and standby databases in the same region, but different availability domains. 
 
- High availability: Primary and standby databases in the same region and availability domain. 
 
 

 

 
 
Before You Begin

 
Before you begin, check the versions of major software components used in this setup and review the product documentation for later reference.

 
 
Review Software Requirements

 

 

 
 
- Oracle Exadata Database Service on Dedicated
 Infrastructure 
 
- Exaimage 22.1.30 or newer (source database) 
 
- Exaimage 24.1.8 or newer (target database) 
 
- Oracle Database 19.25 or newer
 
 
 

 

 
 
Review Documentation

 

 

 
 
- "Remote VCN Peering using a Legacy DRG" in Oracle Cloud
 Infrastructure documentation 
 
- "Using the Console to Enable Data Guard on an Exadata Cloud Infrastructure System" in Oracle Cloud
 Infrastructure documentation 
 
- "Creating a new Oracle Exadata Database Service on Dedicated Infrastructure database with Customer Managed Keys" in Oracle Cloud
 Infrastructure documentation 
 
- "Switching an Oracle Exadata Database Service on Dedicated Infrastructure Database from Oracle Managed Keys to Customer Managed Keys" in Oracle Cloud
 Infrastructure documentation 
 
- "Setting Up Replication for OCI Vault" in Oracle Cloud
 Infrastructure documentation 
 
 

 

 

 
 
Considerations for Configuration

 

 
Before you begin to configure Oracle Data Guard , review these assumptions and considerations. 
 

 
 
- The Oracle Exadata Database Service on Dedicated
 Infrastructure primary and standby databases must be managed in the same OCI tenancy.
 
 
- The standby database is a physical standby. 
 
- A primary database supports up to a maximum of six standby databases
 using the new Data Guard Group model (19c and later). If you have an existing
 standby database using the Data Guard Association model, you can change your
 configuration to a Data Guard Group. This model switch only changes the OCI tooling
 metadata, and does not affect the databases. See Change an Oracle Data Guard
 Association to an Oracle Data Guard Group section to learn more. 
 
 
- The primary and standby databases can run different release updates of
 the same major database version, particularly when performing maintenance and update
 operations. 
 
- For databases running versions 11g and 12c, the OCI interface limits
 the Data Guard configuration to one standby database for each primary database,
 called a Data Guard Association. If more than one standby is required, then Data
 Guard configuration must be done manually. Automatic backups cannot be enabled on
 standby databases, for database versions 11g and 12c. 
 
- Data Guard or Active Data Guard must be enabled to setup a standby database. With Data Guard, the standby
 database runs in mounted mode, while with Active Data Guard, the standby database
 runs in Read-Only mode. Data Guard is the default option and is part of Oracle
 Enterprise Edition license. Configuring Active Data Guard requires proper feature
 licensing. 
 
 
- To ensure maximum fault isolation for production workloads, we recommend primary and
 standby databases are configured on different Exadata Infrastructures. The Data
 Guard Group model enables in-region and cross-region standbys. Configuring cascade
 standby databases is not supported. 
 
- DBaaS Tools and Dbcs Agent versions must be identical between primary
 and standby VM Clusters. Use the dbaascli or rpm
 utility to verify the DBaaS Tools and Dbcs Agent versions.
 
 
- You can use the OCI interface to configure Oracle Data Guard for databases in the same region and across different regions that use
 Transparent Data Encryption (TDE) with customer-managed keys with OCI Vault . Before configuring Data Guard for a database that uses or will use OCI Vault to
 store customer-managed keys, see the section Verify Security Policies and Dynamic
 Groups .
 

 
Note:
After a database
 is configured to use customer-managed keys with OCI Vault , it cannot be re-configured to use Oracle-managed keys, regardless of whether
 Oracle Data Guard is configured or not.
 

 
 
 

 

 
 
About Required Products and Roles

 

 
This solution requires the following products:

 
 
- Oracle Exadata Database Service on Dedicated
 Infrastructure 
 
- Oracle Database 
 
 
These are the roles needed for each product.

 

 
 
 
 Product Name: Role 
 Required to... 
 
 
 
 
 Oracle Exadata Database Service on Dedicated
 Infrastructure : database admin 
 Create Data Guard Association for primary database.
 
 
 
 Oracle Database : sys 
 Create Data Guard Association using primary database sys password.
 
 
 
 
 

 
See Oracle Products, Solutions, and Services to get what you need.
 

 

 

 

 

 

 
 Title and Copyright Information 

 

 
Configure Oracle Data Guard for Oracle Exadata Database Service on Dedicated Infrastructure

 
F81694-03

 
July 2025

 
 Copyright © 2023,2025, 

Oracle and/or its affiliates.
