# Deploy Palo Alto firewall in Active/Active mode with OCI Flexible Network Load Balancer

- Source: https://docs.oracle.com/en/solutions/oci-nlb-palo-alto-active-active/index.html
- Date: 2025-02
- Type: reference-architecture
- Services: load-balancer, vcn, compute
- Tags: networking, security

## Summary (catalog)

Active/Active Palo Alto VM-Series behind OCI Flexible NLB. Symmetric routing with NLB for ingress, route table rules for egress. Health checks for automatic failover on firewall failure.

## Architecture (fetched from source)

Architecture

 

 
The following diagram shows the high-level architecture used for testing the
 Palo Alto Active/Active setup in OCI. 

 
This is a typical hub spoke architecture deployment in OCI, where the Active/Active Palo
 Alto firewall is deployed with four NICs on Hub VCN, added to that we will have a public
 subnet for DMZ in the Hub VCN. The Spoke VCNs will be attached to the DRG in order to
 route all the North-South, East-west via the Palo Alto firewalls. Active/Active setup is
 achieved by adding the Palo Alto VMs as backend of Inbound and Trust NLBs.

 
In this section we will dive deep into the traffic routing and flows in this
 reference architecture. The term "tok" in the names of the resources refer to the region
 Tokyo where this reference architecture model was deployed and tested.

 
 Description of the illustration oci-nlb-palo-alto-active-active-arch.png 

 oci-nlb-palo-alto-active-active-arch-oracle.zip 

 
 North-South Inbound Internet traffic flow to OCI: 

 
The following diagram depicts the flow of DMZ web service exposed to the
 internet. The application load balancer is on a public subnet and the backend servers
 are in private subnets of Spoke VCN. The detailed flow on each hop is described in the
 following steps.

 
 Description of the illustration oci-nlb-palo-alto-active-active-dmz.png 

 oci-nlb-palo-alto-active-active-dmz-oracle.zip 

 
 
- Traffic from the client machine on the internet is routed to the
 Internet gateway (IGW). 
 
- IGW will refer to the internet gateway route table to the subnet
 “hub-tok-publiclb-sn” and route the traffic to the Inbound NLB IP 10.1.1.198. 
 
- Inbound NLB will load balance the traffic to the one of the PA devices
 in the backend using the symmetric hashing algorithm. 
 
- Firewall will validate the policy, route the traffic out of its inbound
 interface on virtual router “inbound-rtr” to the application load balancer that has
 the public IP. 
 

 
Note:
The firewall security policy will be written to the Private IP
 (10.1.1.112) of the public load balancer.
 

 
 
- OCI Flexible Network Load Balancer will perform the Source Network Address Translation (SNAT) for the traffic and
 route it to the dynamic routing gateway (DRG) referring to the subnet route
 table.
 
 
- DRG referring to the route table of the Hub VCN attachment, routes the traffic to
 the Spoke VCN and traffic reaches the web server. 
 
- Web server will send the return traffic to the DRG attachment according to the
 subnet route table. 
 
- DRG will refer to the route table of the Spoke VCN attachment and send
 the traffic to the OCI Flexible Network Load Balancer in the hub.
 
 
- OCI Flexible Network Load Balancer will UNAT the traffic and use the default route of the subnet to send the traffic
 to the Inbound NLB IP 10.1.1.198.
 
 
- Inbound NLB will forward the traffic to the same PA device in the
 backend that initiated the traffic using the symmetric hashing algorithm. 
 
- Palo Alto receives the traffic on the Inbound NIC and per the default
 route of virtual routers sends the traffic back to the internet gateway. 
 
- The internet gateway routes the traffic to the internet client. 
 
 
 North-South Outbound Internet traffic flow from OCI: 

 
The following diagram depicts the flow of outbound internet traffic from OCI.
 All the VMs in OCI will use Palo Alto's SNAT and OCI NAT gateway to access the internet.
 Palo Alto’s SNAT is needed to make the return path symmetric. The outbound public IP
 address will be the IP address of the NAT gateway.

 
 Description of the illustration oci-nlb-palo-alto-active-active-outbound.png 

 oci-nlb-palo-alto-active-active-outbound-oracle.zip 

 
 
