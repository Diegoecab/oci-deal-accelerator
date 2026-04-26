# Deploy Oracle Autonomous Database on Oracle Database@Google Cloud

- Source: https://docs.oracle.com/en/solutions/deploy-adb-db-at-google-cloud/index.html
- Date: 2025-03
- Type: reference-architecture
- Services: adb-s, adg, google-cloud
- Tags: database, multicloud, ha-dr, autonomous

## Summary (catalog)

ADB-S on Database@Google Cloud with cross-region ADG. Non-overlapping CIDR between VPC and VCN required. App tier should span 2+ AZs with Google Global Load Balancer for failover.

## Architecture (fetched from source)

Architecture

 

 
This architecture describes some best practices for deploying an Oracle Autonomous Database in Oracle Database@Google Cloud in multiple regions using Oracle Autonomous Data Guard . 
 

 
Business continuity practices and high-availability topologies should always be considered when designing mission-critical database applications. The architecture diagram shows an application running in two Google Cloud Regions. Users access the application externally through a Google Cloud Load Balancer. Optionally, the Autonomous Database can be configured to have a primary database running in the primary region and a standby database running in the secondary region. In the unlikely event of a Google Cloud Region failure, the standby database in the secondary region can be activated and can become the primary database to serve the application. 
 

 
The application accesses the database through a private connection to the Oracle Database@Google Cloud subnet. If cross-region business continuity is required, Oracle Autonomous Data Guard can optionally be enabled. If Oracle Autonomous Data Guard is enabled, then Oracle will automatically create a standby database in another
 Google Cloud Region. Oracle Autonomous Data Guard keeps the primary database and cross-region standby in sync so that the standby
 database can be activated with minimal data loss in the case of a primary region
 outage.  Oracle-managed automatic backups are always enabled by default.
 

 
The following diagram illustrates this reference architecture.
 
 Description of the illustration adb-oracle-db-google-cloud-region.png 
 adb-oracle-db-google-cloud-region-oracle.zip 

 
The architecture has the following components:

 
 
- Region 
An Oracle Cloud
 Infrastructure (OCI) or Google Cloud Region is a localized geographic area that contains one
 or more data centers. Regions are independent of one another and are in many
 countries across multiple continents. 
 
In regions where the Oracle Database@Google Cloud services are available, a Google Cloud Region is connected to an OCI Region, with
 Google Cloud availability zones (AZs) inter-connected to corresponding OCI
 availability domains (ADs). 
 
 
- Google Availability Zone 
An availability zone is a
 physically separate data center within a region designed to be available and
 fault-tolerant. It is close enough to have low-latency connections to other
 availability zones. 

 
 
- Google Cloud Project 
A Google Cloud Project is required to use Google Workspace APIs and build Google Workspace add-ons or apps. A Cloud project forms the basis for creating, enabling, and using all Google Cloud services, including managing APIs, enabling billing, adding and removing collaborators, and managing permissions.

 
 
- Google Virtual Private Cloud 
Google Cloud Virtual Private Cloud (VPC) provides networking functionality to Compute Engine virtual machine (VM) instances, Google Kubernetes Engine (GKE) containers, database services, and serverless workloads. VPC provides global, scalable, and flexible networking for your cloud-based service.

 
 
- Google Subnets 
Each VPC network consists of one
 or more IP address ranges called subnets. Subnets are regional resources that
 have IP address ranges associated with them. 

 
 
- Google Load Balancer 
 
 
Google Load Balancer provides automated traffic distribution from a
 single entry point to multiple servers in the back end. 

 
 
- Autonomous Data Guard 
 Oracle Autonomous Data Guard enables a standby (peer) database to provide data protection and disaster recovery for your Autonomous Database instance. It provides a comprehensive set of services that create, maintain, manage, and monitor one or more standby databases to enable production Oracle databases to remain available without interruption. Oracle Data Guard maintains these standby databases as copies of the production database. Then, if the production database becomes unavailable because of a planned or an unplanned outage, you can switch any standby database to the production role, minimizing the downtime associated with the outage.
 

 
 
- Object storage 

 OCI Object Storage provides access to large amounts of structured
 and unstructured data of any content type,
 including database backups, analytic data, and
 rich content such as images and videos. You can
 safely and securely store data directly from the
 internet or from within the cloud platform. You
 can scale storage without experiencing any
 degradation in performance or service reliability.
 
 

 
Use standard storage for
 "hot" storage that you need to access quickly,
 immediately, and frequently. Use archive storage
 for "cold" storage that you retain for long
 periods of time and seldom or rarely
 access.

 
 
- Oracle Cloud Infrastructure Vault 
 Oracle Cloud Infrastructure Vault enables you to create and centrally manage the encryption keys that protect your data and the secret credentials that you use to secure access to your resources in the cloud. The default key management is Oracle-managed keys. You can also use customer-managed keys which use OCI Vault . OCI Vault offers a rich set of REST APIs to manage vaults and keys.
 

 
 
 

 

 
 
Considerations

 

 
When implementing this architecture, consider the following:

 
 
- Network Connectivity 
When using private
 connectivity, plan your network connectivity in advance to
 define your network address space (CIDR) and topologies. You
 need at least one VPC that you can pair with a corresponding
 OCI Virtual Cloud Network (VCN). The CIDR blocks for any
 Google Cloud VPCs and OCI VCNs must not overlap. 

 
 
- Application Resiliency 
If using a cross-region
 standby, then the application tier should also have
 cross-region redundancy with Google Cloud Global Load
 Balancer for quick failover.

 
 
- Disaster Recovery Testing 
Test your disaster
 recovery setup by performing a switchover to the standby
 database on a regular cadence to ensure operational
 excellence.

 
 
 

 

 
 
Explore More

 

 
Learn more about Oracle Database@Google Cloud :
 

 
 
- Learn more about Oracle Database@Google Cloud 
 
- Learn about Autonomous Database on Oracle
 Database@Google Cloud 
 
- Getting started with Autonomous
 Database on Oracle Database@Google Cloud 
 (blog)
 
 
- Oracle Database@Google Cloud (video)
 
 
 
 

 

 
 
Acknowledgments

 

 
 
- Authors : Tony Politano, Yasin Baskan, Tammy Bednar,
 Domenick Ficarella, Can Tuzla 
 
 

 

 

 

 

 
 Title and Copyright Information 

 

 
Deploy an Oracle Autonomous Database in Oracle Database@Google Cloud

 
G26642-01

 
March 2025

 
 Copyright © 2025, 

Oracle and/or its affiliates.
