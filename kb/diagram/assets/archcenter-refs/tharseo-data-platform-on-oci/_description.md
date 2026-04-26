# Tharseo IT: Deploy a multicloud public health data management platform on Oracle Cloud

- Source: https://docs.oracle.com/en/solutions/tharseo-data-platform-on-oci/index.html
- Date: 2025-11
- Type: built-deployed
- Services: oke, adb-s, object-storage
- Tags: healthcare, application, multicloud

## Summary (catalog)

Public health data platform on OKE with ADB-S. Multi-tenant SaaS architecture for health data management across cloud providers.

## Architecture (fetched from source)

Architecture

 

 
 Tharseo IT built and deployed a data bridge for DC
 Health by using Oracle Base Database Service and Oracle GoldenGate hosted on Oracle Cloud
 Infrastructure (OCI) Government Region East (Ashburn). The data bridge integrates
 multiple applications and databases into a centralized staging database, using a two-node
 Oracle Base Database Service , Oracle Real Application Clusters (Oracle
 RAC) , and an Oracle Autonomous Data Warehouse .
 

 
The first integration point is a SaaS application used by the state to track
 vaccinations. This application is hosted on a third-party cloud and connected through a
 site-to-site VPN tunnel. An Oracle GoldenGate hub is deployed in the third-party cloud, which helps pull data from the SaaS
 application database to an Oracle GoldenGate manager instance in the state’s OCI tenancy. The data is then stored in the staging
 database.
 

 
The second integration point allows various US Federal Government agencies to integrate
 with Oracle Autonomous Data Warehouse for reporting the state’s data at the federal level.
 

 
A third integration point integrates other state health applications that
 are hosted in various locations from other clouds to on-premises. These integrations
 also use various data integration tools to push to the staging database through Oracle GoldenGate and into the data warehouse, as needed.
 

 
The following diagram illustrates this reference architecture.
 
 Description of the illustration tharseo-data-platform-oci-arch.png 
 tharseo-data-platform-oci-arch-oracle.zip 

 
Data scientists and DBAs access the staging database and the data warehouse
 from the on-premises network that is connected through site-to-site VPN. Data scientists
 access the Oracle Autonomous Data Warehouse and run analytics through the Tableau Web Layer API.
 

 
For additional layers of security, the state agency uses firewalls deployed
 in various locations to enforce rules and policies, and filter network traffic. In
 addition to firewalls, DC Health has also implemented security lists and network
 security groups on the subnet in the OCI tenancy. The IP tunnels are restricted by IP
 addresses to ensure that only trusted source IP addresses are allowed to enter the
 virtual cloud network (VCN). The state uses Oracle Cloud
 Infrastructure Block Storage and Oracle Cloud Infrastructure File
 Storage for additional storage capabilities
 

 
For disaster recovery (DR), the state backs up the database frequently to Oracle Cloud
 Infrastructure Object Storage and offloads the backups to OCI Government Cloud Region Phoenix and on-premises to
 have additional copies of the backups.
 

 
The architecture has the following components:

 
 
- Tenancy 
A tenancy
 is a secure and isolated partition that Oracle
 sets up within Oracle Cloud when you sign up for
 OCI. You can create, organize, and administer your
 resources on OCI within your tenancy. A tenancy is
 synonymous with a company or organization.
 Usually, a company will have a single tenancy and
 reflect its organizational structure within that
 tenancy. A single tenancy is usually associated
 with a single subscription, and a single
 subscription usually only has one
 tenancy.

 
 
- Region 
An OCI region
 is a localized geographic area that contains one
 or more data centers, hosting availability
 domains. Regions are independent of other regions,
 and vast distances can separate them (across
 countries or even continents).

 
 
- Availability domains 
Availability domains are standalone, independent data centers within a region. The physical resources in each availability domain are isolated from the resources in the other availability domains, which provides fault tolerance. Availability domains don’t share infrastructure such as power or cooling, or the internal availability domain network. So, a failure at one availability domain shouldn't affect the other availability domains in the region.

 
 
- Virtual cloud network (VCN) and subnets 
A virtual cloud
 network (VCN) is a customizable, software-defined
 network that you set up in an OCI region. Like
 traditional data center networks, VCNs give you
 control over your network environment. A VCN can
 have multiple non-overlapping classless
 inter-domain routing (CIDR) blocks that you can
 change after you create the VCN. You can segment a
 VCN into subnets, which can be scoped to a region
 or to an availability domain. Each subnet consists
 of a contiguous range of addresses that don't
 overlap with the other subnets in the VCN. You can
 change the size of a subnet after creation. A
 subnet can be public or private. 

 
 
- Route table 
Virtual
 route tables contain rules to route traffic from
 subnets to destinations outside a VCN, typically
 through gateways.

 
 
- Service
 gateway 
A
 service gateway provides access from a VCN to
 other services, such as Oracle Cloud
 Infrastructure Object Storage . The traffic from the VCN to the Oracle service
 travels over the Oracle network fabric and does
 not traverse the internet.
 

 
 
- OCI Object Storage 
 OCI Object Storage provides access to large amounts of structured and unstructured data of any content type, including database backups, analytic data, and rich content such as images and videos. You can safely and securely store data directly from applications or from within the cloud platform. You can scale storage without experiencing any degradation in performance or service reliability. 
 

 
Use standard storage for "hot" storage that you need to access quickly, immediately, and frequently. Use archive storage for "cold" storage that you retain for long periods of time and seldom or rarely access.

 
 
- Oracle Autonomous Database 
 Oracle Autonomous Database is a fully-managed, preconfigured database environment that you can use for transaction processing and data warehousing workloads. You do not need to configure or manage any hardware, or install any software. OCI handles creating, backing up, patching, upgrading, and tuning the database.
 

 
 
- Security list 
For
 each subnet, you can create security rules that
 specify the source, destination, and type of
 traffic that is allowed in and out of the
 subnet.

 
 
- GoldenGate 
 Oracle GoldenGate Cloud
 Service is a fully-managed service that allows data
 ingestion from sources residing on premises or in
 any cloud. It leverages the GoldenGate Change Data
 Capture (CDC) technology for non-intrusive and
 efficient capture of data and delivery to Oracle Autonomous Data Warehouse in real time and at scale.
 

 
 
- Oracle Base Database Service 
Oracle Base Database
 Service enables you to maintain absolute control over your data while leveraging
 the combined capabilities of Oracle Database and Oracle Cloud Infrastructure.
 Oracle Cloud Infrastructure (OCI) offers single-node DB systems and multi-node
 RAC DB systems on virtual machines. 

 
 
- OCI Site-to-Site VPN 
 OCI Site-to-Site VPN provides IPSec VPN connectivity between your on-premises network and VCNs on OCI. The IPSec protocol suite encrypts IP traffic before the packets are transferred from the source to the destination and decrypts the traffic when it arrives.
 

 
 
- OCI File Storage 
 Oracle Cloud Infrastructure File
 Storage provides a durable, scalable, secure, enterprise-grade network file system. You can connect to OCI File Storage from any bare metal, virtual machine, or container instance in a VCN. You can also access OCI File Storage from outside the VCN by using Oracle Cloud
 Infrastructure FastConnect and IPSec VPN.
 

 
 
- OCI Block Volumes 
With Oracle Cloud
 Infrastructure Block Volumes , you can create, attach, connect, and move
 storage volumes, and change volume performance to
 meet your storage, performance, and application
 requirements. After you attach and connect a
 volume to an instance, you can use the volume like
 a regular hard drive. You can also disconnect a
 volume and attach it to another instance 
