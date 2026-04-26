# Implement Oracle Database Autonomous Recovery Service with Oracle Database@Azure

- Source: https://docs.oracle.com/en/solutions/implement-recovery-service-db-at-azure/index.html
- Date: 2025-01
- Type: reference-architecture
- Services: exacs, azure
- Tags: database, multicloud, azure, ha-dr

## Summary (catalog)

Autonomous Recovery Service for ExaCS backups on Database@Azure. Automated backup management with real-time protection and point-in-time recovery capabilities.

## Architecture (fetched from source)

Architecture

 

 
This reference architecture represents Oracle Database@Azure configured for Oracle Database Autonomous
 Recovery Service with the option to choose between Azure or OCI as the backup location.
 

 
The backup replication of Oracle Database Autonomous
 Recovery Service uses the best high-availability architecture available in that region. Backups are
 consistently replicated to another availability domain (AD) or fault domain (if another
 AD is not available) in OCI. In a multicloud deployment, the backups are replicated in
 the same region into a second availability zone (AZ), or fault domain (if another AZ is
 not available) in Azure . For cross region backups,
 use Oracle Data Guard to replicate databases from primary to standby region and backup each region with
 local recovery service. Any backups in the service can be restored across availability
 domains, zones, and regions. Oracle Database Autonomous
 Recovery Service uses a backup subnet private endpoint for enhanced security and seamless integration.
 It's recommended to leverage separate private subnets to create a private endpoint for
 Oracle Database Autonomous
 Recovery Service . While designing subnets for your private endpoint, ensure there are available IP's
 in the CIDR block to assign for the Oracle Database Autonomous
 Recovery Service private endpoint.
 

 
Applications can continue to use databases with minimal to no impact of
 database performance as backup operations are offloaded to Oracle Database Autonomous
 Recovery Service and database resources can be utilized for business needs rather than backup cycles. 
 

 
The following diagram illustrates this reference architecture.

 
 Description of the illustration db-autonomous-recovery-dbatazure.png 

 db-autonomous-recovery-dbatazure.zip 

 
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

 
 
- Azure Route table (User Defined Route –
 UDR) 
Virtual route tables contain rules
 to route traffic from subnets to destinations outside a
 VNet, typically through gateways. Route tables are
 associated with subnets in a VNet.

 
 
- Azure Virtual Network Gateway 
Azure
 Virtual Network Gateway establishes secure, cross-premises
 connectivity between an Azure virtual network and an
 on-premises network. It allows you to create a hybrid
 network that spans your data center and
 Azure.

 
 
 
 Oracle Cloud
 Infrastructure architecture has the following components:
 

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that contains one or more data centers, called availability domains. Regions are independent of other regions, and vast distances can separate them (across countries or even continents).
 

 
 
- Availability domains 
Availability domains are standalone, independent data centers within a region. The physical resources in each availability domain are isolated from the resources in the other availability domains, which provides fault tolerance. Availability domains don’t share infrastructure such as power or cooling, or the internal availability domain network. So, a failure at one availability domain shouldn't affect the other availability domains in the region.

 
 
- Virtual cloud network (VCN) and subnets 
A VCN is a customizable, software-defined network that you set up in an Oracle Cloud
 Infrastructure region. Like traditional data center networks, VCNs give you control over your network environment. A VCN can have multiple non-overlapping CIDR blocks that you can change after you create the VCN. You can segment a VCN into subnets, which can be scoped to a region or to an availability domain. Each subnet consists of a contiguous range of addresses that don't overlap with the other subnets in the VCN. You can change the size of a subnet after creation. A subnet can be public or private. 
 

 
 
- Route table 
Virtual route tables contain rules to route traffic from subnets to destinations outside a VCN, typically through gateways.

 
 
- Security list 
For each subnet, you can create security rules that specify the source, destination, and type of traffic that must be allowed in and out of the subnet.

 
 
- Network security group (NSG) 
Network security group (NSG) acts as a virtual firewall for your cloud resources. With the zero-trust security model of Oracle Cloud
 Infrastructure , all traffic is denied, and you can control the network traffic inside a VCN. An NSG consists of a set of ingress and egress security rules that apply to only a specified set of VNICs in a single VCN.
 

 
 
- Oracle Database Autonomous
 Recovery Service 
 Oracle Database Autonomous
 Recovery Service is a fully managed service designed to protect Oracle Databases from data
 loss and cyber threats. It offers faster backups with reduced database overhead,
 reliable recovery with validated backups, and real-time protection enabling
 recovery to within less than a second of an outage or ransomware attack. This
 service provides a centralized data protection dashboard and is recommended for
 backing up Oracle Databases.
 

 
 
 
- Exadata Database Service 

 enables you to leverage the power of Exadata in
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
 Infrastructure (OCI), deployed in Microsoft Azure data
 centers. The service offers features and price
 parity with OCI, users purchase the service on
 Azure Marketplace.
 

 
 Oracle Database@Azure integrates Oracle Exadata Database
 Service , Oracle Real Application Clusters (Oracle
 RAC) , and Oracle Data Guard technologies into the Azure platform. Users
 manage the service on the Azure console and with
 Azure automation tools. The service is deployed in
 Azure Virtual Network (VNet) and integrated with
 the Azure identity and access management system.
 The OCI and Oracle Database generic metrics and audit logs are natively
 availab
