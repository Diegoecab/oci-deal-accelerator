# Back up from Oracle Base Database Service to Zero Data Loss Autonomous Recovery

- Source: https://docs.oracle.com/en/solutions/back-up-base-database-zero-data-loss-recovery/index.html
- Date: 2025-07
- Type: reference-architecture
- Services: base-db
- Tags: database, ha-dr

## Summary (catalog)

Autonomous Recovery Service for Base DB backups. Real-time protection with continuous redo log shipping. Point-in-time recovery with sub-second RPO for mission-critical workloads.

## Architecture (fetched from source)

Architecture

 

 

 
This playbook describes how to perform backup and recovery operations between Oracle Base Database Service and Recovery
 Service . 
 

 
 Description of the illustration base-database-recovery-backup-architecture.png 

 base-database-recovery-backup-architecture.zip 

 

 

 
 
Before You Begin

 

 
 Before you begin, check the versions of major software components used in this setup, and review the product documentation for later reference

 

 
 
Review Software Requirements

 

 

 
 
- Oracle Database 19.18 and above, or 21.8 and above
 
 
- Oracle Base Database Service 
 
 

 

 
 
Review Documentation

 

 

 
 
- Introducing the Oracle Database Zero Data Loss Autonomous Recovery Service 
 
- About Oracle Database Autonomous Recovery Service 
 
- "Back Up and Recovery in Base Database Service" in Oracle Cloud
 Infrastructure documentation 
 
 

 

 

 
 
Considerations for Configuration

 

 
Before you begin to configure backups and recovery, review these assumptions and considerations. 

 
 
- The virtual cloud network (VCN) where Oracle Base Database Service is configured, must route packages to the OCI Services Network (where Recovery
 Service is configured) via a service gateway.
 
 
- There are two types of backups: Oracle managed backups and unmanaged backups. Oracle managed backups are configured using the OCI console or REST API. Unmanaged backups are configured using dbaascli or RMAN .
 
 
- This playbook uses Oracle managed backups to Recovery
 Service . Unmanaged backups are out of scope of this playbook.
 
 
- Combining Oracle managed backups and unmanaged backups is not supported. 
 
- The Recovery
 Service enables databases to restore to the last known good state with minimal data loss, to a specific timestamp, or SCN. The OCI console, however, does not support restoring a database from a specific backup from the list of backups displayed in the interface. Although it's not possible to restore a database from a backup in this list, the list of backups can be used as a reference as to what data is currently available to restore the database.
 
 
- The OCI console cannot restore a particular pluggable database (PDB) . Only the full container database (CDB) can be restored.
 
 
 

 

 
 
About Required Products and Roles

 

 
This solution requires the following products:

 
 
- Oracle Cloud
 Infrastructure 
 
- Oracle Cloud Infrastructure Identity
 and Access Management 
 
- Oracle Base Database Service 
 
- Oracle Database Zero Data Loss Autonomous Recovery Service 
 
- Oracle Database 
 
 
These are the roles needed for each product.

 

 
 
 
 Product Name: Role 
 Required to... 
 
 
 
 
 Oracle Cloud
 Infrastructure : VCN admin 
 Add OCI services gateway and create security rules to allow connections from Oracle Database Zero Data Loss Autonomous Recovery Service to the Oracle Base Database Service backup network.
 
 
 
 Oracle Cloud Infrastructure Identity
 and Access Management : IAM service admin 
 Add security policies for Oracle Database Zero Data Loss Autonomous Recovery Service .
 
 
 
 Oracle Base Database Service : database admin 
 
 
 
- Create database with automatic backups to Oracle Database Zero Data Loss Autonomous Recovery Service .
 
 
- Modify database to add automatic backups to Oracle Database Zero Data Loss Autonomous Recovery Service .
 
 
 
 
 
 Oracle Database Zero Data Loss Autonomous Recovery Service : admin 
 Add Oracle Database Zero Data Loss Autonomous Recovery Service subnet for Oracle Base Database Service backups.
 
 
 
 Oracle Database : sys 
 Configure backups to Oracle Database Zero Data Loss Autonomous Recovery Service .
 
 
 
 
 

 
See Oracle Products, Solutions, and Services to get what you need.
 

 

 

 

 

 

 
 Title and Copyright Information 

 

 
Back up Oracle Base Database Service to Oracle Database Zero Data Loss Autonomous Recovery

 
F84016-03

 
July 2025

 
 Copyright © 2023,2025, 

Oracle and/or its affiliates.
