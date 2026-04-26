# Deploy Oracle WebLogic Server in a Kubernetes cluster

- Source: https://docs.oracle.com/en/solutions/deploy-wls-on-oke/index.html
- Date: 2025-04
- Type: reference-architecture
- Services: oke, wls, load-balancer
- Tags: application

## Summary (catalog)

WebLogic on OKE using WebLogic Kubernetes Operator. Automated domain lifecycle management, rolling upgrades, and scaling. Load Balancer for external traffic, Traefik for internal routing.

## Architecture (fetched from source)

Architecture

 

 
This reference architecture shows an Oracle WebLogic Server domain deployed in a Kubernetes cluster provisioned in Oracle Cloud by using OCI Kubernetes Engine . This service makes it easy to create a Kubernetes cluster and provide the required
 services, such as a load balancer, block storage, and networking.
 

 
The following diagram illustrates this reference architecture.
 
 Description of the illustration weblogic-oke.png 
 weblogic-oke-oracle.zip 

 
The architecture has the following components:

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that contains one or more data centers, hosting availability domains. Regions are independent of other regions, and vast distances can separate them (across countries or even continents).
 

 
 
- Availability domains 
Availability domains are standalone, independent data centers within a region. The physical resources in each availability domain are isolated from the resources in the other availability domains, which provides fault tolerance. Availability domains don’t share infrastructure such as power or cooling, or the internal availability domain network. So, a failure at one availability domain shouldn't affect the other availability domains in the region.

 
 
- Fault domains 
A fault domain is a grouping of hardware and infrastructure within an availability domain. Each availability domain has three fault domains with independent power and hardware. When you distribute resources across multiple fault domains, your applications can tolerate physical server failure, system maintenance, and power failures inside a fault domain.

 
 
- Virtual cloud network (VCN) and subnets 
A VCN is a customizable, software-defined network that you set up in an Oracle Cloud
 Infrastructure region. Like traditional data center networks, VCNs give you control over your network environment. A VCN can have multiple non-overlapping CIDR blocks that you can change after you create the VCN. You can segment a VCN into subnets, which can be scoped to a region or to an availability domain. Each subnet consists of a contiguous range of addresses that don't overlap with the other subnets in the VCN. You can change the size of a subnet after creation. A subnet can be public or private. 
 

 
 
- Load balancer 
 Oracle Cloud
 Infrastructure Load Balancing provides automated traffic distribution from a single entry point to multiple servers.
 

 
 
- File storage 
 Oracle Cloud Infrastructure File
 Storage provides a durable, scalable, secure, enterprise-grade network file system. You can connect to OCI File Storage from any bare metal, virtual machine, or container instance in a VCN. You can also access OCI File Storage from outside the VCN by using Oracle Cloud
 Infrastructure FastConnect and IPSec VPN.
 

 
 
- Kubernetes Engine 
 Oracle Cloud Infrastructure Kubernetes Engine ( OCI Kubernetes Engine or OKE ) is a fully-managed, scalable, and highly available service that you can use to deploy your containerized applications to the cloud. You specify the compute resources that your applications require, and Kubernetes Engine provisions them on Oracle Cloud
 Infrastructure in an existing tenancy. OKE uses Kubernetes to automate the deployment, scaling, and management of containerized applications across clusters of hosts.
 

 
 
- Oracle WebLogic Server cluster 
A cluster is part of a particular Oracle WebLogic Server domain. A cluster consists of multiple Oracle WebLogic Server instances running simultaneously and working together to provide increased
 scalability and reliability.
 

 
A WebLogic cluster is different
 from a Kubernetes cluster. A WebLogic cluster appears to clients to be a single
 Oracle WebLogic Server instance. The server instances that constitute a cluster can run on the same
 machine or be on different machines. Each server instance in a cluster must run
 the same version of Oracle WebLogic Server .
 

 
 
- WebLogic Kubernetes operator 
A Kubernetes operator
 is software that manages complex applications. The Oracle WebLogic Kubernetes
 Operator is designed to perform a similar role as a human operator in a
 traditional data center deployment. Its tasks include starting and stopping
 environments, initiating backups, performing scaling operations, performing
 manual tasks associated with disaster recovery and high availability needs, and
 coordinating actions with other operators in other data centers.

 
 
 

 

 
 
Recommendations

 

 
Your requirements might differ from the architecture described here. Use the following recommendations as a starting point.

 
 
- VCN 
When you create a VCN, determine the number of CIDR blocks required and the size of each block based on the number of resources that you plan to attach to subnets in the VCN. Use CIDR blocks that are within the standard private IP address space.

 
Select CIDR blocks that don't overlap with any other network (in Oracle Cloud
 Infrastructure , your on-premises data center, or another cloud provider) to which you intend to set up private connections.
 

 
After you create a VCN, you can change, add, and remove its CIDR blocks.

 
When you design the subnets, consider your traffic flow and security requirements. Attach all the resources within a specific tier or role to the same subnet, which can serve as a security boundary.

 
Use regional subnets.

 
This architecture uses a public subnet to host Oracle Cloud Infrastructure Kubernetes Engine . You can also use a private subnet; in that case, use a NAT gateway to allow
 access to the public internet from the cluster.
 

 
 
- OCI Kubernetes Engine 
Although the Oracle WebLogic Kubernetes Operator supports
 any generic Kubernetes cluster, this architecture uses OCI Kubernetes Engine clusters. These clusters have five worker nodes spread across different
 physical hosts. In the cluster, three worker nodes are dedicated for Oracle WebLogic Server managed servers, one for the WebLogic admin server, and one for the WebLogic
 Kubernetes operator. You can create up to 1000 nodes in a cluster. The worker
 nodes are deployed on VM.Standard2.1 Oracle Linux hosts.
 

 
 
- Load balancer 
By default, the Oracle WebLogic Server servers (admin and managed servers) created by the operator are not exposed
 outside the OCI Kubernetes Engine cluster. To expose the application to the outside world, this architecture
 uses a public load balancer on Oracle Cloud
 Infrastructure Load Balancing . A public load balancer has a public IP address accessible from the internet.
 This architecture uses a load balancer with 100 Mbps for handling the traffic.
 If you need to handle more ingress traffic, you can choose higher bandwidth, up
 to 8000 Mbps.
 

 
 
- File Storage 
To comply with best practices for running Oracle WebLogic Server domains, the domain configuration files in this architecture are stored in
 shared file storage that’s accessible from all WebLogic servers in the cluster.
 This setup offers the following advantages:
 

 
 
- You don't need to rebuild Docker images for changes in the
 domain configuration. 
 
- Backups are faster and centralized. 
 
- Logs are stored by default on persistent storage. 
 
 
 
 

 

 
 
Considerations

 

 
 
- Scalability 
You can scale out your application by updating the number of worker nodes in the Kubernetes cluster, depending on the load. Similarly, you can scale in by reducing the number of worker nodes in the cluster. On the Kubernetes cluster, when you create a service, you can create a load balancer to distribute service traffic among the nodes assigned to that service. Instead of creating the file system and then referencing it from the operator scripts, you could create your persistent volume by using the Oracle Cloud
 Infrastructure provisioner.
 

 
 
- Application availability 
The Kubernetes cluster has three worker nodes for managed servers that are spread across different physical infrastructure,
