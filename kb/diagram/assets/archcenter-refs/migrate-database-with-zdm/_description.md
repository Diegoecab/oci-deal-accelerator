# Migrate an on-premises database to the cloud with zero downtime

- Source: https://docs.oracle.com/en/solutions/migrate-database-with-zdm/index.html
- Date: 2025-01
- Type: reference-architecture
- Services: base-db, exacs, goldengate
- Tags: database, migration

## Summary (catalog)

Oracle Zero Downtime Migration for on-premises to OCI. Physical migration for same-version moves, logical for cross-version/platform. GoldenGate for continuous replication during extended cutover windows.

## Architecture (fetched from source)

Architecture

 

 
This architecture shows the components used with Oracle Zero Downtime
 Migration (ZDM). Use this architecture when planning to migrate Oracle Database from
 on-premises to the same database type and version in Oracle Cloud.
 
 Description of the illustration migrate-db-zdm.png 
Zero Downtime Migration uses a controlled switchover method for dynamically
 moving database services to the new database environment (either virtual machine or bare
 metal) in Oracle Cloud
 Infrastructure (OCI). It uses Oracle Recovery Manager (RMAN) to back up the source database to Oracle Cloud
 Infrastructure Object Storage , creating a standby database (with Oracle Data Guard configuration, Oracle Data Guard Maximum Performance protection mode and asynchronous
 redo transport mode) in the target environment from the backup, synchronizes the source
 and target databases, and switches over to the target database as the primary database. 
 

 
 This architecture supports the following components:

 
 
- Databases 
The source database is Oracle Database 19c and the target database is Oracle Base Database Service virtual machine instance in Oracle Cloud
 Infrastructure . You can provision the target from the OCI Console, or you can use Terraform
 code to deploy the topology. The Terraform code includes input variables, which
 you can use to tune the architecture to suit your topology
 requirements.
 

 
 
- ZDM service host 
The ZDM service host is where the
 Zero Downtime Migration software is installed. It is also known as the ZDM node.
 Do not run the ZDM service host on an instance that is running Oracle Grid Infrastructure .
 

 
 
- Bastion host 
The bastion host is a compute instance that serves as a secure, controlled entry point to the topology from outside the cloud. The bastion host is provisioned typically in a demilitarized zone (DMZ). It enables you to protect sensitive resources by placing them in private networks that can't be accessed directly from outside the cloud. The topology has a single, known entry point that you can monitor and audit regularly. So, you can avoid exposing the more sensitive components of the topology without compromising access to them.

 
 
- Block volume 
With Oracle Cloud
 Infrastructure Block Volumes , you can create, attach, connect, and move storage volumes, and change volume performance to meet your storage, performance, and application requirements. After you attach and connect a volume to an instance, you can use the volume like a regular hard drive. You can also disconnect a volume and attach it to another instance without losing data.
 

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that contains one or more data centers, called availability domains. Regions are independent of other regions, and vast distances can separate them (across countries or even continents).
 

 
 
- Object storage 
 Oracle Cloud
 Infrastructure Object Storage provides quick access to large amounts of structured and unstructured data of any content type, including database backups, analytic data, and rich content such as images and videos. You can safely and securely store and then retrieve data directly from the internet or from within the cloud platform. You can scale storage without experiencing any degradation in performance or service reliability. Use standard storage for "hot" storage that you need to access quickly, immediately, and frequently. Use archive storage for "cold" storage that you retain for long periods of time and seldom or rarely access.
 

 
 
- Availability domain 
Availability domains are standalone, independent data centers within a region. The physical resources in each availability domain are isolated from the resources in the other availability domains, which provides fault tolerance. Availability domains don’t share infrastructure such as power or cooling, or the internal availability domain network. So, a failure at one availability domain shouldn't affect the other availability domains in the region.

 
 
- Fault domain 
A fault domain is a grouping of hardware and infrastructure within an availability domain. Each availability domain has three fault domains with independent power and hardware. When you distribute resources across multiple fault domains, your applications can tolerate physical server failure, system maintenance, and power failures inside a fault domain.

 
 
- SQL*Net and SSH connectivity 
The ZDM node requires
 SQL*Net (default database port 1521) and SSH access (default port 22) to the
 source and target databases.

 
Zero Downtime Migration enables
 and allows fallback capability after database migration is complete. Upon
 switchover, the target database running in OCI becomes the primary database, and
 the on-premises becomes the standby. The SQL*Net connectivity between the new
 primary and the new standby after the switchover enables the configuration to
 continue to synchronize data from the new primary in Oracle Cloud
 Infrastructure to the new standby on-premises.
 

 
 
- Internet gateway 
An internet gateway allows traffic between the public subnets in a VCN and the public internet.

 
 
- Service gateway 
The service gateway provides access from a VCN to other services, such as Oracle Cloud
 Infrastructure Object Storage . The traffic from the VCN to the Oracle service travels over the Oracle network fabric and does not traverse the internet.
 

 
 
- Security list 
For each subnet, you can create security rules that specify the source, destination, and type of traffic that must be allowed in and out of the subnet.

 
 
- Route table 
Virtual route tables contain rules to route traffic from subnets to destinations outside a VCN, typically through gateways.

 
 
 
A private connection between on-premises and the cloud is not shown in the diagram.
 Connectivity includes the following components: 
 
 
- Site-to-Site VPN 
Site-to-Site VPN provides IPSec VPN connectivity between your on-premises network and VCNs in Oracle Cloud
 Infrastructure . The IPSec protocol suite encrypts IP traffic before the packets are transferred from the source to the destination and decrypts the traffic when it arrives.
 

 
 
- FastConnect 
 Oracle Cloud
 Infrastructure FastConnect creates a dedicated, private connection between your data center and Oracle Cloud
 Infrastructure . FastConnect provides higher-bandwidth options and a more reliable networking experience when compared with internet-based connections.
 

 
 
- Dynamic routing gateway (DRG) 
The DRG is a virtual router that provides a path for private network traffic between VCNs in the same region, between a VCN and a network outside the region, such as a VCN in another Oracle Cloud
 Infrastructure region, an on-premises network, or a network in another cloud provider.
 

 
 
 
 

 

 

 
 
About Required Services and
 Roles

 

 
This solution requires the following services, products, and
 roles:

 
 
- Oracle Database 11.2.0.4 or higher deployed on-premises 
 
- Oracle Linux 7 
 
- Oracle Zero Downtime Migration software 
 
- Oracle Base Database Service virtual machine. You can provision the system, or you can use Terraform code to deploy
 the target cloud topology. You can use the code available on GitHub to provision the
 required networking resources, a compute instance for the bastion server, and an Oracle Base Database Service .
 
 
 
These are the roles needed for each service.

 

 
 
 
 Service Name: Role 
 Required to... 
 
 
 
 
 Oracle Cloud Infrastructure: Admin 
 Create the target Oracle Base Database Service and set up resources in Oracle Cloud.
 
 
 
 Oracle Cloud
 Infrastructure : Admin
 
 Provision the target Oracle Base Database Service and set up resources in Oracle Cloud.
 
 
 
 Oracle Cloud
 Infrastructure Object Storage : Admin
 
 Create a bucket to store the
 backup data from the on-premises database. 
 
 
 Oracle Database: root 
 Access the database using
 SSH. 
 
 
 Ora
