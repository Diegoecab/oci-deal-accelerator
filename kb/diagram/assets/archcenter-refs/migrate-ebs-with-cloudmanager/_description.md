# Migrate an Oracle E-Business Suite environment to Oracle Cloud

- Source: https://docs.oracle.com/en/solutions/migrate-ebs-with-cloudmanager/index.html
- Date: 2025-10
- Type: reference-architecture
- Services: compute, base-db, load-balancer
- Tags: application, migration, ebs

## Summary (catalog)

EBS lift-and-shift to OCI using EBS Cloud Manager. Automated provisioning of app and DB tiers. Supports EBS 12.2 with Base DB or ExaCS for database tier.

## Architecture (fetched from source)

Architecture

 

 
This solution implements the following architecture:

 
 Description of the illustration migrate-ebs-env-prod.png 

 migrate-ebs-env-prod-oracle.zip 

 
The architecture consists of the following components:

 
 
- Oracle E-Business Suite Cloud Manager 
 Oracle E-Business Suite Cloud Manager is a web-based application that drives the principal automation flows for Oracle E-Business Suite on OCI, including migrating Linux-based environments from on-premises, provisioning new environments, and performing lifecycle management activities.
 

 
 
- Applications tier 
The Oracle E-Business Suite applications tier hosts the various servers and service groups, including web services, forms services, and the concurrent processing server, that process the business logic and manages communication between the desktop tier and the database tier. 
 

 
 
- Oracle Database 
This architecture is valid for target environments which incorporate Oracle Base Database Service 19c or Oracle Exadata Database
 Service 19c.
 

 
 
- OCI Object Storage 
 OCI Object Storage provides access to large amounts of structured and unstructured data of any content type, including database backups, analytic data, and rich content such as images and videos. You can safely and securely store data directly from applications or from within the cloud platform. You can scale storage without experiencing any degradation in performance or service reliability. 
 

 
Use standard storage for "hot" storage that you need to access quickly, immediately, and frequently. Use archive storage for "cold" storage that you retain for long periods of time and seldom or rarely access.

 
 
- Oracle Data Guard 
 Oracle Data Guard and Active Data Guard provide a comprehensive set of services that
 create, maintain, manage, and monitor one or more
 standby databases and that enable production
 Oracle databases to remain available without
 interruption. Oracle Data Guard maintains these standby databases as copies of
 the production database by using in-memory
 replication. If the production database becomes
 unavailable due to a planned or an unplanned
 outage, Oracle Data Guard can switch any standby database to the
 production role, minimizing the downtime
 associated with the outage. Oracle Active Data
 Guard provides the additional ability to offload
 read-mostly workloads to standby databases and
 also provides advanced data protection
 features.
 

 
 
 

 

 
 
Address the Prerequisites

 

 
Before proceding with this solution, you need to meet the following
 prerequisites:

 
 
- Connect Cloud Manager to the source application and database tier over SSH, either
 directly or through a bastion server. 
 
- Connect the target application tier to the source application tier over SSH, either
 directly or via a bastion server. 
 
- Verify connectivity between source and target database tiers by using
 TNSPing in both directions. 
 
- Open firewall ports for the source application and database nodes. 
 
- Ensure source and target hostnames and scan names are DNS resolvable from both the
 source and target database tiers. 
 
- Enable Transparent Data Encryption (TDE) for the source environment and encrypt all
 tablespaces (except TEMP) in both CDB and PDB. Include oratab entries, listener
 entries, and use Oracle Managed Files (OMF) for redo log. Set the
 dg_broker_config_file parameter. for more information on TDE, see the Oracle
 Advanced Security Guide 19c, which you can access from Explore More, elsewhere in
 this playbook. 
 
- Unset the LOG_ARCHIVE_DEST parameter on the
 source; use LOG_ARCHIVE_DEST_1 instead.
 
 
- Keep the database at 19c Release Update (RU) 19.21 or later, following the latest
 quarterly update requirements for Oracle E-Business Suite Cloud Manager. For more
 details, see "Cloud Automation Support for Database Quarterly Updates" in My Oracle
 Support Knowledge Document 2517025.1, Getting Started with Oracle E-Business Suite
 on Oracle Cloud Infrastructure, which you can access from Explore More, elsewhere in
 this playbook. 
 
- Create a stage folder in the source environment with the correct
 permissions: use chmod 777 for /u01/STAGE and chmod 755 for
 /u01 .
 
 
- Match operating systems between the source and target. If the target uses Oracle Database@Azure , run the source database on OL8.
 
 
- Provide at least 2GB temporary space in the source database tier for both CDB and
 PDB. 
 
- Make sure no adop sessions are active or running; do not start any after standby is
 created, as this will cause promotion to fail. 
 
- Ensure /tmp has enough space and the sudo user can read and write to it, as ZDM uses
 this directory. 
 
- Set passwords for APPS, WebLogic Server, SYS, and TDE encryption to meet Oracle
 E-Business Suite Cloud Manager security standards. 
 
- Do not change the TDE wallet password on either the source or target, as this may
 cause issues during standby instance promotion. 
 
 

 

 

 

 

 
 Title and Copyright Information 

 

 
Migrate an Oracle E-Business Suite environment to Oracle Cloud

 
G38722-01

 
October 2025

 
 Copyright © 2025, 

Oracle and/or its affiliates.
