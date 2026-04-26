# Implement Oracle GoldenGate in Microsoft Azure with Oracle Database@Azure

- Source: https://docs.oracle.com/en/solutions/implement-goldengate-azure/index.html
- Date: 2024-10
- Type: reference-architecture
- Services: goldengate, exacs, azure
- Tags: database, multicloud, azure, integration

## Summary (catalog)

GoldenGate deployment patterns for Database@Azure. Real-time replication between on-premises and ExaCS, or between ExaCS instances across Azure regions.

## Architecture (fetched from source)

Architecture

 

 

 This reference architecture implements Oracle GoldenGate running on Azure linux virtual machines, or containers hosted on Azure Kubernetes Service . Oracle GoldenGate has deep integration with Oracle Database@Azure for change data capture to facilitate organization to stay up-to-date with the latest
 data in near real time and avoid relying on stale data. 
 
 

 
 Oracle GoldenGate empowers organizations to optimize their data management processes and facilitates
 the seamless integration of data stored in Oracle Database@Azure into data lakes and lakehouses for advanced analytics and machine learning workloads.
 You can build robust data streaming platforms on Azure , ensuring seamless data integration, scalability, and real-time analytics. Oracle GoldenGate provides data consistency and synchronization to make it an invaluable technology for
 organizations striving to leverage real-time data to make informed decisions based on
 accurate and timely data, driving the success of your business in the cloud-native era
 and enhancing business operations. 
 

 
The following diagram illustrates this reference architecture for an Oracle GoldenGate implementation hosted in Microsoft Azure for integration between Oracle Database@Azure and Azure native services for streaming, data processing, machine learning, and analytics. You
 can leverage this reference architecture for reusing an existing Oracle GoldenGate implementation, or a fresh implementation for reasons like legal obligations, latency
 sensitive workloads, and centralized data management. 
 

 
The following diagram illustrates this reference architecture.

 
 Description of the illustration goldengate-dbatazure-integration.png 

 goldengate-dbatazure-integration.zip 

 
The architecture has the following components:

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that
 contains one or more data centers, called
 availability domains. Regions are independent of
 other regions, and vast distances can separate
 them (across countries or even
 continents).
 

 
 
- On-premises network 
This
 network is the local network used by your
 organization. It is one of the spokes of the
 topology.

 
 
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
 

 
 
- VNIC 
A virtual network
 interface card (VNIC) enables an instance to
 connect to a VCN and determines how the instance
 connects with endpoints inside and outside the
 VCN. Each VNIC resides in a subnet in a VCN and
 includes these items:

 
 
- A primary private IPv4 address
 from the subnet the VNIC is in, chosen by either
 you or Oracle. 
 
- Optional secondary private IPv4
 addresses from the same subnet the VNIC is in,
 chosen by either you or Oracle. 
 
- An optional public IPv4 address
 for each private IP, chosen by Oracle but assigned
 by you at your discretion. 
 
- An optional hostname for DNS for
 each private IP address. 
 
- A MAC address. 
 
- A VLAN tag assigned by Oracle and
 available when attachment of the VNIC to the
 instance is complete (relevant only for bare metal
 instances). 
 
- A flag to enable or disable the
 source/destination check on the VNIC's network
 traffic. 
 
- Optional membership in one or
 more network security groups (NSGs) of your
 choice. NSGs have security rules that apply only
 to the VNICs in that NSG. 
 
- Optional IPv6 addresses. IPv6
 addressing is supported for all commercial and
 government regions. 
 
 
 
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
 

 
 
- Oracle GoldenGate 
 Oracle GoldenGate is an application that provides real-time data integration, data replication,
 transactional change data capture, data transformations, high availability
 solutions, and verification between operational and analytical enterprise
 systems. This architecture consists of running Oracle GoldenGate on Linux Virtual Machine or Azure Kubernetes Service.
 

 
 
- Oracle Database@Azure 

 Oracle Database@Azure integrates Oracle Exadata Database
 Service , Oracle Real Application Clusters (Oracle RAC),
 and Oracle Data Guard technologies into the Azure
 platform. Oracle Database@Azure service offers the same low latency as other
 Azure-native services and meets mission-critical
 workloads and cloud-native development needs.
 Users manage the service on the Azure console and
 with Azure automation tools. The service is
 deployed in Azure Virtual Network (VNet) and
 integrated with the Azure identity and access
 management system. The OCI and Oracle Database
 metrics and audit logs are natively available in
 Azure. The service requires users to have an Azure
 tenancy and an OCI tenancy. Oracle Autonomous Database Serverless is also available with Oracle Database@Azure as the world’s first autonomous data
 management, fully managed in the cloud, to deliver
 automated patching, upgrades, and tuning, without
 human intervention. Autonomous Database is built on Oracle Exadata infrastructure, is
 self-managing, self-securing, and self-repairing,
 helping eliminate manual database management and
 human errors. Autonomous Database enables development of scalable AI-powered apps
 with any data using built-in AI capabilities using
 your choice of large language model (LLM) and
 deployment location.
 

 
 
 
- Oracle Autonomous Database Serverless 
 Oracle Autonomous Database is the world’s first autonomous data management, fully managed in the cloud,
 to deliver automated patching, upgrades, and tuning, without human intervention.
 Autonomous Database is built on Oracle Exadata infrastructure, is self-managing,
 self-securing, and self-repairing, helping eliminate manual database management
 and human errors. Autonomous Database enables development of scalable AI-powered
 apps with any data using built-in AI capabilities using your choice of large
 language model (LLM) and deployment location.
 

 
 
- Oracle Exadata Database Service on Dedicated
 Infrastructure 
 Oracle Exadata Database Service on Dedicated
 Infrastructure provides Oracle Exadata Database Machine as a service in an Oracle Cloud
 Infrastructure (OCI) data center. The Oracle Exadata Database Service on Dedicated
 Infrastructure instance is a virtual machine (VM) cluster that
 resides on Exadata racks in an OCI region.
 

 
 Oracle Exadata Database
 Service delivers proven Oracle Database capabilities on purpose-built, optimized Oracle Exadata infrastructure in the
 public cloud. Built-in cloud automation, elastic resource scaling, security, and
 fast performance for OLTP, in-memory analytics, and converged Oracle Database workloads help simplify management and reduce costs.
 

 
 
 
The architecture has the following Azure components:
 

 
 
- Azure Virtual Network (VNet) 
Azure Virtual Netw
