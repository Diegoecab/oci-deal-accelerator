# Deploy a hybrid DR solution on OCI for Oracle WebLogic or Fusion Middleware domain environments

- Source: https://docs.oracle.com/en/solutions/deploy-hybrid-dr-wls-fmw/index.html
- Date: 2025-03
- Type: reference-architecture
- Services: wls, compute, fsdr, load-balancer, base-db, adg
- Tags: ha-dr, application

## Summary (catalog)

Hybrid DR for WebLogic/FMW with on-premises primary and OCI standby. Greatest automation when primary follows Oracle EDG best practices. Continuous replication via Data Guard, WLS HYDR Framework for mid-tier.

## Architecture (fetched from source)

Architecture

 

 
This architecture shows a typical hybrid disaster recovery topology for an Oracle WebLogic
 Server or Oracle Fusion Middleware system.
 

 
In this architecture, the framework creates and configures a secondary environment in OCI, including the following components:
 
 
- Internet, Service, and NAT Gateways 
 
- Route table 
 
- Web-tier, which can be a public or private subnet, with security list, load balancer, and web host compute instances 
 
- Mid-tier private subnet with security list with app host compute instances and block volumes 
 
- FSS-tier private subnet with security list and OCI File Storage service
 
 
- DB tier private subnet with security list 
 
 

 
The following diagram illustrates this reference architecture.

 
 Description of the illustration maa-wls-hybrid-dr-tool-highlights.png 

 maa-wls-hybrid-dr-tool-highlights-oracle.zip 

 
The framework enables you to perform a complete DR setup where you create a continuously mirrored system for an existing primary Oracle WebLogic
 Server or Oracle Fusion Middleware domain. Consider using the framework for the following scenarios:
 

 
 
- COMPLETE DR SETUP 
This is the main use case addressed by the framework. In this scenario, use the framework to create a continuously mirrored system for an existing primary Oracle WebLogic
 Server or Oracle Fusion Middleware domain. Connectivity between primary and OCI is required. Periodic replication is setup to maintain both systems in sync. In this scenario, the database uses Oracle Data Guard for continuous synchronization of the DB tier.
 

 
 
- BACKUP AND RESTORE TO OCI 
In this scenario, an Oracle WebLogic
 Server or Oracle Fusion Middleware domain is restored (or migrated) to OCI from a backup. In this use case, continuous connectivity between the primary datacenter and OCI is not needed. You upload the binary and configuration contents from primary to a bastion node in OCI. The OCI resources are created based on this information and the required input properties provided in the framework's configuration files. The RTO and RPO of this solution is considerably worse than in the "COMPLETE DR SETUP" case. When using this "backup and restore" approach, Oracle recommends that the secondary system is created and tested on a regular basis. However, and to reduce costs, it is also possible to "leave" the backup in the bastion and use it only when a restore is required (hence not incurring in the additional costs of having resources created and running upfront). In this scenario, the database uses Oracle Data Pump for exporting and importing the data used by Oracle WebLogic
 Server or Oracle Fusion Middleware in the DB tier. 
 

 
 
- INFRASTRUCTURE CREATION 
You can use the framework to create the infrastructure required by an Oracle WebLogic environment in OCI (Load Balancer, Compute instances, shared storage, network, security rules, and so on) without a primary system as a reference. 

 
There is no discovery of resources from a primary system. You provide all the required input properties to create the OCI resources that a highly available Oracle WebLogic domain typically uses. There is no replication phase, since there is no primary system. You run the framework to create infrastructure resources in OCI, then install Oracle products and configure the Oracle WebLogic or Fusion Middleware domain manually. 

 
The WLS_HYDR framework only creates the OCI artifacts that you need for an Oracle WebLogic EDG-like system in OCI: compute instances for WebLogic and for OHS, storage artifacts, OCI Load Balancer, network infrastructure and security rules for the subnets in the VCN.
 

 
 
 
The architecture has the following components:

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that contains one or more data centers, hosting availability domains. Regions are independent of other regions, and vast distances can separate them (across countries or even continents).
 

 
 
- Virtual cloud network (VCN) and subnets 
A VCN is a customizable, software-defined network that you set up in an Oracle Cloud
 Infrastructure region. Like traditional data center networks, VCNs give you control over your network environment. A VCN can have multiple non-overlapping CIDR blocks that you can change after you create the VCN. You can segment a VCN into subnets, which can be scoped to a region or to an availability domain. Each subnet consists of a contiguous range of addresses that don't overlap with the other subnets in the VCN. You can change the size of a subnet after creation. A subnet can be public or private. 
 

 
 
- Site-to-Site VPN 
OCI Site-to-Site VPN provides IPSec VPN connectivity between your on-premises network and VCNs in Oracle Cloud
 Infrastructure . The IPSec protocol suite encrypts IP traffic before the packets are transferred from the source to the destination and decrypts the traffic when it arrives.
 

 
 
- Dynamic routing gateway (DRG) 
The DRG is a virtual router that provides a path for private network traffic between VCNs in the same region, between a VCN and a network outside the region, such as a VCN in another Oracle Cloud
 Infrastructure region, an on-premises network, or a network in another cloud provider.
 

 
 
- FastConnect 
 Oracle Cloud
 Infrastructure FastConnect creates a dedicated, private connection between your data center and Oracle Cloud
 Infrastructure . FastConnect provides higher-bandwidth options and a more reliable networking experience when compared with internet-based connections.
 

 
 
- Internet gateway 
An internet gateway allows traffic between the public subnets in a VCN and the public internet.

 
 
- Network address translation (NAT) gateway 
A NAT gateway enables private resources in a VCN to access hosts on the internet, without exposing those resources to incoming internet connections.

 
 
- Security list 
For each subnet, you can create security rules that specify the source, destination, and type of traffic that is allowed in and out of the subnet.

 
 
- Network Firewall 
 OCI Network Firewall is a cloud native, machine learning-powered firewall with advanced intrusion detection and prevention capabilities, supported by Palo Alto Networks next-generation firewall (NGFW) technology that scales automatically.
 

 
 
- On-premises network 
This is a local network used by your organization.

 
 
- Data Catalog 
 Oracle Cloud Infrastructure Data Catalog is a fully-managed, self-service data discovery and governance solution for your enterprise data. It provides data engineers, data scientists, data stewards, and chief data officers a single collaborative environment to manage the organization's technical, business, and operational metadata.
 

 
 
- Application server 
Application servers use a secondary peer that, like the database, will take over processing in the event of a disaster. Application servers use configuration and metadata that is stored both in the database and the file system. Application server clustering provides protection in the scope of a single region but ongoing modifications and new deployments need to be replicated to the secondary location on an ongoing basis for a consistent disaster recovery. 

 
 
- Bastion service 
 Oracle Cloud Infrastructure
 Bastion provides restricted and time-limited secure access to resources that don't have public endpoints and that require strict resource access controls, such as bare metal and virtual machines, Oracle MySQL Database Service , Autonomous Transaction
 Processing (ATP), Oracle Cloud Infrastructure Kubernetes Engine ( OKE ), and any other resource that allows Secure Shell Protocol (SSH) access. With OCI Bastion service, you can enable access to private hosts without deploying and maintaining a jump host. In addition, you gain improved security posture with identity-based permissions and a centralized, audited, and time-bound SSH session. OCI Bastion removes the need for a public IP
