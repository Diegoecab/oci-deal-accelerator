# Set up a hub-and-spoke network topology by using local peering gateways

- Source: https://docs.oracle.com/en/solutions/hub-spoke-network/index.html
- Date: 2025-08
- Type: reference-architecture
- Services: vcn
- Tags: networking

## Summary (catalog)

Hub-spoke topology using Local Peering Gateways. Simpler than DRG for same-region peering. Limited to 10 LPGs per VCN. Suitable for smaller deployments without cross-region requirements.

## Architecture (fetched from source)

Architecture

 

 
This reference architecture shows an Oracle Cloud
 Infrastructure region with a hub virtual cloud network (VCN) connected to two spoke VCNs. Each spoke VCN
 is peered with the hub VCN by using a pair of local peering gateways (LPGs).
 

 
The architecture shows a few sample subnets and virtual machine (VMs). Security
 lists are used to control network traffic to and from each subnet. Every subnet has a
 route table that contains rules to direct traffic bound for targets outside the VCN.

 
The hub VCN has an internet gateway for network traffic to and from the public
 internet. It also has a dynamic routing gateway (DRG) to enable private connectivity
 with your on-premises network, which you can implement by using Oracle Cloud
 Infrastructure FastConnect , Site-to-Site VPN, or both.
 

 
You can use either Oracle Cloud Infrastructure
 Bastion or a Bastion host to provide secure access to your resources. This architecture uses
 OCI Bastion .
 

 
The following diagram illustrates the reference architecture.

 
 Description of the illustration hub-spoke-oci.png 

 hub-and-spoke-oci.zip 

 
The architecture has the following components:
 
 
- On-premises network 
This network is the local network used by your organization. It is one of the spokes of the topology.

 
 
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

 
 
- Local Peering Group (LPG) 
An LPG provides peering between VCNs in the same region. Peering means the VCNs communicate using private IP addresses, without the traffic traversing the internet or routing through your on-premises network.

 
 
- OCI Site-to-Site VPN 
 OCI Site-to-Site VPN provides IPSec VPN connectivity between your on-premises network and VCNs on OCI. The IPSec protocol suite encrypts IP traffic before the packets are transferred from the source to the destination and decrypts the traffic when it arrives.
 

 
 
- OCI FastConnect 
 Oracle Cloud
 Infrastructure FastConnect creates a dedicated, private connection between your data center and OCI. FastConnect provides higher-bandwidth options and a more reliable networking experience when compared with internet-based connections.
 

 
 
 

 

 

 
 
Recommendations

 

 
Your requirements might differ from the architecture described here. Use the following recommendations as a starting point.

 
 
- VCNs 
When you create a VCN, determine the number of CIDR blocks required and the size of each block based on the number of resources that you plan to attach to subnets in the VCN. Use CIDR blocks that are within the standard private IP address space.

 
Select CIDR blocks that don't overlap with any other network (in Oracle Cloud
 Infrastructure , your on-premises data center, or another cloud provider) to which you intend to set up private connections.
 

 
After you create a VCN, you can change, add, and remove its CIDR blocks.

 
When you design the subnets, consider your traffic flow and security requirements. Attach all the resources within a specific tier or role to the same subnet, which can serve as a security boundary.

 
Use regional subnets.

 
 
- Security lists 
Use security lists to define ingress and egress rules that apply to the entire subnet.

 
 
 

 

 
 
Considerations

 

 
When you design a hub-and-spoke network topology in the cloud, consider the following factors:

 
 
- Cost 
The only components of this architecture that have a cost are the compute instances and FastConnect (port hours and provider charges). The other components have no associated cost.

 
 
- Security 
Use appropriate security mechanisms to protect the topology.

 
The topology that you deploy by using the provided Terraform code incorporates the following security characteristics:
 
 
- The default security list of the hub VCN allows SSH traffic from 0.0.0.0/0. Adjust the security list to allow only the hosts and networks that should have SSH access (or whatever other services ports are required) to your infrastructure. 
 
- This deployment places all components in the same compartment. 
 
- Spoke VCNs are not accessible from the internet. 
 
 

 
 
- Scalability 
Consider the service limits for VCNs and subnets for your tenancy. If more networks are required, request an increase in the limits.

 
 
- Performance 
Within a region, performance isn’t affected by the
 number of VCNs. When you peer VCNs in different regions, consider latency. When you use
 spokes connected through OCI Site-to-Site VPN or OCI FastConnect , the throughput of the connection is an additional factor.
 

 
 
- Availability and redundancy 
Except for the instances, the
 remaining components have no redundancy requirements.

 
The OCI Site-to-Site VPN and OCI FastConnect components are redundant. For further redundancy, use multiple connections, preferably
 from different providers.
 

 
 
 

 

 
 
Deploy

 

 
The Terraform code for this reference architecture is available in GitHub. You can pull the code into Oracle Cloud Infrastructure Resource
 Manager with a single click, create the stack, and deploy it. Alternativel
