# Migrate Oracle RAC Databases to OCI

- Source: https://docs.oracle.com/en/solutions/ensure-ha-migrate-vmware-workloads-to-oci/migrate-oracle-rac-databases1.html
- Date: 2025-01
- Type: reference-architecture
- Services: exacs, exascale, adb-d, base-db
- Tags: database, migration, ha-dr

## Summary (catalog)

Compares 4 RAC migration targets: ExaCS Dedicated, Exascale, ADB-D, and 2-node RAC on Base DB. ExaCS recommended for full RAC feature parity. Exascale for 23ai-only without dedicated infra commitment.

## Architecture (fetched from source)

Migrate Oracle RAC Databases 
 
 
 
 
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
 
- 
 
 
 
 

 Previous 
 Next 
 JavaScript must be enabled to correctly display this content
 
 

 

 
 
 
- Learn about ensuring high availability when migrating VMware workloads to OCI 
 
- Migrate Oracle RAC
 Databases 
 
 
 
 
Migrate Oracle RAC
 Databases

 
 

 

 

 In this configuration option, you migrate an application and an Oracle RAC database running on VMware on-premises with Oracle Database backup to an on-premises location. Oracle Database management and operations are usually manual and your full
 responsibility. 
 
 

 
The following architecture diagram shows an Oracle RAC database in an on-premises deployment:
 
 
 Description of the illustration migrate-orclracdb-vmware-premises.png 
You have the following options to ensure database high availability when
 migrating this deployment to OCI:

 
 
- Migrate to Oracle Exadata Database Service on Dedicated
 Infrastructure 
 
- Migrate to Oracle Exadata Database Service on Exascale Infrastructure 
 
- Migrate to Oracle Autonomous Database on Dedicated Exadata Infrastructure 
 
- Migrate to a two-node Oracle RAC Database on Oracle Base Database Service 
 
- Migrate to Oracle Cloud VMware Solution 
 
 

 
 
Migrate to Oracle Exadata Database Service on Dedicated
 Infrastructure 

 

 

 Oracle Exadata Database
 Service delivers proven Oracle Database capabilities on purpose-built, optimized Oracle Exadata Cloud Infrastructure . Built-in cloud automation, elastic resource scaling, security, and fast performance
 for all Oracle Database workloads help you simplify management and reduce costs. 
 
 

 
 Oracle Exadata Database Service on Dedicated
 Infrastructure runs on Oracle Exadata and Oracle RAC , benefits from their high availability, scalability, and redundancy, and complies
 with the Oracle MAA Silver Level by default.
 

 
The following architecture shows an Oracle RAC database on Oracle Exadata Database Service on Dedicated
 Infrastructure :
 
 
 Description of the illustration migrate-orclracdb-exadbdisrv.png 
This architecture consists of the following
 components:

 
 
- VCN with three subnets and a Service Gateway to
 access OCI-managed services. 
 
- Application on OCI Compute VM running in the application subnet.
 
 
- Oracle Exadata Cloud Infrastructure and Exadata VM Cluster deployed in the client and backup subnet.
 
 
- Oracle RAC database deployed in the Exadata VM Cluster with an Oracle RAC node on each VM of
 the VM Cluster.
 
 
- Oracle Database Autonomous
 Recovery Service for database automatic backups.
 
 
- (Optional) OCI Object Storage service as an alternative solution for database automatic backups.
 
 
- (Optional) OCI Vault for Transparent Data Encryption (TDE) key management.
 
 
 
This architecture benefits from:

 
 
- Built-in high availability and redundancy provided
 by Oracle Exadata and Oracle RAC .
 
 
- Application protection from interruptions during
 outages and maintenance operations with Application Continuity .
 
 
- Enhanced data protection with Oracle Database Autonomous
 Recovery Service .
 
 
- Online scalability of compute and storage
 resources. 
 
- Automated database provisioning and lifecycle
 operations. 
 
- TDE is enabled by default with the option to use OCI Vault for key management.
 
 
- Automated migrations using ZDM. 
 
- Oracle Cloud licensing models. 
 
 
 Recommendations 

 
 
