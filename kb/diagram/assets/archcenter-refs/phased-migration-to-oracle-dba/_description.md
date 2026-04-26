# Migrate business critical applications to Oracle Database@Azure using a phased strategy

- Source: https://docs.oracle.com/en/solutions/phased-migration-to-oracle-dba/index.html
- Date: 2025-03
- Type: reference-architecture
- Services: exacs, azure, goldengate, adg
- Tags: database, multicloud, azure, migration

## Summary (catalog)

Phased migration to Database@Azure. Leverages OCI networking for DR replication with low-latency, high-bandwidth connectivity. Integrates Autonomous Recovery Service with Data Guard for data protection.

## Architecture (fetched from source)

Architecture

 

 
This architecture outlines a phased approach for migrating on-premises Oracle
 Database onto Oracle Exadata Database
 Service at Oracle Database@Azure with minimal downtime.
 

 
To simplify this strategy, we break it down into three key aspects: current
 state, future state, and migration phases.

 
This reference architecture has four primary components (marked with blue
 numbers in diagram).
 

 
 
 
 Number 
 Component 
 Description 
 
 
 
 
 1 
 On-premises primary data center 
 Hosts the database and application as the primary system before
 migration. 
 
 
 2 
 On-premises standby data center 
 Maintains a standby system, replicating the on-premises primary
 database. 
 
 
 3 
 Azure primary region 
 Runs the application and database on Oracle Database@Azure , becoming the primary system post-migration.
 
 
 
 4 
 Azure standby region 
 A disaster recovery site replicating the primary region using Oracle Data Guard .
 
 
 
 
 

 

 
 Description of the illustration logical-architecture-diagram.png 

 logical-architecture-diagram-oracle.zip 

 
 Current state 

 
In the existing setup, both the primary data center (1) and standby data center (2) are
 hosted on-premises, supporting application workloads and databases. The primary data
 center handles all requests, while the standby data center maintains asynchronous
 replication using Oracle Data Guard . This ensures high availability, with the standby system ready for failover in case
 of unexpected failures.
 

 
 Future state 

 
The future architecture mirrors the current setup but is fully hosted in the
 cloud, spanning two Azure regions: the primary region (3) and the standby region (4). The database is migrated
 to Oracle Database@Azure Exadata services, with asynchronous replication between the primary and standby
 databases managed via Oracle Data Guard over the Oracle Cloud
 Infrastructure (OCI) network.
 

 
For secure connectivity between the on-premises data center and Azure , an Azure Firewall is deployed within a secure Virtual WAN (vWAN) Hub in Azure .
 

 
 Migration phases 

 
The migration follows a two-phase approach to ensure a controlled and
 reliable transition.

 
 Phase 1 – Transitioning on-premises standby to Azure and switchover 

 
In this phase, the on-premises standby system (2) is migrated to Azure (3). Once completed, the primary (1) and standby (3) roles are swapped, making Azure the new primary region.
 

 
 
- Establish connectivity between on-premises and Azure using Azure ExpressRoute .
 
 
- Configure Azure secure hub, Azure Firewall, and vWAN for security (if not already in place).
 
 
- Provision Oracle Exadata Cloud Infrastructure in Azure ’s primary region, then:
 
 
- Set up an Oracle Exadata virtual machine (VM) cluster and create
 the target database. 
 
- Enable archive logs and forced logging on the primary database
 (if not already enabled). 
 
 
 
- Configure Oracle Net for listener and TNS names for discovery. 
 
- Restore from service to set up a standby database in Azure ’s primary region (3).
 
 
- Perform a switchover, making the Azure database (3) the new primary.
 
 
- Migrate applications to the Azure primary region (3) and update DNS routes.
 
 
- Verify the Data Guard configuration and monitor the replication status.
 
 
 
 Phase 2 – Establishing standby in Azure and decommissioning on-premises 

 
In this phase, a standby system (4) is set up in Azure , and on-premises resources (1 and 2) are decommissioned.
 

 
 
