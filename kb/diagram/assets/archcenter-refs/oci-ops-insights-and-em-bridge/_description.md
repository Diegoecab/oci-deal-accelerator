# Uncover performance issues, forecast consumption, and plan capacity with OCI Ops Insights

- Source: https://docs.oracle.com/en/solutions/oci-ops-insights-and-em-bridge/index.html
- Date: 2024-03
- Type: reference-architecture
- Services: ops-insights, exacs, adb-s
- Tags: observability, database

## Summary (catalog)

Ops Insights for database performance analysis and capacity planning. SQL analytics for query optimization, AWR data integration from Enterprise Manager, cross-database performance comparison.

## Architecture (fetched from source)

Architecture

 

 
This architecture describes the process to use OCI Ops Insights to perform resource analysis against databases and hosts, including Exadata systems
 managed by Oracle Enterprise Manager . Use this architecture for retaining and analyzing longer-term telemetry to provide
 insights on future resource demand and application performance.
 

 
Configuring OCI service connectivity requires setup of both Oracle Enterprise Manager and the OCI service, and is performed in two steps:
 

 
 
- Export Oracle Enterprise Manager data to OCI.
 
 
- Import data from the OCI Object Storage bucket to the OCI service.
 
 
 
To move target data from Oracle Enterprise Manager to OCI, you create a Cloud Bridge in Oracle Enterprise Manager . The Cloud Bridge defines a data connection to the OCI Object Storage bucket residing in OCI. Bridge creation is a one-time setup. Once created, it can be
 edited, updated, or deleted as needed. Install EM Agent on application and database
 servers for Oracle Enterprise Manager to fetch data from these servers. After installing EM Agent on these servers, these
 databases need to be discovered in Oracle Enterprise Manager .
 

 
Once you've set up the Cloud Bridge to move data from Oracle Enterprise Manager to the OCI Object Storage bucket, you will need to create an EM Bridge in OCI to move Oracle Enterprise Manager target data from the OCI Object Storage bucket to OCI Ops Insights for processing.
 

 
When selecting the OCI service while enabling data export, select the
 appropriate OCI Ops Insights service for your needs:
 

 
 
- Capacity planning and SQL warehouse 
For Exadata Insights, Host
 Capacity Planning, Database Capacity Planning, SQL Warehouse, and SQL
 Explorer.

 
 
- EM Warehouse 
The Oracle Enterprise Manager repository contains critical information such as operational, performance and
 configuration metrics, and target inventory data for the targets monitored by
 Oracle Enterprise Manager . EM Warehouse provides a convenient way to access and analyze this data using
 cloud-based tools and services.
 

 
 
- Exadata Warehouse 
Exadata Warehouse provides a store-based
 custom analytics solution that helps maximize the performance and utilization of
 critical workloads running on all Exadata deployments that are monitored by EM
 13.5 RU10 or later.

 
 
 
Before setting up the EM Bridge, you need to create Oracle Identity and Access Management (IAM) policies in order to read from the configured OCI Object Storage bucket. Create a dynamic group and provide permissions for the dynamic group to
 access the data in the above OCI Object Storage compartment.
 

 
 Reference architecture using Oracle Enterprise Manager Agents 

 
This reference architecture illustrates the on-premises or third-party cloud
 setup of Oracle Enterprise Manager Agents on target application or database servers. Oracle Management Agent is one of the core components of Oracle Enterprise Manager Cloud Control ( Cloud Control ) that enables you to convert an un-managed host to a managed host in the Oracle Enterprise Manager system. Oracle Management Agent works in conjunction with the plug-ins to monitor the targets running on that managed
 host. Oracle Management Agent posts the data to OCI via the proxy or a firewall. The agent is responsible for
 collecting log, metrics, performance, configuration, orchestration jobs, and compliance
 checks to be used in the various services (for example, log analytics, IT analytics,
 infrastructure monitoring, configuration, and compliance).
 

 

 
Note:
Starting with Oracle Enterprise Manager Cloud Control 13c Release 5 Update 15 (13.5.0.15), Cloud Bridge supports the specification of proxy
 details which are used for outbound connections to OCI. This release update (patch)
 needs to be applied to the OMS, central agent, and all other participating
 agents.
 

 
The following diagram illustrates this reference architecture.

 
 Description of the illustration oracle-enterprise-manager-agents.png 

 oracle-enterprise-manager-agents-oracle.zip 

 
 Reference architecture with routing via Enterprise Manager 

 
This reference architecture illustrates how to transport your Oracle Cloud Observability and
 Management Platform data, collected on-premises or in a third-party cloud network. Oracle Enterprise Manager Cloud Control agents route all the traffic to the Management Gateway and from there is gets routed
 to OCI via the proxy. Using the Management Gateway as the single point for traffic to
 and from OCI means that the enterprise firewall only needs to allow HTTPS communication
 from the host where the Management Gateway resides. The Management Gateway can reside in
 the EM OMS or on a separate host.
 

 
All communication from Management Agent Gateway to Oracle Cloud is over HTTPS (port 443)
 and is outbound only.

 
The following diagram illustrates this reference architecture.

 
 Description of the illustration routing-enterprise-manager.png 

 routing-enterprise-manager-oracle.zip 

 
The architecture has the following components:

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that contains one or more data centers, called availability domains. Regions are independent of other regions, and vast distances can separate them (across countries or even continents).
 

 
 
- Virtual cloud network (VCN) and subnets 
A VCN is a customizable, software-defined network that you set up in an Oracle Cloud
 Infrastructure region. Like traditional data center networks, VCNs give you complete control over your network environment. A VCN can have multiple non-overlapping CIDR blocks that you can change after you create the VCN. You can segment a VCN into subnets, which can be scoped to a region or to an availability domain. Each subnet consists of a contiguous range of addresses that don't overlap with the other subnets in the VCN. You can change the size of a subnet after creation. A subnet can be public or private. 
 

 
 
- VCN attachments 
You can attach multiple VCNs to a single DRG. Each VCN can
 be in the same tenancy as the DRG, or they can be in different
 tenancies.

 
 
- Route table 
Virtual route tables contain rules to route traffic from subnets to destinations outside a VCN, typically through gateways.

 
 
- Security list 
For each subnet, you can create security rules that specify the source, destination, and type of traffic that must be allowed in and out of the subnet.

 
 
- Site-to-Site VPN 
Site-to-Site VPN provides IPSec VPN connectivity between your on-premises network and VCNs in Oracle Cloud
 Infrastructure . The IPSec protocol suite encrypts IP traffic before the packets are transferred from the source to the destination and decrypts the traffic when it arrives.
 

 
 
- Management Gateway 
Management Gateway provides a single egress point for
 management agents and other clients to connect to OCI services.

 
 
- Oracle Enterprise Manager Management Agent 
 Oracle Enterprise Manager (OEM) Management Agent is a software component that monitors targets running
 on hosts and communicates that information to the middle-tier Oracle Management
 Service (OMS). The Management Agent is an integral software component that
 enables you to convert an un-managed host to a managed host in the Oracle Enterprise Manager system. The Management Agent works in conjunction with the plug-ins to
 monitor the targets running on that managed host.
 

 
 
- Oracle Management Service 
 Oracle Management Service (OMS) is a web-based application that orchestrates with the Management Agents
 and the plug-ins to discover targets, monitor and manage them, and store the
 collected information in a repository for future reference and analysis. The OMS
 also renders the user interface for Oracle Enterprise Manager Cloud Control .
 

 
 
- Central Agent 
With the first Oracle Management Service (OMS) you install, by default you receive a Management Agent called the
 Central Ag
