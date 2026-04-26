# Deploy Oracle Key Vault for Oracle Database@Azure

- Source: https://docs.oracle.com/en/solutions/deploy-key-vault-database-at-azure/index.html
- Date: 2024-10
- Type: reference-architecture
- Services: vault, exacs, azure
- Tags: security, database, multicloud, azure

## Summary (catalog)

Key Vault for TDE key management on Database@Azure. Centralized encryption key lifecycle with multi-master replication for HA. Supports PKCS#11, REST API, and Oracle-native key management.

## Architecture (fetched from source)

Architecture

 

 
This architecture shows how to deploy Oracle Key Vault on an Microsoft Azure virtual machine (VM) as a secure long-term external key management storage for
 Oracle Exadata Database
 Service encryption keys in Oracle Database@Azure .
 

 
The architecture diagram depicts the recommended Oracle Key Vault multi-master cluster in Azure to provide continuously available, extremely scalable, and fault-tolerant
 key management for the Oracle Database in Oracle Exadata Database
 Service ( Oracle Database@Azure ).
 

 
The following diagram illustrates this reference architecture.

 
 Description of the illustration key-vault-database-azure-diagram.png 

 key-vault-database-azure-diagram-oracle.zip 

 
 Oracle Key Vault for Oracle Database@Azure can be deployed on-premises, in Azure , or any other cloud, as long as network connectivity can be established.
 Stretched Oracle Key Vault clusters (on-premises to cloud, or across cloud providers) are also
 possible, giving you maximum deployment flexibility and local availability
 of your encryption keys. Oracle Key Vault provides "hold your own key" functionality out of the box, without the
 need for an additional, expensive third-party key management appliance.
 

 
The architecture has the following components:

 
 
- Azure region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that contains one
 or more data centers, called availability domains. Regions
 are independent of other regions, and vast distances can
 separate them (across countries or even continents).
 

 
An Azure region is a geographical area in which one or more
 physical Azure data centers, called availability zones, reside. Regions
 are independent of other regions, and vast distances can
 separate them (across countries or even continents).
 

 
 Azure and OCI regions are localized geographic areas. For Oracle Database@Azure , an Azure region is connected to an OCI region, with availability
 zones (AZs) in Azure connected to availability domains (ADs) in OCI. Azure and OCI region pairs are selected to minimize distance
 and latency.
 

 
 
- Azure availability zone 
An availability zone
 is a physically separate data center within a region that is
 designed to be available and fault tolerant. Availability
 zones are close enough to have low-latency connections to
 other availability zones.

 
 
- Microsoft Azure Virtual Network 
 Microsoft Azure Virtual Network (VNet) is the fundamental building block for your private
 network in Azure . VNet enables many types of Azure resources, such as Azure virtual machines (VM), to securely communicate with each other, the internet,
 and on-premises networks.
 

 
 
- Exadata Database Service on Dedicated Infrastructure 
 Oracle Exadata Database
 Service delivers proven Oracle Database capabilities on purpose-built, optimized
 Oracle Exadata infrastructure in the public cloud. Built-in cloud automation,
 elastic resource scaling, security, and fast performance for OLTP, in-memory
 analytics, and converged Oracle Database workloads help simplify management and
 reduce costs.
 

 
Exadata Cloud Infrastructure X9M brings more CPU cores,
 increased storage, and a faster network fabric to the public cloud. Exadata X9M
 storage servers include Exadata RDMA Memory (XRMEM), creating an additional tier
 of storage, boosting overall system performance. Exadata X9M combines XRMEM with
 innovative RDMA algorithms that bypass the network and I/O stack, eliminating
 expensive CPU interrupts and context switches.

 
Exadata Cloud
 Infrastructure X9M increases the throughput of its 100 Gbps active-active Remote
 Direct Memory Access over Converged Ethernet (RoCE) internal network fabric,
 providing a faster interconnect than previous generations with extremely
 low-latency between all compute and storage servers.

 
 