- Traffic from the VM in the Spoke subnet using the default route to DRG,
 routes the traffic to the DRG attachment. 
 
- DRG refers to the attachment route table of the spoke and routes the
 traffic to the Hub VCN and transit Route table of VCN routes the traffic to the
 Trust NLB IP 10.1.1.229. 
 
- NLB load balances the traffic to one of the Firewalls in Active/Active
 mode. 
 
- Firewall receives the traffic on trust interface in default virtual
 router. It does SNAT for the traffic to the untrust interface IP and referring to
 default route forwards the traffic to the OCI NAT gateway. 
 
- NAT gateway routes to the traffic to internet using the NAT gateway’s
 Public IP. 
 
- Internet re-routes the return traffic to the NAT gateway. 
 
- NAT gateway UNAT's the traffic and routes it back to the same Palo
 Alto interface as there was a SNAT on Palo Alto. 
 
- Palo Alto based state table and routes on the default virtual router
 sends the traffic out of trust NIC to the DRG after the reverse NAT gateway. 
 
- DRG refers to the route table attached to the Hub VCN and routes to the
 respective Spoke VCN and reaches the source VM. 
 
 
 East-west traffic between spokes in OCI or on-premises to OCI: 

 
The following diagram depicts the flow of traffic between on-premises and
 OCI. To understand the flow of traffic between spokes in OCI, we can consider
 on-premises as one of the spokes. In that case the only change is the route table
 referred on the Spoke attachment. This deployment can be referred to single arm mode,
 where the traffic will enter and leave the same interface of the firewall, here the
 interface is the trust interface.

 
 Description of the illustration oci-nlb-palo-alto-active-active-onprem.png 

 oci-nlb-palo-alto-active-active-onprem-oracle.zip 

 
 
- On-premises traffic is routed to the OCI DRG either via IPSec or OCI FastConnect .
 
 
- DRG refers to the attachment route table of the OCI FastConnect or IPSec and route the traffic to Hub VCN, The VCN attachment route table on the
 hub routes traffic to the Trust NLB IP 10.1.1.229.
 
 
- NLB load balances traffic to the one of the firewalls in Active/Active
 mode. 
 
- Firewall processes traffic according to the security rule and routes
 back to DRG on the Hub route table in the Hub attachment. 
 
- DRG refers to the route table attached to the Hub attachment and routes
 the traffic to respective Spoke VCN and the respective VM. 
 
- The VM sends the return traffic to the DRG referring to the default
 route rule in the route table. 
 
- DRG refers to the route table attached to the Spoke VCN and routes the
 traffic to Hub VCN, Hub transit route table routes the traffic to the Trust
 NLB. 
 
- NLB load balances the traffic to the same Palo Alto device using the
 symmetric hashing algorithm. 
 
- Firewall refers the state table and routes of default virtual router and send the
 traffic back to the DRG on the Hub route table in the Hub attachment. 
 
- DRG refers to the Hub route table in the Hub attachment and routes the
 traffic to on-premises via the OCI FastConnect or IPSec tunnel.
 
 
 
 East-west Outbound traffic flow from OCI VMs to Oracle Services
 Network: 

 
The following diagram depicts the flow of outbound traffic from OCI VMs to
 the Oracle Services Network. All VMs in OCI will use Palo Alto’s SNAT and OCI gervice
 gateway to access the Oracle Services Network. Palo Alto’s SNAT is needed to make the
 return path symmetric. On the Oracle Services Network, if you need to whitelist the VCN,
 it will be the Hub VCN ranges.

 
 Description of the illustration oci-nlb-palo-alto-active-active-osn.png 

 oci-nlb-palo-alto-active-active-osn-oracle.zip 

 
 
- Traffic from the VM in Spoke subnet using the default route to DRG, routes the
 traffic to the DRG attachment. 
 
- DRG refers to the attachment route table of the spoke and routes the
 traffic to Hub VCN and VCN Attachment route table on Hub VCN routes the traffic to
 the Trust NLB IP 10.1.1.229. 
 
- Trust NLB load balances the traffic to the one of the firewalls in
 Active/Active mode. 
 
- Firewall receives the traffic on trust interface on the default virtual
 router. It does SNAT for the traffic to the untrust interface IP. Then referring to
 default route it forwards the traffic to OCI Subne