- Configure automatic backup to Oracle Database Autonomous
 Recovery Service to minimize the backup workload on the database by implementing the incremental
 forever backup strategy that eliminates weekly full backups. Additionally, it
 enables a faster restore and recovery by providing a virtual full backup copy and
 eliminating the need to recover incremental backups.
 
 
- Enable Oracle Database Autonomous
 Recovery Service real-time data protection to synchronize your transactions in real time to the
 recovery service. Real-time data protection minimizes the possibility of data loss
 to achieve a sub-second Recovery Point Objective (RPO).
 
 
- 
 
 
Enable Application Continuity to mask database outages during planned and unplanned events from end-users and
 ensure uninterrupted applications.
 

 
 
 
 

 

 
 
Migrate to Oracle Exadata Database Service on Exascale Infrastructure 

 

 
 Oracle Exadata Database Service on Exascale Infrastructure provides the same cloud service experience as Oracle Exadata Database Service on Dedicated
 Infrastructure , but without requiring you to subscribe to dedicated infrastructure. You can start with a
 small virtual machine (VM) cluster, and easily scale as your needs grow. Oracle manages all
 the physical infrastructure in a shared multitenancy infrastructure service model. Oracle Exadata Database Service on Exascale Infrastructure is available for Oracle Database 
 version 23ai only.
 

 
 Oracle Exadata Database Service on Exascale Infrastructure runs on Oracle Exadata and Oracle RAC , benefits from their high availability, scalability, and redundancy, and complies
 with the Oracle MAA Silver Level by default.
 

 
The following architecture diagram shows Oracle RAC database on Oracle Exadata Database Service on Exascale Infrastructure : 
 
 
 Description of the illustration migrate-orclracdb-exadbsrv-exascale-infra.png 
This architecture consists of the following
 components:

 
 
- VCN with three subnets and a Service Gateway to
 access OCI-managed services. 
 
- Application on OCI Compute VM running in the application subnet.
 
 
- Exadata VM Cluster deployed in the client and
 backup subnet. 
 
- Oracle RAC database deployed in the Exadata VM Cluster with an Oracle RAC node on each VM of the VM Cluster.
 
 
- Oracle Database Autonomous
 Recovery Service for database automatic backups.
 
 
- (Optional) OCI Object Storage service as an alternative solution for database automatic backups.
 
 
- (Optional) OCI Vault for Transparent Data Encryption (TDE) key management.
 
 
 
This architecture benefits from:

 
 
- Built-in high availability and redundancy provided
 by Oracle Exadata and Oracle RAC .
 
 
- Application protection from interruptions during
 outages and maintenance operations with Application Continuity .
 
 
- Enhanced data protection with Oracle Database Autonomous
 Recovery Service .
 
 
- Online scalability of compute and storage
 resources. 
 
- Automated database provisioning and lifecycle
 operations. 
 
- TDE is enabled by default with the option to use
 OCI Vault for key management.
 
 
- Automated migrations using ZDM. 
 
- Oracle Cloud licensing models. 
 
- Lower entry size and cost than Oracle Exadata Database Service on Dedicated
 Infrastructure .
 
 
- Advanced space-efficient snapshot and cloning
 capabilities that are tightly integrated with Oracle Database and eliminate the need
 for a test master database to support snapshots and clones on Exadata. 
 
 
 Recommendations 

 
 
- Configure automatic backup to Oracle Database Autonomous
 Recovery Service to minimize the backup workload on the database by implementing the incremental
 forever backup strategy that eliminates weekly full backups. Additionally, it
 enables a faster restore and recovery by providing a virtual full backup copy and
 eliminating the need to recover incremental backups.
 
 
- Enable Oracle Database Autonomous
 Recovery Service real-time data protection to synchronize your transactions in real time to the
 recovery service. Real-time data protection minimizes the possibility of data loss
 to achieve a sub-second Recovery Point Objective (RPO).
 
 
- Enable Application Continuity to mask database outages during planned and unplanned events from end-users to
 ensure uninterrupted applications.
 
 
 

 

 
 
Migrate to Oracle Autonomous Database on Dedicated Exadata Infrastructure 

 

 
 Oracle Autonomous Database provides an easy-to-use, fully autono
