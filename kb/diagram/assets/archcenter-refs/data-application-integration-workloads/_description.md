# Design network architecture for data and application integration workloads on OCI

- Source: https://docs.oracle.com/en/solutions/data-application-integration-workloads/index.html
- Date: 2025-11
- Type: reference-architecture
- Services: vcn, drg, fastconnect, oic, data-integration, adb-s
- Tags: networking, integration, multicloud, data-platform

## Summary (catalog)

4 integration patterns: single VCN, cross-VCN, cross-region, and multicloud. FastConnect+DRG for on-prem, RPC for cross-region. Multicloud via FastConnect+ExpressRoute/DirectConnect/PartnerInterconnect.

## Architecture (fetched from source)

Architecture

 

 
The provided architecture patterns, deployment steps, and connectivity models
 offer a blueprint for implementing efficient and future-ready cloud integration
 strategies.

 
 Architecture pattern 1 

 
The source system, data integration tool, and target system are all deployed within the same subnet, either public or private, inside a single VCN in OCI. The advantages include:

 
 
- Simplified network configuration and setup 
 
- Low-latency communication between components 
 
- Optimized data transfer performance 
 
- Minimal security management due to co-location 
 
- Ideal for high-throughput, intra-VCN integration workloads 
 
 
The following diagram illustrates this reference architecture.

 
 Description of the illustration integration-architecuture-pattern-1.png 

 integration-architecture-pattern-1-oracle.zip 

 
 Architecture pattern 2 

 
The source system is located on-premises, the data integration tool is deployed in a private subnet within VCN 1, and the target system resides in a private subnet within VCN 2. Both VCNs are part of the same OCI tenancy. Connectivity between the on-premises environment and OCI is established using OCI FastConnect or VPN, while VCN peering or a dynamic routing gateway (DRG) enables communication between VCN 1 and VCN 2. The advantages include:
 

 
 
- Support for hybrid cloud integration with secure on-premises
 connectivity 
 
- Network segmentation and resource isolation across VCNs 
 
- Secure and efficient data flow between components 
 
- Dedicated or encrypted links for consistent performance 
 
- Scaling for multi-tier or distributed integration workloads 
 
 
The following diagram illustrates this reference architecture.

 
 Description of the illustration integration-architecuture-pattern-2.png 

 integration-architecture-pattern-2-oracle.zip 

 
 Architecture pattern 3 

 
The source system is hosted on-premises in region 1. The data integration tool is deployed in a private subnet within VCN 1 located in region 1, while the target system and Oracle Integration reside in a private subnet within VCN 2. To enable secure communication across these distributed environments, a remote peering connection (RPC) is used to link the VCNs across different OCI regions. A DRG facilitates the routing and management of this inter-region traffic. The advantages include:
 

 
 
- Secure, private connectivity between different regions and
 tenancies 
 
- Preventative exposure to the public internet for inter-VCN
 communication 
 
- Support for high-availability, multi-region deployment models 
 
- Scalable architecture for global integration solutions 
 
- Network isolation while enabling seamless data exchange 
 
 
The following diagram illustrates this reference architecture.

 
 Description of the illustration integration-architecuture-pattern-3.png 

 integration-architecture-pattern-3-oracle.zip 

 
 Architecture pattern 4 

 
The source system is located on-premises in region 1. The data integration tool is deployed in a private subnet within VCN 1 in region 1, while the target system resides in a private subnet within VCN 2. The source system resides in a multicloud environment, spanning providers such as Google Cloud , Microsoft Azure , and Amazon Web Services (AWS). Seamless and secure connectivity between OCI and these cloud platforms is achieved using dedicated interconnect solutions:
 

 
 
- OCI to Google Cloud : OCI FastConnect + Google Partner
 Interconnect ensures a private, low-latency link between OCI and Google Cloud .
 
 
- OCI to Azure : OCI FastConnect + Azure ExpressRoute (private peering) enables direct, secure connectivity while bypassing the public
 internet.
 
 
- OCI to AWS : OCI FastConnect + AWS Direct Connect (private) provides dedicated network paths for optimized data transfer between
 OCI and AWS . 
 
 
 
The advantages include:

 
 
- High-performance, private connectivity across multiple cloud
 platforms 
 
- Low-latency, secure data transfer between OCI and third-party
 clouds 
 
- Compliance and governance by avoiding public internet routing 
 
- Scalable, distributed integration architectures 
 
- Flexibility for deploying cross-platform enterprise workloads 
 
 
The following diagram illustrates this reference architecture.

 
 Description of the illustration integration-architecuture-pattern-4.png 

 integration-architecture-pattern-4-oracle.zip 

 
OCI delivers a comprehensive and flexible integration framework supporting
 data and application synchronization across hybrid, multi-region, and multi-cloud
 deployments. By leveraging its enterprise-grade services such as Oracle Data
 Integrator , Oracle Data Transforms , and Oracle Integration and pairing them with robust networking constructs like DRGs, OCI FastConnect , and RPCs, organizations can implement highly secure, scalable, and resilient
 architectures.
 

 
The architecture has the following components:

 
 
- Dynamic routing gateway
 (DRG) 
The DRG is a
 virtual router that provides a path for private
 network traffic between VCNs in the same region,
 between a VCN and a network outside the region,
 such as a VCN in another OCI region, an
 on-premises network, or a network in another cloud
 provider.

 
 
- OCI FastConnect 
 Oracle Cloud
 Infrastructure FastConnect creates a dedicated, private connection between your data center and OCI. FastConnect provides higher-bandwidth options and a more reliable networking experience when compared with internet-based connections.
 

 
 
- Internet
 gateway 
An
 internet gateway allows traffic between the public
 subnets in a VCN and the public internet.

 
 
- Local
 peering 
Local peering allows two VCNs
 within the same OCI region to communicate directly
 using private IP addresses. This communication
 does not traverse the internet or your on-premises
 network. Local peering is enabled by a Local
 Peering Gateway (LPG), which serves as the
 connection point between VCNs. Configure an LPG in
 each VCN and establish a peering relationship to
 allow instances, load balancers, and other
 resources in one VCN to securely access resources
 in another VCN within the same region.

 
 
- Network security group
 (NSG) 
NSGs act as virtual firewalls for your cloud resources. With the zero-trust security model of OCI you control the network traffic inside a VCN. An NSG consists of a set of ingress and egress security rules that apply to only a specified set of virtual network interface cards (VNICs) in a single VCN.

 
 
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

 
 
- Route table 
Virtual
 route tables contain rules to route traffic from
 subnets to destinations outside a VCN, typically
 through gateways.

 
 
- Service
 gateway 
A
 service gateway provides access from a VCN to
 other services, such as Oracle Cloud
 Infrastructure Object Storage . The traffic from the VCN to the Oracle service
 travels over the Oracle network fabric and does
 not traverse the internet.
 

 
 
- OCI Site-to-Site VPN 
 OCI Site-to-Site VPN provides IPSec VPN connectivity between your on-premises network and VCNs on OCI. The IPSec protocol suite encrypts IP traffic before the packets are transferred from the source to the destination and decrypts the traffic when it arrives.
 

 
 
- Oracle
 Analytics Cloud 
 Oracle
 Analytics Cloud is a scalable and
