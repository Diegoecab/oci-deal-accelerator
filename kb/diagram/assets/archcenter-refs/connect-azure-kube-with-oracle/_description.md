# Connect Azure Kubernetes with Oracle Exadata Database Service on Oracle Database at Azure

- Source: https://docs.oracle.com/en/solutions/connect-azure-kube-with-oracle/index.html
- Date: 2025-02
- Type: reference-architecture
- Services: exacs, azure, oke
- Tags: application, multicloud, azure, database

## Summary (catalog)

AKS workloads connecting to ExaCS on Database@Azure. Network connectivity via VNet peering, connection pooling with Oracle Universal Connection Pool for Kubernetes pod scaling.

## Architecture (fetched from source)

Architecture

 

 

 The architecture shows a containerized application deployed in Azure
 Kubernetes Service (AKS) and Oracle Exadata Database
 Service in a Microsoft Azure Region with automatic backups going to Oracle Database Autonomous
 Recovery Service in the Azure Region or OCI Object Storage in the OCI Region. 
 
 

 
Kubernetes is a portable, extensible, open source platform for managing
 containerized workloads and services, that facilitates both declarative configuration
 and automation. Kubernetes is considered a cornerstone technology for cloud native
 computing and has a large, rapidly growing ecosystem. Kubernetes services, support, and
 tools are widely available.

 
In this architecture a containerized application in AKS is in its own
 application subnet. A Kubernetes cluster can contain multiple pods, each connecting to
 its own respective Oracle Pluggable Database (PDB). The PDBs in the primary database are
 deployed on Oracle Database@Azure that runs on Oracle Exadata Database Service on Dedicated
 Infrastructure in an Azure Availability Zone. The container images are stored in the Azure container
 registry. Users access the application externally through a public load balancer. 
 

 
Cloud automation simplifies most lifecycle and management tasks for Oracle
 Exadata Infrastructure and Oracle multitenant databases (CDBs and PDBs). For example,
 adding servers and scaling OCPUs up and down, creating databases and database homes,
 scheduling infrastructure maintenance, updating and upgrading the VM operating system,
 Grid Infrastructure, and databases, performing backup and recovery operations, and even
 enabling disaster recovery protections through Oracle Data Guard . 
 

 
The following diagram illustrates this reference architecture.
 
 Description of the illustration azure-kube-exadata-db.png 
 azure-kube-exadata-db-oracle.zip 

 
The architecture has the following components:

 
 
- Regions 
An Oracle Cloud
 Infrastructure region is a localized geographic area that contains one or more data centers,
 called availability domains. Regions are independent of other regions, and vast
 distances can separate them (across countries or even continents).
 

 
An Azure region is a geographical area in which one or more physical Azure data centers, called availability zones, reside. Regions are independent of
 other regions, and vast distances can separate them (across countries or even
 continents).
 

 
 Azure and OCI regions are localized geographic areas. For Oracle Database@Azure , an Azure region is connected to an OCI region, with availability zones (AZs) in Azure connected to availability domains (ADs) in OCI. Azure and OCI region pairs are selected to minimize distance and latency.
 

 
 
- Azure availability zone 
An availability zone is a
 physically separate data center within a region that is designed to be available
 and fault tolerant. Availability zones are close enough to have low-latency
 connections to other availability zones.

 
Subnet delegation is
 Microsoft's ability to inject a managed service, specifically a
 platform-as-a-service service, directly into your virtual network.

 
 
- Microsoft Azure Virtual Network 
Microsoft Azure Virtual Network (VNet) is
 the fundamental building block for your private network in
 Azure. VNet enables many types of Azure resources, such as
 Azure virtual machines (VM), to securely communicate with
 each other, the internet, and on-premises networks.

 
Subnet delegation is Microsoft's ability to inject
 a managed service, specifically a platform-as-a-service service, directly into
 your virtual network.

 
 