- Provision Oracle Exadata Cloud Infrastructure in the standby region (4) with Oracle Database@Azure .
 
 
- Set up an Oracle Exadata VM cluster and create the standby database. 
 
- Enable Oracle Data Guard to associate the primary region database (3) with the standby database (4).
 
 
- Use OCI networking for high-throughput replication, leveraging local and remote
 peering within a hub-and-spoke topology between the primary and standby
 databases. 
 
- Migrate application workloads to the Azure standby region (4).
 
 
- Stop the synchronization with the on-premises resources and then
 decommission the on-premises application and database resources from the primary (1)
 and standby (2) data centers. 
 
 
The following diagram illustrates this reference architecture.

 
 Description of the illustration physical-architecture-diagram.png 

 physical-architecture-diagram-oracle.zip 

 
 Microsoft Azure provides the following components:
 

 
 
- Azure Region 
An Azure region is a geographical area in which one or more
 physical Azure data centers, called availability zones, reside. Regions
 are independent of other regions, and vast distances can
 separate them (across countries or even continents).
 

 
 Azure and OCI regions are localized geographic areas. For Oracle Database@Azure , an Azure region is connected to an OCI region, with availability
 zones (AZs) in Azure connected to availability domains (ADs) in OCI. Azure and OCI region pairs are selected to minimize distance
 and
 latency.
 

 
 
- Azure Availability Zone 
Azure
 availability zones are physically separate locations within
 an Azure region, designed to ensure high availability and
 resiliency by providing independent power, cooling, and
 networking.

 
 
- Azure VNet 
Microsoft Azure Virtual Network (VNet) is
 the fundamental building block for your private network in
 Azure. VNet enables many types of Azure resources, such as
 Azure virtual machines (VM), to securely communicate with
 each other, the internet, and on-premises networks.

 
 
- Azure Delegated Subnet 
Subnet delegation is
 Microsoft's ability to inject a managed service,
 specifically a platform-as-a-service (PaaS) service,
 directly into your virtual network. This allows you to
 designate or delegate a subnet to be a home for an external
 managed service inside of your virtual network, such that
 external service acts as a virtual network resource, even
 though it is an external PaaS service.

 
 
- Azure VNIC 
The services in Azure
 data centers have physical network interface cards (NICs).
 Virtual machine instances communicate using virtual NICs
 (VNICs) associated with the physical NICs. Each instance has
 a primary VNIC that's automatically created and attached
 during launch and is available during the instance's
 lifetime.

 
 
- Azure Virtual Network Gateway 
Azure
 Virtual Network Gateway establishes secure, cross-premises
 connectivity between an Azure virtual network and an
 on-premises network. It allows you to create a hybrid
 network that spans your data center and
 Azure.

 
 
- Azure Virtual WAN 
Microsoft Azure Virtual
 WAN (VWAN) is a networking service that brings many
 networking, security, and routing functionalities together
 to provide a single operational interface.

 
 
- Azure Secure Hub 
An Azure secure hub, also known as a
 secured virtual hub, is an Azure Virtual WAN hub enhanced
 with security and routing policies managed by Azure Firewall
 Manager. It simplifies the creation of hub-and-spoke and
 transitive network architectures by integrating native
 security services for traffic governance and protection.
 This setup automates traffic routing, eliminating the need
 for user-defined routes (UDRs). Organizations can use a
 secure hub to filter and secure traffic between virtual
 networks, branch offices, and the internet, ensuring robust
 security and streamlined network management.
 

 
 
- Azure Firewall Manager 
Azure Firewall
 Manager is a centralized security management service that
 simplifies the deployment and configuration of Azure
 Firewall across multiple regions and subscriptions. It
 allows for hierarchical policy management, enabling global
 and local firewall policies to be applied consistently. When
 integrated with Azure Virtual WAN (vWAN) and a secure hub,
 Azure Firewall Manager enhances security by automating
 traffic routing and filtering without the need for
 user-defined routes (UDRs). This integration ensures that
 tr
