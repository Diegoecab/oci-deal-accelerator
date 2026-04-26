# Deploy Oracle E-Business Suite on Oracle Database@Azure

- Source: https://docs.oracle.com/en/solutions/deploy-ebs-on-db-at-azure/index.html
- Date: 2025-05
- Type: reference-architecture
- Services: exacs, azure, compute, load-balancer
- Tags: application, multicloud, azure, ebs

## Summary (catalog)

EBS application tier on Azure VMs with database on ExaCS via Database@Azure. App-to-DB connectivity through VNet peering. Load balancer for EBS web tier high availability.

## Architecture (fetched from source)

Architecture
 
 
This architecture follows Microsoft Azure landing zone best practices and employs multiple subscriptions to logically separate shared and workload resources. 
 
The highly-scalable network topology uses Azure Virtual WAN hub or secured virtual hub, simplifying the deployment of complex hub-and-spoke networks. The network infrastructure facilitates seamless routing across Azure regions, between virtual networks, and to on-premises locations by using ExpressRoute, point-to-site VPN, and site-to-site VPN, all secured by Azure Firewall. 
 
The following diagram illustrates the architecture:

 
 Description of the illustration ebs-db-azure-arch.png 

 ebs-db-azure-arch-oracle.zip 
 
The architecture has the following Oracle Cloud Infrastructure (OCI) components: 
 
- Region 
An OCI region is a localized geographic area that contains one or more data centers, hosting availability domains. Regions are independent of other regions, and vast distances can separate them (across countries or even continents).
 
- Virtual cloud network (VCN) and subnets 
A VCN is a customizable, software-defined network that you set up in an OCI region. Like traditional data center networks, VCNs give you control over your network environment. A VCN can have multiple non-overlapping classless inter-domain routing (CIDR) blocks that you can change after you create the VCN. You can segment a VCN into subnets, which can be scoped to a region or to an availability domain. Each subnet consists of a contiguous range of addresses that don't overlap with the other subnets in the VCN. You can change the size of a subnet after creation. A subnet can be public or private. 
 
- Route table 
Virtual route tables contain rules to route traffic from subnets to destinations outside a VCN, typically through gateways.
 
- Security list 
For each subnet, you can create security rules that specify the source, destination, and type of traffic that is allowed in and out of the subnet.
 
- Network security group (NSG) 
NSGs act as virtual firewalls for your cloud resources. With the zero-trust security model of OCI you control the network traffic inside a VCN. An NSG consists of a set of ingress and egress security rules that apply to only a specified set of virtual network interface cards (VNICs) in a single VCN.
 
- Oracle Database@Azure 
 Oracle Database@Azure is the Oracle Database service ( Oracle Exadata Database Service on Dedicated Infrastructure and Oracle Autonomous Database Serverless ) running on OCI, deployed in Microsoft Azure data centers. The service offers features and price parity with OCI. Purchase the service on Azure Marketplace. 
 
 Oracle Database@Azure integrates Oracle Exadata Database Service , Oracle Real Application Clusters (Oracle RAC) , and Oracle Data Guard technologies into the Azure platform. Users manage the service on the Azure console and with Azure automation tools. The service is deployed in Azure Virtual Network (VNet) and integrated with the Azure identity and access management system. The OCI and Oracle Database generic metrics and audit logs are natively available in Azure. The service requires users to have an Azure subscription and an OCI tenancy. 
 
 Autonomous Database is built on Oracle Exadata infrastructure, is self-managing, self-securing, and self-repairing, helping eliminate manual database management and human errors. Autonomous Database enables development of scalable AI-powered apps with any data using built-in AI capabilities using your choice of large language model (LLM) and deployment location. 
 
Both Oracle Exadata Database Service and Oracle Autonomous Database Serverless are easily provisioned through the native Azure Portal, enabling access to the broader Azure ecosystem. 
 
- Exadata Database Service on Dedicated Infrastructure 
 Oracle Exadata Database Service on Dedicated Infrastructure enables you to leverage the power of Exadata in the cloud. Oracle Exadata Database Service delivers proven Oracle Database capabilities on purpose-built, optimized Oracle Exadata infrastructure in the public cloud. Built-in cloud automation, elastic resource scaling, security, and fast performance for all Oracle Database workloads helps you simplify management and reduce costs. 
 
- Object storage 
 OCI Object Storage provides access to large amounts of structured and unstructured data of any content type, including database backups, analytic data, and rich content such as images and videos. You can safely and securely store data directly from the internet or from within the cloud platform. You can scale storage without experiencing any degradation in performance or service reliability. 
 
Use standard storage for "hot" storage that you need to access quickly, immediately, and frequently. Use archive storage for "cold" storage that you retain for long periods of time and seldom or rarely access.
 
This architecture has the following Microsoft Azure components:
 
- Azure availability zone 
Azure availability zones are physically separate locations within an Azure region, designed to ensure high availability and resiliency by providing independent power, cooling, and networking.
 
- Azure Virtual Network (VNet) 
Azure Virtual Network (VNet) is the fundamental building block for your private network in Azure. VNet enables many types of Azure resources, such as Azure virtual machines (VMs), to securely communicate with each other, the internet, and on-premises networks.
 
- Azure availability sets 
Availability sets are logical groupings of VMs that reduce the chance of correlated failures bringing down related VMs at the same time.
 
- Recovery Service Vault 
Recovery Service Vault is an Azure service that stores backup data, such as server and virtual machine configurations, workstation data, and Azure SQL database data, in an organized way.
 
- Azure DNS 
Azure DNS is a cloud-based domain name system (DNS) service that provides fast and reliable domain name resolution for Azure resources and external domains. It allows users to host their DNS zones in Azure, ensuring high availability and low-latency query responses. The service integrates with Azure Resource Manager for seamless management and supports features such as custom DNS records, traffic routing, and private DNS zones. Azure DNS does not support domain registration but works with third-party registrars for end-to-end domain management.
 
- Azure Firewall 
Azure Firewall is a cloud-native, stateful firewall security service that provides network and application-level protection for resources in Microsoft Azure. It offers high availability and scalability, ensuring secure and controlled traffic flow across Azure Virtual Networks. With built-in threat intelligence and filtering capabilities, it allows administrators to define rules for inbound and outbound traffic. Azure Firewall integrates with Azure Security Center and other security services to enhance network security and compliance.
 
- Azure ExpressRoute 
Azure ExpressRoute is a service that enables private connections between on-premises data centers and Microsoft Azure, bypassing the public internet. This results in higher security, reliability, and faster speeds with consistent latencies. ExpressRoute connections can be established through a connectivity provider using various methods such as point-to-point ethernet, any-to-any (IP VPN), or virtual cross-connections. When integrating with on-premises data centers, ExpressRoute allows seamless extension of your network into the cloud, facilitating hybrid cloud scenarios, disaster recovery, and data migration with enhanced performance and security. 
 
- Azure Virtual WAN 
Azure Virtual WAN (VWAN) is a networking service that brings many networking, security, and routing functionalities together to provide a single operational interface.
 
- Azure secure hub 
An Azure secure hub, also known as a secured virtual hub, is an Azure Virtual WAN hub enhanced with security and r
