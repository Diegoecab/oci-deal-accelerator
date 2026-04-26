# Protect your workloads in the cloud using security zones

- Source: https://docs.oracle.com/en/solutions/oci-security-zones/index.html
- Date: 2024-11
- Type: reference-architecture
- Services: cloud-guard
- Tags: security

## Summary (catalog)

Security Zones for preventive policy enforcement. Prevents creation of non-compliant resources (public buckets, unencrypted volumes). Combines with Cloud Guard for detective + preventive controls.

## Architecture (fetched from source)

Architecture

 

 
This reference architecture shows a typical three-tier architecture that you can use to securely run applications such as e-commerce applications. Data persistence is achieved using an Oracle Autonomous Transaction
 Processing database. Media and image files for the application are stored in Oracle Cloud
 Infrastructure Object Storage .
 

 
The following diagram shows a basic compartment architecture.

 
 Description of the illustration msz-01.png 

 msz-01-oracle.zip 

 
The architecture has the following security limitations:

 
 
- Object storage : Unencrypted object storage is exposed directly to the internet.
 
 
- Database : The database is not encrypted with customer-managed key and can be exposed to the internet with a single configuration change (public IP address).
 
 
- Compartment : The compartment does not restrict movement of data, assets, volumes in or out of the environment.
 
 
- Virtual machines : VMs do not use encrypted boot volumes or storage. 
 
 
- Internet : Web application firewall (WAF) protections are not provided. 
 
 
- Network : All resources are on a single plane and provide insufficient isolation.
 
 
 
The following diagram shows an architecture that addresses these concerns by providing a highly secure environment that isolates multiple spoke networks, each representing an application tier, such as web, application, and database. This architecture works in specific environments, such as production, test, and development environments, and on different infrastructures, such as cloud region, on-premises data center, and multicloud infrastructures.

 
 Description of the illustration msz-02.png 

 msz-02-oracle.zip 

 
The architecture has the following components:

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that contains one or more data centers, called availability domains. Regions are independent of other regions, and vast distances can separate them (across countries or even continents).
 

 
 
- Availability domain 
Availability domains are standalone, independent data centers within a region. The physical resources in each availability domain are isolated from the resources in the other availability domains, which provides fault tolerance. Availability domains don’t share infrastructure such as power or cooling, or the internal availability domain network. So, a failure at one availability domain shouldn't affect the other availability domains in the region.

 
 
- Fault domain 
A fault domain is a grouping of hardware and infrastructure within an availability domain. Each availability domain has three fault domains with independent power and hardware. When you distribute resources across multiple fault domains, your applications can tolerate physical server failure, system maintenance, and power failures inside a fault domain.

 
 
- Compartment 
Compartments are cross-regional logical partitions within an Oracle Cloud
 Infrastructure tenancy. Use compartments to organize, control access, and set usage quotas for your Oracle Cloud resources. In a given compartment, you define policies that control access and set privileges for resources.
 

 
 
- Security zone 
Security zones ensure Oracle's security best practices from the start by enforcing policies such as encrypting data and preventing public access to networks for an entire compartment. A security zone is associated with a compartment of the same name and includes security zone policies or a "recipe" that applies to the compartment and its sub-compartments. You can't add or move a standard compartment to a security zone compartment.

 
In this use-case, the security zone enforces the following policies:

 
 
- Encrypt boot volumes of the compute instances and object storage buckets 
 
- Prevent compute resources from being accessed from the public internet 
 
- Encrypt resources using customer-managed keys 
 
- Regularly and automatically back up all resources 
 
 
 
- Virtual cloud network (VCN) and subnets 
A VCN is a customizable, software-defined network that you set up in an Oracle Cloud
 Infrastructure region. Like traditional data center networks, VCNs give you control over your network environment. A VCN can have multiple non-overlapping CIDR blocks that you can change after you create the VCN. You can segment a VCN into subnets, which can be scoped to a region or to an availability domain. Each subnet consists of a contiguous range of addresses that don't overlap with the other subnets in the VCN. You can change the size of a subnet after creation. A subnet can be public or private. 
 

 
 
- Security lists 
For each subnet, you can create security rules that specify the source, destination, and type of traffic that must be allowed in and out of the subnet.

 
 
- Load balancers 
The Oracle Cloud
 Infrastructure Load Balancing service provides automated traffic distribution from a single entry point to multiple servers in the back end.
 

 
This architecture uses separate load balancers for the administrator's applications and the self-service applications, for tighter security and traffic separation. You can upgrade the load balancer shape if needed.

 
 
- Service gateway 
The service gateway provides access from a VCN to other services, such as Oracle Cloud
 Infrastructure Object Storage . The traffic from the VCN to the Oracle service travels over the Oracle network fabric and does not traverse the internet.
 

 
 
- Local peering gateway (LPG) 
An LPG enables you to peer one VCN with another VCN in the same region. Peering means the VCNs communicate using private IP addresses, without the traffic traversing the internet or routing through your on-premises network.

 
 
- Object storage 
 Oracle Cloud
 Infrastructure Object Storage provides quick access to large amounts of structured and unstructured data of any content type, including database backups, analytic data, and rich content such as images and videos. You can safely and securely store and then retrieve data directly from the internet or from within the cloud platform. You can scale storage without experiencing any degradation in performance or service reliability. Use standard storage for "hot" storage that you need to access quickly, immediately, and frequently. Use archive storage for "cold" storage that you retain for long periods of time and seldom or rarely access.
 

 
 
- Compute 
With Oracle Cloud Infrastructure
 Compute , you can provision and manage compute hosts in the cloud. You can launch compute instances with shapes that meet your resource requirements for CPU, memory, network bandwidth, and storage. After creating a compute instance, you can access it securely, restart it, attach and detach volumes, and terminate it when you no longer need it.
 

 
 
- 
 
 Web Application Firewall 

 
 Oracle Cloud Infrastructure Web
 Application Firewall (WAF) is a cloud-based, payment card industry (PCI) compliant, global security service that protects applications from malicious and unwanted internet traffic. WAF can protect any internet-facing endpoint, providing consistent rule enforcement across a customer's applications.
 

 
 
 

 

 
 
Recommendations

 

 
Your requirements might differ from the architecture described here. Use the following recommendations as a starting point.

 
 
- VCN 
When you create a VCN, determine the number of CIDR blocks required and the size of each block based on the number of resources that you plan to attach to subnets in the VCN. Use CIDR blocks that are within the standard private IP address space.

 
Select CIDR blocks that don't overlap with any other network (in Oracle Cloud
 Infrastructure , your on-premises data center, or another cloud provider) to which you intend to set up private connections.
 

 
After you create a VCN, you can change, add, and remove its CIDR blocks.

 
When you design the subnets, consider your traffic flow and security requirements. Attach all the resour
