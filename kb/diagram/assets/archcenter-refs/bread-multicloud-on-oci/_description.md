# Run PeopleSoft ERP and Autonomous Database in an HA multicloud deployment

- Source: https://docs.oracle.com/en/solutions/bread-multicloud-on-oci/index.html
- Date: 2025-02
- Type: reference-architecture
- Services: adb-s, compute, load-balancer
- Tags: application, ha-dr, multicloud, peoplesoft, autonomous

## Summary (catalog)

PeopleSoft HA with ADB-S across cloud providers. Application tier on OCI compute with database on ADB-S. Multi-AZ deployment for high availability with automatic failover.

## Architecture (fetched from source)

Architecture

 

 
The Oracle partner has built and deployed a highly-available Oracle
 PeopleSoft application using two availability domains in the Oracle Cloud
 Infrastructure (OCI) region in Ashburn. They use the Phoenix region as a standby region for Oracle Autonomous Database and as a disaster recovery site. 
 

 
Each of the web and application virtual machine (VM) instances are
 configured as a high availability pair by using load balancers and by being placed in
 different availability domains (AD). Each of the load balancers handles certain
 PeopleSoft functions and URLs. 

 
Separate instances of Oracle Autonomous Transaction
 Processing on Dedicated Infrastructure (ATP-D) are created for each of the PeopleSoft functions:
 Financials, Phire, Vertex, and Human Capital Management (HCM). Oracle Data Guard is used
 to replicate the primary databases in Ashburn to standby databases in Phoenix. 
 

 
They have also built and deployed development (DEV), user acceptance test
 (UAT), quality assurance (QA), and test environments in the Phoenix region. Oracle Data
 Guard and RackWare are also used for the DEV, UAT, QA, and test environments. 

 
Windows Servers with file shares are used to store PeopleSoft configuration
 files. Users are able to access PeopleSoft by using the Internet through an internet
 gateway or from the partner private network by using Oracle Cloud
 Infrastructure FastConnect to connect to the load balancers. After connecting to the load balancers, users are
 redirected to an OKTA Access Gateway (OAG). The OAG is used for access authentication
 and single sign-on (SSO) before allowing users to access PeopleSoft.
 

 
The move to OCI involved first migrating its PeopleSoft web/application tier
 and Oracle Database to Oracle Exadata Database
 Service . After realizing the benefits of ATP, the partner successfully migrated its 7 TB
 PeopleSoft database to Oracle Autonomous Database . They recognized ease of maintenance and operation of Autonomous Database as key benefits for their modernization effort. 
 

 
The following diagram illustrates the migration process:

 
 Description of the illustration peoplesoft-migration-process.png 

 peoplesoft-migration-process-oracle.zip 

 
The partner has built a multicloud architecture that integrates with banking
 systems, SaaS applications, Microsoft Azure for Active Directory single sign-on (SSO),
 and MuleSoft (SaaS) for data integration. These integrations connect to Oracle Cloud through their data center private network by using a customer-premises router and
 then connect into the virtual cloud network (VCN) by using ATP.
 

 
For disaster recovery, they use Oracle Data Guard to replicate databases to
 the Phoenix region and uses Oracle Cloud
 Marketplace partner RackWare to take snapshots of VM instances. This allows them to quickly
 recover in another region and continue operations in case of a disaster event.
 

 
To continue their cloud modernization and maturation journey, the partner has
 future plans to move more systems into cloud native services to reduce the amount of
 patching, upgrades, and maintenance required.

 
The following diagram illustrates this reference architecture.

 
 Description of the illustration peoplesoft-prod-oci.png 

 peoplesoft-prod-oci-oracle.zip 

 
The architecture has the following components:

 
 
- Tenancy 
A tenancy is a secure and isolated partition that Oracle sets up within Oracle Cloud when you sign up for Oracle Cloud
 Infrastructure . You can create, organize, and administer your resources in Oracle Cloud within your tenancy. A tenancy is synonymous with a company or organization. Usually, a company will have a single tenancy and reflect its organizational structure within that tenancy. A single tenancy is usually associated with a single subscription, and a single subscription usually only has one tenancy.
 

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that contains one or more data centers, called availability domains. Regions are independent of other regions, and vast distances can separate them (across countries or even continents).
 

 
 
- Audit 
The Oracle Cloud Infrastructure Audit service automatically records calls to all supported Oracle Cloud
 Infrastructure public application programming interface (API) endpoints as log events. All OCI services support logging by Oracle Cloud Infrastructure Audit .
 

 
 
- Policy 
An Oracle Cloud Infrastructure Identity
 and Access Management policy specifies who can access which resources, and how. Access is granted at the group and compartment level, which means you can write a policy that gives a group a specific type of access within a specific compartment, or to the tenancy.
 

 
 
- Logging 
 Oracle Cloud Infrastructure Logging is a highly-scalable and fully-managed service that provides access to the following types of logs from your resources in the cloud:
 
 
- Audit logs: Logs related to events produced by OCI Audit .
 
 
- Service logs: Logs published by individual services such as OCI API Gateway , OCI Events , OCI Functions , OCI Load Balancing , OCI Object Storage , and VCN flow logs. 
 
 
- Custom logs: Logs that contain diagnostic information from custom applications, other cloud providers, or an on-premises environment. 
 
 

 
 
- Object storage 
 OCI Object Storage provides quick access to large amounts of structured and unstructured data of any content type, including database backups, analytic data, and rich content such as images and videos. You can safely and securely store data directly from the internet or from within the cloud platform. You can scale storage without experiencing any degradation in performance or service reliability. 
 

 
Use standard storage for "hot" storage that you need to access quickly, immediately, and frequently. Use archive storage for "cold" storage that you retain for long periods of time and seldom or rarely access.

 
 
- Compartment 
Compartments are cross-regional logical partitions within an Oracle Cloud
 Infrastructure tenancy. Use compartments to organize, control access, and set usage quotas for your Oracle Cloud resources. In a given compartment, you define policies that control access and set privileges for resources.
 

 
 
- Availability domain 
Availability domains are standalone, independent data centers within a region. The physical resources in each availability domain are isolated from the resources in the other availability domains, which provides fault tolerance. Availability domains don’t share infrastructure such as power or cooling, or the internal availability domain network. So, a failure at one availability domain shouldn't affect the other availability domains in the region.

 
 
- Virtual cloud network (VCN) and subnets 
A VCN is a customizable, software-defined network that you set up in an Oracle Cloud
 Infrastructure region. Like traditional data center networks, VCNs give you control over your network environment. A VCN can have multiple non-overlapping CIDR blocks that you can change after you create the VCN. You can segment a VCN into subnets, which can be scoped to a region or to an availability domain. Each subnet consists of a contiguous range of addresses that don't overlap with the other subnets in the VCN. You can change the size of a subnet after creation. A subnet can be public or private. 
 

 
 
- Security list 
For each subnet, you can create security rules that specify the source, destination, and type of traffic that must be allowed in and out of the subnet.

 
 
- Route table 
Virtual route tables contain rules to route traffic from subnets to destinations outside a VCN, typically through gateways.

 
 
- Internet gateway 
An internet gateway allows traffic between the public subnets in a VCN and the public internet.

 
 
- Dynamic routing gateway (DRG) 
The DRG is a virtual router that provides a path for private network traffic between VCNs in the sa
