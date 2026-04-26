# Deploy a migrated MongoDB workload to Oracle Autonomous Transaction Processing Serverless

- Source: https://docs.oracle.com/en/solutions/mongodb-to-atp/index.html
- Date: 2025-06
- Type: reference-architecture
- Services: adb-s, compute
- Tags: database, migration, autonomous

## Summary (catalog)

MongoDB to ADB-S migration using Oracle Database API for MongoDB. Applications use MongoDB wire protocol against ADB-S JSON collections. No application code changes required for basic CRUD operations.

## Architecture (fetched from source)

Deploy a Migrated MongoDB Workload to Oracle Autonomous Transaction Processing Serverless 
 
 
 
 
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
 
 

 

 
 
 
Deploy a Migrated MongoDB Workload to Oracle Autonomous Transaction Processing Serverless

 

 

 
Migrate an existing workload that uses a document database, in this case MongoDB, to Oracle Autonomous Transaction Processing Serverless (ATP Serverless) database on Oracle Cloud
 Infrastructure (OCI) to modernize the development of your JSON-centric applications alongside other multi-model workloads.
 

 
Workloads and applications that use documents and document databases to evolve data schemas and applications are popular due to the flexibility they offer to developers. Schema flexibility, rapid development, and scalability enable accelerated prototyping of application features, easier application evolution, and the ability to build iteratively smaller applications and features that developers can scale to address a large user base. However, these types of workloads have their challenges, including weaker transactional guarantees, data query versatility, and the inability to support other workloads on documents, such as analytics or machine learning.

 
What if these workloads can benefit from the advantages of traditional document databases and leverage the benefits of relational databases? For instance, have stronger transactional guarantees and added functionality such as analytics and machine learning, without the need to replicate data to another database or system. 

 
Autonomous Transaction Processing Serverless is a fully automated database service optimized to run transactional, analytical, and batch workloads concurrently. To accelerate performance, it’s preconfigured for row format, indexes, and data caching while providing scalability, availability, transparent security, and real-time operational analytics. Application developers and DBAs can rapidly and cost-effectively develop and deploy applications without sacrificing functionality or atomicity, consistency, isolation, and durability (ACID) properties.

 

 
 
Functional Architecture

 

 
 This reference architecture assumes that you have a workload with an application and a MongoDB database, either on-premises or in the cloud, and will migrate to OCI. It describes the future state architecture, its benefits, how you can deploy it and what additional features you can use to augment the existing workload.
 

 
This reference architecture focuses on the deployment of the migrated workload and not on the migration process itself. For more details on the migration process, see the Explore More section.
 

 
One of the key products used in this architecture is Oracle Database API for MongoDB, which enables applications to interact with collections of JSON documents in Oracle Database using MongoDB drivers, tools, and SDKs. This enables existing application code to work with data stored in Autonomous Transaction Processing Serverless (ATP Serverless) without the need to refactor the code.

 
The following diagram depicts a typical application composed of a database, back-end and front-end tiers.

 
 Description of the illustration mongodb-atp-s-logical-arch-migration.png 

 mongodb-atp-s-logical-arch-migration-oracle.zip 

 
The MEAN stack is a popular stack used to implement this pattern:
 
 
- MongoDB: Document database 
 
- Express: Back-end framework 
 
- Angular: Front-end framework 
 
- Node.js : Back-end server
 
 
 

 
This example uses a MEAN stack to migrate an existing deployment to OCI and ATP Serverless.

 
The migration of this workload to OCI and ATP Serverless is straightforward and consists, at high level, of the following steps:

 
 
- Deploy an ATP Serverless instance, enabling at creation time the Oracle Database Mongo DB API. 
 
- Migrate metadata and data from MongoDB to ATP Serverless. 
 
- Deploy application servers to run Node.js and Express using either VMs, containers, or Kubernetes, to the same region and availability domain as ATP Serverless.
 
 
- Deploy the back-end application code to the application servers. 
 
- Connect the back-end application to ATP Serverless using the same MongoDB tools and drivers used on the current application. 
 
- Connect users to the new application URI. 
 
 
After the workload is migrated to ATP Serverless, several features are available to augment the existing functionality, whether that is to 1) support additional nonfunctional requirements such as easily improve scalability, resiliency or high availability or 2) have additional functional features such as operational reporting, analytics and machine learning in place, without the need to copy data out of the database.

 
To improve scalability and high availability, use the Autonomous Transaction Processing Serverless auto scaling feature. With a single click or API call, it allows the workload to use up to 3 times the baseline capacity without any downtime. Note that Autonomous Transaction Processing Serverless uses Oracle Real Application Clusters (Oracle RAC) technology for high availability. For the backend tier, use compute instance pools with auto scaling rules to enable application high availability and scalability.

 
Since Autonomous Transaction Processing Serverless is built on top of multi-model, multi-workload database technology, you can add features that rely on relational, spatial, graph or vector data types that work alongside the existing application.

 

 

 
 
Physical Architecture

 

 
The physical architecture includes public and private subnets in OCI with a secondary backup region to support high availability.

 
The architecture supports the following:

 
 
- Front-end tier 
 
- Application users can connect from the internet or the corporate network. 
 
- User connection is secured using an OCI Web Application Firewall. 
 
- User connection to the application is load balanced for increased resiliency and scalability. 
 
- Load balancer is deployed with high availability. 
 
 
 
- Back-end tier 
 
- Application servers are deployed in a high availability fashion using an instance pool. 
 
- Instance Pool is used with auto scaling to achieve horizontal scalability. 
 
- Instance Pool is configured to deploy instances in the same Availability Domain as ATP Serverless, to have application and database colocation, hence optimizing connection latency. 
 
- Instance Pool is configured to distribute instances across fault domains in the same availability domain where ATP Serverless is placed, to increase workload resiliency. 
 
 
 
- Database tier 
 
- ATP Serverless provides high availability as Oracle Real Application Clusters (Oracle RAC) and several database nodes underpin the service instance. Therefore, by default the database tier is highly available and resilient. 
 
- Oracle Database API for MongoDB enabled in ATP Serverless enables you to use existing application code without changes. 
 
- The Oracle Database API for MongoDB is highly resilient, and that resiliency is guaranteed internally by ATP Serverless. 
 
- ATP Serverless can use auto scaling, adjusting to increases and decreases of system load. 
 
- ATP Serverless business continuity is achieved with Oracle Autonomous Data Guard based cross-region disaster recovery.
 
 
- Cross-region Oracle Autonomous Data Guard Standby Recovery Time Objective (RTO) is fifteen minutes and Recovery Point Objective (RPO) is one minute.
 
 
 
 
- Disaster recovery 
 
- Two regions support cross-region disaster recovery for the entire cloud deployment. 
 
- The standby region supports a warm standby where cloud instances are predeployed to lower the total recovery time objective (RTO). 
 
- ATP Serverless in the primary region has a Oracle Autonomous Data Guard cross-region peer on the standby region