- Exadata Database Service on Dedicated
 Infrastructure 
 Oracle Exadata Database
 Service delivers proven Oracle Database capabilities on purpose-built, optimized Oracle Exadata Cloud Infrastructure in the public cloud. Built-in cloud automation, elastic resource scaling,
 security, and fast performance for OLTP, in-memory analytics, and converged
 Oracle Database workloads help simplify management and reduce costs.
 

 
 Oracle Exadata Cloud Infrastructure brings more CPU cores, increased storage, and a faster network fabric to the
 public cloud. Oracle Exadata storage servers include Exadata RDMA Memory
 (XRMEM), creating an additional tier of storage, boosting overall system
 performance. Exadata combines XRMEM with innovative RDMA algorithms that bypass
 the network and I/O stack, eliminating expensive CPU interrupts and context
 switches.
 

 
 Oracle Exadata Cloud Infrastructure increases the throughput of its 100 Gbps active-active Remote Direct Memory
 Access over Converged Ethernet (RoCE) internal network fabric, providing a
 faster interconnect than previous generations with extremely low-latency between
 all compute and storage servers.
 

 
 
- Oracle Database Autonomous
 Recovery Service 
 Oracle Database Autonomous
 Recovery Service is a fully managed service designed to protect Oracle Databases from data
 loss and cyber threats. It offers faster backups with reduced database overhead,
 reliable recovery with validated backups, and real-time protection enabling
 recovery to within less than a second of an outage or ransomware attack. This
 service provides a centralized data protection dashboard and is recommended for
 backing up Oracle Databases.
 

 
 
- Azure Kubernetes Services 
Azure Kubernetes Service
 (AKS) is a managed Kubernetes service offered by Microsoft Azure to deploy and
 manage containerized applications. A Kubernetes cluster can contain multiple
 pods.

 
 
- Oracle Database@Azure 
 Oracle Database@Azure is the Oracle Database service ( Oracle Exadata Database Service on Dedicated
 Infrastructure and Oracle Autonomous Database Serverless ) running on Oracle Cloud Infrastructure (OCI), deployed in Microsoft Azure
 data centers. The service offers features and price parity with OCI, users
 purchase the service on Azure Marketplace.
 

 
 Oracle Database@Azure integrates Oracle Exadata Database
 Service , Oracle Real Application Clusters (Oracle
 RAC) , and Oracle Data Guard technologies into the Azure platform. Users manage the service on the Azure
 console and with Azure automation tools. The service is deployed in Azure
 Virtual Network (VNet) and integrated with the Azure identity and access
 management system. The OCI and Oracle Database generic metrics and audit logs
 are natively available in Azure. The service requires users to have an Azure
 subscription and an OCI tenancy. Oracle Autonomous Database is built on Oracle Exadata Cloud Infrastructure , is self-managing, self-securing, and self-repairing, helping eliminate
 manual database management and human errors. Autonomous Database enables development of scalable AI-powered apps with any data using built-in
 AI capabilities using your choice of large language model (LLM) and deployment
 location.
 

 
Both Oracle Exadata Database
 Service and Oracle Autonomous Database Serverless are easily provisioned through the native Azure Portal, enabling access to
 the broader Azure ecosystem.
 

 
Customer commercial benefits
 include using Azure commitments (MACC) for procuring Oracle Exadata Database
 Service , OCI Object Storage and Oracle Cloud Infrastructure
 Networking Data Transfer fees. It is possible to leverage existing Oracle licenses as
 BYOL as well as license included, a collaborative support model and procurement
 in Microsoft Azure Marketplace, all presented as one unified
 bill.
 

 
 
- Control Plane 
A Kubernetes control plane manages the resources for the worker nodes and pods within a Kubernetes cluster. The control plane components detect and respond to events, perform scheduling, and move cluster resources.

 
 
- Object storage 
 OCI Object Storage provides quick access to large amounts of structured and unstructured data of any content type, including database backups, analytic data, and rich content such as images and videos. You can safely and securely store data dire
