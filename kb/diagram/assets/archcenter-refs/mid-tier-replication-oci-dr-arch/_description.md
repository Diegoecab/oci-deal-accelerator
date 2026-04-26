# Implement mid-tier replication in an OCI disaster recovery architecture

- Source: https://docs.oracle.com/en/solutions/mid-tier-replication-oci-dr-arch/index.html
- Date: 2025-11
- Type: reference-architecture
- Services: compute, fsdr, load-balancer
- Tags: ha-dr, application

## Summary (catalog)

Mid-tier replication patterns for OCI DR. Application server state replication across regions using rsync, block volume replication, or container image promotion. FSDR for automated failover.

## Architecture (fetched from source)

Architecture

 

 
This architecture shows a high-level overview of middleware active-passive disaster recovery topology. This playbook assumes that the primary and secondary systems are already created.

 
Any active-passive disaster recovery solution for a mid-tier system must implement the following essential features :
 

 
 
- Geographic separation 
Primary and secondary systems are geographically separated, far enough so they can’t be affected by the same disaster event.

 
 
- Symmetry 
The primary and secondary systems are symmetric. The secondary system has the same number of nodes in the mid-tier and the db-tier, with similar CPU and memory capacity.

 
 
- Unique front-end name 
 
Unique front-end names for the primary and secondary. The access from clients to the system must be agnostic to the site being used as the primary one. To accomplish this, the front-end address names must be unique and always map to the IP of the system that is the primary at that moment. This name is usually referred to as a virtual front-end or vanity URL . 
 

 
 
- Listen addresses 
The listen addresses of the mid-tier processes must be host names resolvable in both systems and mapped to the IPs of the hosts of the local site. 

 
 
- Database replication 
 
The data of the primary database must be replicated to the standby database using Oracle Data Guard .
 

 
 
- Mid-tier replication 
 
Primary and secondary mid-tiers must be in sync. They must have the same configuration, the same product version, and the same patch level. There are different approaches to achieve this. You can maintain primary and secondary systems separately: if a change is performed in primary, the same change is repeated in secondary, if a patch is installed in primary, the same patch is installed in standby. However, this duplicates the work and is prone to errors. Oracle Maximum Availability
 Architecture ( Oracle MAA ) recommends implementing an automatic replication to copy the mid-tier file system artifacts. This ensures that the primary and standby systems are always in sync.
 

 
 
- Management of the information that is specific to each site 
The configuration of the secondary is an exact copy of the primary, but there may be file artifacts that contain information specific to each site, which must be different in primary and secondary. The DR topology must support this and allow site-specific information customization.

 

 
Tip:

 
 Oracle WebLogic
 Server Example 

 
In an Oracle WebLogic system, the primary mid-tier connects to the primary region’s database, and the secondary mid-tier connects to the secondary region’s database. The primary and secondary mid-tier systems have the same configuration, so there must be a mechanism to ensure that each system uses the appropriate connection string that points to its local database. Oracle Maximum Availability
 Architecture ( Oracle MAA ) recommends using TNS aliases for the data sources, with different tnsnames.ora files in each site. The mid-tier replication methods must take this into account, either skipping the file containing the database connect string ( tnsnames.ora ) or replacing the database connect string in the files to point to the local database.
 

 

 
 
 
The following image is an example of an active-passive disaster recovery solution for a mid-tier system.

 
 Description of the illustration active-passive-dr-mid-tier.png 

 active-passive-dr-mid-tier-oracle.zip 

 

 

 
 
Terminology

 

 
You should be familiar with the following concepts and terminology: 

 
 
- Mid-tier (also middle tier or middleware) 
The mid-tier refers to the layer within a multi-tiered application architecture that sits between the user interface (front-end) and the data storage (back-end). It handles business logic, data processing, and security, acting as a bridge between the user and the database. 

 
 
- Disaster 
A sudden, unplanned catastrophic event that causes unacceptable damage or loss in a site or geographical area. A disaster is an event that compromises an organization's ability to provide critical functions, processes, or services for unacceptable period and causes the organization to invoke its recovery plans.

 
 
- 
 
 Disaster Recovery (DR) 

 
 Ability to safeguard against natural or unplanned outages at a production site by having a recovery strategy for applications and data to a geographically separate secondary site.

 
 
- Disaster Recovery Topology 
The production site and the secondary site hardware and software components that comprise an Oracle Fusion Middleware Disaster Recovery solution.

 
 
- Oracle Maximum Availability Architecture 
 Oracle Maximum Availability
 Architecture ( Oracle MAA ) is the best practice blueprint for data protection and availability of Oracle products (Database, Fusion Middleware, Applications). Implementing Oracle MAA best practices is one of the key requirements for any Oracle deployment. It provides recommendations for setting up and managing an Oracle system. Oracle MAA includes the Oracle Fusion Middleware Enterprise Deployment Guide recommendations and adds disaster protection best practices to minimize planned and unplanned downtime for outages affecting an entire data center or region. 
 

 
 
- System 
A System is a set of targets (hosts, databases, application servers, and so on) that work together to host your applications. For example, to monitor an application in Oracle Enterprise Manager, you would first create a System, that consists of the database, listener, application server, and hosts targets on which the application runs.

 
 
- Site 
A site is the set of different components in a data center needed to run a group of applications. For example, a site could consist of Oracle Fusion Middleware instances, databases, storage, and so on.

 
 
- Production or Primary site 
The site that is carrying the system’s workload at a precise point in time. It is a group of hardware, network, and storage resources, and processes that is actively used to carry business logic and process requests at a precise point in time.

 
 
- Secondary (or standby or DR) site 
A secondary site is a backup location that can take over the business logic and requests that a primary site was processing. Typically, secondary sites are also named as "Standby" because they remain on "standby or inactive mode". This means that they are not processing the production workload during normal operations. However, this does not imply that the secondary site cannot be used for other purposes. This is especially true in more modern models where the secondary site is used for reporting operations and more importantly for validating changes before applying them in the primary site.

 
 
- Recovery Point Objective (RPO) 
Recovery point objective is the amount of data loss that a system can tolerate from a business point of view. For example, the amount of data loss that is acceptable when an outage takes place.

 
 
- Recovery Time Objective (RTO) 
Recovery time objective is the amount of downtime a system can tolerate or the acceptable amount of time that an application or service can remain unavailable when an outage takes place, from a business point of view.

 
 
- Oracle Cloud Infrastructure (OCI) 
OCI is a set of complementary cloud services that enable you to build and run a range of applications and services in a highly available hosted environment. OCI provides high-performance compute capabilities (as physical hardware instances) and storage capacity in a flexible overlay virtual network that is securely accessible from your on-premises network.

 
 
- OCI region 
An OCI region is a localized geographic area, composed of one or more availability domains. Regions are independent of other regions and can be separated by vast distances—across countries or even continents. A region is a site in terms of Disaster Recovery.

 
 
- OCI Block Volumes 
 OCI Block Volumes provide reliable, high perform
