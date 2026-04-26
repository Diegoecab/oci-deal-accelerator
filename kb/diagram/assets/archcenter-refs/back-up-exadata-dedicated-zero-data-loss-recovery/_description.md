# Back up from Exadata on Dedicated Infrastructure to Zero Data Loss Autonomous Recovery

- Source: https://docs.oracle.com/en/solutions/back-up-exadata-dedicated-zero-data-loss-recovery/index.html
- Date: 2025-07
- Type: reference-architecture
- Services: exacs
- Tags: database, ha-dr

## Summary (catalog)

Autonomous Recovery Service for ExaCS backups. Automated backup management with real-time redo protection. Validates backup recoverability automatically.

## Architecture (fetched from source)

Architecture

 

 

 
This playbook describes how to perform backup and recovery operations between Oracle Exadata Database Service on Dedicated
 Infrastructure and Recovery
 Service . 
 

 
 Description of the illustration exadata-dedicated-recovery-backup-architecture.png 

 exadata-dedicated-recovery-backup-architecture.zip 

 

 

 
 
Before You Begin

 

 
 Before you begin, check the versions of major software components used in this setup, and review the product documentation for later reference

 

 
 
Review Software Requirements

 

 

 
 
- Oracle Exadata Database Service on Dedicated
 Infrastructure 
 
- Oracle Database Enterprise Edition Extreme Performance 19.18 or newer
 
 
 

 

 
 
Review Documentation

 

 

 
 
- Introducing the Oracle Database Zero Data Loss Autonomous Recovery Service 
 
- About Oracle Database Autonomous Recovery Service 
 
- "Back Up and Recovery in Base Database Service" in Oracle Cloud
 Infrastructure documentation 
 
 

 

 

 
 
Considerations for Configuration

 

 
Before you begin to configure backups and recovery, review these assumptions and considerations. 

 
 
- The virtual cloud network (VCN) where Oracle Exadata Database Service on Dedicated
 Infrastructure is configured, must route packages to the OCI Services Network (where Recovery
 Service is configured) via a service gateway.
 
 
- There are two types of backups: Oracle managed backups and user configured backups. Oracle managed backups are configured using the OCI console or REST API. User configured backups are configured using the dbaascli only.
 
 
- This playbook uses Oracle managed backups to Recovery
 Service . User configured backups are out of scope of this playbook.
 
 
- Combining Oracle managed backups and user configured backups is not supported. 
 
- The Recovery
 Service enables databases to restore to the last known good state with minimal data loss, to a specific timestamp, or SCN. The OCI console, however, does not support restoring a database from a specific backup from the list of backups displayed in the console. Although it's not possible to restore a database from a backup in this list, the list of backups can be used as a reference as to what data is currently available for restore operations.
 
 
- The OCI console cannot restore a particular pluggable database (PDB) . Only the full container database (CDB) can be restored.
 
 
 

 

 
 
About Required Products and Roles

 

 
This solution requires the following products and roles:

 
 
- Oracle Cloud
 Infrastructure 
 
- Oracle Cloud Infrastructure Identity
 and Access Management 
 
- Oracle Exadata Database Service on Dedicated
 Infrastructure 
 
- Oracle Database Zero Data Loss Autonomous Recovery Service 
 
- Oracle Database 
 
 
These are the roles needed for each product.

 

 
 
 
 Service Name: Role 
 Required to... 
 
 
 
 
 Oracle Cloud
 Infrastructure : VCN admin 
 Add OCI services gateway and create security rules to allow connections from Oracle Database Zero Data Loss Autonomous Recovery Service to the Oracle Exadata Database Service on Dedicated
 Infrastructure backup network.
 
 
 
 Oracle Cloud Infrastructure Identity
 and Access Management : IAM service admin 
 Add security policies for Oracle Database Zero Data Loss Autonomous Recovery Service .
 
 
 
 Oracle Exadata Database Service on Dedicated
 Infrastructure : database admin 
 
 
 
- Create database with Oracle managed backups to Oracle Database Zero Data Loss Autonomous Recovery Service .
 
 
- Modify database to add Oracle managed backups to Oracle Database Zero Data Loss Autonomous Recovery Service .
 
 
 
 
 
 Oracle Database Zero Data Loss Autonomous Recovery Service : admin 
 Add Oracle Database Zero Data Loss Autonomous Recovery Service subnet for Oracle Exadata Database Service on Dedicated
 Infrastructure backups.
 
 
 
 Oracle Database : sys 
 Configure backups to Oracle Database Zero Data Loss Autonomous Recovery Service .
 
 
 
 
 

 
See Oracle Products, Solutions, and Services to get what you need.
 

 

 

 

 

 

 
 Title and Copyright Information 

 

 
Back up Oracle Exadata on Dedicated Infrastructure to Oracle Zero Data Loss Autonomous Recovery Service

 
F84015-04

 
July 2025

 
 Copyright © 2023,2025, 

Oracle and/or its affiliates.
