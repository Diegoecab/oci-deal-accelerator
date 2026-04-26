# Implement cross-region disaster recovery for Exadata Database on Oracle Database@Azure

- Source: https://docs.oracle.com/en/solutions/exadb-dr-on-db-azure/index.html
- Date: 2025-01
- Type: reference-architecture
- Services: exacs, adg, azure, fsdr
- Tags: database, multicloud, azure, ha-dr

## Summary (catalog)

Cross-region DR for ExaCS on Database@Azure. OCI-managed networks for peering (better performance, first 10 TB/month free). Data Guard for cross-region replication, FSDR for automated failover orchestration.

## Architecture (fetched from source)

Architecture

 

 
This architecture shows a high-availability, containerized Azure Kubernetes
 Service (AKS) application with Oracle Exadata Database
 Service on Oracle AI Database@Azure in a cross-region, disaster recovery topology.
 

 
A high-availability, containerized Azure Kubernetes Service (AKS)
 application is deployed in two Azure regions: a primary region and a standby region. The
 container images are stored in the Azure container registry and are replicated between
 primary and standby regions. Users access the application externally through a public
 load balancer. 

 
For data protection, the Oracle Database is running in an Exadata virtual machine (VM) cluster in the primary region, with Oracle Data Guard or Oracle Active Data Guard replicating the data to the standby database running on
 an Exadata VM cluster in the standby region.
 

 
The database transparent data encryption (TDE) keys are stored in Oracle Cloud Infrastructure Vault and replicated between the Azure and OCI regions. The automatic backups are in OCI
 for both the primary and standby regions. Customers can use Oracle Cloud
 Infrastructure Object Storage or Oracle Database Autonomous
 Recovery Service as the preferred storage solution.
 

 
The Oracle Exadata Database
 Service on Oracle AI Database@Azure network is connected to the Exadata client subnet by using a dynamic routing gateway
 (DRG) managed by Oracle. A DRG is also required to create a peer connection between VCNs
 in different regions. Because only one DRG is allowed per VCN in OCI, a second VCN with
 its own DRG is required to connect the primary and standby VCNs in each region. In this
 example:
 

 
 
- The primary Exadata VM cluster is deployed in the VCN
 Primary VCN client subnet (10.5.0.0/24).
 
 
- The Hub VCN Primary VCN for the transit network
 is 10.15.0.0/29.
 
 
- The standby Exadata VM cluster is deployed in the VCN
 Standby VCN client subnet (10.6.0.0/24).
 
 
- The Hub VCN Standby VCN for the transit network
 is 10.16.0.0/29.
 
 
 
No subnet is required for the Hub VCNs to enable transit routing, therefore
 these VCNs can use a very small network. The VCNs on the OCI child site are created
 after the Oracle Exadata Database
 Service VM clusters on Oracle AI Database@Azure have been created for the primary and standby databases. 
 

 
The following diagram illustrates the architecture:

 
 Description of the illustration exadb-dr-db-azure.png 

 exadb-dr-db-azure-oracle.zip 

 
Microsoft Azure provides the following components:

 
 
- Microsoft Azure region 
An Azure region is a
 geographical area in which one or more physical Azure data centers, called
 availability zones, reside. Regions are independent of other regions, and vast
 distances can separate them (across countries or even continents).

 
Azure and OCI regions are localized geographic areas. For Oracle
 Database@Azure, an Azure region is connected to an OCI region, with availability
 zones (AZs) in Azure connected to availability domains (ADs) in OCI. Azure and
 OCI region pairs are selected to minimize distance and latency.

 
 
- Microsoft Azure availability zone 
An availability
 zone is a physically-separate data center within a region that is designed to be
 highly available and fault tolerant. Availability zones are close enough to have
 low-latency connections to other availability zones.

 
 
