# Learn about dynamic routing gateway solutions

- Source: https://docs.oracle.com/en/solutions/learn-about-drg-solutions/index.html
- Date: 2024-09
- Type: reference-architecture
- Services: drg, vcn, fastconnect
- Tags: networking

## Summary (catalog)

DRG v2 capabilities overview. Transit routing, cross-tenancy peering, route distribution policies, and ECMP for link aggregation. Foundation for enterprise-grade OCI network architectures.

## Architecture (fetched from source)

Learn About Dynamic Routing Gateway Solutions 
 
 
 
 
- 
 
- 
 
 
 
 
 
- 
 
 
 
 
 
 
 
 
 
- 
 
 
 
 
 
 
 
 
 
- 
 
- 
 
- 
 
- 
 
- 
 
- 
 
- 
 
- 
 
- 
 
- 
 
- 
 
- 
 
 
 
 

 Previous 
 Next 
 JavaScript must be enabled to correctly display this content
 
 

 

 
 
 
- Learn about dynamic routing gateway solutions 
 
- Learn About Dynamic Routing
 Gateway Solutions 
 
 
 
 
Learn About Dynamic Routing
 Gateway Solutions

 
 

 

 

 
 Use this reference document to learn about Oracle Cloud
 Infrastructure (OCI) virtual network routing. It deciphers IPv4 routing in OCI cloud
 networks, and introduces basic OCI routing functions. It also provides
 typical use cases in different deployment scenarios, which is helpful if you
 need to design, operate, or troubleshoot OCI virtual networks. 
 
 

 
OCI offers a software-defined virtual network solution. An OCI network consists
 of virtual cloud networks (VCNs), subnets, network gateways, OCI native or
 3rd party L4-7 network service virtual appliances, and so on. Routing is the
 core function to establish network connectivity among the elements in an OCI
 network, or between an OCI network and on-premises networks or other cloud
 networks.

 
Full network reachability requires network connectivity that is
 achieved by proper routing and network security policies that are managed
 through Security Lists or Network Security Groups, or policies on network
 firewall appliances. This document solely focuses on routing functions and
 designs, it doesn't discuss management of network security policies. 

 
OCI uses the same routing mechanisms for both IPv4 and IPv6.
 However, there are unique considerations that you must add into an IPv6
 network design. For example, the different scopes of IPv6 addresses and the
 fact that IPv6 Internet Routing does not go through NATing. While the same
 theories apply to IPv4 and IPv6 routing, the discussions and examples here
 focus on IPv4 routing. 

 

 
 
About DRG Routing

 

 
A dynamic routing gateway (DRG) is a regional
 virtual router that inter-connects VCNs in a region and connects the VCNs with on-premises
 networks through Oracle Cloud
 Infrastructure FastConnect virtual circuits or IPSec VPN tunnels. It also provides network connectivity between
 regions through a Remote Peering Connection (RPC).
 

 
A DRG acts like a central hub to connect the network resources that are
 attached to it. The network resources can be VCNs, site-to-site IPSec VPN tunnels, OCI FastConnect virtual circuits, or RPC. When a network resource is attached to a DRG, an attachment
 of the corresponding type is created:
 
 
- Virtual Cloud Network Attachment (VCN Attachment): When a VCN
 attached to the DRG 
 
- Virtual Circuit Attachment (VC Attachment): When an OCI FastConnect virtual circuit is attached to the DRG
 
 
- IPSec Tunnel Attachment: When an IPSec tunnel is attached to the
 DRG 
 
- Remote Peering Connection Attachment (RPC Attachment): When an RPC
 is attached to the DRG 
 DRG routes traffic between the attachments using DRG route tables. Each attachment
 is associated with a DRG route table. Traffic enters DRG from an attachment and is
 routed to another attachment by the DRG based on the DRG route table associated with the
 ingress attachment of the traffic.
 

 

 

 
 
Routing Tables on DRG

 

 

 A dynamic routing gateway (DRG) uses
 DRG route tables to route traffic between its attachments. OCI automatically generates
 two route tables for each DRG, one for VCN attachments and the second one is for IPSec,
 OCI FastConnect Virtual Circuit Attachment, and Remote Peering Connection (RPC) attachments. You can
 create more DRG route tables. 
 
 

 
The route rules in a DRG route table contains the following fields:
 
 
- Type: The route type can be dynamic or static. Dynamic routes are imported from
 the DRG attachments. You can use the OCI Console or API to create static routes. 
 
- Destination CIDR: The destination CIDR. 
 
