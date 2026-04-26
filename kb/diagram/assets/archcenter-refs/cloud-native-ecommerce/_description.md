# Deploy a microservices-based application in Kubernetes connected to an autonomous database

- Source: https://docs.oracle.com/en/solutions/cloud-native-ecommerce/index.html
- Date: 2025-04
- Type: reference-architecture
- Services: oke, adb-s, api-gateway, streaming, waf, vault, functions
- Tags: application, autonomous

## Summary (catalog)

Cloud-native e-commerce on OKE with ADB-S. Regional VCN subnets, VM.Standard2.1 shapes, up to 1000 nodes. API Gateway for ingress, WAF + Vault for security, Streaming for event-driven microservices.

## Architecture (fetched from source)

Architecture

 

 
In a microservices architecture, each microservice performs a simple task, and communicates with clients or other microservices by using lightweight mechanisms such as REST API requests.

 
This reference architecture is for an e-commerce application that's composed of multiple polyglot microservices deployed as Docker containers in a Kubernetes cluster. Data persistence is achieved using an Oracle Autonomous Transaction
 Processing database. Media and image files for the e-commerce application are stored in Oracle Cloud
 Infrastructure Object Storage .
 

 
The following diagram illustrates the architecture.

 
 Description of the illustration mushop-infrastructure.png 

 mushop-infrastructure-oracle.zip 

 
The architecture has the following components:

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that contains one or more data centers, hosting availability domains. Regions are independent of other regions, and vast distances can separate them (across countries or even continents).
 

 
 
- Availability domain 
Availability domains are standalone, independent data centers within a region. The physical resources in each availability domain are isolated from the resources in the other availability domains, which provides fault tolerance. Availability domains don’t share infrastructure such as power or cooling, or the internal availability domain network. So, a failure at one availability domain shouldn't affect the other availability domains in the region.

 
 
- Fault domains 
A fault domain is a grouping of hardware and infrastructure within an availability domain. Each availability domain has three fault domains with independent power and hardware. OCI Kubernetes Engine handles distribution of the nodes in the cluster across multiple fault domains. So your containerized application is protected against physical server failure, system maintenance, and power failure within an fault domain.
 

 
 
- Virtual cloud network (VCN) and subnets 
A VCN is a customizable, software-defined network that you set up in an Oracle Cloud
 Infrastructure region. Like traditional data center networks, VCNs give you control over your network environment. A VCN can have multiple non-overlapping CIDR blocks that you can change after you create the VCN. You can segment a VCN into subnets, which can be scoped to a region or to an availability domain. Each subnet consists of a contiguous range of addresses that don't overlap with the other subnets in the VCN. You can change the size of a subnet after creation. A subnet can be public or private. 
 

 
 
- Service gateway 
A service gateway provides access from a VCN to other services, such as Oracle Cloud
 Infrastructure Object Storage . The traffic from the VCN to the Oracle service travels over the Oracle network fabric and does not traverse the internet.
 

 
 
- Network address translation (NAT) gateway 
A NAT gateway enables private resources in a VCN to access hosts on the internet, without exposing those resources to incoming internet connections.

 
 
- Internet gateway 
An internet gateway allows traffic between the public subnets in a VCN and the public internet.

 
 
- Autonomous Transaction
 Processing 
 Oracle Autonomous Transaction
 Processing is a self-driving, self-securing, self-repairing database service that is optimized for transaction processing workloads. You do not need to configure or manage any hardware, or install any software. Oracle Cloud
 Infrastructure handles creating, backing up, patching, upgrading, and tuning the database.
 

 
 
- Object storage 

 OCI Object Storage provides access to large amounts of structured
 and unstructured data of any content type,
 including database backups, analytic data, and
 rich content such as images and videos. You can
 safely and securely store data directly from the
 internet or from within the cloud platform. You
 can scale storage without experiencing any
 degradation in performance or service reliability.
 
 

 
In this architecture, the media assets of the application are stored in Oracle Cloud
 Infrastructure Object Storage in a bucket of the standard storage class.
 

 
 
- Kubernetes Engine 
 Oracle Cloud Infrastructure Kubernetes Engine ( OCI Kubernetes Engine or OKE ) is a fully-managed, scalable, and highly available service that you can use to deploy your containerized applications to the cloud. You specify the compute resources that your applications require, and Kubernetes Engine provisions them on Oracle Cloud
 Infrastructure in an existing tenancy. OKE uses Kubernetes to automate the deployment, scaling, and management of containerized applications across clusters of hosts.
 

 
The following diagram shows the interactions
 between the containerized microservices in this architecture:

 
 Description of the illustration mushop-infrastructure-expand.png 

 mushop-infrastructure-expand-oracle.zip 

 
Traffic from the public internet is routed by the DNS service
 through a web application firewall (WAF) to the load balancer, which forwards
 the incoming requests to an Ingress (Nginx) microservice. The Ingress
 microservice sends traffic to a Router (Traefik) microservice. Depending on the
 nature of the requests, the Router microservice routes them to the appropriate
 microservices in the application. Besides interacting with other microservices,
 many of the microservices also interact with Oracle Cloud
 Infrastructure services: OCI Object Storage , OCI API Gateway , OCI Functions , OCI Email Delivery , OCI Streaming , and Oracle Autonomous Database .
 

 
 
 

 

 
 
Recommendations

 

 
 Use the following recommendations as a starting point. Your requirements might differ from the architecture described here. 

 
 
- VCN 
When you create a VCN, determine the number of CIDR blocks required and the size of each block based on the number of resources that you plan to attach to subnets in the VCN. Use CIDR blocks that are within the standard private IP address space.

 
Select CIDR blocks that don't overlap with any other network (in Oracle Cloud
 Infrastructure , your on-premises data center, or another cloud provider) to which you intend to set up private connections.
 

 
After you create a VCN, you can change, add, and remove its CIDR blocks.

 
When you design the subnets, consider your traffic flow and security requirements. Attach all the resources within a specific tier or role to the same subnet, which can serve as a security boundary.

 
Use regional subnets.

 

 
Note:
The Terraform code to implement this architecture provisions the Oracle Autonomous Transaction
 Processing database in the Oracle services network. If you prefer to expose only a private endpoint for the database, then you can adjust the Terraform code to attach the database to a private subnet, as shown in the architecture diagram.
 

 
 
- OCI Kubernetes Engine 
In this architecture, the worker nodes in the Kubernetes
 cluster use the VM.Standard2.1 shape, and they run on Oracle Linux. You can
 create up to 1000 nodes in a cluster.

 
 
 

 

 
 
Considerations

 

 
When implementing this architecture, consider your requirements for the following parameters:

 
 
- Scalability 
You can scale out your application by updating the number of worker nodes in the Kubernetes cluster, depending on the load. Similarly, you can scale in by reducing the number of worker nodes in the cluster. When you create a service on the Kubernetes cluster, you can create a load balancer to distribute service traffic among the nodes assigned to the service. This architecture uses a load balancer to handle incoming requests.

 
 
- Application availability 
Fault domains provide resilience
 within a single availability domain. You can also deploy instances or nodes that
 perform the same tasks in multiple availability domains. This design removes
 single points of failure by introducing redundancy. In this architecture, Oracle Cl
