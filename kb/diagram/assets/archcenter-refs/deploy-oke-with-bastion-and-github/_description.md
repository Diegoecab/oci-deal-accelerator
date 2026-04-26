# Deploy applications on a private OKE cluster using OCI Bastion and GitHub Actions

- Source: https://docs.oracle.com/en/solutions/deploy-oke-with-bastion-and-github/index.html
- Date: 2024-10
- Type: reference-architecture
- Services: oke, bastion
- Tags: devops, application

## Summary (catalog)

GitHub Actions deployment to private OKE clusters via Bastion. SSH tunnel through Bastion for kubectl access from CI/CD. Eliminates need for public OKE API endpoint.

## Architecture (fetched from source)

Architecture

 

 
This reference architecture showcases the integration of an OCI Bastion and GitHub Actions to facilitate deployments to a private OKE cluster.
 

 
The private OKE cluster is inaccessible from external networks. To access
 the K8s API private endpoint, an SSH port-forwarding OCI Bastion session is established. This setup enables the execution of kubectl 
 commands to perform various deployment operations within the cluster.
 

 
When code is pushed to the repository, the GitHub Actions workflow is automatically triggered. During the workflow run, the OCI Bastion session is created and utilized to connect to the private K8s API endpoint for
 executing deployment actions.
 

 
Upon completion of the workflow, the OCI Bastion session is deleted. This approach ensures a highly secure and efficient deployment
 process. Additionally, this workflow serves as a framework for executing continuous
 integration tasks and can be further tailored to align with your specific development
 processes and requirements.
 

 
The following diagram illustrates this reference architecture.

 
 Description of the illustration oke-bastion-deployment-diagram.png 

 oke-bastion-deployment-diagram-oracle.zip 

 
 Before you begin 

 
 
- Provision an OKE cluster with the Kubernetes API endpoint and worker
 nodes configured in a private subnet.
 

 
Note:
The private Kubernetes API
 endpoint will be utilized for establishing the OCI Bastion port-forwarding session.
 

 
 
- Set the created OCI Bastion service to have the OKE VCN as the target VCN and the OKE node subnet as the
 target subnet.
 
 
- Set the required IAM service policy.
 

 
Note:
See Explore More for links to
 the Policy Configuration for Cluster Creation and Deployment for setting
 up necessary IAM policies.
 

 
 
 
The architecture has the following components:

 
 
- Tenancy 
A tenancy is a
 secure and isolated partition that Oracle sets up
 within Oracle Cloud when you sign up for Oracle Cloud
 Infrastructure . You can create, organize, and administer your
 resources in Oracle Cloud within your tenancy. A
 tenancy is synonymous with a company or
 organization. Usually, a company will have a
 single tenancy and reflect its organizational
 structure within that tenancy. A single tenancy is
 usually associated with a single subscription, and
 a single subscription usually only has one
 tenancy.
 

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that
 contains one or more data centers, called
 availability domains. Regions are independent of
 other regions, and vast distances can separate
 them (across countries or even
 continents).
 

 
 
- Compartment 
Compartments are cross-regional logical partitions within an Oracle Cloud
 Infrastructure tenancy. Use compartments to organize, control access, and set usage quotas for your Oracle Cloud resources. In a given compartment, you define policies that control access and set privileges for resources.
 

 
 
- Availability domains 
Availability domains are standalone, independent data centers within a region. The physical resources in each availability domain are isolated from the resources in the other availability domains, which provides fault tolerance. Availability domains don’t share infrastructure such as power or cooling, or the internal availability domain network. So, a failure at one availability domain shouldn't affect the other availability domains in the region.

 
 
- Fault domains 
A fault
 domain is a grouping of hardware and
 infrastructure within an availability domain. Each
 availability domain has three fault domains with
 independent power and hardware. When you
 distribute resources across multiple fault
 domains, your applications can tolerate physical
 server failure, system maintenance, and power
 failures inside a fault domain.

 
 
- Virtual cloud network (VCN) and subnets 
A VCN is a customizable,
 software-defined network that you set up in an Oracle Cloud
 Infrastructure region. Like traditional data center networks,
 VCNs give you control over your network
 environment. A VCN can have multiple
 non-overlapping CIDR blocks that you can change
 after you create the VCN. You can segment a VCN
 into subnets, which can be scoped to a region or
 to an availability domain. Each subnet consists of
 a contiguous range of addresses that don't overlap
 with the other subnets in the VCN. You can change
 the size of a subnet after creation. A subnet can
 be public or private. 
 

 
 
- Load balancer 
The Oracle Cloud
 Infrastructure Load Balancing service provides automated traffic distribution
 from a single entry point to multiple servers in
 the back end.
 

 
 
- Security list 
For each
 subnet, you can create security rules that specify
 the source, destination, and type of traffic that
 must be allowed in and out of the subnet.

 
 
- Network
 address translation (NAT) gateway 
A
 NAT gateway enables private resources in a VCN to
 access hosts on the internet, without exposing
 those resources to incoming internet
 connections.

 
 
- Service
 gateway 
The service gateway
 provides access from a VCN to other services, such
 as Oracle Cloud
 Infrastructure Object Storage . The traffic from the VCN to the Oracle service
 travels over the Oracle network fabric and does
 not traverse the internet.
 

 
 
- Cloud Guard 
You can use Oracle Cloud Guard to monitor and maintain the security of your resources in Oracle Cloud
 Infrastructure . Cloud Guard uses detector recipes that you can define to examine your resources for security weaknesses and to monitor operators and users for certain risky activities. When any misconfiguration or insecure activity is detected, Cloud Guard recommends corrective actions and assists with taking those actions, based on responder recipes that you can define.
 

 
 
- Security zone 
Security
 zones ensure Oracle's security best practices from
 the start by enforcing policies such as encrypting
 data and preventing public access to networks for
 an entire compartment. A security zone is
 associated with a compartment of the same name and
 includes security zone policies or a "recipe" that
 applies to the compartment and its
 sub-compartments. You can't add or move a standard
 compartment to a security zone
 compartment.

 
 
- Kubernetes Engine 
 Oracle Cloud Infrastructure Kubernetes Engine ( OCI Kubernetes Engine or OKE ) is a fully managed, scalable, and highly available service that you can use to deploy your containerized applications to the cloud. You specify the compute resources that your applications require, and Kubernetes Engine provisions them on Oracle Cloud
 Infrastructure in an existing tenancy. OKE uses Kubernetes to automate the deployment, scaling, and management of containerized applications across clusters of hosts.
 

 
 
- Bastion service 
 Oracle Cloud Infrastructure
 Bastion provides restricted and time-limited secure access to resources that don't have public endpoints and that require strict resource access controls, such as bare metal and virtual machines, Oracle MySQL Database Service , Autonomous Transaction
 Processing (ATP), Oracle Cloud Infrastructure Kubernetes Engine ( OKE ), and any other resource that allows Secure Shell Protocol (SSH) access. With OCI Bastion service, you can enable access to private hosts without deploying and maintaining a jump host. In addition, you gain improved security posture with identity-based permissions and a centralized, audited, and time-bound SSH session. OCI Bastion removes the need for a public IP for bastion access, eliminating the hassle and potential attack surface when providing remote access.
 

 
 
 

 

 
 
Recommendations

 

 
 Use the following recommendations as a starting point.
 Your requirements might differ from the architecture described here. 
 

 
 
- VCN 
When you create a VCN, determine the number of CIDR blocks required and the size of each block based on the number of reso
