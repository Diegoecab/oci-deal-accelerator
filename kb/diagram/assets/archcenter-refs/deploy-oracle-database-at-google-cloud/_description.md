# Deploy Oracle Database@Google Cloud

- Source: https://docs.oracle.com/en/solutions/deploy-oracle-database-at-google-cloud/index.html
- Date: 2025-10
- Type: reference-architecture
- Services: exacs, adb-d, google-cloud
- Tags: database, multicloud, autonomous

## Summary (catalog)

ExaCS and ADB-D on Database@Google Cloud. RAC for active-active HA, ASM for storage redundancy. Backups to OCI Object Storage via Autonomous Recovery Service.

## Architecture (fetched from source)

Architecture

 

 
This architecture shows a detailed topology for
 Oracle AI Database@Google
 Cloud :
 

 
 Description of the illustration google-detailed-arch.png 

 google-detailed-arch-oracle.zip 

 
The architecture displays application resources within a
 VPC of a Google Cloud project, located in a single zone of a Google Cloud region. An application subnet in the VPC connects to Oracle AI Database@Google
 Cloud using the ODB network in the OCI child site, located in the same Google Cloud region. The client subnet of the Oracle Autonomous AI Database Serverless , the Oracle Exadata Database Service on Dedicated
 Infrastructure client subnet, and the backup subnets of Oracle Database Autonomous
 Recovery Service are defined in the ODB network . The VCN extends into the OCI region to enable connections to other resources within
 OCI. The OCI region hosts the following OCI services: OCI Vault , OCI Object Storage , and control plane.
 

 
This architecture supports the following components:

 
 
- Google Cloud region 
A
 Google Cloud region is a geographical area that contains
 data centers and infrastructure for hosting resources.
 Regions are made up of zones, which are isolated from each
 other within the region.

 
 
- Google Virtual Private Cloud 
Google
 Virtual Private Cloud (VPC) provides networking
 functionality to Compute Engine virtual machine (VM)
 instances, Google Kubernetes Engine (GKE) containers,
 database services, and serverless workloads. VPC provides
 global, scalable, and flexible networking for your
 cloud-based service.

 
 
- Google Cloud zone 
A zone in
 Google Cloud is a deployment area for resources within a
 region. Zones are isolated from each other within a region,
 and are treated as a single failure domain.

 
 
- Google Cloud project 
A Google
 Cloud Project is required to use Google Workspace APIs and
 build Google Workspace add-ons or apps. A Cloud Project
 forms the basis for creating, enabling, and using all Google
 Cloud services, including managing APIs, enabling billing,
 adding and removing collaborators, and managing
 permissions.

 
 
- ODB network 
The ODB network creates a metadata construct around the Google Virtual Private Cloud (VPC), serving as the foundation for all database provisioning. The ODB network enables support for Shared VPC by abstracting and centralizing network configuration - such as subnets, CIDR ranges, and routing. This allows network administrators to manage connectivity independently of database deployment workflows.

 
 
- OCI region 
An OCI region
 is a localized geographic area that contains one
 or more data centers, hosting availability
 domains. Regions are independent of other regions,
 and vast distances can separate them (across
 countries or even continents).

 
 
- OCI virtual cloud
 network and subnet 
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

 
 
- Oracle Autonomous AI Database Serverless 
 Oracle Autonomous AI Database Serverless is an Oracle Autonomous AI Database . You have a fully elastic database where Oracle autonomously operates all aspects of the database lifecycle from database placement to backup and updates.
 

 
 
- Oracle Exadata Database Service on Dedicated
 Infrastructure 
 Oracle Exadata Database Service on Dedicated
 Infrastructure enables you to leverage the power of Exadata in the cloud. Oracle Exadata Database
 Service delivers proven Oracle AI Database capabilities on purpose-built, optimized Oracle Exadata infrastructure in the public cloud. Built-in cloud automation, elastic resource scaling, security, and fast performance for all Oracle AI Database workloads helps you simplify management and reduce costs.
 

 
 
- OCI Object Storage 
 OCI Object Storage provides access to large amounts of structured and unstructured data of any content type, including database backups, analytic data, and rich content such as images and videos. You can safely and securely store data directly from applications or from within the cloud platform. You can scale storage without experiencing any degradation in performance or service reliability. 
 

 
 
- OCI Vault 
 Oracle Cloud Infrastructure Vault enables you to create and centrally manage the encryption keys that protect your data and the secret credentials that you use to secure access to your resources in the cloud. The default key management is Oracle-managed keys. You can also use customer-managed keys which use OCI Vault . OCI Vault offers a rich set of REST APIs to manage vaults and keys.
 

 
 
 

 

 
 
Recommendations

 

 

 Use the following recommendations as a starting point when deploying
 multicloud workloads. Your requirements might differ from the architecture described
 here. 
 
 

 
 
- High Availability 
 
 
 Oracle Autonomous AI Database and Oracle Exadata Database
 Service provide high availability through several built-in features that ensure
 minimal downtime and data protection. It leverages Oracle Real Application
 Cluster (RAC) for active-active clustering, enabling database instances to run
 on multiple nodes, ensuring continuous availability even if one node fails.
 Additionally it offers Oracle Automatic Storage Management (ASM) with
 redundancy, fault tolerance, and fast recovery options, making it a robust
 platform for mission-critical workloads. 
 

 
 
- Backup 
 Oracle Autonomous AI Database in Oracle AI Database@Google
 Cloud is automatically backed up to OCI Object Storage in the OCI region. Both the backup and restore processes are initiated
 through Oracle Autonomous AI Database . Autonomous AI Database also can have customer initiated backups through the Autonomous AI Database service. All recovery is done through Autonomous AI Database via console, command line, or API interfaces.
 

 
 Oracle Exadata Database
 Service has a choice of using Oracle Database Zero Data Loss Autonomous Recovery Service or OCI Object Storage for automatic database backups. Autonomous Recovery Service dramatically
 shortens backup windows by configuring database-optimized automatic backups and
 implements an incremental backup forever strategy. It reduces recovery time by
 using virtual full backups to immediately restore instead of having to apply
 multiple days of incremental backups in a traditional recovery. 
 

 
 
- Security 
 Oracle Data Safe is an OCI cloud-native tool that enables you to achieve data privacy and data
 compliance for your Oracle databases. Oracle Data Safe empowers organizations to understand data sensitivity, evaluate data risks,
 mask sensitive data, implement and monitor security controls, assess user
 security, monitor user activity, and manage Oracle Database 23ai SQL
 Firewall—all in a single, unified console. These capabilities help to manage the
 day-to-day security and compliance requirements of Oracle databases.
 

 
 
 

 

 
 
Considerations

 

 
When deploying this architecture, consider the following information. 

 
 
- Tenancy 
The tenancy must support OCI identity domains. You can
 create an OCI tenancy when signing up.

 
 
- Network Connectivity 
Plan your network connectivity in advance
 to define your network address space (CIDR) and
 topologies. Create the ODB network in the same Google Cloud project as the VPC to which you will connect.
 The CIDR blocks for any Google Cloud VPCs and OCI
 VCNs must not overlap.
 

 
 
- Configuration 
 
 
Database subnet
