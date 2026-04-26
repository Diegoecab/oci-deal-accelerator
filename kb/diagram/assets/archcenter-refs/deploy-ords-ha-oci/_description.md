# Deploy ORDS with High Availability on OCI

- Source: https://docs.oracle.com/en/solutions/deploy-ords-ha-oci/index.html
- Date: 2025-06
- Type: reference-architecture
- Services: compute, load-balancer, adb-s, bastion
- Tags: database, application, ha-dr

## Summary (catalog)

Multi-instance ORDS behind OCI Load Balancer for HA REST access to Oracle DB. Works with ADB-S, DBCS, or ExaCS. Recommends DB in private subnet, ORDS in public with granular NSG rules.

## Architecture (fetched from source)

Architecture

 

 
This architecture shows you how to deploy Oracle REST Data Services with high
 availability on OCI.

 
The architecture starts with a Virtual Cloud Network (VCN) within a single
 region. While this VCN can span multiple Availability Domains (AD), for this reference
 architecture, it uses a single AD. That AD contains multiple fault domains—areas within
 an AD that have grouped hardware and infrastructure. Compute VMs with ORDS are deployed
 across multiple fault domains to help in attaining high availability. 

 
In the VCN, multiple subnets contain specific architectural components. It
 starts with an Internet gateway, which only allows traffic over a specified port to the
 load balancers on the front end of this VCN in a public subnet. The load balancers also
 have a public facing IP you can later use to apply custom domain names, if needed. The
 load balancer will talk to the subnet containing the ORDS compute mid-tiers.
 Communication is secured by subnet-wide security lists as well as network security
 groups (NSG). You can apply these NSGs to a set of VNICs on the compute and load
 balancers to provide granular security rules for communication between these resources. 

 
Finally, again employing security lists and NSGs, the ORDS mid-tiers can
 access an Oracle database in a private subnet. Resources using private subnets are not
 given public facing IPs. This way, you can use the NSGs for a secure communication layer
 between the public and private subnets. The Oracle database instance in this private
 subnet can be a VM DB instance, an autonomous database, or an Exadata Cloud Service
 database. 

 
The following diagram illustrates this reference architecture.

 
 
 Description of the illustration ha-ords-oci3.png 

 

 ha-ords-oci3.zip 
 
 

 
This architecture has the following components:
 
 
- Region 
 
 
An OCI region is a localized geographic area that contains one or
 more data centers, called availability domains. Regions are independent of
 other regions, and vast distances can separate them (across countries or
 even continents). 

 
 
- Availability domains 
 
 
Availability domains are standalone, independent data centers within a
 region. The physical resources in each availability domain are isolated from
 the resources in the other availability domains, which provides fault
 tolerance. Availability domains don’t share infrastructure such as power or
 cooling, or the internal availability domain network. So, a failure at one
 availability domain is unlikely to affect the other availability domains in
 the region. The resources in this architecture are deployed in a single
 availability domain. 

 
 
- Fault domains 
 
 
A fault domain is a grouping of hardware and infrastructure within an
 availability domain. Each availability domain has three fault domains with
 independent power and hardware. When you distribute resources across
 multiple fault domains, your applications can tolerate physical server
 failure, system maintenance, and power failures inside a fault domain. The
 resources in this architecture are deployed in multiple fault domains.
 

 
 
- Virtual cloud network (VCN) and subnets 
 
 
A VCN is a customizable, software-defined network that you set up
 in an OCI region. Like traditional data center networks, VCNs give you
 complete control over your network environment. A VCN can have multiple
 non-overlapping CIDR blocks that you can change after you create the VCN.
 You can segment a VCN into subnets, which can be scoped to a region or to an
 availability domain. Each subnet consists of a contiguous range of addresses
 that don't overlap with the other subnets in the VCN. You can change the
 size of a subnet after creation. A subnet can be public or private. 

 
In this reference architecture, the compute instances with ORDS
 are attached to a public subnet along with the load balancer while the
 databases can use either a private or public subnet. Database Security best
 practices put database instances in private subnets whenever
 possible.

 
 
- Load Balancer 
 
 
The Oracle Cloud
 Infrastructure Load Balancing service provides automated traffic distribution from a single entry point
 to multiple servers in the back end. This load balancer's public IP will
 also serve as where we can register custom domain names if needed.
 

 
 
- API Gateway 
Oracle Cloud Infrastructure API Gateway enables you to
 publish APIs with private endpoints that are accessible from within your
 network, and which you can expose to the public internet, if required. The
 endpoints support API validation, request and response transformation, CORS,
 authentication and authorization, and request limiting.

 
 
- Compute Instances/ORDS Hosts 
 Oracle Cloud Infrastructure
 Compute lets you provision and manage compute hosts. You can launch compute
 instances with shapes that meet your resource requirements (CPU, memory,
 network bandwidth, and storage). After creating a compute instance, you can
 access it securely, restart it, attach and detach volumes, and terminate it
 when you don't need it. The web servers in this architecture run on compute
 virtual machines using either an x86 or ARM CPU architecture 
 

 
 
- Database Instances 
 
 
The Database service offers autonomous and co-managed Oracle Database cloud solutions. Autonomous databases are preconfigured, fully-managed
 environments that are suitable for either transaction processing or for data
 warehouse workloads. Co-managed solutions are bare metal, virtual machine,
 and Exadata DB systems that you can customize with the resources and
 settings that meet your needs. 
 

 
This reference
 architecture can be used for either autonomous databases or co-managed
 database instances. 

 
 
- Network security groups (NSG) 
 
 
NSGs act as virtual firewalls for your compute instances. With
 the zero-trust security model of OCI, all traffic is denied, and you can
 control the network traffic inside a VCN. An NSG consists of a set of
 ingress and egress security rules that apply to only a specified set of
 VNICs in a single VCN. In this architecture, separate NSGs are used for the
 load balancer, web servers, and the database.

 
 
- Route Tables 
 
 
Virtual route tables contain rules to route traffic from subnets to
 destinations outside a VCN, typically through gateways.

 
 
- Internet Gateway 
The internet gateway allows traffic between the
 public subnets in a VCN and the public internet.

 
 
- Security Lists 
Security list are a set of
 ingress and egress rules that specify the types of traffic allowed in and
 out for all VNICs/instances in a subnet. Security Lists are applied at
 subnet level vs NSGs are applied at a VNIC level. Both effectively act as a
 firewall for a VNIC. With OCI's zero-trust security model, all traffic to a
 VNIC is denied. Both SL and NSG need to allow the traffic explicitly, for
 the traffic to be permitted to the VNIC.

 
 
- Zero-Trust Packet Routing (ZPR) 
 
 
In addition to SL and NSG, OCI has a network security construct called
 Zero-Trust Packet Routing. ZPR is intent-based secure networking acting at
 layer 4 and can be implemented in human readable policy language. By
 assigning security attributes ("tags" for ZPR) to your resources, you can
 create granular access controls to ensure that only authorized entities can
 communicate with sensitive components, such as databases and application
 servers. This approach not only reduces the risk of unauthorized access but
 also simplifies policy management as your application evolves. ZPR operates
 alongside existing NSGs and SLs, providing a more comprehensive security
 posture that adapts to changes in your network architecture. Here you can
 assign security attributes (special ZPR tags) to nodes in each subnet, in
 such a way that only required traffic is permitted (flow direction, protocol
 and ports), no matter how the network architecture changes/shifts in
 future.

 
 
 


