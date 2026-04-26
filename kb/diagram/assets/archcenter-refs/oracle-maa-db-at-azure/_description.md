# Oracle MAA for Oracle Database@Azure

- Source: https://docs.oracle.com/en/solutions/oracle-maa-db-at-azure/index.html
- Date: 2025-05
- Type: reference-architecture
- Services: exacs, adg, vault, azure
- Tags: database, multicloud, azure, ha-dr, autonomous

## Summary (catalog)

Cross-AZ Data Guard on ExaCS in Database@Azure. Active Data Guard recommended for cross-AZ replication (block repair, app continuity, read offload). Backups to Autonomous Recovery Service.

## Architecture (fetched from source)

Architecture

 

 
This reference architecture shares the best practice for a cross availability
 zone (AZ) Oracle Data Guard solution.
 

 
When designing mission-critical database applications, business continuity
 practices and high availability topologies should always be considered. The architecture
 shows a containerized application in Azure Kubernetes Service (AKS). The container images are stored in the Azure container registry. Users access the application externally through a public load
 balancer. The primary database is deployed on Exadata VM cluster in Azure AZ1. The
 application VNet connects to the database VNet via VNet peering. The applications in AKS
 access the database in the client subnet through the delegated subnet. The secondary
 database is deployed in a separate availability zone in the region; in this case AZ2.
 Oracle Data Guard or Active Data Guard can be used to replicate the data from the primary database to the secondary
 database. Active Data Guard is recommended in cross AZ database replication. Active Data Guard provides key enhancements for data protection including automatic block repair and
 application continuity as well as the ability to offload "read-mostly" workloads from
 the primary to the standby for scalability benefits. The database keys are stored in OCI Vault , and the automatic backups are configured to Oracle Database Autonomous
 Recovery Service .
 

 
We recommend the following principles:

 
 
- Oracle Exadata Database Service on Dedicated
 Infrastructure (ExaDB-D). Each Exadata infrastructure deployment has at least one Exadata VM
 cluster in a separate virtual network (VNet) to form the primary and standby
 environments.
 
 
- Primary and standby client and backup subnets are separated VNets without
 overlapping IP CIDR ranges. 
 
- The application tier spans at least two AZs, and the VNet is peered with each VNet
 of primary and standby VM clusters. 
 
- Backups to Oracle Database Autonomous
 Recovery Service minimize the backup workload on the database by implementing the incremental
 forever backup strategy that eliminates weekly full backups. Additionally, it
 enables a faster restore and recovery by providing a virtual full backup copy and
 eliminating the need to recover incremental backups. Alternatively, automatic
 backups can be stored on OCI Object Storage .
 
 

 
 Description of the illustration cross-az-dr.png 

 cross-az-dr-oracle.zip 

 
This architecture has the following components:

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that contains one or more data centers,
 called availability domains. Regions are independent of other regions, and vast
 distances can separate them (across countries or even continents).
 

 
An Azure region is a geographical area in which one or more physical Azure data centers, called availability zones, reside. Regions are independent of
 other regions, and vast distances can separate them (across countries or even
 continents).
 

 
 Azure and OCI regions are localized geographic areas. For Oracle AI Database@Azure , an Azure region is connected to an OCI region, with availability zones (AZs) in Azure connected to availability domains (ADs) in OCI. Azure and OCI region pairs are selected to minimize distance and latency.
 

 
 
- Oracle Database Autonomous
 Recovery Service 
 Oracle Database Autonomous
 Recovery Service is a fully managed service designed to protect Oracle AI Database s from data loss and cyber threats. It offers faster backups with reduced database overhead, reliable recovery with validated backups, and real-time protection enabling recovery to within less than a second of an outage or ransomware attack. This service provides a centralized data protection dashboard and is recommended for backing up Oracle AI Database s with high resiliency.
 

 
 
- Data Guard and Active Data Guard 
 Oracle Data Guard provides a comprehensive set of services that create, maintain, manage, and
 monitor one or more standby databases to enable primary Oracle databases to
 remain available without interruption. Oracle Data Guard maintains these standby databases as copies of the production database using
 in-memory replication. Then, if the production database becomes unavailable
 because of a planned or an unplanned outage, Oracle Data Guard can switch any standby database to the production role, minimizing the
 downtime associated with the outage.
 

 
 Active Data Guard extends the capabilities of Oracle Data Guard by providing the ability to offload read-mostly workloads to standby
 databases in addition to advanced data protection features like automatic block
 repair and application continuity.
 

 
 
- Data Guard Observer 
The primary job of Data Guard
 Observer is to perform an automatic failover when conditions permit it to do so
 without violating the data durability constraints set by the DBA. It is a
 low-footprint Oracle Call Interface client built into the DGMGRL CLI. Like any
 other client, an observer can be run from any hardware platform that supports
 it, and that platform can be different from the primary or target standby
 database platform.

 
 
- Vault 
 Oracle Cloud Infrastructure Vault enables you to centrally manage the encryption keys that protect your data
 and the secret credentials that you use to secure access to your resources in
 the cloud. OCI Vault is used to store transparent data encryption (TDE) keys to encrypt ExaDB-D
 databases at rest.
 

 
 
- Exadata Database Service 
 Oracle Exadata Database
 Service enables you to leverage the power of Exadata in the cloud. You can provision
 flexible Exadata X9M systems that allow you to add database compute servers and
 storage servers to your system as your needs grow. Exadata X9M systems offer
 RDMA over Converged Ethernet (RoCE) networking for high bandwidth and low
 latency, persistent memory (PMEM) modules, and intelligent Exadata software. You
 can provision Exadata X9M systems by using a shape that's equivalent to a
 quarter-rack X9M system, and then add database and storage servers at any time
 after provisioning.
 

 
 Oracle Exadata Database Service on Dedicated
 Infrastructure provides Oracle Exadata Database Machine as a service in an Oracle Cloud
 Infrastructure (OCI) data center. The Oracle Exadata Database Service on Dedicated
 Infrastructure instance is a virtual machine (VM) cluster that resides on Exadata racks in
 an OCI region.
 

 
 Oracle AI Database@Azure provides the Oracle Exadata Database
 Service running on OCI, colocated in Microsoft Azure data centers.
 

 
 
- OCI Object Storage 
 OCI Object Storage provides access to large amounts of structured and unstructured data of any content type, including database backups, analytic data, and rich content such as images and videos. You can safely and securely store data directly from applications or from within the cloud platform. You can scale storage without experiencing any degradation in performance or service reliability. 
 

 
Use standard storage for "hot" storage that you need to access quickly, immediately, and frequently. Use archive storage for "cold" storage that you retain for long periods of time and seldom or rarely access.

 
 
- Oracle AI Database@Azure 
 Oracle AI Database@Azure integrates Oracle Exadata Database
 Service , Oracle Real Application Clusters (Oracle
 RAC) , and Oracle Data Guard technologies into the Azure platform.
 

 
 Oracle AI Database@Azure is the Oracle Database service running on Oracle Cloud Infrastructure (OCI),
 and is colocated in Microsoft Azure data centers. The service offers features and price parity with OCI. Users
 purchase the service on Azure Marketplace.
 

 
 Oracle AI Database@Azure service offers the same low latency as other Azure -native services and meets mission-critical workloads and cloud-native
 development needs. Users manage the service on the Azure console and with Azure automation tools. The serv
