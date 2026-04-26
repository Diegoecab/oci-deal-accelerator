# Deploy Oracle Autonomous Database on Oracle Database@Azure

- Source: https://docs.oracle.com/en/solutions/deploy-autonomous-database-db-at-azure/index.html
- Date: 2024-10
- Type: reference-architecture
- Services: adb-s, adg, azure
- Tags: database, multicloud, azure, ha-dr, autonomous

## Summary (catalog)

Multi-AZ deployment of ADB-S on Database@Azure with Autonomous Data Guard. Recommends VNet peering between app and DB VNets, TAC for availability, and ADG standby in a different AZ for automatic failover.

## Architecture (fetched from source)

Architecture

 

 
This reference architecture describes some best practices for deploying Oracle Autonomous Database in a Microsoft Azure multi-availability zone (AZ) region.
 

 
Business continuity practices and high availability topologies should always be
 considered when designing mission-critical database applications. The architecture below
 shows a containerized application using Azure Kubernetes Service (AKS). The container images are stored in the Azure container registry. Users access the application externally through a public load
 balancer. Since Oracle Autonomous Database is a PaaS service, there is no administrative control over into which AZ the
 Autonomous Database will be provisioned. However, in the unlikely event of an Azure AZ failure, Oracle ensures that a local Autonomous Data Guard standby is always
 deployed in a different AZ (data center) from its primary.
 

 

 
Note:
If application-to-database-availability-zone affinity is required, Autonomous Database
 provides a user queryable database view to determine its AZ placement. Once the AZ of
 the Autonomous Database is determined, networking can be aligned as appropriate.
 

 
In the diagram below, the application virtual network (VNet) connects to the database
 VNet in availability zone 1 (AZ1) using VNet peering. The AKS-hosted application
 accesses the database via a private endpoint that connects to the Oracle Database@Azure delegated subnet. If multi-AZ business continuity is required, Autonomous Data Guard
 can optionally be enabled, in which case, it is availability zone 2 (AZ2). Autonomous
 Data Guard keeps the primary database and local standby in sync and automatically fails
 over in the case of a primary AZ outage. Oracle-managed automatic backups are always
 enabled by default.
 

 
The following diagram illustrates this reference architecture.

 
 Description of the illustration autonomous-database-db-azure-diagram.png 

 autonomous-database-db-azure-diagram-oracle.zip 

 
The architecture has the following components:

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that
 contains one or more data centers, called
 availability domains. Regions are independent of
 other regions, and vast distances can separate
 them (across countries or even
 continents).
 

 
 
- Virtual cloud network (VCN) and subnets 
A VCN is a customizable,
 software-defined network that you set up in an Oracle Cloud
 Infrastructure region. Like traditional data center networks,
 VCNs give you control over your network
 environment. A VCN can have multiple
 non-overlapping CIDR blocks that you can change
 after you create the VCN. You can segment a VCN
 into subnets, which can be scoped to a region or
 to an availability domain. Each subnet consists of
 a contiguous range of addresses that don't overlap
 with the other subnets in the VCN. You can change
 the size of a subnet after creation. A subnet can
 be public or private. 
 

 
 
- Autonomous
 Database 

 Oracle Autonomous Database is a fully managed, preconfigured database
 environments that you can use for transaction
 processing and data warehousing workloads. You do
 not need to configure or manage any hardware, or
 install any software. Oracle Cloud
 Infrastructure handles creating the database, as well as
 backing up, patching, upgrading, and tuning the
 database.
 

 
 
- Object storage 

 Oracle Cloud
 Infrastructure Object Storage provides quick access to large
 amounts of structured and unstructured data of any
 content type, including database backups, analytic
 data, and rich content such as images and videos.
 You can safely and securely store and then
 retrieve data directly from the internet or from
 within the cloud platform. You can scale storage
 without experiencing any degradation in
 performance or service reliability. Use standard
 storage for "hot" storage that you need to access
 quickly, immediately, and frequently. Use archive
 storage for "cold" storage that you retain for
 long periods of time and seldom or rarely
 access.
 

 
 
- Azure Container Registry 
 Azure Container Registry (ACR) is a managed service for storing and managing
 container images and related artifacts.
 

 
 
- Azure availability zone 
An availability zone is a physically separate data
 center within a region designed to be available and fault-tolerant. Availability
 zones are close enough to have low-latency connections to other availability
 zones.

 
 
- Azure Kubernetes Service 
 Azure Kubernetes Service (AKS) is a managed Kubernetes service offered by Microsoft Azure .
 

 
 
- Azure Load Balancer 
 Azure Load Balancer provides automated traffic distribution from a single entry
 point to multiple servers in the back end.
 

 
 
- Microsoft Azure Virtual Network 
 Microsoft Azure Virtual Network (VNet) is the fundamental building block for your private
 network in Azure. VNet enables many Azure resources, such as Azure virtual machines (VMs), to securely communicate with
 each other, the internet, and on-premises networks.
 

 
 
- Oracle Database@Azure 
 Oracle Database@Azure is an Oracle Cloud Database service that runs
 Oracle Database workloads in your Azure
 environment. All hardware for Oracle Database@Azure is colocated in Azure's data centers and uses
 Azure networking. The service benefits from the
 simplicity, security, and low latency of a single
 operating environment within Azure. Federated
 identity and access management for Oracle Database@Azure is provided by Microsoft Entra ID. Oracle Database metrics and audit logs are natively available
 in Azure. The service requires that users have an
 Azure tenancy and an OCI tenancy.
 

 
 
 

 

 
 
Recommendations

 

 
 Use the following recommendations as a starting point.
 Your requirements might differ from the architecture described here. 
 

 
 
- Primary and standby database subnets should be in distinct VNets
 configured with non-overlapping IP classless inter-domain routing (CIDR)
 ranges. 
 
- The application tier (AKS, Docker, VMs, etc.) should span at least two
 AZs, with the application VNet peered to both the primary and standby VNet of the
 Autonomous Database .
 
 
- Optionally, client applications can be configured to use Oracle
 transparent application continuity (TAP) to maximize availability during planned and
 unplanned outages. 
 
 

 

 
 
Explore More

 

 
For more details about the components and considerations shared in this
 document, please refer to the following links.

 
Review these additional resources:

 
 
- Oracle Autonomous
 Database Serverless 
 
- Oracle
 Database@Azure 
 
- Learn about selecting
 network topologies for Oracle Database@Azure 
 
- Configure Application Continuity on Autonomous
 Database in Using Oracle Autonomous
 Database Serverless 
 
- Oracle
 Database@Azure Videos 
 
- Oracle Cloud
 Infrastructure Documentation 
 
- Best practices framework
 for Oracle Cloud Infrastructure 
 
- Oracle Cloud Cost
 Estimator 
 
- Cloud Adoption
 Framework 
 
 

 

 
 
Acknowledgments

 

 
 
- Authors : Domenick Ficarella, Can Tuzla, Martin
 Gubar 
 
- Contributors : Wei Han, John Sulyok 
 
 

 

 

 

 

 
 Title and Copyright Information 

 

 
Deploy Autonomous Database on Oracle Database@Azure

 
G13089-02

 
October 2024

 
 Copyright © 2024, 

Oracle and/or its affiliates.
