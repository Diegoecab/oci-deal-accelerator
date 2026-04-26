# Deploy a migrated MongoDB workload to Oracle Autonomous JSON Database

- Source: https://docs.oracle.com/en/solutions/mongodb-to-auto-json-db/index.html
- Date: 2025-06
- Type: reference-architecture
- Services: adb-s
- Tags: database, migration, autonomous

## Summary (catalog)

MongoDB to Autonomous JSON Database migration. JSON-centric workloads with document model support. SODA API and MongoDB API for application compatibility.

## Architecture (fetched from source)

Deploy a Migrated MongoDB Workload to Oracle Autonomous JSON Database 
 
 
 
 
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
 
 

 

 
 
 
Deploy a Migrated MongoDB Workload to Oracle Autonomous JSON Database 

 

 

 
Migrate an existing workload that uses a document database, in this case MongoDB, to Oracle Autonomous JSON Database on Oracle Cloud
 Infrastructure (OCI) to modernize the development of your JSON-centric applications.
 

 
Workloads and applications that use documents and document databases to evolve data schemas and applications are quite popular due to the flexibility they offer to developers. Schema flexibility, rapid development, and scalability enable rapid prototyping of application features, easier application evolution, and the assurance of building iteratively smaller applications and features that developers can scale to address a large user base. However, these types of workloads have their challenges, including weaker transactional guarantees, data query versatility, and the inability to support other workloads on documents, such as analytics or machine learning.

 
What if these workloads could benefit from all the advantages of traditional document databases, but at the same time, leverage the benefits of relational databases? For instance, have stronger transactional guarantees and use additional functionality such as analytics and machine learning, without the need to replicate data to another database or system. 

 
 Autonomous JSON Database features NoSQL-style document APIs (Simple Oracle Document Access (SODA) and Oracle Database API for MongoDB), serverless scaling, high performance ACID transactions, comprehensive security, and low pay-per-use pricing. Autonomous JSON Database automates provisioning, configuring, tuning, scaling, patching, encrypting, and repairing of databases, eliminating database management and delivering 99.95% availability.
 

 

 
 
Functional Architecture

 

 
 This architecture assumes, as a starting point, that a workload with an application and a MongoDB database exists, either an on premises or cloud deployment, and will be migrated to OCI. It describes the future state architecture, its benefits, how it can be deployed and what additional features can be used to augment the existing workload.
 

 
One of the key features that are used in this architecture is Oracle Database API for MongoDB, which enables applications interact with collections of JSON documents in Oracle Database using MongoDB drivers, tools, and SDKs. Existing applications code can work with data stored in Autonomous JSON Database, without the need to refactor it.

 
The following diagram depicts a typical application composed of a database, back-end and front-end tier.

 
 Description of the illustration mongodb-json-logical-arch-migration.png 

 mongodb-json-logical-arch-migration-oracle.zip 

 
A popular stack, used to implement this pattern, is the MEAN stack, using MongoDB as the document database, Express as the back-end framework, Angular as the front-end framework and Node.js as the back-end server. This document uses a MEAN stack as an example of an existing deployment that will be migrated to OCI and Autonomous JSON Database .
 

 
The migration of this workload to OCI and Autonomous JSON Database is straightforward and consists, at high level, of the following steps:
 

 
 
- Deploy an Autonomous JSON Database instance, enabling at creation time the Oracle Database Mongo DB API
 
 
- Migrate metadata and data from MongoDB to Autonomous JSON Database .
 
 
- Deploy application servers to run Node.js and Express using either VMs, containers or Kubernetes, to the same region and availability domain as Autonomous JSON Database .
 
 
- Deploy the back-end application code to the application servers. 
 
- Connect the back-end application to Autonomous JSON Database using the same MongoDB tools and drivers used on the current application.
 
 
- Have users connecting to the new application URI. 
 
 
Note this reference architecture focuses on the deployment of the migrated workload and not on the migration process itself. For more details on the migration process please refer to the Explore More section.
 

 
After the workload is migrated to Autonomous JSON Database , you can use several features to augment the existing functionality, whether that is to 1) support additional nonfunctional requirements such as easily improve scalability, resiliency or high availability or 2) have additional functional features such as operational reporting, analytics and machine learning in place, without the need to copy data out of the database.
 

 
To improve scalability and high availability, use the Autonomous JSON Database auto scaling feature, that with a single click or API call, allows the workload to use up to 3 times the baseline capacity, without any downtime. Note that Autonomous JSON Database uses Oracle Real Application Clusters (Oracle RAC) technology for high availability. For the back-end tier, use compute instance pools, with auto scaling rules, thus enabling application high availability and scalability.
 

 
Since Autonomous JSON Database is built on top of a multimodel, multiworkload database technology, additional features that rely on relational, spatial, graph or vector data types can be added, working alongside the existing application. It is common that users want to perform analytics on top of JSON data, and using SQL in Autonomous JSON Database , simplifies creating operational and analytical reporting, using the same engine and data.
 

 
 Autonomous JSON Database has a limit of 20 Gb of non JSON data, but can easily be converted to Autonomous Transaction Processing Serverless, supporting the same features, if data volume requirements change. Do note that Views and Materialized Views storage doesn't count towards the Autonomous JSON Database 20 Gb non-JSON data limit, so those can be easily created and used, for instance, to support operational analytics using SQL on top of JSON documents.
 

 

 

 
 
Physical Architecture

 

 
The physical architecture includes public and private subnets in OCI with a secondary backup region to support high availability.

 
The architecture supports the following:

 
 
- Front-end tier 
 
- Application users can connect from the internet or the corporate network 
 
- User connection is secured using a Web Application Firewall 
 
- User connection to the application is load balanced for increased resiliency and scalability 
 
- Load balancer is deployed with high availability 
 
 
 
- Back-end tier 
 
- Application servers are deployed in a high availability fashion using an instance pool 
 
- Instance pool is used with auto scaling to achieve horizontal scalability 
 
- Instance Pool is configured to deploy instances in the same Availability Domain as the Autonomous JSON Database , to have application and database colocation, hence optimizing connection latency
 
 
- Instance Pool is configured to distribute instances across fault domains in the same availability domain where the Autonomous JSON Database is placed, to increase workload resiliency
 
 
 
 
- Database tier 
 
- Autonomous JSON Database provides high availability as Oracle Real Application Clusters (Oracle
 RAC) and several database nodes underpin the service instance. Therefore, by default the database tier is highly available and resilient.
 
 
- Oracle Database API for MongoDB enabled in Autonomous JSON Database allows you to use existing application code without changes.
 
 
- The Oracle Database API for MongoDB is highly resilient, and that resiliency is guaranteed internally by Autonomous JSON Database .
 
 
- Autonomous JSON Database can use auto scaling, adjusting to increases and decreases of system load.
 
 
- Autonomous JSON Database b
