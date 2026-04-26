# Use private DNS in interconnected VCNs and on-premises

- Source: https://docs.oracle.com/en/solutions/private-dns/index.html
- Date: 2024-11
- Type: reference-architecture
- Services: vcn, dns, drg
- Tags: networking

## Summary (catalog)

Private DNS configuration for hybrid and multi-VCN environments. DNS forwarding between on-premises and OCI, conditional forwarding for split-horizon DNS, and cross-VCN name resolution via DRG.

## Architecture (fetched from source)

Architecture

 

 
This architecture demonstrates the use of Private DNS in Oracle Cloud
 Infrastructure .
 

 
A private DNS resolver allows resolution of local, internal resources that have
 custom domain names. The domain names do not need to be
 subdomains of oraclevcn.com, as with the default internet and
 VCN resolver. The private DNS resolves your custom domain names,
 and forwards requests for other domains to the internet and VCN
 resolver. For example, in the architecture described here, the
 private DNS resolver on the spoke VCN resolves a query for a
 hostname on the example.com domain. Also, a query originating
 from the on-premises network can be forwarded to the private
 resolver of the hub.example.com VCN to resolve addresses in the
 spoke.example.com domain.

 
The following diagram illustrates this reference architecture.
 
 Description of the illustration architecture-deploy-private-dns.png 
 architecture-deploy-private-dns.zip 

 
The architecture has the following components:

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that
 contains one or more data centers, called
 availability domains. Regions are independent of
 other regions, and vast distances can separate
 them (across countries or even
 continents).
 

 
 
- Availability domains 
Availability domains are standalone, independent data centers within a region. The physical resources in each availability domain are isolated from the resources in the other availability domains, which provides fault tolerance. Availability domains don’t share infrastructure such as power or cooling, or the internal availability domain network. So, a failure at one availability domain shouldn't affect the other availability domains in the region.

 
 
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
 

 
 
- Local
 peering gateway (LPG) 
An LPG enables you to
 peer one VCN with another VCN in the same region.
 Peering means the VCNs communicate using private
 IP addresses, without the traffic traversing the
 internet or routing through your on-premises
 network.

 
 
- Dynamic routing gateway
 (DRG) 
The DRG
 is a virtual router that provides a path for
 private network traffic between VCNs in the same
 region, between a VCN and a network outside the
 region, such as a VCN in another Oracle Cloud
 Infrastructure region, an on-premises network, or a network in
 another cloud provider.
 

 
 
- Private DNS Resolver 
A Private DNS Resolver provides full control of naming and record management in a private DNS zone. The listening, or ingress, interface receives queries from another VCN or from your on-premises DNS server for name resolution. The forwarding, or egress, interface forwards queries to another VCN or to your on-premises DNS server for name resolution.

 
 
- DNS 

 Oracle Cloud
 Infrastructure Domain Name System (DNS) service is a highly
 scalable, global anycast domain name system (DNS)
 network that offers enhanced DNS performance,
 resiliency, and scalability, so that end users
 connect to customers’ application as quickly as
 possible, from wherever they are.
 

 
 
 

 

 
 
Recommendations

 

 
Your requirements might differ from the architecture described here. Use the following recommendations as a starting point.

 
 
- VCN 
When you create a VCN, determine the number of CIDR blocks required and the size of each block based on the number of resources that you plan to attach to subnets in the VCN. Use CIDR blocks that are within the standard private IP address space.

 
Select CIDR blocks that don't overlap with any other network (in Oracle Cloud
 Infrastructure , your on-premises data center, or another cloud provider) to which you intend to set up private connections.
 

 
After you create a VCN, you can change, add, and remove its CIDR blocks.

 
When you design the subnets, consider your traffic flow and security requirements. Attach all the resources within a specific tier or role to the same subnet, which can serve as a security boundary.

 
 
- DNS resolver 
VCNs always have resolvers, but you need to enable DNS on subnets if you want to use the internal resolver and OCI system-generated zone within the subnet.

 
 
 

 

 
 
Considerations

 

 
Consider the following points when deploying this reference architecture.

 
 
- Performance 
There are no performance considerations. The service is offered as a managed platform, requiring no intervention for operation.

 
 
- Security 
The security is integrated with OCI Identity and Access Management (IAM).

 
 
- Availability 
There are no availability considerations. The DNS service is a platform service and fully redundant.

 
 
- Cost 
Private DNS has no cost and is provided with Oracle Cloud
 Infrastructure .
 

 
 
 

 

 
 
Explore More

 

 
To learn more about DNS in Oracle Cloud
 Infrastructure , see the following resources:
 

 
 
- Overview of the DNS Service 
 
- DNS in Your Virtual Cloud Network 
 
- Tutorial: Configure Private DNS Zones, Views, and Resolvers 
 
- LiveLab: Configuring Private DNS 
 
 

 

 
 
Change Log

 

 
This log lists significant changes:

 
 
 November 1, 2024 
 
 
 
 
- Fixed a broken link in Explore More. 
 
- Updated diagram. 
 
- Updated content in Architecture. 
 
 
 
 
 
 

 

 

 

 

 
 Title and Copyright Information 

 

 
Use private DNS in interconnected VCNs and on-premises

 
F36796-08

 
November 2024

 
 Copyright © 2020,2024, 

Oracle and/or its affiliates.
