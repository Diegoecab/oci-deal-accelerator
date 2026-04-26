# Deploy a disaster recovery solution for OCI API Gateway

- Source: https://docs.oracle.com/en/solutions/deploy-data-rcvy-oci-api-gateway/index.html
- Date: 2025-02
- Type: reference-architecture
- Services: api-gateway, dns, load-balancer
- Tags: ha-dr, networking

## Summary (catalog)

Active-passive DR for API Gateway using DNS failover. Traffic Manager for health-check-based routing. API deployment replication across regions using Terraform or Resource Manager stacks.

## Architecture (fetched from source)

Architecture

 

 
This reference architecture for OCI API Gateway consists of two OCI API Gateway s in two different cloud regions, which are accessed by using a single custom endpoint
 (URL). To implement single custom endpoint, you can use an OCI Domain Name System (DNS) zone
 to resolve the custom endpoint name.
 

 
You can use these custom URLs as the entry point to the OCI API Gateway s; for example, api.mycompany.com . For more information about
 configuring custom endpoints, see "Managing DNS Service Zones", which you can access
 from "Explore More", below. 
 

 
The two OCI API Gateway s in the architecture are designated as primary and secondary, and both gateways run
 concurrently; however, only one of the gateways receives traffic. Initially, the primary
 gateway receives the traffic flow. If the primary region becomes unavailable, the DNS
 record can be updated to route the traffic to the secondary region. 
 

 
The following diagram illustrates this reference architecture for a public
 gateway (landing zone pattern for OCI API Gateway ):
 

 

 
 
 Description of the illustration apigw-oci-customer-managed-dr-topology.png 

 
 

 

 apigw-oci-customer-managed-dr-topology-oracle.zip 
 
 

 
These architectures have the following components:
 
 
- Tenancy 
A tenancy is a secure and isolated partition that Oracle sets up within Oracle Cloud when you sign up for Oracle Cloud
 Infrastructure . You can create, organize, and administer your resources in Oracle Cloud within your tenancy. A tenancy is synonymous with a company or organization. Usually, a company will have a single tenancy and reflect its organizational structure within that tenancy. A single tenancy is usually associated with a single subscription, and a single subscription usually only has one tenancy.
 

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that contains one or more data centers, called availability domains. Regions are independent of other regions, and vast distances can separate them (across countries or even continents).
 

 
 
- Compartment 
Compartments are cross-regional logical partitions within an Oracle Cloud
 Infrastructure tenancy. Use compartments to organize, control access, and set usage quotas for your Oracle Cloud resources. In a given compartment, you define policies that control access and set privileges for resources.
 

 
 
- Availability domain 
Availability domains are standalone, independent data centers within a region. The physical resources in each availability domain are isolated from the resources in the other availability domains, which provides fault tolerance. Availability domains don’t share infrastructure such as power or cooling, or the internal availability domain network. So, a failure at one availability domain shouldn't affect the other availability domains in the region.

 
 
- Virtual cloud network (VCN) and subnet 
A VCN is a customizable, software-defined network that you set up in an Oracle Cloud
 Infrastructure region. Like traditional data center networks, VCNs give you control over your network environment. A VCN can have multiple non-overlapping CIDR blocks that you can change after you create the VCN. You can segment a VCN into subnets, which can be scoped to a region or to an availability domain. Each subnet consists of a contiguous range of addresses that don't overlap with the other subnets in the VCN. You can change the size of a subnet after creation. A subnet can be public or private. 
 

 
 
- Route table 
Virtual route tables contain rules to route traffic from subnets to destinations outside a VCN, typically through gateways.

 
 
- Security list 
For each subnet, you can create security rules that specify the source, destination, and type of traffic that must be allowed in and out of the subnet.

 
 
- Oracle Cloud Infrastructure DNS service 
Public DNS zones hold the authoritative DNS records that reside on OCI's
 name servers. You can create public zones with publicly available domain
 names reachable on the internet. For more information, see "Overview of
 DNS", which you can access from "Explore More", below..

 
 
- Internet gateway 
The internet gateway allows traffic between the public subnets in a VCN and the public internet.

 
 
- Oracle Cloud Infrastructure Web
 Application Firewall (WAF) 
WAFs protect applications from malicious and
 unwanted internet traffic with a cloud-based, PCI-compliant, global web
 application firewall service. By combining threat intelligence with
 consistent rule enforcement on OCI Flexible Network Load Balancer , Oracle Cloud Infrastructure Web
 Application Firewall strengthens defenses and protects internet-facing application servers and
 internal applications. (This component is optional) 
 

 
 
- Flexible Load Balancer 
 
 
A load balancer improves resource utilization by directing
 requests across application services that operate in parallel. As demand
 increases, the number of application services can be increased, and the load
 balancer will use them to balance the processing of requests. (This
 component is optional) 

 
 
- Bastion service 
 Oracle Cloud Infrastructure
 Bastion provides restricted and time-limited secure access to resources that
 don't have public endpoints and that require strict resource access
 controls, such as bare metal and virtual machines, Oracle MySQL Database Service , Autonomous Transaction
 Processing (ATP), Oracle Cloud Infrastructure Kubernetes Engine ( OKE ), and any other resource that allows Secure Shell Protocol (SSH) access.
 With OCI Bastion service, you can enable access to private hosts without deploying and
 maintaining a jump host. In addition, you gain improved security posture
 with identity-based permissions and a centralized, audited, and time-bound
 SSH session. OCI Bastion removes the need for a public IP for bastion access, eliminating the
 hassle and potential attack surface when providing remote access.
 

 
 
- API Gateway 
 Oracle Cloud Infrastructure API Gateway enables you to publish APIs with private endpoints that are accessible
 from within your network, and which you can expose to the public internet if
 required. The endpoints support API validation, request and response
 transformation, CORS, authentication and authorization, and request
 limiting.
 

 
 
- Analytics 
 Oracle
 Analytics Cloud is a scalable and secure public cloud service that empowers business
 analysts with modern, AI-powered, self-service analytics capabilities for
 data preparation, visualization, enterprise reporting, augmented analysis,
 and natural language processing and generation. With Oracle
 Analytics Cloud , you also get flexible service management capabilities, including fast
 setup, easy scaling and patching, and automated lifecycle
 management.
 

 
 
- Identity and Access Management (IAM) 
 Oracle Cloud Infrastructure Identity
 and Access Management (IAM) is the access control plane for Oracle Cloud
 Infrastructure (OCI) and Oracle Cloud Applications. The IAM API and the user interface enable you to manage identity domains and the resources within the identity domain. Each OCI IAM identity domain represents a standalone identity and access management solution or a different user population.
 

 
 
- Identity Domain (IDom) 
IAM uses Identity
 Domains (IDom) to provide identity and access management features such as
 authentication, single sign-on (SSO), and identity lifecycle management for
 Oracle Cloud as well as for Oracle and non-Oracle applications, whether
 SaaS, cloud hosted, or on premises.

 
 
- Policy 
An Oracle Cloud Infrastructure Identity
 and Access Management policy specifies who can access which resources, and how. Access is granted at the group and compartment level, which means you can write a policy that gives a group a specific type of access within a specific compartment, or to the tenancy.
 

 
 
- Audit 
The Oracle Cloud Infrastructure Audit service automatic