- Next Hop Attachment Type: The next hop of a route rule in a DRG
 route table is the DRG attachment of the network where the destination resides
 or in route to the destination. The attachment can be a VCN attachment, a
 cross-regional RPC attachment, or a cross-tenancy RPC attachment. It cannot be a
 VPN attachment or OCI FastConnect virtual circuit attachment.
 
 
- Next Hop Attachment Name: The name of the attachment. 
 
- Route Status: Status. 
 
 

 
The following is an example of the contents of a DRG route table.
 

 
 
 
 Type 
 Destination CIDR 
 Next Hop Attachment Type 
 Next Hop Attachment Name 
 Route Status 
 
 
 
 
 Dynamic 
 0.0.0.0/0 
 Virtual Cloud Network (VCN) 
 Att-DRG-1-VCN-0 
 Active 
 
 
 Dynamic 
 10.0.0.0/8 
 IPSec Tunnel 
 DRG Attachment for IPSec Tunnel: IPSec Tunnel to
 On-premises 2 
 Active 
 
 
 Dynamic 
 10.0.0.0/16 
 Virtual Cloud Network 
 Attachment DRG 1 to VCN 0 
 Active 
 
 
 Dynamic 
 21.0.1.0/24 
 Remote Peering Connection 
 DRG Attachment for RPC: RPC to SJC-DRG-1 (us-west-1
 San Jose-DRG-1) 
 Active 
 
 
 
 

 
 

 
Each DRG attachment has one DRG route table associated with it. By default, it is the
 auto-generated DRG route table for the attachment type. You can change it to a
 user-created DRG route table.

 
When traffic gets onto a DRG, the DRG performs ingress routing lookup based on the DRG
 route table associated with the ingress attachment of the traffic. The routing lookup
 resolves the next-hop attachment (the egress attachment). The DRG sends the traffic onto
 the egress attachment through which the traffic will get to the next-hop network. There
 is no routing lookup at the egress attachment on the DRG. 

 

 

 
 
Route Preference in DRG Route
 Table

 

 

 It's possible that multiple routes for the identical prefix
 and mask show up in a DRG route table. The dynamic routing gateway has a
 built-in mechanism to resolve such route conflicts. The decision is made
 based on the following route preference and is evaluated in the following
 order: 
 
 

 
 
- In a DRG route table, static routes have higher preference
 than dynamic routes. 
 
- Among dynamic routes in a DRG route table, routes with
 shorter AS-path are preferred over routes with a longer
 AS-path.
 

 
Note:
Routes with a route source of VCN or STATIC always have an
 empty AS Path. Routes with a route source of IPSec VPN
 tunnel or OCI FastConnect virtual circuit will have the AS Paths shown in the
 following table.
 

 

 
 
 
 Route Source 
 Details of how Oracle prefers
 the path 
 Resulting AS path for the
 route 
 
 
 
 
 OCI FastConnect 
 OCI prepends no ASNs to the
 routes. This results in a total AS path length of
 1. 
 Customer ASN 
 
 
 Site-to-Site VPN with Border
 Gateway Protocol (BGP) routing 
 OCI prepends a single private
 ASN on all the routes that customer edge device
 advertises over Site-to-Site VPN with BGP, for a
 total AS path length of 2. 
 
 
Private ASN,
 
Customer ASN
 
 
 
 Site-to-Site VPN with static
 routing 
 OCI advertises those static
 routes to DRG as BGP dynamic routes. OCI prepends
 3 private ASNs on these routes. This results in a
 total AS path length of 3. 
 
 
Private ASN,
 

 
Private ASN, 
Private
 ASN
 
 
 
 
 

 
 
 
- The attachment type that imported the route is evaluated
 according to the following priority based on the attachment type:
 
 
- VCN 
 
- VIRTUAL_CIRCUIT : If
 Equal-cost multi-path routing (ECMP) is disabled for
 the DRG route table, then the DRG makes an arbitrary
 but stable selection. If ECMP is enabled, then all
 routes are added to the route table and the DRG
 makes routing choices using ECMP. The maximum
 supported ECMP width inside a DRG is 8.
 
 
- IPSEC_TUNNEL : If ECMP is
 disabled for the DRG route table, the DRG makes an
 arbitrary but stable selection. If ECMP is enabled,
 all routes will be added to the route table and the
 DRG makes routing choices using ECMP. The maximum
 supported ECMP width inside a DRG is 8.
 
 
- REMOTE_PEERING_CONNECTION 
 (RP
