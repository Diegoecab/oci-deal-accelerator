# Create a modern platform with Oracle Database@Azure, OCI GoldenGate, and Azure services

- Source: https://docs.oracle.com/en/solutions/modern-platform-oracle-db-at-azure/index.html
- Date: 2024-08
- Type: reference-architecture
- Services: goldengate, exacs, azure
- Tags: database, multicloud, azure, integration, data-platform

## Summary (catalog)

Modern data platform combining Database@Azure with Azure PaaS services. GoldenGate for real-time data synchronization between ExaCS and Azure SQL, Cosmos DB, or Synapse Analytics.

## Architecture (fetched from source)

Architecture

 

 
This architecture shows how you can use Oracle Database@Azure , Oracle Cloud Infrastructure GoldenGate, and Microsoft Azure services to load
 your data lake or data lakehouse infrastructure in Azure for processing machine
 learning (ML) and Analytics
 workloads.
 
 

 
The platforms are connected by an Oracle Cloud Infrastructure (OCI) Managed
 Network and a VCN that spans both regions and includes a local peering
 gateway. Oracle Database@Azure resides within the VCN in the Azure region and uses local peering to send
 data through the OCI Managed Network to the services located in the HUB VCN
 in OCI. OCI GoldenGate is accessible using a private endpoint (PE) from
 within the OCI network that secures access to OCI resources. 
 

 
In addition, Oracle Interconnect for Azure and a site-to-site VPN provide a path for data going from OCI to Azure.
 Data flows from the dynamic routing gateway on the OCI HUB VCN to the
 Site-to-Site VPN and Oracle Interconnect for Azure. The data from both of
 these sources flows through a virtual network gateway on the Azure VNet that
 includes the private link and private endpoint. From there, it flows to the
 Azure resources. 
 

 
The following diagram illustrates this reference architecture.
 
 Description of the illustration oracle-database-azure-services-platform.png 
 oracle-database-azure-services-platform-oracle.zip 

 
The architecture has the following Oracle Cloud
 Infrastructure (OCI) components:
 

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that
 contains one or more data centers, called
 availability domains. Regions are independent of
 other regions, and vast distances can separate
 them (across countries or even
 continents).
 

 
 
- Availability domains 
Availability domains
 are standalone, independent data centers within a
 region. The physical resources in each
 availability domain are isolated from the
 resources in the other availability domains, which
 provides fault tolerance. Availability domains
 don’t share infrastructure such as power or
 cooling, or the internal availability domain
 network. So, a failure at one availability domain
 shouldn't affect the other availability domains in
 the region.

 
 
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
 

 
 
- Dynamic routing gateway (DRG) 
The DRG is a virtual router that provides a path
 for private network traffic between VCNs in the same region,
 between a VCN and a network outside the region, such as a
 VCN in another Oracle Cloud
 Infrastructure region, an on-premises network, or a network in another
 cloud provider.
 

 
A DRG is required to set
 up a private interconnection using OCI FastConnect between a
 VCN in an OCI region and a VNet in an Azure region.

 
 
- Local
 peering gateway (LPG) 
An LPG enables you to
 peer one VCN with another VCN in the same region.
 Peering means the VCNs communicate using private
 IP addresses, without the traffic traversing the
 internet or routing through your on-premises
 network.

 
 
- Site-to-site VPN 
Provides a
 site-to-site IPSec VPN between your on-premises network and
 your VCN over a secure, encrypted connection.

 
 
- Network security group
 (NSG) 
Network
 security group (NSG) acts as a virtual firewall
 for your cloud resources. With the zero-trust
 security model of Oracle Cloud
 Infrastructure , all traffic is denied, and you can control the
 network traffic inside a VCN. An NSG consists of a
 set of ingress and egress security rules that
 apply to only a specified set of VNICs in a single
 VCN.
 

 
 
- Route table 
Virtual
 route tables contain rules to route traffic from
 subnets to destinations outside a VCN, typically
 through gateways.

 
 
- Service
 gateway 
The service gateway
 provides access from a VCN to other services, such
 as Oracle Cloud
 Infrastructure Object Storage . The traffic from the VCN to the Oracle service
 travels over the Oracle network fabric and does
 not traverse the internet.
 

 
 
- Oracle Exadata Database
 Service 
Oracle
 Exadata is an enterprise database platform that
 runs Oracle Database workloads of any scale and criticality with
 high performance, availability, and security.
 Exadata’s scale-out design employs unique
 optimizations that let transaction processing,
 analytics, machine learning, and mixed workloads
 run faster and more efficiently. Consolidating
 diverse Oracle Database workloads on Exadata platforms in enterprise
 data centers, on Oracle Cloud
 Infrastructure (OCI), and in multicloud environments helps
 organizations increase operational efficiency,
 reduce IT administration, and lower costs.
 

 
 Oracle Exadata Database
 Service enables you to leverage the power of Exadata in
 the cloud. Oracle Exadata Database
 Service delivers proven Oracle Database capabilities on purpose-built, optimized Oracle
 Exadata infrastructure in the public cloud and on
 Cloud@Customer. Built-in cloud automation, elastic
 resource scaling, security, and fast performance
 for all Oracle Database workloads helps you simplify management and
 reduce costs.
 

 
 
- Oracle Exadata Database Service on Dedicated
 Infrastructure 
 Oracle Exadata Database Service on Dedicated
 Infrastructure provides Oracle Exadata Database Machine as a service in an Oracle Cloud
 Infrastructure (OCI) data center. The Oracle Exadata Database Service on Dedicated
 Infrastructure instance is a virtual machine (VM) cluster that
 resides on Exadata racks in an OCI region.
 

 
Oracle Exadata Database Service
 delivers proven Oracle Database capabilities on
 purpose-built, optimized Oracle Exadata infrastructure in
 the public cloud. Built-in cloud automation, elastic
 resource scaling, security, and fast performance for OLTP,
 in-memory analytics, and converged Oracle Database workloads
 help simplify management and reduce costs.

 
Exadata Cloud Infrastructure X9M brings more CPU cores,
 increased storage, and a faster network fabric to the public
 cloud. Exadata X9M storage servers include Exadata RDMA
 Memory (XRMEM), creating an additional tier of storage,
 boosting overall system performance. Exadata X9M combines
 XRMEM with innovative RDMA algorithms that bypass the
 network and I/O stack, eliminating expensive CPU interrupts
 and context switches.

 
Exadata Cloud
 Infrastructure X9M increases the throughput of its 100 Gbps
 active-active Remote Direct Memory Access over Converged
 Ethernet (RoCE) internal network fabric, providing a faster
 interconnect than previous generations with extremely
 low-latency between all compute and storage
 servers.

 
 
- Oracle Autonomous Database Serverless 

 Oracle Autonomous Database is a fully managed, preconfigured database environments
 that you can use for transaction processing and data
 warehousing workloads. You do not need to configure or
 manage any hardware, or install any software. Oracle Cloud
 Infrastructure handles creating the database, as well as backing up,
 patching, upgrading, and tuning the database.
 

 
 Oracle Autonomous Database Serverless is an Oracle Autonomous Database . You have a fully elastic database where Oracle
 autonomously operates all aspects of the database lifecycle
 from database placement to backup and updates.
 

 
Oracle Database Autonomous Serverless is also
 available with Oracle Database@Azure as the world’s first
 autonomous data managem