- Microsoft Azure Virtual Netwok 
Microsoft Azure
 Virtual Network (VNet) is the fundamental building block for a private network
 in Azure. VNet enables many types of Azure resources, such as Azure virtual
 machines (VM), to securely communicate with each other, the internet, and with
 on-premises networks.

 
 
- Microsoft Azure Delegated Subnet 
Subnet delegation alows
 you to inject a managed service, specifically a platform-as-a-service (PaaS)
 service, directly into your virtual network. A delegated subnet can be a home
 for an externally managed service inside of your virtual network so that the
 external service acts as a virtual network resource, even though it is an
 external PaaS service.

 
 
- Microsoft Azure VNIC 
The services in Azure data centers have physical
 network interface cards (NICs). Virtual machine instances communicate using
 virtual NICs (VNICs) associated with the physical NICs. Each instance has a
 primary VNIC that's automatically created and attached during launch and is
 available during the instance's lifetime.

 
 
- Microsoft Azure Route table 
Virtual route tables
 contain rules to route traffic from subnets to destinations outside a VNet,
 typically through gateways. Route tables are associated with subnets in a
 VNet.

 
 
- Azure Virtual Network Gateway 
Azure Virtual
 Network Gateway service establishes secure, cross-premises connectivity between
 an Azure virtual network and an on-premises network. It allows you to create a
 hybrid network that spans your data center and Azure.

 
 
 
 Oracle Cloud
 Infrastructure provides the following components:
 

 
 
- OCI region 
An OCI region
 is a localized geographic area that contains one
 or more data centers, hosting availability
 domains. Regions are independent of other regions,
 and vast distances can separate them (across
 countries or even continents).

 
 
- Availability domain 
Availability domains are standalone, independent data centers within a region. The physical resources in each availability domain are isolated from the resources in the other availability domains, which provides fault tolerance. Availability domains don’t share infrastructure such as power or cooling, or the internal availability domain network. So, a failure at one availability domain shouldn't affect the other availability domains in the region.

 
 
- Virtual cloud network (VCN) and subnets 
A virtual cloud
 network (VCN) is a customizable, software-defined
 network that you set up in an OCI region. Like
 traditional data center networks, VCNs give you
 control over your network environment. A VCN can
 have multiple non-overlapping classless
 inter-domain routing (CIDR) blocks that you can
 change after you create the VCN. You can segment a
 VCN into subnets, which can be scoped to a region
 or to an availability domain. Each subnet consists
 of a contiguous range of addresses that don't
 overlap with the other subnets in the VCN. You can
 change the size of a subnet after creation. A
 subnet can be public or private. 

 
 
- Route table 
Virtual
 route tables contain rules to route traffic from
 subnets to destinations outside a VCN, typically
 through gateways.

 
 
- Security list 
For
 each subnet, you can create security rules that
 specify the source, destination, and type of
 traffic that is allowed in and out of the
 subnet.

 
 
- Dynamic routing gateway
 (DRG) 
The DRG is a
 virtual router that provides a path for private
 network traffic between VCNs in the same region,
 between a VCN and a network outside the region,
 such as a VCN in another OCI region, an
 on-premises network, or a network in another cloud
 provider.

 
 
- Service
 gateway 
A
 service gateway provides access from a VCN to
 other services, such as Oracle Cloud
 Infrastructure Object Storage . The traffic from the VCN to the Oracle service
 travels over the Oracle network fabric and does
 not traverse the internet.
 

 
 
- Local
 peering 
Local peering allows two VCNs
 within the same OCI region to communicate directly
 using private IP addresses. This communication
 does not traverse the internet or your on-premises
 network. Local peering is enabled by a Local
 Peering Gateway (LPG), which serves as the
 connection point between VCNs. Configure an LPG in
 each VCN and establish a peering relationship to
 allow instances, load balancers, and other
 resources in one VCN to securely access resources
 in another VCN within the same region.

 
 
- Network security group
 (NSG) 
NSGs act as virtual firewalls for your cloud resources. With the zero-trust security model of OCI you cont
