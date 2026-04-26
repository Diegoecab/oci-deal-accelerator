# Deploy TCS BaNCS on Oracle Cloud Infrastructure with Exadata Cloud Service

- Source: https://docs.oracle.com/en/solutions/deploy-tcs-banc-oci-exa/index.html
- Date: 2024-08
- Type: built-deployed
- Services: exacs, compute, load-balancer
- Tags: application, database

## Summary (catalog)

TCS BaNCS banking platform on OCI with ExaCS. High-performance database for core banking transactions, compute instances for application tier with Load Balancer for HA.

## Architecture (fetched from source)

Architecture

 

 
 TCS BaNCS follows a multi-tier architecture with
 and API-first design. This solution leverages a number of OCI networking and security
 capabilities such as OCI compartments, and hub-and-spoke peering of OCI virtual cloud
 networks to isolate the various application components and provide fine grained access
 control across environments and application tiers. The primary production
 BaNCS application is deployed in one OCI region and the DR deployment is configured on a
 secondary OCI region. The OCI cross region replication services are leveraged to synchronize
 the primary and secondary sites and provide a low recovery point objective (RPO) and
 recovery time objective (RTO). Additionally, the virtual machines that host the BaNCS
 application services are distributed across multiple OCI fault domains to create a highly
 available cluster within each OCI region. 
 

 
The following diagram illustrates this reference architecture for a production and
 disaster recovery BaNCS environment. In order to simplify the diagram the non-production
 environments have not been depicted. Those environments will follow the same design
 pattern and will be contained in there own isolated network. 

 
Detailed descriptions of the various solution component follow after the
 diagram..

 

 
 
 Description of the illustration bancs-ref-architecture-no-fd.png 

 
 

 

 bancs-ref-architecture-no-fd-oracle.zip 
 
 

 
This architecture has the following components:
 
 
- Tenancy 
 
 
A tenancy is a secure and isolated partition that Oracle sets up
 within Oracle Cloud when you sign up for OCI. You can create, organize, and
 administer your resources in Oracle Cloud within your tenancy. 

 
A tenancy is synonymous with a company or organization. Usually,
 a company will have a single tenancy and reflect its organizational
 structure within that tenancy. A single tenancy is usually associated with a
 single subscription, and a single subscription usually only has one tenancy.
 A company may chose to split their OCI resources, environments or
 applications across multiple tenancies if they wish. The tenancies can be
 linked and networks can be peered across tenancies if required. For the
 purpose of this BaNCS solution design a single tenancy has been used and the
 OCI concept of compartments (see below) has been used to provide fine
 grained isolation and access control to the various solution components.
 

 
 
- Region 
 
 
An OCI region is a localized geographic area that contains one
 or more data centers, called availability domains. Regions are independent
 of other regions, and vast distances can separate them (across countries or
 even continents). In this solution two regions are used in order to provide
 a disaster recovery site that is geographically isolated from the primary
 site. 

 
 
- Compartment 
 
 
Compartments are cross-region logical partitions within an OCI
 tenancy. Use compartments to organize your resources in Oracle Cloud,
 control access to the resources, and set usage quotas. To control access to
 the resources in a given compartment, you define policies that specify who
 can access the resources and what actions they can perform. 

 
 
- Availability domains 
 
 
Availability domains are standalone, independent data centers within a
 region. The physical resources in each availability domain are isolated from
 the resources in the other availability domains, which provides fault
 tolerance. Availability domains don’t share infrastructure such as power or
 cooling, or the internal availability domain network. So, a failure at one
 availability domain is unlikely to affect the other availability domains in
 the region. 

 
 
- Fault domains 
 
 
A fault domain is a grouping of hardware and infrastructure within an
 availability domain. Each availability domain has three fault domains with
 independent power and hardware. When you distribute resources across
 multiple fault domains, your applications can tolerate physical server
 failure, system maintenance, and power failures inside a fault domain. For
 this deployment it is recommended that the BaNCS load balancers, network
 firewalls, web tier and application tier VMs are deployed in highly
 available clusters across multiple fault domains in order to ensure the
 maximum resilience to hardware failures. 

 
 
- Identity and access management (IAM) 
 
 
 OCI Identity and Access Management (IAM) enables you to control who can access your resources in OCI and the
 operations that they can perform on those resources. 
 

 
 
- Policy 
 
 
An OCI IAM policy specifies who can access which resources, and
 how. Access is granted at the group and compartment level, which means you
 can write a policy that gives a group a specific type of access within a
 specific compartment, or to the tenancy. 

 
 
- Virtual cloud network (VCN) and subnets 
 
 
A VCN is a customizable, software-defined network that you set up
 in an OCI region. Like traditional data center networks, VCNs give you
 complete control over your network environment. A VCN can have multiple
 non-overlapping CIDR blocks that you can change after you create the VCN.
 You can segment a VCN into subnets, which can be scoped to a region or to an
 availability domain. Each subnet consists of a contiguous range of addresses
 that don't overlap with the other subnets in the VCN. You can change the
 size of a subnet after creation. A subnet can be public or private. This
 BaNCS reference architecture leverages multiple VCN's in a hub and spoke
 topology. This will be discussed in more detail in the section below.
 

 
 
- FastConnect 
 
 
 OCI FastConnect provides an easy way to create a dedicated, private connection between
 your data center and OCI. FastConnect provides higher-bandwidth options and
 a more reliable networking experience when compared with internet-based
 connections. 
 

 
 
- Site-to-Site VPN 
 
 
Site-to-Site VPN provides IPSec VPN connectivity between your
 on-premises network and VCNs in OCI. The IPSec protocol suite encrypts IP
 traffic before the packets are transferred from the source to the
 destination and decrypts the traffic when it arrives. 

 
 
- Dynamic routing gateway (DRG) 
 
 
The DRG is a virtual router that provides a path for private
 network traffic between a VCN and a network outside the region, such as a
 VCN in another OCI region, an on-premises network, or a network in another
 cloud provider. 

 
 
- Local peering gateway (LPG) 
An LPG enables you to peer one VCN with
 another VCN in the same region. Peering means the VCNs communicate using
 private IP addresses, without the traffic traversing the internet or routing
 through your on-premises network. This solution has been created using a
 multi-attach DRG as the method of achieving local peering for the hub and
 spoke network. However it could equally be created using local peering
 gateways instead. 

 
 
- Network address translation (NAT) gateway 
The
 NAT gateway enables private resources in a VCN to access hosts on the
 internet, without exposing those resources to incoming internet connections.
 

 
 
- Service gateway 
The service gateway provides
 access from a VCN to other services, such as OCI Object Storage . The traffic from the VCN to the Oracle service travels over the Oracle
 network fabric and never traverses the internet. 
 

 
 
- Security list 
For each subnet, you can create security rules that
 specify the source, destination, and type of traffic that must be allowed in
 and out of the subnet.

 
 
- Network security group (NSG) 
NSGs act as
 virtual firewalls for your cloud resources. With the zero-trust security
 model of OCI all traffic is denied, and you can control the network traffic
 inside a VCN. An NSG consists of a set of ingress and egress security rules
 that apply to only a specified set of VNICs in a single VCN. 

 
 
- Security zone 
 
 
Security zones ensure Oracle's security best practices
