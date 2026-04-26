# Implement disaster recovery with multi-region standby on Oracle Database@Azure

- Source: https://docs.oracle.com/en/solutions/multi-region-standby-dr-db-at-azure/index.html
- Date: 2025-04
- Type: reference-architecture
- Services: exacs, adg, azure
- Tags: database, multicloud, azure, ha-dr

## Summary (catalog)

Multi-region DR for ExaCS on Database@Azure using Data Guard. Cross-region standby with switchover/failover capabilities. Includes network topology for Azure-to-Azure cross-region connectivity.

## Architecture (fetched from source)

Architecture

 

 
This architecture shows Oracle Exadata Database Service on Dedicated
 Infrastructure on Oracle Database@Azure in a multi-region disaster recovery topology using two remote standby
 databases.
 

 
The following diagram illustrates this reference architecture.

 
 Description of the illustration multi-region-standby-dr-db-azure-arch.png 

 multi-region-standby-dr-db-azure-arch-oracle.zip 

 
The Oracle Database runs in an Exadata virtual machine (VM) cluster in the Primary region. For data
 protection and disaster recovery, Oracle Active Data Guard replicates the data to two standby databases running on Exadata VM clusters in two
 different Standby regions. A remote standby database setup ensures data protection
 against regional failures and can also be used to offload read-only query processing.
 Replicate the application across regions to avoid higher latency after switching over to
 a Standby database.
 

 
You can route Active Data Guard traffic through the Azure network. However, this architecture focuses on Active Data Guard network traffic through the OCI network to optimize network throughput and
 latency.
 

 
The Oracle Exadata Database Service on Dedicated
 Infrastructure on Oracle Database@Azure network is connected to the Exadata client subnet using a Dynamic Routing Gateway
 (DRG) managed by Oracle. A DRG is also required to create a peer connection between
 Virtual Cloud Networks (VCNs) in different regions. Because only one DRG is allowed per
 VCN in OCI, a second VCN acting as a Hub VCN with its own DRG is required to connect the
 primary and standby VCNs in each region. In this architecture:
 

 
 
- The primary Exadata VM cluster is deployed in
 Region 1 in VCN1 with CIDR
 10.10.0.0/16 .
 
 
- The hub VCN in the primary Region 1 
 is HubVCN1 with CIDR 10.11.0.0/16 .
 
 
- The first standby Exadata VM cluster is deployed in
 Region 2 in VCN2 with CIDR
 10.20.0.0/16 .
 
 
- The hub VCN in the first standby region is HubVCN2 with
 CIDR 10.22.0.0/16 .
 
 
- The second standby Exadata VM cluster is deployed in Region
 3 in VCN3 with CIDR
 10.30.0.0/16 .
 
 
- The hub VCN in the second standby region is HubVCN3 
 with CIDR 10.33.0.0/16 .
 
 
 
No subnet is required for the hub VCNs to enable transit
 routing, therefore these VCNs can use very small IP CIDR ranges. The VCNs on the OCI
 child site are created after the Oracle Exadata Database Service on Dedicated
 Infrastructure VM clusters on Oracle Database@Azure are created for the Primary and Standby databases.
 

 
Microsoft Azure provides the following components:

 
 
- Azure region 
An Azure region is a geographical area in which one or more physical Azure data centers, called availability zones, reside. Regions are independent of other regions, and vast distances can separate them (across countries or even continents).
 

 
 Azure and OCI regions are localized geographic areas. For Oracle Database@Azure , an Azure region is connected to an OCI region, with availability zones (AZs) in Azure connected to availability domains (ADs) in OCI. Azure and OCI region pairs are selected to minimize distance and latency.
 

 
 
- Azure availability zone 
Azure availability zones are physically separate locations within an Azure region, designed to ensure high availability and resiliency by providing independent power, cooling, and networking.

 
 
- Azure Virtual Network (VNet) 
Azure
 Virtual Network (VNet) is the fundamental building block for
 your private network in Azure. VNet enables many types of
 Azure resources, such as Azure virtual machines (VMs), to
 securely communicate with each other, the internet, and
 on-premises networks.

 
 
- Azure delegated subnet 
A delegated subnet allows you to insert a managed service, specifically a platform-as-a-service (PaaS) service, directly into your virtual network as a resource. You have full integration management of external PaaS services within your virtual networks.

 
 
- Azure Virtual Network Interface Card (VNIC) 
The
 services in Azure data centers have physical network
 interface cards (NICs). Virtual machine instances
 communicate using virtual NICs (VNICs) associated with the
 physical NICs. Each instance has a primary VNIC that's
 automatically created and attached during launch and is
 available during the instance's
 lifetime.

 
 
 
OCI provides the following components:

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that contains one or more data centers, hosting availability domains. Regions are independent of other regions, and vast distances can separate them (across countries or even continents).
 

 
 
- Availability domains 
Availability domains are standalone, independent data centers within a region. The physical resources in each availability domain are isolated from the resources in the other availability domains, which provides fault tolerance. Availability domains don’t share infrastructure such as power or cooling, or the internal availability domain network. So, a failure at one availability domain shouldn't affect the other availability domains in the region.

 
 
- Virtual cloud network (VCN) and subnets 
A VCN is a customizable, software-defined network that you set up in an Oracle Cloud
 Infrastructure region. Like traditional data center networks, VCNs give you control over your network environment. A VCN can have multiple non-overlapping CIDR blocks that you can change after you create the VCN. You can segment a VCN into subnets, which can be scoped to a region or to an availability domain. Each subnet consists of a contiguous range of addresses that don't overlap with the other subnets in the VCN. You can change the size of a subnet after creation. A subnet can be public or private. 
 

 
 
- Route table 
Virtual route tables contain rules to route traffic from subnets to destinations outside a VCN, typically through gateways.

 
 
- Local peering 
Local peering enables you to peer one VCN with another VCN in the same region. Peering means the VCNs communicate using private IP addresses, without the traffic traversing the internet or routing through your on-premises network.

 
 
- Dynamic routing gateway (DRG) 
The DRG is a virtual router that provides a path for private network traffic between VCNs in the same region, between a VCN and a network outside the region, such as a VCN in another Oracle Cloud
 Infrastructure region, an on-premises network, or a network in another cloud provider.
 

 
 
- Object storage 

 OCI Object Storage provides access to large amounts of structured
 and unstructured data of any content type,
 including database backups, analytic data, and
 rich content such as images and videos. You can
 safely and securely store data directly from the
 internet or from within the cloud platform. You
 can scale storage without experiencing any
 degradation in performance or service reliability.
 
 

 
Use standard storage for
 "hot" storage that you need to access quickly,
 immediately, and frequently. Use archive storage
 for "cold" storage that you retain for long
 periods of time and seldom or rarely
 access.

 
 
- Data Guard 
 Oracle Data Guard and Oracle Active Data Guard provide a comprehensive set of services that create, maintain, manage, and monitor one or more standby databases and that enable production Oracle databases to remain available without interruption. Oracle Data Guard maintains these standby databases as copies of the production database by using in-memory replication. If the production database becomes unavailable due to a planned or an unplanned outage, Oracle Data Guard can switch any standby database to the production role, minimizing the downtime associated with the outage. Oracle Active Data Guard provides the additional ability to offload read-mostly workloads to standby databases and also provides advanced data protection features.
 

 
 
- Oracle Database Autonomous
 Recovery Service 
 Oracle Databas
