# Build Azure CI/CD Pipelines using Oracle Exadata Database Service in Oracle Database@Azure

- Source: https://docs.oracle.com/en/solutions/azure-pipeline-exacs-dbazure/index.html
- Date: 2025-04
- Type: reference-architecture
- Services: exacs, azure
- Tags: database, multicloud, azure, devops

## Summary (catalog)

Azure DevOps pipeline integration with ExaCS on Database@Azure. Automated schema deployment, testing, and migration using Azure Pipelines with Oracle database tooling.

## Architecture (fetched from source)

Architecture

 

 

 This architecture shows how you can build and deploy Microsoft Azure
 Pipelines using Azure DevOps with Oracle Exadata Database Service on Dedicated
 Infrastructure . 
 
 

 
The application and database source code are hosted on a Microsoft Azure
 DevOps code repository, GitHub, or similar. A user commits changes into the code
 repository which triggers the continuous integration (CI) pipeline. This phase includes
 running unit tests, integration tests, static code analysis, and also testing of
 containers within the Azure Kubernetes Service (AKS) cluster to verify deployment
 readiness.

 
Once testing is complete, the build pipeline creates Docker images and pushes
 them to the Azure container registry. These artifacts then initiate the continuous
 delivery (CD) pipeline. In the CD phase, the artifacts are deployed to AKS where
 end-to-end and system tests are run to ensure microservices operate correctly within the
 Kubernetes environment and the Oracle Database. Staging and production environments,
 using strategies like blue/green or canary deployments, are then initiated for zero
 downtime deployment of the new changes.

 
A Kubernetes cluster can contain multiple pods, each connecting to its own
 respective pluggable database (PDB). The PDBs in the primary database are deployed on
 Oracle Database@Azure that runs on Oracle Exadata Database Service on Dedicated
 Infrastructure in an Azure Availability Zone. The container images are stored in the Azure container
 registry. Users access the application externally through a public load balancer.
 

 
Cloud automation simplifies most lifecycle and management tasks for Oracle Exadata Cloud Infrastructure and Oracle multitenant databases ( CDB s, PDB s). For example, adding servers and scaling OCPUs up and down, creating databases and
 database homes, scheduling infrastructure maintenance, updating and upgrading the VM
 operating system, Oracle Grid Infrastructure , and databases, performing backup and recovery operations, and even enabling disaster
 recovery protections through Oracle Data Guard . 
 

 
Metrics, logs, and tracing of the entire CI/CD process are observed continuously using
 tools like Azure Monitor, Oracle Cloud
 Infrastructure (OCI) and Oracle Database's Unified Observability OpenTelemetry framework which
 provides traces from the entry point of the application residing on Azure, across all
 subsystems, and into the Oracle Database ensuring the performance and reliability of
 both the microservices and the database. This approach ensures a robust, efficient, and
 scalable solution for deploying and managing modern applications in a cloud-native
 environment.
 

 
The following diagram illustrates this reference architecture.
 
 Description of the illustration exadata-database-service.png 
 exadata-database-service-oracle.zip 

 
The architecture has the following components:

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that contains one or more data centers, hosting availability domains. Regions are independent of other regions, and vast distances can separate them (across countries or even continents).
 

 
An Azure region is a geographical area in which
 one or more physical Azure data centers, called availability zones, reside.
 Regions are independent of other regions, and vast distances can separate them
 (across countries or even continents).

 
Azure and OCI regions
 are localized geographic areas. For Oracle Database@Azure, an Azure region is
 connected to an OCI region, with availability zones (AZs) in Azure connected to
 availability domains (ADs) in OCI. Azure and OCI region pairs are selected to
 minimize distance and latency.

 
 
- Azure availability zone 
An availability zone is a physically separate data
 center within a region that is designed to be available and fault tolerant.
 Availability zones are close enough to have low-latency connections to other
 availability zones.

 
Subnet delegation is Microsoft's ability to inject a
 managed service, specifically a platform-as-a-service service, directly into
 your virtual network.

 
 
- Microsoft Azure Virtual Network 
Microsoft Azure Virtual Network (VNet) is
 the fundamental building block for your private network in Azure. VNet enables
 many types of Azure resources, such as Azure virtual machines (VM), to securely
 communicate with each other, the internet, and on-premises
 networks.

 
Subnet delegation is Microsoft's ability to inject a managed
 service, specifically a platform-as-a-service service, directly into your
 virtual network.

 
 
- Azure Pipelines 
Azure Pipelines are part of the
 Azure DevOps service offered by Microsoft Azure to automatically builds, tests,
 and deploys code projects for continuous integration, continuous testing and
 continuous delivery. (CI-CD)

 
 
- Azure Kubernetes Service 
Azure Kubernetes Service
 (AKS) is a managed Kubernetes service offered by Microsoft Azure to deploy and
 manage containerized applications. A Kubernetes cluster can contain multiple
 pods.

 
 
- Kubernetes Control Plane 
A Kubernetes control plane manages the resources
 for the worker nodes and pods within a Kubernetes cluster. The control plane
 components detect and respond to events, perform scheduling, and move cluster
 resources.

 
 
- Oracle Exadata Database Service on Dedicated
 Infrastructure 
 Oracle Exadata Database
 Service delivers proven Oracle Database capabilities on purpose-built, optimized
 Oracle Exadata Cloud Infrastructure in the public cloud. Built-in cloud
 automation, elastic resource scaling, security, and fast performance for OLTP,
 in-memory analytics, and converged Oracle Database workloads help simplify
 management and reduce costs.
 

 
Oracle Exadata Cloud Infrastructure brings
 more CPU cores, increased storage, and a faster network fabric to the public
 cloud. Oracle Exadata storage servers include Exadata RDMA Memory (XRMEM),
 creating an additional tier of storage, boosting overall system performance.
 Exadata combines XRMEM with innovative RDMA algorithms that bypass the network
 and I/O stack, eliminating expensive CPU interrupts and context
 switches.

 
Oracle Exadata Cloud Infrastructure increases the throughput of
 its 100 Gbps active-active Remote Direct Memory Access over Converged Ethernet
 (RoCE) internal network fabric, providing a faster interconnect than previous
 generations with extremely low-latency between all compute and storage
 servers.

 
 
- Oracle Database Autonomous
 Recovery Service 
 Oracle Database Autonomous
 Recovery Service is a fully managed service designed to protect Oracle Databases from data loss and cyber threats. It offers faster backups with reduced database overhead, reliable recovery with validated backups, and real-time protection enabling recovery to within less than a second of an outage or ransomware attack. Oracle Database Zero Data Loss Autonomous Recovery Service is a Zero Data Loss option for the Autonomous Recovery Service. This service provides a centralized data protection dashboard and is recommended for backing up Oracle Databases.
 

 
 
- Oracle Database@Azure 
 Oracle Database@Azure is the Oracle Database service ( Oracle Exadata Database Service on Dedicated
 Infrastructure and Oracle Autonomous Database Serverless ) running on Oracle Cloud
 Infrastructure (OCI), deployed in Microsoft Azure data centers. The service offers features and price parity with OCI. Purchase the service on Azure Marketplace.
 

 
 Oracle Database@Azure integrates Oracle Exadata Database
 Service , Oracle Real Application Clusters (Oracle
 RAC) , and Oracle Data Guard technologies into the Azure platform. Users manage the service on the Azure console and with Azure automation tools. The service is deployed in Azure Virtual Network (VNet) and integrated with the Azure identity and access management system. The OCI and Oracle Database generic metrics and audit logs are natively 
