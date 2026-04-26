# Deploy secure ADB and APEX application

- Source: https://docs.oracle.com/en/solutions/deploy-autonomous-database-and-app/index.html
- Date: 2024-06
- Type: reference-architecture
- Services: adb-s, apex, load-balancer, bastion, cloud-guard
- Tags: database, application, security, autonomous

## Summary (catalog)

APEX on ADB-S with private endpoint behind Load Balancer. OCI Landing Zone via Terraform provisions in minutes. Recommends NSGs over Security Lists, Cloud Guard with custom detector recipes.

## Architecture (fetched from source)

Architecture

 

 
This architecture leverages the load balancer to isolate an Oracle Autonomous Transaction
 Processing database in a separate private subnet. The Oracle Cloud
 Infrastructure (OCI) landing zone automated by Terraform provides a secure infrastructure for running
 the Oracle APEX application on top of the shared Oracle Autonomous Database exposed by the private
 endpoint.
 

 
The following diagram illustrates this reference architecture.
 
 Description of the illustration apex-app-adb.png 
 apex-app-adb-oracle.zip 

 
The architecture has the following components:

 
 
- Tenancy 
A tenancy is a secure and isolated partition that Oracle sets up within Oracle Cloud when you sign up for Oracle Cloud
 Infrastructure . You can create, organize, and administer your resources in Oracle Cloud within your tenancy. A tenancy is synonymous with a company or organization. Usually, a company will have a single tenancy and reflect its organizational structure within that tenancy. A single tenancy is usually associated with a single subscription, and a single subscription usually only has one tenancy.
 

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that contains one or more data centers, called availability domains. Regions are independent of other regions, and vast distances can separate them (across countries or even continents).
 

 
 
- Compartment 
Compartments are cross-region logical partitions within an Oracle Cloud
 Infrastructure tenancy. Use compartments to organize your resources in Oracle Cloud , control access to the resources, and set usage quotas. To control access to the resources in a given compartment, you define policies that specify who can access the resources and what actions they can perform.
 

 
 
- Availability domains 
Availability domains are standalone, independent data centers within a region. The physical resources in each availability domain are isolated from the resources in the other availability domains, which provides fault tolerance. Availability domains don’t share infrastructure such as power or cooling, or the internal availability domain network. So, a failure at one availability domain is unlikely to affect the other availability domains in the region.

 
 
- Virtual cloud network (VCN) and subnets 
A VCN is a customizable, software-defined network that you set up in an Oracle Cloud
 Infrastructure region. Like traditional data center networks, VCNs give you complete control over your network environment. A VCN can have multiple non-overlapping CIDR blocks that you can change after you create the VCN. You can segment a VCN into subnets, which can be scoped to a region or to an availability domain. Each subnet consists of a contiguous range of addresses that don't overlap with the other subnets in the VCN. You can change the size of a subnet after creation. A subnet can be public or private. 
 

 
 
- Load balancer 
The Oracle Cloud
 Infrastructure Load Balancing service provides automated traffic distribution from a single entry point to multiple servers in the back end.
 

 
 
- Network security group (NSG) 
NSGs act as virtual firewalls for your cloud resources. With the zero-trust security model of Oracle Cloud
 Infrastructure , all traffic is denied, and you can control the network traffic inside a VCN. An NSG consists of a set of ingress and egress security rules that apply to only a specified set of VNICs in a single VCN.
 

 
 
- Network address translation (NAT) gateway 
A NAT gateway enables private resources in a VCN to access hosts on the internet, without exposing those resources to incoming internet connections.

 
 
- Service gateway 
The service gateway provides access from a VCN to other services, such as Oracle Cloud
 Infrastructure Object Storage . The traffic from the VCN to the Oracle service travels over the Oracle network fabric and never traverses the internet.
 

 
 
- Internet gateway 
The internet gateway allows traffic between the public subnets in a VCN and the public internet.

 
 
- Autonomous database 
 Oracle Cloud
 Infrastructure autonomous databases are fully managed, preconfigured database environments that you can use for transaction processing and data warehousing workloads. You do not need to configure or manage any hardware, or install any software. Oracle Cloud
 Infrastructure handles creating the database, as well as backing up, patching, upgrading, and tuning the database.
 

 
 
- Autonomous Transaction Processing 
 Oracle Autonomous Transaction
 Processing is a self-driving, self-securing, self-repairing database service that is
 optimized for transaction processing workloads.
 

 
 
- Bastion service 
 Oracle Cloud
 Infrastructure Bastion provides restricted and time-limited secure access to resources that don't have public endpoints and that require strict resource access controls, such as bare metal and virtual machines, Oracle MySQL Database Service , Autonomous Transaction
 Processing (ATP), Oracle Container Engine for
 Kubernetes (OKE), and any other resource that allows Secure Shell Protocol (SSH) access. With Oracle Cloud
 Infrastructure Bastion service, you can enable access to private hosts without deploying and maintaining a jump host. In addition, you gain improved security posture with identity-based permissions and a centralized, audited, and time-bound SSH session. Oracle Cloud
 Infrastructure Bastion removes the need for a public IP for bastion access, eliminating the hassle and potential attack surface when providing remote access.
 

 
 
 

 

 
 
Recommendations

 

 
 Use the following recommendations as a starting
 point. Your requirements might differ from the
 architecture described here. 
 

 
 
- VCN 
A VCN is deployed by the terraform solution, but this solution is
 modular and you can use an existing VCN.

 
When you create a VCN, determine the number of CIDR blocks required and the size of each block based on the number of resources that you plan to attach to subnets in the VCN. Use CIDR blocks that are within the standard private IP address space.

 
Select CIDR blocks that don't overlap with any other network (in Oracle Cloud
 Infrastructure , your on-premises data center, or another cloud provider) to which you intend to set up private connections.
 

 
After you create a VCN, you can change, add, and remove its CIDR blocks.

 
When you design the subnets, consider your traffic flow and security requirements. Attach all the resources within a specific tier or role to the same subnet, which can serve as a security boundary.

 
 
- Network security groups (NSGs) 
You can use NSGs to define a set of ingress and egress rules that apply to specific VNICs. We recommend using NSGs rather than security lists, because NSGs enable you to separate the VCN's subnet architecture from the security requirements of your application.

 
 
- Cloud Guard 
Clone and customize the default recipes provided by Oracle to create custom detector and responder recipes. These recipes enable you to specify what type of security violations generate a warning and what actions are allowed to be performed on them. For example, you might want to detect Object Storage buckets that have visibility set to public. 

 
Apply Cloud Guard at the tenancy level to cover the broadest scope and to reduce the administrative burden of maintaining multiple configurations.

 
You can also use the Managed List feature to apply certain configurations to detectors.

 
 
- Load balancer bandwidth 
While creating the load balancer, you can either select a predefined shape that provides a fixed bandwidth, or specify a custom (flexible) shape where you set a bandwidth range and let the service scale the bandwidth automatically based on traffic patterns. With either approach, you can change the shape at any time after creating the load balancer. 

 
 
 

 

 
 
Considerations

 

 
Consider the following points when deploying this reference
 archit
