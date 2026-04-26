# Provision and deploy a maximum availability solution for PeopleSoft on Oracle Cloud

- Source: https://docs.oracle.com/en/solutions/deploy-maa-for-peoplesoft-on-oci/index.html
- Date: 2024-08
- Type: reference-architecture
- Services: exacs, adg, load-balancer, compute
- Tags: application, ha-dr, peoplesoft

## Summary (catalog)

Step-by-step PeopleSoft MAA deployment on OCI. Terraform stacks for infrastructure provisioning, Data Guard configuration, and PeopleSoft application tier setup.

## Architecture (fetched from source)

Architecture

 

 
This architecture shows an Oracle Maximum Availability Architecture (Oracle
 MAA) solution for PeopleSoft. The PeopleSoft high availability architecture is layered on
 top of Oracle Database and Oracle Fusion Middleware maximum availability architectures,
 including a secondary site to provide business continuity in the event of a primary site
 failure.

 
The following shows a full-stack Oracle MAA architecture, including primary
 and secondary sites. The secondary site is a replica of the primary. 
 
 Description of the illustration peoplesoft-maa-arch.png 

 peoplesoft-maa-arch-oracle.zip 
 
 

 
Each site consists of the following:

 
 
- An HTTPS load balancer for web-based application services 
 
- Two servers that host the PeopleSoft Pure Internet Architecture (PIA)
 domain 
 
- Two servers that host both the PeopleSoft Application Server and the
 Process Scheduler domains 
 
- A shared file system for PeopleSoft application software and report
 repository 
 
- An Oracle Real Application Clusters (Oracle
 RAC) database, with two database servers and shared storage
 
 
- Oracle Active Data Guard , which allows routing of “mostly read operations” to the standby database while
 keeping the standby database current with the primary
 
 
 
Both the application tier shared file system and the database are replicated
 to the secondary site – the application tier using rsync, and the database tier using
 Oracle Data Guard .
 

 
The data at the second site is kept in sync with the primary by using appropriate
 replication mechanisms.

 
 
- For the database itself, Oracle Active Data Guard ensures the standby database is kept in sync and transactionally consistent.
 
 
- For file system output generated during the operation of the application,
 rsync is used to frequently replicate the output to another
 region. There will be a small gap to resolve by identifying missing file system
 components and determining the action to take for each.
 
 
 

 

 
 
About Required Services and
 Roles

 

 
This solution requires the following services and roles:

 
 
- Oracle Cloud
 Infrastructure (OCI)
 
 
- PeopleSoft 
 
- Oracle Exadata Database Service on Dedicated
 Infrastructure 
 
 
These are the roles needed for each service.

 

 
 
 
 Service Name: Role 
 Required to... 
 
 
 
 
 Oracle Cloud
 Infrastructure : Tenancy Administrator
 
 
 
 
 
- Create OCI users and groups 
 
- Establish resource management roles by creating OCI policies for
 each group 
 
- Create OCI compartments for specific resource types 
 
- Subscribe to additional OCI regions 
 
 
 
 
 
 Oracle Cloud
 Infrastructure : Network Administrators
 
 
 
 
 
- Define network topology 
 
- Provision Virtual Cloud Networks (VCNs) 
 
- Provision network resources such as route tables, gateways and
 subnets 
 
- Establish network firewalls rules by creating security lists and
 applying them to the appropriate subnet. 
 
- Provision and manage OCI load balancer (LBaaS) 
 
- Obtain signed TLS/SSL certificates for LBaaS 
 
 
 
 
 
 Oracle Cloud
 Infrastructure 
 Oracle Exadata Database Service on Dedicated
 Infrastructure : Tenancy Administrator / PeopleSoft administrator
 
 
 
 
 
- Provision Oracle Exadata Database Service on Dedicated
 Infrastructure , compute instances and OCI File Storage resources
 
 
- Provision/migrate the PeopleSoft database, application tier
 software 
 
- Cluster and Database patching / maintenance 
 
- Configure Data Guard Association cloud service 
 
- Provision and manage OCI compute instances for PeopleSoft
 application tier 
 
- Configure PeopleSoft at both database and application tiers 
 
 
 
 
 
 Oracle Exadata Database Service on Dedicated
 Infrastructure Cloud Service VM operating system: root 
 
 
 
 
- Monitor system logs 
 
- Apply patches and upgrades to the OS on domUs within the VM
 cluster 
 
- Apply patches and upgrade the grid infrastructure 
 
 
 
 
 
 Oracle Exadata Database Service on Dedicated
 Infrastructure Cloud Service VM operating system: oracle 
 
 
 
 
- Start, stop and manage database services and instances 
 
- Manage pluggable databases within a CDB 
 
- Lifecycle management including database patching, upgrades,
 database administrator 
 
 
 
 
 
 Compute Instances VM OS: root 
 
 
 
 
- Create required OS group and users 
 
- Execute commands to configure OS ports 
 
 
 
 
 
 Compute Instances VM OS: psadm2 
 Install, configure and manage PeopleSoft application
 tier components 
 
 
 PeopleSoft Application Administrator: ps 
 Configure roles and responsibilities, UI configuration, Process
 scheduler setup, and so on within the application 
 
 
 
 

 
 

 
Note:

 
 
There are other users and passwords that are specific to the PeopleSoft deployment.
 For example, Tuxedo and Oracle WebLogic
 Server domains, that are only known to the implementation team and are not covered
 here.
 

 
 

 
See Oracle Products, Solutions, and Services to get what you need.
 

 

 

 

 

 

 
 Title and Copyright Information 

 

 
Provision and deploy a maximum availability solution for PeopleSoft on Oracle Cloud

 
F87906-01

 
August 2024

 
 Copyright © 2024, 

Oracle and/or its affiliates.
