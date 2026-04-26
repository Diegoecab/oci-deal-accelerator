# Secure network architecture for on-premises database backups to OCI Object Storage with Private Endpoint

- Source: https://docs.oracle.com/en/solutions/secure-backup-oci-object-storage/index.html
- Date: 2025-06
- Type: reference-architecture
- Services: object-storage, fastconnect, vcn
- Tags: security, networking, ha-dr

## Summary (catalog)

Private endpoint for Object Storage backup from on-premises. No internet exposure — traffic stays on FastConnect/VPN. Granular IAM policies for backup write access without delete permissions.

## Architecture (fetched from source)

Architecture

 

 
This reference architecture shows a secure, high performance, and private
 network design to backup Oracle Exadata Database Service
 on Cloud@Customer data to OCI Object Storage .
 

 
For optimal network performance, Oracle Cloud
 Infrastructure FastConnect with private peering connects the on-premises data center with an OCI region of a
 customer tenant.
 

 
 OCI Object Storage private endpoint provides secure access to Object Storage using a private IP in a
 customer subnet within a VCN.
 

 
An OCI private DNS Zone provides responses only for clients connecting
 through a VCN. By configuring an OCI DNS listening endpoint and implementing forwarding
 rules in the on-premises customer data center, seamless hybrid DNS resolution is
 achieved.

 
The following diagram illustrates this reference architecture.

 
 Description of the illustration secure-backup-oci-object-storage.png 

 secure-backup-oci-object-storage-oracle.zip 

 
The architecture has the following components:

 
 
- Region 
An
 OCI region is a localized geographic area that
 contains one or more data centers, hosting
 availability domains. Regions are independent of
 other regions, and vast distances can separate
 them (across countries or even
 continents).

 
 
- Availability domains 
Availability domains are standalone, independent data centers within a region. The physical resources in each availability domain are isolated from the resources in the other availability domains, which provides fault tolerance. Availability domains don’t share infrastructure such as power or cooling, or the internal availability domain network. So, a failure at one availability domain shouldn't affect the other availability domains in the region.

 
 
- Virtual cloud network (VCN) and subnets 
A
 VCN is a customizable, software-defined network
 that you set up in an OCI region. Like traditional
 data center networks, VCNs give you control over
 your network environment. A VCN can have multiple
 non-overlapping classless inter-domain routing
 (CIDR) blocks that you can change after you create
 the VCN. You can segment a VCN into subnets, which
 can be scoped to a region or to an availability
 domain. Each subnet consists of a contiguous range
 of addresses that don't overlap with the other
 subnets in the VCN. You can change the size of a
 subnet after creation. A subnet can be public or
 private. 

 
 
- Dynamic routing gateway (DRG) 
The DRG is a
 virtual router that provides a path for private
 network traffic between VCNs in the same region,
 between a VCN and a network outside the region,
 such as a VCN in another OCI region, an
 on-premises network, or a network in another cloud
 provider.

 
 
- FastConnect 
 Oracle Cloud
 Infrastructure FastConnect creates a dedicated, private connection between
 your data center and OCI. FastConnect provides
 higher-bandwidth options and a more reliable
 networking experience when compared with
 internet-based connections.
 

 
 
- Object Storage 
 OCI Object Storage provides access to large amounts of structured and unstructured data of any content type, including database backups, analytic data, and rich content such as images and videos. You can safely and securely store data directly from the internet or from within the cloud platform. You can scale storage without experiencing any degradation in performance or service reliability. 
 

 
Use standard storage for "hot" storage that you need to access quickly, immediately, and frequently. Use archive storage for "cold" storage that you retain for long periods of time and seldom or rarely access.

 
 
- Object Storage private endpoint 
Object Storage Private
 Endpoint provides secure access to Object Storage from your OCI VCNs or
 on-premises networks. The private endpoint is a VNIC with a private IP address
 in a subnet you choose within your VNC. This method is an alternative to using a
 service gateway using public IP addresses associated with OCI services.

 
 
