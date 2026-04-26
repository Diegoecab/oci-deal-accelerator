# Perform cross-region disaster recovery for Oracle Essbase on OCI

- Source: https://docs.oracle.com/en/solutions/cross-region-dr-essbase-oci/index.html
- Date: 2025-10
- Type: reference-architecture
- Services: compute, fsdr, base-db
- Tags: ha-dr, application

## Summary (catalog)

Cross-region DR for Essbase on OCI. Full Stack DR for orchestrated failover of Essbase compute, database, and storage components. Block volume replication for Essbase data and configuration.

## Architecture (fetched from source)

Architecture

 

 

 This architecture illustrates a cross-region disaster recovery setup
 for Essbase on OCI, using VCN peering for secure connectivity between regions, automated volume
 copy for Essbase servers, and schema export/import to synchronize data and ensure minimal downtime in
 case one region fails. 
 
 

 
The following diagram illustrates this reference architecture:

 
 Description of the illustration essbase-oci-cross-region-dr.png 

 essbase-oci-cross-region-dr-oracle.zip 

 
Deploy Essbase across two OCI regions. Use multiple availability domains and fault domains for
 resilience within each region.
 

 
Use OCI FastConnect for dedicated links to both primary and secondary regions, to reduce reliance on the
 public internet and provide higher bandwidth and reliability. Match virtual circuit
 throughput to the selected port (1 Gbps or 10 Gbps). For inter-region private traffic,
 use remote peering with Dynamic Routing Gateways (DRGs) to keep traffic off the public
 internet.
 

 
Deploy bastion hosts in both regions for secure and auditable administration paths.

 
Apply multi-layer isolation and compartmentalization to clearly segment public,
 application, and data tiers, and manage access with policies and quotas.

 

 
Tip:
Remember to add CIDR ranges for the VCN and subnets.
 

 
The architecture has the following components:

 
 
- OCI region 
An OCI region
 is a localized geographic area that contains one
 or more data centers, hosting availability
 domains. Regions are independent of other regions,
 and vast distances can separate them (across
 countries or even continents).

 
 
- Availability domain 
Availability domains are standalone, independent data centers within a region. The physical resources in each availability domain are isolated from the resources in the other availability domains, which provides fault tolerance. Availability domains don’t share infrastructure such as power or cooling, or the internal availability domain network. So, a failure at one availability domain shouldn't affect the other availability domains in the region.

 
 
- Fault domain 
A
 fault domain is a grouping of hardware and
 infrastructure within an availability domain. Each
 availability domain has three fault domains with
 independent power and hardware. When you
 distribute resources across multiple fault
 domains, your applications can tolerate physical
 server failure, system maintenance, and power
 failures inside a fault domain.

 
 
- Compartment 
Compartments
 are cross-regional logical partitions within an
 OCI tenancy. Use compartments to organize, control
 access, and set usage quotas for your Oracle Cloud resources. In a given compartment, you define
 policies that control access and set privileges
 for resources.
 

 
 
- OCI virtual cloud
 network and subnet 
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

 
 
- Security list 
For
 each subnet, you can create security rules that
 specify the source, destination, and type of
 traffic that is allowed in and out of the
 subnet.

 
 
- Route table 
Virtual
 route tables contain rules to route traffic from
 subnets to destinations outside a VCN, typically
 through gateways.

 
 
- OCI FastConnect 
 Oracle Cloud
 Infrastructure FastConnect creates a dedicated, private connection between your data center and OCI. FastConnect provides higher-bandwidth options and a more reliable networking experience when compared with internet-based connections.
 

 
 
- Remote
 peering 
Remote
 peering enables private communication between
 resources in different VCNs, which can be located
 in the same or different OCI regions. Each VCN
 uses its own Dynamic Routing Gateway (DRG) for
 remote peering. The DRGs securely route traffic
 between the VCNs over OCI's private backbone,
 allowing resources to communicate using private IP
 addresses without routing traffic over the
 internet or through on-premises networks. Remote
 peering removes the need for internet gateways or
 public IP addresses for instances that need to
 connect across regions.

 
 
- Dynamic routing gateway
 (DRG) 
The DRG is a
 virtual router that provides a path for private
 network traffic between VCNs in the same region,
 between a VCN and a network outside the region,
 such as a VCN in another OCI region, an
 on-premises network, or a network in another cloud
 provider.

 
 
- Network
 address translation (NAT) gateway 
A NAT
 gateway enables private resources in a VCN to
 access hosts on the internet, without exposing
 those resources to incoming internet
 connections.

 
 
- Service
 gateway 
A
 service gateway provides access from a VCN to
 other services, such as Oracle Cloud
 Infrastructure Object Storage . The traffic from the VCN to the Oracle service
 travels over the Oracle network fabric and does
 not traverse the internet.
 

 
 
- Load balancer 
 Oracle Cloud
 Infrastructure Load Balancing provides automated traffic distribution from a single entry point to multiple servers.
 

 
 
- OCI Compute 
With Oracle Cloud Infrastructure
 Compute , you can provision and manage compute hosts in the cloud. You can launch compute instances with shapes that meet your resource requirements for CPU, memory, network bandwidth, and storage. After creating a compute instance, you can access it securely, restart it, attach and detach volumes, and terminate it when you no longer need it.
 

 
 
- OCI Object Storage 
 OCI Object Storage provides access to large amounts of structured and unstructured data of any content type, including database backups, analytic data, and rich content such as images and videos. You can safely and securely store data directly from applications or from within the cloud platform. You can scale storage without experiencing any degradation in performance or service reliability. 
 

 
Use standard storage for "hot" storage that you need to access quickly, immediately, and frequently. Use archive storage for "cold" storage that you retain for long periods of time and seldom or rarely access.

 
 
- Oracle Autonomous Data Warehouse 
 Oracle Autonomous Data Warehouse is a self-driving, self-securing, self-repairing database service that is optimized for data warehousing workloads. You do not need to configure or manage any hardware, or install any software. OCI handles creating, backing up, patching, upgrading, and tuning the database.
 

 
 
 

 

 
 
Recommendations

 

 
 Use the following recommendations as a starting point.
 Your requirements might differ from the architecture described here. 
 

 
 
- Essbase : Use the same Essbase Marketplace image version in both the primary and standby regions. Because
 Marketplace provides only the latest image, deploy the standby region at the same
 time as the primary and upgrade both regions together to keep versions aligned.
 After any upgrade to the primary region, remember to upgrade the standby region as
 well, so both always use the same Essbase image version. 
 
Follow the backup and restore instructions for Essbase Marketplace linked in Explore More .
 

 
 
- OCI FastConnect : Provides both primary and secondary region connectivity back to the
 on-premises data centre. This approach protects against the network connection
 failure to one of the regions.
 
 
- Multi-Layer Isolation and Compartmentalization : Clear segmentation between
 public, application, and database resou
