# Learn about selecting network topologies for Oracle Database@Azure

- Source: https://docs.oracle.com/en/solutions/network-topology-oracle-database-at-azure/index.html
- Date: 2025-05
- Type: reference-architecture
- Services: vcn, drg, azure
- Tags: networking, multicloud, azure

## Summary (catalog)

Network topology options for Database@Azure. Compares single-VNet, hub-spoke, and transit gateway patterns. Guidance on IP address planning and NSG rules for database traffic.

## Architecture (fetched from source)

Learn About Oracle AI Database@Azure 
 
 
 
 
- 
 
- 
 
 
 
 
 
- 
 
 
 
 
 
 
 
 
 
- 
 
 
 
 
 
 
 
 
 
- 
 
- 
 
- 
 
- 
 
- 
 
- 
 
- 
 
- 
 
- 
 
- 
 
- 
 
- 
 
 
 
 

 Previous 
 Next 
 JavaScript must be enabled to correctly display this content
 
 

 

 
 
 
Learn About Oracle AI Database@Azure 

 

 

 
 Oracle AI Database@Azure is the Oracle Database service running on Oracle Cloud
 Infrastructure (OCI), colocated in Microsoft Azure data centers.
 

 
 Oracle AI Database@Azure brings
 Oracle technologies, such as Oracle Exadata Database
 Service , Oracle Autonomous AI Database Serverless , Oracle Real Application Clusters (Oracle
 RAC) , and Oracle Data Guard , into the Azure platform. The solution uses Azure networking and Azure Virtual Network (VNet) access. You can manage the service on the
 Azure console or using Azure automation tools. Oracle AI Database@Azure 
 consists of a fully-managed Autonomous Database and a co-managed Oracle Exadata Database
 Service . Both services are natively integrated in Azure providing a simple, secure, and low latency operating environment. Microsoft Entra
 ID provides federated identity and access management for Oracle AI Database@Azure . The
 solution is deployable across multiple Azure availability zones (AZs) and regions to ensure business continuity and cloud
 resilience.
 

 
In this solution, you learn about the available network topology options
 considerations and options for selecting the one best suited to your organizational
 needs.

 

 
 
Before You Begin

 

 
 Before you begin, ensure you are familiar with Oracle AI Database@Azure :
 

 
 
- Oracle AI Database@Azure 
 
- Oracle Autonomous AI Database Serverless 
 
- Oracle Exadata Database Service on Dedicated
 Infrastructure 
 
- Plan for IP Address Space 
 
- Oracle AI Database@Azure Landing Zone Network Topology 
 
- Oracle AI Database@Azure Network Planning 
 
 

 

 
 
Considerations for Oracle Autonomous AI Database Serverless Networking
 

 

 

 Consider the following requirements for Oracle Autonomous AI Database Serverless networking: 
 
 

 
 
- A VNet with 1x subnet (DB subnet) in Azure 
 
- Create and delegate the DB subnet to Oracle AI Database@Azure before Oracle Autonomous AI Database Serverless deployment
 
 
- Reuse (or share) the delegated subnet with additional
 databases 
 
 
The following table shows the minimum required subnet size for Oracle Autonomous AI Database Serverless :
 

 

 
 
 
 Database Subnet: Number of
 Required IP Addresses 
 Database Subnet: Minimum
 Size 
 
 
 
 
 1 address Deployed Oracle Autonomous AI Database Serverless instance
 
 + 13 addresses for Oracle AI Database@Azure service
 

 
 Minimum CIDR requirement for 1
 deployed Oracle Autonomous AI Database Serverless is /27 (16 Addresses) 
 
 
 
 

 

 

 
 
Considerations for Oracle Exadata Database Service on Dedicated
 Infrastructure Networking
 

 

 
Consider the following for Oracle Exadata Database Service on Dedicated
 Infrastructure VM Cluster networking:
 

 
 
- A VNet with 1x subnet (Client subnet) in Azure .
 
 
- Create and delegate the client subnet to Oracle AI Database@Azure before Oracle Exadata Database Service on Dedicated
 Infrastructure VM Cluster deployment.
 
 
- CIDR blocks for the backup subnet during Oracle Exadata Database Service on Dedicated
 Infrastructure VM Cluster deployment. Deploy the backup subnet in OCI, not in Azure .
 
 
- Non overlapping networks with separate CIDR blocks for each deployment
 in a disaster recovery scenario. 
 
 
Each database node requires 4x IP addresses and
 3x additional addresses reserved for Single Client Access Names
 (SCANs).
 

 
The following table shows the minimum required subnet size depending on the
 Oracle Exadata Database Service on Dedicated
 Infrastructure configuration you choose.
 

 

 
 
 
 Client Subnet: Number of Required IP Addresses 
 Client Subnet: Minimum size* 
 Backup Subnet (Not in Azure): Number of Required IP
 Addresses 
 Backup Subnet (Not in Azure): Minimum size* 
 
 
 
 
 4 addresses per database node (minimum 2 nodes) 
 + 3 for SCANs +13 for Oracle AI Database@Azure service
 
 
 
 
Client subnet minimum size /27 

 
 
The minimum size determined by total number of IP
 addresses needed for database node

 
 
 3 IP addresses per database node (minimum 2
 nodes) 
 
 
 
Backup subnet minimum size /28 

 
 
Minimum size determined by total number of IP addresses
 needed for database nodes

 
 
 
 
 
 

 

 

 

 

 

 
 Title and Copyright Information 

 

 
Learn about network topologies for Oracle AI Database@Azure

 
F97692-03

 
April 2026

 
 Copyright © 2024,2026, 

Oracle and/or its affiliates.
