# Implement disaster recovery with cross-regional Data Guard on Oracle Database@AWS

- Source: https://docs.oracle.com/en/solutions/implement-dr-cross-region-dg-odb-aws/index.html
- Date: 2025-08
- Type: reference-architecture
- Services: exacs, adg, aws
- Tags: database, multicloud, aws, ha-dr

## Summary (catalog)

Cross-region Data Guard on Database@AWS for DR. Asynchronous redo transport for cross-region replication. Planned switchover for maintenance, forced failover for disaster scenarios.

## Architecture (fetched from source)

About Implementing Disaster Recovery with Cross-Regional Active Data Guard on Oracle Database@AWS 
 
 
 
 
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
 
 

 

 
 
 
About Implementing Disaster Recovery with Cross-Regional Active Data Guard on Oracle Database@AWS 

 

 

 
 This solution playbook describes how to set up Oracle Active Data Guard on Oracle Exadata Database Service on Dedicated
 Infrastructure on Oracle Database@AWS across two different regions. Oracle Database@AWS is the Oracle Database service running on Oracle Cloud Infrastructure (OCI), colocated in Amazon AWS data centers. Oracle Database@AWS offers Oracle Exadata Database Service on Dedicated
 Infrastructure and Oracle Autonomous Database on Dedicated Exadata Infrastructure , natively integrated into the AWS platform. Oracle Data Guard enables you to transport the data from the primary to the standby database to ensure minimal data loss across regions. 
 

 
 Oracle Database@AWS offers built-in high availability and scalability with Oracle Real Application Clusters (Oracle
 RAC) while ensuring low latency for AWS applications. Extending the solution with an Active Data Guard standby database hosted on another Oracle Exadata Cloud Infrastructure in another region ensures data protection and disaster recovery in case of regional outages. 
 

 
 Active Data Guard adds comprehensive data corruption prevention with automatic block repair, online upgrades and migrations, offload workload to standby with read-mostly scale-out, and enable Application Continuity to mask database outages during planned and unplanned events from end-users and ensure uninterrupted applications.
 

 
 Oracle Exadata Database
 Service on Oracle Database@AWS is certified at the Gold tier of Oracle Maximum Availability Architecture (MAA). This validation confirms that the service meets Oracle’s highest standards for high availability and disaster recovery, with support for failover across multiple AWS availability zones as well as across AWS regions. With Gold MAA certification, Oracle Exadata Database
 Service on Oracle Database@AWS blends cloud flexibility with proven resilience, ensuring your mission-critical workloads stay protected from server failures as well as data center outages. 
 

 

 
 
Before You Begin

 

 
 Ensure your deployment meets the following requirement: 

 
The configuration and deployment instructions in this solution playbook require the Exadata infrastructure and the Exadata VM Cluster to be already deployed in the standby region, and that the network IP CIDR ranges for the primary and standby Exadata VM Clusters do not overlap.

 
Review the following resources:

 
 
- Oracle Exadata Database Service on Dedicated Infrastructure Overview 
 
- Deploy Oracle
 Database@AWS 
 
 
Review these related solutions:

 
 
- Security best practices for your VPC in the Amazon Virtual Private Cloud User Guide 
 
- Plan for AWS IP address space using ODB Network Design 
 
 

 

 
 
About Required Services and
 Roles

 

 
This solution requires the following services and roles:

 
 
- Oracle Cloud Infrastructure
 Networking 
 
- Oracle Exadata Database
 Service 
 
 
These are the roles needed for each service.

 

 
 
 
 Service Name: Role 
 Required to... 
 
 
 
 
 Oracle Exadata Database
 Service : manage database-family 
 Manage the database, including adding and operating Active Data Guard deployments 
 
 
 OCI Networking : manage vcn-family 
 Manage the network components, including VCNs, subnets, security rules, and VCN
 peering 
 
 
 
 

 

 

 

 

 

 
 Title and Copyright Information 

 

 
Implement disaster recovery with cross-regional Active Data Guard on Oracle Database@AWS

 
G40860-01

 
August 2025

 
 Copyright © 2025, 

Oracle and/or its affiliates.
