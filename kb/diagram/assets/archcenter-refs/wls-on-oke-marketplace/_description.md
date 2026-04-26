# Deploy Oracle WebLogic Server for OKE using a marketplace stack

- Source: https://docs.oracle.com/en/solutions/wls-on-oke-marketplace/index.html
- Date: 2025-04
- Type: reference-architecture
- Services: oke, wls, load-balancer
- Tags: application

## Summary (catalog)

One-click WebLogic on OKE via OCI Marketplace. Resource Manager stack provisions OKE cluster, WebLogic domain, and networking. Simplified deployment for standard WebLogic topologies.

## Architecture (fetched from source)

Architecture 

 

 
 Oracle WebLogic Server
 for OCI is fully integrated with the underlying infrastructure. This integration makes it easy to
 provision a WebLogic cluster, to create and configure the required infrastructure, and to
 provide the required services, such as load balancers and file storage. 
 

 
The architecture uses a region with one availability domain and regional subnets. The same reference architecture can be used in a region with multiple availability domains. We recommend using a regional subnet for your deployment, regardless of the number of availability domains.

 
When provisioned, this reference architecture includes the following:

 
 
- An OCI Kubernetes Engine (OKE) cluster deployed in a private subnet with two node pools
 
 
- A file storage service that's shared across pods 
 
- An administrative host deployed in a private subnet to easily access the following areas:
 
 
- The OCI Kubernetes Engine cluster
 
 
- Logs for the Oracle WebLogic Server domain
 
 
- Jenkins home configuration 
 
- Helper scripts to manage your domain 
 
- The file storage service 
 
 
 
- A bastion host deployed in a public subnet to access the resources deployed in the private subnet 
 
- n private load balancer to access the Jenkins console and Oracle WebLogic Server administrative console
 
 
- A public load balancer to access the Oracle WebLogic Server cluster
 
 
 
The following diagram illustrates this reference architecture:

 
 Description of the illustration wls-oke-marketplace.png 

 wls-oke-marketplace-oracle.zip 

 
 This architecture has the following components: 

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that contains one or more data centers, hosting availability domains. Regions are independent of other regions, and vast distances can separate them (across countries or even continents).
 

 
 
- Availability domain 
Availability domains are standalone, independent data centers within a region. The physical resources in each availability domain are isolated from the resources in the other availability domains, which provides fault tolerance. Availability domains don’t share infrastructure such as power or cooling, or the internal availability domain network. So, a failure at one availability domain shouldn't affect the other availability domains in the region.

 
 
- Virtual cloud network (VCN) and subnet 
A VCN is a customizable, software-defined network that you set up in an Oracle Cloud
 Infrastructure region. Like traditional data center networks, VCNs give you control over your network environment. A VCN can have multiple non-overlapping CIDR blocks that you can change after you create the VCN. You can segment a VCN into subnets, which can be scoped to a region or to an availability domain. Each subnet consists of a contiguous range of addresses that don't overlap with the other subnets in the VCN. You can change the size of a subnet after creation. A subnet can be public or private. 
 

 
 
- Service gateway 
A service gateway provides access from a VCN to other services, such as Oracle Cloud
 Infrastructure Object Storage . The traffic from the VCN to the Oracle service travels over the Oracle network fabric and does not traverse the internet.
 

 
 
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
 

 
 
- Oracle Cloud Infrastructure
 Registry 
 Oracle Cloud Infrastructure
 Registry is an Oracle-managed service that enables you to simplify your development-to-production workflow. Registry makes it easy for you to store, share, and manage development artifacts, like Docker images.
 

 
 
- WebLogic domain 
A WebLogic domain is a group of related applications and resources and the configuration information necessary to run them. The domain consists of one administration server and one or more managed servers to host your Java application deployments. Managed server instances can be clustered, non-clustered, or a combination of clustered and non-clustered instances. All clusters in the domain use the same administration server.

 
 
- WebLogic cluster components 
Components in a cluster can take advantage of failover and load balancing options. The following types of objects can be clustered in a Oracle WebLogic Server deployment:
 

 
 
- Servlets 
 
- JavaServer Pages (JSPs) 
 
- Enterprise Java Beans (EJBs) 
 
- Remote Method Invocation (RMI) objects 
 
- Java Messaging Service (JMS) destinations 
 
- Java Database Connectivity (JDBC) connections 
 
 
 
- Oracle WebLogic Server Kubernetes Operator 
The Oracle WebLogic Server for
 OKE domain includes the open source Oracle WebLogic Server Kubernetes Operator, which has several key features to assist with managing domains in a Kubernetes environment. A WebLogic Server domain is modeled as a custom resource in the Kubernetes configuration file. The operator uses this configuration and the Kubernetes API to automate WebLogic Server operations, such as provisioning, starting or stopping servers, patching, scaling, and security.
 

 
 
- Jenkins 
 Oracle WebLogic Server for
 OKE uses Jenkins to automate the creation of custom images for your Oracle WebLogic Server domain and to deploy these images to the Kubernetes cluster. Jenkins is an open source automation engine that facilitates a development workflow based on continuous integration and continuous delivery (CI/CD). You create projects that perform a series of steps such as checking out files from a source control system, compiling code, or running a script. Pipelines are a type of project that organizes complex activities into stages, such as building, testing, and deploying applications.
 

 
 
 

 

 
 
Recommendations 

 

 
Use the following recommendations as a starting point. Your requirements might differ.

 
 
- VCN 
When you create a VCN, determine the number of CIDR blocks required and the size of each block based on the number of resources that you plan to attach to subnets in the VCN. Use CIDR blocks that are within the standard private IP address space.

 
Select CIDR blocks that don't overlap with any other network (in Oracle Cloud
 Infrastructure , your on-premises data center, or another cloud provider) to which you intend to set up private connections.
 

 
After you create a VCN, you can change, add, and remove its CIDR blocks.

 
In this architecture, Oracle WebLogic Server for
 OKE creates a virtual cloud network (VCN) and subnets in Oracle Cloud
 Infrastructure to support Oracle WebLogic Server , Kubernetes, and the load balancers. But if you want, you can also use an existing VCN and existing subnets. Oracle WebLogic Server for
 OKE creates private subnets for the administration host compute instance, for the Kubernetes components, and for file storage. It creates public subnets for the public load balancer and the bastion compute instances. We recommend that you follow the same architecture when using existing subnets.
 

 
 
- Load balancer 
When you create a domain, Orac
