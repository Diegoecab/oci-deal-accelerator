# Implement an Oracle Retail Xstore Point of Service on Oracle Cloud Infrastructure

- Source: https://docs.oracle.com/en/solutions/deploy-xstore-oci/index.html
- Date: 2025-06
- Type: reference-architecture
- Services: compute, base-db, load-balancer
- Tags: application

## Summary (catalog)

Oracle Retail Xstore POS on OCI. Compute instances for Xstore application, Base DB for central office database. Load Balancer for HA across multiple Xstore instances.

## Architecture (fetched from source)

Architecture

 

 
This architecture implements Oracle Retail Xstore Point of Service on OCI.
 This architecture containerizing the components of Xstore Point of Service so that they can
 be independently deployed on POS terminals or extended terminals hosted on cloud
 VMs.

 
The following diagram illustrates this reference architecture.

 

 
 
 Description of the illustration deploy-xstore-oci.png 

 
 

 

 deploy-xstore-oci-oracle.zip 
 
 

 
This architecture contains the following components:
 
 
- Tenancy 
A tenancy is a secure and isolated partition that Oracle sets up within Oracle Cloud when you sign up for Oracle Cloud
 Infrastructure . You can create, organize, and administer your resources in Oracle Cloud within your tenancy. A tenancy is synonymous with a company or organization. Usually, a company will have a single tenancy and reflect its organizational structure within that tenancy. A single tenancy is usually associated with a single subscription, and a single subscription usually only has one tenancy.
 

 
 
- Region 
 
 
An Oracle Cloud Infrastructure region is a localized geographic area that
 contains one or more data centers, called availability domains. Regions are
 independent of other regions, and vast distances can separate them (across
 countries or even continents). 

 
 
- Compartment 
 
 
Compartments are cross-region logical partitions within an Oracle Cloud
 Infrastructure tenancy. Use compartments to organize your resources in
 Oracle Cloud, control access to the resources, and set usage quotas. To
 control access to the resources in a given compartment, you define policies
 that specify who can access the resources and what actions they can perform.
 

 
 
- Availability domains 
Availability domains are standalone, independent
 data centers within a region. The physical resources in each availability
 domain are isolated from the resources in the other availability domains,
 which provides fault tolerance. Availability domains don’t share
 infrastructure such as power or cooling, or the internal availability domain
 network. So, a failure at one availability domain is unlikely to affect the
 other availability domains in the region. 

 
 
- Virtual cloud network (VCN) and subnets 
 
 
A VCN is a customizable, software-defined network that you set up in an
 Oracle Cloud Infrastructure region. Like traditional data center networks,
 VCNs give you complete control over your network environment. A VCN can have
 multiple non-overlapping CIDR blocks that you can change after you create
 the VCN. You can segment a VCN into subnets, which can be scoped to a region
 or to an availability domain. Each subnet consists of a contiguous range of
 addresses that don't overlap with the other subnets in the VCN. You can
 change the size of a subnet after creation. A subnet can be public or
 private. 

 
 
- Load balancer 
 
 
The Oracle Cloud Infrastructure Load Balancing service provides automated
 traffic distribution from a single entry point to multiple servers in the
 back end. The load balancer provides access to different applications.
 

 
 
- Security list 
For each subnet, you can create security rules that
 specify the source, destination, and type of traffic that must be allowed in
 and out of the subnet. 

 
 
- NAT gateway 
The NAT gateway enables private resources in a VCN to
 access hosts on the internet, without exposing those resources to incoming
 internet connections. 

 
 
- Service gateway 
The service gateway provides access from a VCN to
 other services, such as Oracle Cloud Infrastructure Object Storage. The
 traffic from the VCN to the Oracle service travels over the Oracle network
 fabric and never traverses the internet.

 
 
- Cloud Guard 
 
 
You can use Oracle Cloud Guard to monitor and maintain the security of your
 resources in Oracle Cloud Infrastructure. Cloud Guard uses detector recipes
 that you can define to examine your resources for security weaknesses and to
 monitor operators and users for risky activities. When any misconfiguration
 or insecure activity is detected, Cloud Guard recommends corrective actions
 and assists with taking those actions, based on responder recipes that you
 can define. 

 
 
- Security zone 
Security zones ensure Oracle's security best practices
 from the start by enforcing policies such as encrypting data and preventing
 public access to networks for an entire compartment. A security zone is
 associated with a compartment of the same name and includes security zone
 policies or a "recipe" that applies to the compartment and its
 sub-compartments. You can't add or move a standard compartment to a security
 zone compartment. 

 
 
- Object storage 
Object storage provides quick access to large amounts
 of structured and unstructured data of any content type, including database
 backups, analytic data, and rich content such as images and videos. You can
 safely and securely store and then retrieve data directly from the internet
 or from within the cloud platform. You can seamlessly scale storage without
 experiencing any degradation in performance or service reliability. Use
 standard storage for "hot" storage that you need to access quickly,
 immediately, and frequently. Use archive storage for "cold" storage that you
 retain for long periods of time and seldom or rarely access. 

 
 
- FastConnect 
 
 
Oracle Cloud Infrastructure FastConnect provides an easy way to create a
 dedicated, private connection between your data center and Oracle Cloud
 Infrastructure. FastConnect provides higher-bandwidth options and a more
 reliable networking experience when compared with internet-based
 connections. 

 
 
- Local peering gateway (LPG) 
An LPG enables you to peer one VCN with
 another VCN in the same region. Peering means the VCNs communicate using
 private IP addresses, without the traffic traversing the internet or routing
 through your on-premises network. 

 
 
- Bastion service 
Oracle Cloud Infrastructure Bastion provides
 restricted and time-limited secure access to resources that don't have
 public endpoints and that require strict resource access controls, such as
 bare metal and virtual machines, Oracle MySQL Database Service Autonomous
 Transaction Processing (ATP), Oracle Container Engine for Kubernetes (OKE),
 and any other resource that allows Secure Shell Protocol (SSH) access. With
 Oracle Cloud Infrastructure Bastion service, you can enable access to
 private hosts without deploying and maintaining a jump host. In addition,
 you gain improved security posture with identity-based permissions and a
 centralized, audited, and time-bound SSH session. Oracle Cloud
 Infrastructure Bastion removes the need for a public IP for bastion access,
 eliminating the hassle and potential attack surface when providing remote
 access.

 
 
- Container Engine for Kubernetes 
Oracle Cloud Infrastructure Container
 Engine for Kubernetes is a fully managed, scalable, and highly available
 service that you can use to deploy your containerized applications to the
 cloud. You specify the compute resources that your applications require, and
 Container Engine for Kubernetes provisions them on Oracle Cloud
 Infrastructure in an existing tenancy. Container Engine for Kubernetes uses
 Kubernetes to automate the deployment, scaling, and management of
 containerized applications across clusters of hosts.

 
 
- Registry 
 
 
Oracle Cloud Infrastructure Registry is an Oracle-managed registry that
 enables you to simplify your development-to-production workflow. Registry
 makes it easy for you to store, share, and manage development artifacts,
 like Docker images. The highly available and scalable architecture of Oracle
 Cloud Infrastructure ensures that you can deploy and manage your
 applications reliably.

 
 
 

 

 

 
 
Recommendations

 

 
 Use the following recommendations as a starting point
 when implementing Oracle Retail Xstore Point of Service on OCI.
 Your requirem
