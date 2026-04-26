# Deploy Active Data Guard Far Sync to protect data across Oracle Database@Azure regions

- Source: https://docs.oracle.com/en/solutions/active-data-guard-far-sync-oracle-db-at-azure/index.html
- Date: 2025-02
- Type: reference-architecture
- Services: exacs, adg, azure
- Tags: database, multicloud, azure, ha-dr

## Summary (catalog)

Far Sync instance for zero data loss protection across Azure regions. Synchronous redo transport to Far Sync, async to remote standby. Eliminates performance impact of synchronous shipping over long distances.

## Architecture (fetched from source)

Architecture

 

 
This reference architecture shows a cross-region disaster recovery with Active Data Guard .
 

 
Two Active Data Guard far sync instances are created in the corresponding Oracle Cloud
 Infrastructure (OCI) regions. The primary database in Toronto sends the redo data in SYNC mode to
 the local far sync instance in Toronto, which forwards the redo data in ASYNC mode to
 the standby database in the remote Sydney region.
 

 
After a role switch and the database in Sydney becomes the primary, it sends
 the redo data in SYNC mode to its local far sync instance in Sydney, which forwards the
 redo data in ASYNC mode to the standby database in the remote Toronto region.

 
The Oracle Exadata Database
 Service on the Oracle Database@Azure network is connected to the Exadata client subnet using a dynamic routing gateway
 (DRG) managed by Oracle. A DRG is also required to create a peer connection between VCNs
 in different regions. Because only one DRG is allowed per VCN in OCI, a second VCN with
 its own DRG is required to connect the primary and standby VCNs in each region.
 

 
The application is replicated across regions to access the database in the same region
 and achieve the lowest latency and highest performance.

 
The following diagram illustrates this reference architecture.

 
 Description of the illustration active-data-guard-far-sync-dba.png 

 active-data-guard-far-sync-dba-oracle.zip 

 
 Microsoft Azure provides the following components:
 

 
 
- Azure Region 
An Azure region is a geographical area in which one or more
 physical Azure data centers, called availability zones, reside. Regions
 are independent of other regions, and vast distances can
 separate them (across countries or even continents).
 

 
 Azure and OCI regions are localized geographic areas. For Oracle Database@Azure , an Azure region is connected to an OCI region, with availability
 zones (AZs) in Azure connected to availability domains (ADs) in OCI. Azure and OCI region pairs are selected to minimize distance
 and
 latency.
 

 
 
- Azure VNet 
Microsoft Azure Virtual Network (VNet) is
 the fundamental building block for your private network in
 Azure. VNet enables many types of Azure resources, such as
 Azure virtual machines (VM), to securely communicate with
 each other, the internet, and on-premises networks.

 
 
- Azure Delegated Subnet 
Subnet delegation is
 Microsoft's ability to inject a managed service,
 specifically a platform-as-a-service (PaaS) service,
 directly into your virtual network. This allows you to
 designate or delegate a subnet to be a home for an external
 managed service inside of your virtual network, such that
 external service acts as a virtual network resource, even
 though it is an external PaaS service.

 
 
- Azure VNIC 
The services in Azure
 data centers have physical network interface cards (NICs).
 Virtual machine instances communicate using virtual NICs
 (VNICs) associated with the physical NICs. Each instance has
 a primary VNIC that's automatically created and attached
 during launch and is available during the instance's
 lifetime.

 
 
 
 Oracle Cloud
 Infrastructure provides the following components:
 

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that contains one or more data centers, called availability domains. Regions are independent of other regions, and vast distances can separate them (across countries or even continents).
 

 
 
- Virtual cloud network (VCN) and subnet 
A VCN is a customizable, software-defined network that you set up in an Oracle Cloud
 Infrastructure region. Like traditional data center networks, VCNs give you control over your network environment. A VCN can have multiple non-overlapping CIDR blocks that you can change after you create the VCN. You can segment a VCN into subnets, which can be scoped to a region or to an availability domain. Each subnet consists of a contiguous range of addresses that don't overlap with the other subnets in the VCN. You can change the size of a subnet after creation. A subnet can be public or private. 
 

 
 
- Route table 
Virtual route tables contain rules to route traffic from subnets to destinations outside a VCN, typically through gateways.

 
 
- Security list 
For each subnet, you can create security rules that specify the source, destination, and type of traffic that must be allowed in and out of the subnet.

 
 
- Dynamic routing gateway (DRG) 
The DRG is a virtual router that provides a path for private network traffic between VCNs in the same region, between a VCN and a network outside the region, such as a VCN in another Oracle Cloud
 Infrastructure region, an on-premises network, or a network in another cloud provider.
 

 
 
- Local peering gateway (LPG) 
An LPG enables you to peer one VCN with another
 VCN in the same region. Peering means the VCNs communicate using private IP
 addresses, without the traffic traversing the internet or routing through your
 on-premises network.

 
 
- Data Guard 
 Oracle Data Guard and Oracle Active Data Guard provide a comprehensive set of services that create, maintain, manage, and monitor one or more standby databases and that enable production Oracle databases to remain available without interruption. Oracle Data Guard maintains these standby databases as copies of the production database by using in-memory replication. If the production database becomes unavailable due to a planned or an unplanned outage, Oracle Data Guard can switch any standby database to the production role, minimizing the downtime associated with the outage. Oracle Active Data Guard provides the additional ability to offload read-mostly workloads to standby databases and also provides advanced data protection features.
 

 
 
- Active Data Guard Far Sync 
Oracle Active Data Guard Far Sync is a lightweight Oracle database instance that receives redo data
 synchronously from the primary database and forwards it asynchronously to one or
 more standby databases. It ensures zero data loss at any distance with minimal
 impact on the primary database performance and without requiring a local
 synchronous standby database.
 

 
 
- Exadata Database Service on Dedicated Infrastructure 
 Oracle Exadata Database Service on Dedicated
 Infrastructure enables you to leverage the power of Exadata in
 the cloud. Oracle Exadata Database
 Service delivers proven Oracle Database capabilities on purpose-built, optimized Oracle
 Exadata infrastructure in the public cloud.
 Built-in cloud automation, elastic resource
 scaling, security, and fast performance for all
 Oracle Database workloads helps you simplify management and
 reduce costs.
 

 
 
- Oracle Database@Azure 
 Oracle Database@Azure is the Oracle Database service ( Oracle Exadata Database Service on Dedicated
 Infrastructure and Oracle Autonomous Database Serverless ) running on Oracle Cloud
 Infrastructure (OCI), deployed in Microsoft Azure data centers. The service offers features and price parity with OCI. Purchase the service on Azure Marketplace.
 

 
 Oracle Database@Azure integrates Oracle Exadata Database
 Service , Oracle Real Application Clusters (Oracle
 RAC) , and Oracle Data Guard technologies into the Azure platform. Users manage the service on the Azure console and with Azure automation tools. The service is deployed in Azure Virtual Network (VNet) and integrated with the Azure identity and access management system. The OCI and Oracle Database generic metrics and audit logs are natively available in Azure. The service requires users to have an Azure subscription and an OCI tenancy. 
 

 
 Autonomous Database is built on Oracle Exadata infrastructure, is self-managing, self-securing, and self-repairing, helping eliminate manual database management and human errors. Autonomous Database enables development of scalable AI-powered apps with any data using built-in AI capabilities using your choice of large language model (LLM) and deploymen