- Oracle Database@Azure 
 Oracle Database@Azure is the Oracle Database service ( Oracle Exadata Database Service on Dedicated
 Infrastructure or Oracle Autonomous Database Serverless ) running on Oracle Cloud
 Infrastructure (OCI), deployed in Microsoft Azure data centers. The service offers features and price
 parity with OCI. Users purchase the service on Azure Marketplace.
 

 
 Oracle Database@Azure integrates Oracle Exadata Database
 Service , Oracle Real Application Clusters (Oracle
 RAC) , and Oracle Data Guard technologies into the Azure platform. Oracle Database@Azure service offers the same low latency as other Azure -native services and meets mission-critical workloads and
 cloud-native development needs. Users manage the service on
 the Azure console and with Azure automation tools. The service is deployed in Azure Virtual Network (VNet) and integrated with the Azure identity and access management system. The OCI and Oracle
 Database metrics and audit logs are natively available in
 Azure . The service requires that users have an Azure tenancy and an OCI tenancy.
 

 
 
- Transparent Data Encryption (TDE) 
 Transparent Data Encryption (TDE) transparently encrypts data at rest in an Oracle Database . It stops unauthorized attempts from the
 operating system to access database data stored in
 files, without impacting how applications access
 the data using SQL. TDE is fully integrated with
 Oracle Database and can encrypt entire database backups (RMAN),
 Data Pump exports, entire application tablespaces,
 or specific sensitive columns. Encrypted data
 remains encrypted in the database, whether it is
 in tablespace storage files, temporary
 tablespaces, undo tablespaces, or other files such
 as redo logs.
 

 
 
- Key Vault 
 Oracle Key Vault securely stores encryption keys, Oracle Wallets, Java
 KeyStores, SSH key pairs, and other secrets in a scalable,
 fault-tolerant cluster that supports the OASIS KMIP standard
 and deploys in Oracle Cloud
 Infrastructure , Microsoft Azure , and Amazon Web Services as well as on-premises on dedicated hardware or virtual
 machines.
 

 
 
 

 

 
 
Recommendations

 

 
 Use the following recommendations as a starting point.
 Your requirements might differ from the architecture described here. 
 

 
 
- Oracle Key Vault ISO 
To build the right Oracle Key Vault solution, make sure to use the latest Oracle Key Vault installation medium. See Explore More for the Oracle Software
 Delivery Cloud link.
 

 
 
- Oracle Key Vault image building 
To build the Oracle Key Vault image from the ISO, do so on a local system with at least 1 TB of storage
 with at least 32 GB in RAM. Create the virtual hard disk as
 Fixed size and in the VHD 
 format.
 

 
 
- Multi-node cluster 
Deploy Oracle Key Vault as a multi-node cluster to achieve maximum availability and reliability with
 read-write pairs of Oracle Key Vault nodes.
 

 
 Oracle Key Vault multi-master cluster is created with a first node, then additional nodes can
 e subsequently inducted to eventually form a multi-node cluster with up to 8
 read-write pairs.
 

 
The initial node is in read-only restricted
 mode and no critical data can be added to it. Oracle recommends to deploy a
 second node to form a read-write pair with the first node. After which, the
 cluster can be expanded with read-write pairs so that both critical and
 non-critical data can be added to the read-write nodes. Read-only nodes can help
 with load balancing or operation continuity during maintenance operations.

 
Consult the documentation to learn how a multi-master cluster
 affects endpoints, both in the way an endpoint connects and with
 restrictions.

 
For large deployments, install at least four Oracle Key Vault servers. Endpoints should be enrolled by making them unique and balanced
 across the four servers to ensure high availability. For example, if a data
 center has 1,000 database endpoints to register, and you have four Oracle Key Vault servers to accommodate them, then enroll 250 endpoints across each of the
 four servers.
 

 
Ensure that the system clocks of the endpoint
 host and the Orac
