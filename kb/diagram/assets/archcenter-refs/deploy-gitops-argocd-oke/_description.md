# Deploy GitOps with Argo CD and Oracle Container Engine for Kubernetes

- Source: https://docs.oracle.com/en/solutions/deploy-gitops-argocd-oke/index.html
- Date: 2024-10
- Type: reference-architecture
- Services: oke
- Tags: devops, application

## Summary (catalog)

GitOps with Argo CD on OKE. Declarative application deployment from Git repositories. Automated sync, drift detection, and rollback capabilities for Kubernetes workloads.

## Architecture (fetched from source)

Architecture

 

 

 This architecture shows an OCI Kubernetes Engine cluster with the Argo CD tool deployed in its own namespace. 
 
 

 
You can access the Argo CD application through its web UI or the Argo CD
 command-line interface. Connectivity to the Argo CD tool is provided by a load balancer
 service deployed in the OCI Kubernetes Engine cluster. Once the Argo CD is deployed, you configure it to sync with Git repositories
 hosted internally or externally to Oracle Cloud Infrastructure, so long as the OCI Kubernetes Engine cluster has IP connectivity on the required ports and the credentials for the Git
 repositories. Once Argo CD has synced with the repositories, any updates to the
 application configuration made in the repository will be applied to the OCI Kubernetes Engine cluster. If changes are made to the application outside of the Git repository, Argo
 CD will consider the application out of sync and revert the changes so it is in line
 with the desired state of the Git repository. 
 

 
The following diagram illustrates this reference architecture.

 
 
 Description of the illustration argocd.png 

 

 argocd-oracle.zip 
 
 

 
This architecture has the following components:
 
 
- Tenancy 
 
 
Oracle Autonomous Transaction Processing is a self-driving, self-securing,
 self-repairing database service that is optimized for transaction processing
 workloads. You do not need to configure or manage any hardware, or install
 any software. Oracle Cloud Infrastructure handles creating the database, as
 well as backing up, patching, upgrading, and tuning the database. 

 
 
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
 that specify who can access the resources and what actions they can
 perform.

 
 
 
- Availability domains 
 
 
Availability domains are standalone, independent data centers within a
 region. The physical resources in each availability domain are isolated from
 the resources in the other availability domains, which provides fault
 tolerance. Availability domains don’t share infrastructure such as power or
 cooling, or the internal availability domain network. So, a failure at one
 availability domain is unlikely to affect the other availability domains in
 the region. 

 
 
- Fault domains 
 
 
A fault domain is a grouping of hardware and infrastructure within an
 availability domain. Each availability domain has three fault domains with
 independent power and hardware. When you distribute resources across
 multiple fault domains, your applications can tolerate physical server
 failure, system maintenance, and power failures inside a fault domain.

 
 
 
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
The Oracle Cloud Infrastructure Load Balancing service
 provides automated traffic distribution from a single entry point to
 multiple servers in the back end. The load balancer provides access to
 different applications. 

 
 
- Code Repository 
 
 
In the DevOps service, you can create your own private code repositories or
 connect to external code repositories such as GitHub, GitLab, and Bitbucket
 Cloud.

 
 
 
- Security list 
 
 
For each subnet, you can create security rules that specify the source,
 destination, and type of traffic that must be allowed in and out of the
 subnet.

 
 
 
- NAT gateway 
 
 
The NAT gateway enables private resources in a VCN to access hosts on the
 internet, without exposing those resources to incoming internet connections.
 

 
 
- Service gateway 
 
 
The service gateway provides access from a VCN to other services, such as
 Oracle Cloud Infrastructure Object Storage. The traffic from the VCN to the
 Oracle service travels over the Oracle network fabric and never traverses
 the internet. 

 
 
- Cloud Guard 
 
 
You can use Oracle Cloud Guard to monitor and maintain the security of your
 resources in Oracle Cloud Infrastructure. Cloud Guard uses detector recipes
 that you can define to examine your resources for security weaknesses and to
 monitor operators and users for risky activities. When any misconfiguration
 or insecure activity is detected, Cloud Guard recommends corrective actions
 and assists with taking those actions, based on responder recipes that you
 can define. 

 
 
- Security zone 
 
 
Security zones ensure Oracle's security best practices from the start by
 enforcing policies such as encrypting data and preventing public access to
 networks for an entire compartment. A security zone is associated with a
 compartment of the same name and includes security zone policies or a
 "recipe" that applies to the compartment and its sub-compartments. You can't
 add or move a standard compartment to a security zone compartment. 

 
 
- Object storage 
 
 
Object storage provides quick access to large amounts of structured and
 unstructured data of any content type, including database backups, analytic
 data, and rich content such as images and videos. You can safely and
 securely store and then retrieve data directly from the internet or from
 within the cloud platform. You can seamlessly scale storage without
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
 
 
An LPG enables you to peer one VCN with another VCN in the same region.
 Peering means the VCNs communicate using private IP addresses, without the
 traffic traversing the internet or routing through your on-premises network.
 

 
 
- Autonomous database 
 
 
Oracle Cloud Infrastructure autonomous databases are fully managed,
 preconfigured database environments that you can use for transaction
 processing and data warehousing workloads. You do not need to configure or
 manage any hardware, or install any software. Oracle Cloud Infrastructure
 handles creating the database, as well as backing up, patching, upgrading,
 and tuning the database.

 
 
 
- Autonomous Data Warehouse 
 
 
Oracle Autonomous Data Warehouse is a self-driving, self-securing,
 self-repairing database service that is optimized for data warehousing
 workloads. You do not need to configure or manage any hardware, or install
 any software. Oracle Cloud Infrastructure handles creating the database, as
 well as backing up, patching, upgrading, and tuning the database. 

 
 
- Autonomous Transaction Processing 
 
 
Oracle
