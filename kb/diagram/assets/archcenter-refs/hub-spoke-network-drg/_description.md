# Set up a hub-and-spoke network topology using dynamic routing gateway

- Source: https://docs.oracle.com/en/solutions/hub-spoke-network-drg/index.html
- Date: 2025-09
- Type: reference-architecture
- Services: vcn, drg, fastconnect
- Tags: networking

## Summary (catalog)

Hub-spoke topology using DRG as central router. Spoke VCNs attached to DRG with route tables for inter-spoke and on-premises routing. Centralized network security appliances in hub VCN.

## Architecture (fetched from source)

Architecture

 

 
A dynamic routing gateway (DRG) allows you to connect up to 300 virtual cloud
 networks (VCNs) and helps to simplify the overall architecture, security list and route
 table configuration, and to simplify security policy management by advertising Oracle cloud
 indentifiers (OCIDs) through the DRG. 

 
In this architecture, a dynamic routing gateway is connected to multiple VCNs. There
 are sample subnets and virtual machines (VMs) in each VCN. The DRG has a route table
 that specifies rules to direct traffic to targets outside the VCN. The DRG enables
 private connectivity with an on-premises network, which you can implement by using Oracle Cloud
 Infrastructure FastConnect , Oracle Cloud Infrastructure Site-to-Site VPN , or both. The DRG also enables you to connect to multiple cloud environments using a
 OCI FastConnect partner.
 

 
You can use either Oracle Cloud Infrastructure
 Bastion or a Bastion host to provide secure access to your resources. This architecture uses
 OCI Bastion .
 

 
The following diagram illustrates this reference architecture.

 
 
 Description of the illustration hub-and-spoke-drg.png 

 
 hub-and-spoke-drg-oracle.zip 

 
The architecture has the following components:

 
 
- On-premises network 
This
 is a local network used by your
 organization.

 
 
- OCI region 
An OCI region
 is a localized geographic area that contains one
 or more data centers, hosting availability
 domains. Regions are independent of other regions,
 and vast distances can separate them (across
 countries or even continents).

 
 
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

 
 
- Network security group
 (NSG) 
NSGs act as virtual firewalls for your cloud resources. With the zero-trust security model of OCI you control the network traffic inside a VCN. An NSG consists of a set of ingress and egress security rules that apply to only a specified set of virtual network interface cards (VNICs) in a single VCN.

 
 
- Route table 
Virtual
 route tables contain rules to route traffic from
 subnets to destinations outside a VCN, typically
 through gateways.

 
 
- Dynamic routing gateway
 (DRG) 
The DRG is a
 virtual router that provides a path for private
 network traffic between VCNs in the same region,
 between a VCN and a network outside the region,
 such as a VCN in another OCI region, an
 on-premises network, or a network in another cloud
 provider.

 
 
- OCI Site-to-Site VPN 
 OCI Site-to-Site VPN provides IPSec VPN connectivity between your on-premises network and VCNs on OCI. The IPSec protocol suite encrypts IP traffic before the packets are transferred from the source to the destination and decrypts the traffic when it arrives.
 

 
 
- OCI FastConnect 
 Oracle Cloud
 Infrastructure FastConnect creates a dedicated, private connection between your data center and OCI. FastConnect provides higher-bandwidth options and a more reliable networking experience when compared with internet-based connections.
 

 
 
- OCI Bastion 
 Oracle Cloud Infrastructure
 Bastion provides restricted and time-limited secure access to resources that don't have public endpoints and that require strict resource access controls, such as bare metal and virtual machines, Oracle MySQL Database Service , Autonomous Transaction
 Processing (ATP), Oracle Cloud Infrastructure Kubernetes Engine ( OKE ), and any other resource that allows Secure Shell Protocol (SSH) access. With OCI Bastion service, you can enable access to private hosts without deploying and maintaining a jump host. In addition, you gain improved security posture with identity-based permissions and a centralized, audited, and time-bound SSH session. OCI Bastion removes the need for a public IP for bastion access, eliminating the hassle and potential attack surface when providing remote access.
 

 
 
- Bastion host 
The
 bastion host is a compute instance that serves as
 a secure, controlled entry point to the topology
 from outside the cloud. The bastion host is
 provisioned typically in a demilitarized zone
 (DMZ). It enables you to protect sensitive
 resources by placing them in private networks that
 can't be accessed directly from outside the cloud.
 The topology has a single, known entry point that
 you can monitor and audit regularly. So, you can
 avoid exposing the more sensitive components of
 the topology without compromising access to
 them.

 
 
- OCI Compute 
With Oracle Cloud Infrastructure
 Compute , you can provision and manage compute hosts in the cloud. You can launch compute instances with shapes that meet your resource requirements for CPU, memory, network bandwidth, and storage. After creating a compute instance, you can access it securely, restart it, attach and detach volumes, and terminate it when you no longer need it.
 

 
 
 

 

 
 
Recommendations

 

 
 Use the following recommendations as a starting point to <rest of sentence.> Your requirements might differ from the architecture described here. 
 

 
 
- VCN 
When you create a VCN, determine the number of CIDR blocks required and the size of each block based on the number of resources that you plan to attach to subnets in the VCN. Use CIDR blocks that are within the standard private IP address space.

 
Select CIDR blocks that don't overlap with any other network (in Oracle Cloud
 Infrastructure , your on-premises data center, or another cloud provider) to which you intend to set up private connections.
 

 
After you create a VCN, you can change, add, and remove its CIDR blocks.

 
When you design the subnets, consider your traffic flow and security requirements. Attach all the resources within a specific tier or role to the same subnet, which can serve as a security boundary.

 
 
- Security lists 
Use security lists to define ingress and egress rules that apply to the entire subnet.

 
 
- Security 
Use Oracle Cloud Guard to monitor and maintain the
 security of your resources in Oracle Cloud
 Infrastructure proactively. Cloud Guard uses detector recipes that you can define to examine
 your resources for security weaknesses and to monitor operators and users for
 risky activities. When any misconfiguration or insecure activity is detected,
 Cloud Guard recommends corrective actions and assists with taking those actions,
 based on responder recipes that you can define.
 

 
For resources that require
 maximum security, Oracle recommends that you use security zones. A security zone
 is a compartment associated with an Oracle-defined recipe of security policies
 that are based on best practices. For example, the resources in a security zone
 must not be accessible from the public internet and they must be encrypted using
 customer-managed keys. When you create and update resources in a security zone,
 Oracle Cloud
 Infrastructure validates the operations against the policies in the security-zone recipe and
 denies operations that violate any of the policies.
 

 
 
 

 

 
 
Considerations

 

 
Consider the following points when deploying this reference architecture. 

 
 
- Performance 
Within a region, performance isn’t affected by the
 number of VCNs. When you peer VCNs in different regions, consider latency. W