- Private DNS resolvers 
A private DNS resolver answers DNS
 queries for a VCN. A private resolver can be configured to use views and zones
 as well as conditional forwarding rules to define how to respond to DNS
 queries.

 
 
- Listening endpoint 
A listening endpoint receives queries from
 within the VCN or from other VCN resolvers, from the DNS of other cloud service
 providers (such as AWS, GCP, or Azure), or from the DNS of your on-premises
 network. Once created, no further configuration is needed for a listening
 endpoint.

 
 
 

 

 
 
Recommendations

 

 

 Use the following recommendations when designing your network for
 backing up Oracle Exadata Database Service
 on Cloud@Customer data to OCI Object Storage via private endpoint. Your requirements might differ from
 the architecture described here. 
 
 

 
 
- VCN 
When you create a VCN, determine the number of CIDR blocks required and the size of each block based on the number of resources that you plan to attach to subnets in the VCN. Use CIDR blocks that are within the standard private IP address space.

 
Select CIDR blocks that don't overlap with any other network (in Oracle Cloud
 Infrastructure , your on-premises data center, or another cloud provider) to which you intend to set up private connections.
 

 
After you create a VCN, you can change, add, and remove its CIDR blocks.

 
When you design the subnets, consider your traffic flow and security requirements. Attach all the resources within a specific tier or role to the same subnet, which can serve as a security boundary.

 
 
- IAM Policies and network Sources 
Creating a private endpoint
 in a VCN and associating it with a bucket doesn't limit access to the bucket
 from the internet or other network sources. You need to define rules using IAM
 polices on the bucket, so requests are only authorized if they originate from a
 specific VCN or a CIDR block within that VCN. All other access, including over
 the internet, is blocked to these buckets.

 
 
- Security 
Assign a network security group (NSG) to the OCI
 listening endpoint and configure the security group following a deny-all
 security posture, allowing only the on-premises DNS IP on port UDP:53. Object
 Storage private endpoint can be configured for restricting access to specific
 buckets and compartments.

 
 
- High availability 
This architecture shows a simplified design.
 In a production deployment, make sure your design follows high availability best
 practices.

 
 
 

 

 
 
 Deploy 

 

 
To configure the network communication and DNS resolution from on-premises
 to OCI in the above architecture diagram, complete the following high-level
 steps.

 

 
 Network Configuration 

 
 
 
- Create a VCN. 
 
- Create a private subnet for the Object Storage private endpoint. 
 
- Deploy the Object Storage private endpoint. 
 
- Create a private subnet for the DNS endpoint. 
 
- Create a DRG. 
 
- Attach the VCN to the DRG. 
 
- Create a FastConnect with a Private Virtual Circuit to connect to on-premises
 and attach it to the DRG. 
 
 
 
 DNS Configuration 

 
 
 
- Create a listening endpoint in the VCN DNS resolver, deploy it in the DNS
 subnet. 
 
- In the DNS Subnet Security list, allow UDP:53 with source IP for the on-premises
 DNS server. 
 
- Create DNS forwarding rules in the on-premises DNS Server. Configure the rules
 from the table below. 
 

 
 
 
 Domain name* 
 Destination IP:Port 
 
 
 objectstorage.
 <oci-region-identifier>.oci.customer-oci.com 
 OCI Listening Endpoint IP. Port 53 
 
 
 swiftobjectstorage.
 <oci-region-identifier>.oci.customer-oci.com 
 OCI Listening Endpoint IP. Port 53 
 
 
 
 

 
*See Regions and Availability Domains 
 for the latest information about regions and availability domains.
 

 
 
 

 

 

 
 
Explore More

 

 
Review these additional resources to learn more about the features in this
 reference architecture.

 
 
- Private Endpoints in Object Storage 
 
- Oracle Exadata Database Service on Clou
