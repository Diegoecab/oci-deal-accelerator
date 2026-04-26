# Move to Oracle Database@Google Cloud with Oracle Zero Downtime Migration

- Source: https://docs.oracle.com/en/solutions/oracle-db-at-google-cloud-migration/index.html
- Date: 2024-11
- Type: reference-architecture
- Services: exacs, google-cloud, goldengate
- Tags: database, multicloud, migration

## Summary (catalog)

Zero Downtime Migration to Database@Google Cloud. Physical or logical migration methods with GoldenGate for minimal-downtime cutover. Supports on-premises Oracle DB to ExaCS on Google Cloud.

## Architecture (fetched from source)

Architecture

 

 

 Peform your Oracle Database migrations from on-premises to Oracle Exadata Database
 Service on Oracle Database@Google Cloud by using the physical online migration workflow based on Oracle Data Guard and direct data transfer, providing simplicity, automation, and business continuity
 during your database migrations to Oracle Database@Google Cloud . 
 
 

 
The Oracle Zero Downtime Migration service host is installed on a separate,
 on-premises virtual machine (VM) next to the source database. The target Oracle Exadata Database
 Service is provisioned in Google Cloud’s data center within Google’s Virtual Private Cloud
 (VPC). The on-premises data center is connected to Google Cloud by using Google Cloud
 Interconnect or site-to-site VPN. The Oracle Zero Downtime Migration workflow uses
 direct data transfer and creates the target database by using the Restore From a Service
 method, eliminating the need to back up the source database to an intermediate storage
 location. Oracle Zero Downtime Migration uses Oracle Data Guard to replicate the data from the on-premises database to the target database. Oracle
 Zero Downtime Migration sets up Oracle Data Guard , maintains it, and cleans up the configuration after the migration completes, so you
 don't have to. After the migration is complete, the target database can use the
 Automatic Backup feature to back up the database into Oracle Database Autonomous
 Recovery Service . 
 

 
The following diagram illustrates the architecture:

 
 Description of the illustration oracle_database_at_google_cloud_w_zdm.png 

 oracle_database_at_google_cloud_w_zdm-oracle.zip 

 
The architecture has the following on-premises and Oracle Cloud
 Infrastructure components:
 

 
 
- On-premises network 
This network is the local network used by your organization. It is one of the spokes of the topology.

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that contains one or more data centers, called availability domains. Regions are independent of other regions, and vast distances can separate them (across countries or even continents).
 

 
 
- Virtual cloud network (VCN) and subnets 
A VCN is a customizable, software-defined network that you set up in an Oracle Cloud
 Infrastructure region. Like traditional data center networks, VCNs give you control over your network environment. A VCN can have multiple non-overlapping CIDR blocks that you can change after you create the VCN. You can segment a VCN into subnets, which can be scoped to a region or to an availability domain. Each subnet consists of a contiguous range of addresses that don't overlap with the other subnets in the VCN. You can change the size of a subnet after creation. A subnet can be public or private. 
 

 
 
- Route table 
Virtual route tables contain rules to route traffic from subnets to destinations outside a VCN, typically through gateways.

 
 
- Security list 
For each subnet, you can create security rules that specify the source, destination, and type of traffic that must be allowed in and out of the subnet.

 
 
- Site-to-Site VPN 
Site-to-Site VPN provides IPSec VPN connectivity between your on-premises network and VCNs in Oracle Cloud
 Infrastructure . The IPSec protocol suite encrypts IP traffic before the packets are transferred from the source to the destination and decrypts the traffic when it arrives.
 

 
 
- Oracle Exadata Database
 Service 
 Oracle Exadata Database
 Service enables you to leverage the power of Exadata in the cloud. Oracle Exadata Database
 Service delivers proven Oracle Database capabilities on purpose-built, optimized Oracle Exadata infrastructure in the public cloud. Built-in cloud automation, elastic resource scaling, security, and fast performance for all Oracle Database workloads helps you simplify management and reduce costs.
 

 
 Oracle Exadata Database Service on Dedicated
 Infrastructure provides Oracle Exadata Database Machine as a service in an Oracle Cloud
 Infrastructure (OCI) data center. The Oracle Exadata Database Service on Dedicated
 Infrastructure instance is a virtual machine (VM) cluster that resides on Exadata racks in an OCI region.
 

 
 
- Oracle Database Autonomous
 Recovery Service 
 Oracle Database Autonomous
 Recovery Service is an Oracle Cloud service that protects Oracle databases. With backup automation and enhanced data protection capabilities for OCI databases, you can offload all backup processing and storage requirements to Oracle Database Autonomous
 Recovery Service , thereby eliminating backup infrastructure costs and manual administration overhead.
 

 
 
- Oracle Database@Google Cloud 
 Oracle Database@Google Cloud is an Oracle Cloud database service that runs Oracle Database workloads in your Google Cloud environment. All hardware for Oracle Database@Google Cloud is colocated in Google Cloud's data centers and uses Google Cloud networking. The service benefits from the simplicity, security, and low latency of a single operating environment within Google Cloud. You can manage the service on the Google Cloud console or by using Google Cloud automation tools. Google Cloud IAM and Admin provide federated identity and access management for Oracle Exadata Database
 Service .
 

 
 
- Oracle Cloud Infrastructure Vault 
 Oracle Cloud Infrastructure Vault enables you to centrally manage the encryption keys that protect your data and the secret credentials that you use to secure access to your resources in the cloud. You can use the Vault service to create and manage vaults, keys, and secrets.
 

 
 
- Zero Downtime Migration service host 
The Oracle Zero Downtime Migration
 service host should be a dedicated system but can be shared for other
 purposes.

 
Oracle Zero Downtime Migration software requires a standalone
 Oracle Linux host running on either Oracle Linux 7 or 8 or Red Hat Enterprise
 Linux 8 or 9.

 
The Oracle Zero Downtime Migration service host must be able
 to connect to the source and the target database servers; if connectivity is
 guaranteed, the service host can be located anywhere.

 
 
- Data Guard 
 Oracle Data Guard and Oracle Active Data Guard provide a comprehensive set of services that create, maintain, manage, and monitor one or more standby databases and that enable production Oracle databases to remain available without interruption. Oracle Data Guard maintains these standby databases as copies of the production database by using in-memory replication. If the production database becomes unavailable due to a planned or an unplanned outage, Oracle Data Guard can switch any standby database to the production role, minimizing the downtime associated with the outage. Oracle Active Data Guard provides the additional ability to offload read-mostly workloads to standby databases and also provides advanced data protection features.
 

 
 
 
The architecture has the following Google components:

 
 
- Google Cloud Region 
A Google Cloud region is a
 geographical area that contains data centers and infrastructure for hosting
 resources. It is made up of zones that are isolated from each other within the
 region.

 
 
- Google Cloud Project 
A Google Cloud Project is
 required to use Google Workspace APIs and to build Google Workspace add-ons or
 apps. A project forms the basis for creating, enabling, and using all Google
 Cloud services, including managing APIs, enabling billing, adding and removing
 collaborators, and managing permissions.

 
 
- Google Virtual Private Cloud 
Google Cloud Virtual
 Private Cloud (VPC) provides networking functionality to Compute Engine virtual
 machine (VM) instances, Google Kubernetes Engine (GKE) containers, database
 services, and serverless workloads. VPC provides global, scalable, and flexible
 networking for your cloud-based service.

 
 
- Google Cloud Interconnect 
Cloud Interconnect
 extends your on-premises network to the Google network through a highly
 available, low-latenc
