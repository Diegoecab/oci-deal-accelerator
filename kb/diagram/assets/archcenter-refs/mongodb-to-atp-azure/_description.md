# Deploy a migrated MongoDB workload to Oracle Autonomous Transaction Processing Serverless@Azure

- Source: https://docs.oracle.com/en/solutions/mongodb-to-atp-azure/index.html
- Date: 2025-08
- Type: reference-architecture
- Services: adb-s, azure
- Tags: database, migration, multicloud, azure, autonomous

## Summary (catalog)

MongoDB to ADB-S migration on Database@Azure. Uses Oracle Database API for MongoDB for wire protocol compatibility. Applications connect via Azure VNet peering to ADB-S private endpoint.

## Architecture (fetched from source)

Deploy a Migrated MongoDB Workload to Oracle Autonomous Transaction Processing Serverless@Azure 
 
 
 
 
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
 
 

 

 
 
 
Deploy a Migrated MongoDB Workload to Oracle Autonomous Transaction
 Processing Serverless@ Azure 

 

 

 

 Migrate an existing workload that uses a document database,
 in this case MongoDB , to Microsoft Azure and Oracle Autonomous Transaction
 Processing Serverless deployed in Azure , a cloud document database service that makes it simple to modernize the
 development of your JSON-centric applications alongside other multi-model
 workloads. 
 
 

 
Workloads and applications that use documents and document databases to evolve
 data schemas and applications are popular due to the flexibility they offer
 to developers. Schema flexibility, rapid development, and scalability enable
 accelerated prototyping of application features, easier application
 evolution, and the ability to build iteratively smaller applications and
 features that developers can scale to address a large user base. However,
 these types of workloads have their challenges, including weaker
 transactional guarantees, data query versatility, and the inability to
 support other workloads on documents, such as analytics or machine
 learning.

 
What if these workloads can benefit from the advantages of traditional document
 databases and leverage the benefits of relational databases? For instance,
 have stronger transactional guarantees and added functionality such as
 analytics and machine learning, without the need to replicate data to
 another database or system.

 
 Autonomous Transaction
 Processing (ATP) Serverless is a fully automated database service optimized to run
 transactional, analytical, and batch workloads concurrently. To accelerate
 performance, it’s preconfigured for row format, indexes, and data caching
 while providing scalability, availability, transparent security, and
 real-time operational analytics. Application developers and DBAs can rapidly
 and cost-effectively develop and deploy applications without sacrificing
 functionality or atomicity, consistency, isolation, and durability (ACID)
 properties.
 

 

 
 
Functional Architecture

 

 
This architecture assumes, as a starting point, that a workload with an
 application and a MongoDB database exists, either an on-premises or cloud deployment, and
 will be migrated to Azure and Oracle Database@Azure . It describes the future state architecture, its benefits, how it can be deployed and
 what additional features you can use to augment the existing workload.
 

 
One of the key features used in this architecture is Oracle Database API for
 MongoDB , which enables applications to interact with collections of JSON documents in Oracle
 Database using MongoDB drivers, tools, and SDKs. Existing application code can work with data stored in Oracle Autonomous Transaction
 Processing Serverless, without the need to refactor code.
 

 
The following diagram depicts a typical application composed of a database, back-end, and
 front-end tiers.

 
 Description of the illustration mongodb-atp-s-azure-logical-arch-migration.png 

 mongodb-atp-s-azure-logical-arch-migration.zip 

 
The MEAN stack is a popular stack used to implement this pattern:

 
 
- MongoDB : Document database
 
 
- Express: Back-end framework 
 
- Angular: Front-end framework 
 
- Node.js : Back-end server
 
 
 
This document uses a MEAN stack as an example of an existing deployment that
 will be migrated to Azure and ATP Serverless.
 

 
The migration of this workload to Azure and ATP Serverless is straightforward and consists, at high level, of the following
 steps:
 

 
 
- Deploy an ATP Serverless instance, enabling at creation time the Oracle Database
 MongoDB API. 
 
- Migrate metadata and data from MongoDB to ATP Serverless.
 
 
- Deploy application servers to run Node.js and Express
 using either Azure App Service, VMs, containers, or Kubernetes , to the same region and availability domain as ATP Serverless.
 
 
- Deploy the back-end application code to the application servers. 
 
- Connect the back-end application to ATP Serverless using the same MongoDB tools and drivers used on the current application.
 
 
- Connect users to the new application URI. 
 
 
Note this reference architecture focuses on the deployment of the migrated
 workload and not on the migration process itself. For more details on the migration
 process, see the Explore More section.
 

 
After the workload is migrated to ATP Serverless, several features are
 available to augment the existing functionality, whether that is to 1) support
 additional nonfunctional requirements, such as easily improving scalability, resiliency,
 or high availability, or 2) have additional functional features such as operational
 reporting, analytics, and machine learning in place, without the need to copy data out
 of the database.

 
To improve scalability and high availability, use the Autonomous Transaction
 Processing Serverless auto scaling feature. With a single click or API call, it allows the
 workload to use up to 3 times the baseline capacity without any downtime. Note that Autonomous Transaction
 Processing Serverless uses Oracle Real Application Clusters (Oracle
 RAC) technology for high availability. For the backend tier, either use Azure VM Scale
 Sets with Autoscale setup, or a PaaS service such as App Service with Automatic Scaling
 setup to enable application high availability and scalability.
 

 
Since ATP Serverless is built on top of multi-model, multi-workload database technology,
 you can add features that rely on relational, spatial, graph or vector data types that
 work alongside the existing application.

 

 

 
 
Physical Architecture

 

 
The physical architecture includes Autonomous Transaction Processing
 Serverless deployed using delegated subnets in two Azure regions to support high
 availability. OCI services support automatic backup to Oracle Cloud
 Infrastructure Object Storage .
 

 
The architecture supports the following:

 
 
- Front-end tier 
 
- Application users can connect from the internet or the corporate
 network. 
 
- User connection is routed to the active region that is running
 the application, using Azure Front
 Door .
 
 
- User connection is secured using Azure Web Application Firewall.
 
 
- User connection to the application is load balanced using App
 Service. 
 
 
 
- Back-end tier 
 
- Application is deployed in a high availability fashion using Azure App Service.
 
 
- Azure App Service AutoScale is used to achieve horizontal scalability.
 
 
 
 
- Database tier 
 
- ATP Serverless provides high availability, as Oracle Real Application Clusters (Oracle
 RAC) and several database nodes underpin the service instance. Therefore, by
 default the database tier is highly available and resilient.
 
 
- Oracle Database API for MongoDB enabled in ATP Serverless allows
 you to use existing application code without changes. 
 
- The Oracle Database API for MongoDB is highly resilient, and
 that resiliency is guaranteed internally by ATP Serverless. 
 
- ATP Serverless can use auto scaling, adjusting to increases and
 decreases of system load. 
 
- ATP Serverless business continuity is achieved through
 cross-region Autonomous Data Guard. 
 
 
 
- Disaster Recovery 
 
- The second region is deployed with a similar topology to reduce
 the overall recovery time objective. 
 
- Use a warm DR strategy to reduce the overall RTO. In a warm DR
 strategy, the back-end tier cloud resources are already provisioned
 alongside the ATP Serverless standby database. 
 
- Alternatively you can provision the back-end tier resources in
 the event of a failure, decreasing the cost of running the DR resources but
 increasing the overall RTO. 
 
 
 
