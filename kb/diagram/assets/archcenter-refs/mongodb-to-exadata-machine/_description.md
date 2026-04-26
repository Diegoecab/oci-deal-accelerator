# Deploy a migrated MongoDB workload to Oracle Exadata Database Machine

- Source: https://docs.oracle.com/en/solutions/mongodb-to-exadata-machine/index.html
- Date: 2025-06
- Type: reference-architecture
- Services: exacs
- Tags: database, migration

## Summary (catalog)

MongoDB to Exadata migration for high-performance workloads. Oracle Database API for MongoDB on Exadata infrastructure. Suitable when performance requirements exceed ADB-S capabilities.

## Architecture (fetched from source)

Deploy a Migrated MongoDB Workload to Oracle Exadata Database Machine 
 
 
 
 
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
 
 

 

 
 
 
Deploy a Migrated MongoDB Workload
 to Oracle Exadata Database Machine

 

 

 

 Migrate an existing workload that uses a document database, in this
 case MongoDB, to Oracle Database 23ai on Exadata infrastructure for simplified
 development of JSON-centric applications using a converged, multi-model
 database. 
 
 

 
Workloads and applications that use documents and document databases to evolve data
 schemas and applications are popular due to the flexibility they offer to developers.
 Schema flexibility, rapid development, and scalability enable accelerated prototyping of
 application features, easier application evolution, and the ability to build iteratively
 smaller applications and features that developers can scale to address a large user
 base. However, these types of workloads have their challenges, including weaker
 transactional guarantees, data query versatility, and the inability to support other
 workloads on documents, such as analytics or machine learning. 

 
What if these workloads can benefit from the advantages of traditional document databases
 and leverage the benefits of relational databases? For instance, have stronger
 transactional guarantees and added functionality such as analytics and machine learning,
 without the need to replicate data to another database or system.

 
Oracle Database 23ai, designed to simplify development for AI, microservices, graph,
 document, spatial, and relational applications, is a converged database platform
 offering everything that is needed in one powerful solution.

 
Oracle Exadata Database Machine is engineered to be the highest performing
 and most available platform for running Oracle Database. Exadata runs all types of
 database workloads including online transaction processing (OLTP), data warehousing (DW)
 and consolidation of mixed workloads. Simple and fast to implement, Exadata is designed
 to power and protect your most important databases and is an ideal foundation for
 Database as a Service.

 

 
 
Functional Architecture

 

 
 This reference architecture assumes a workload
 composed of an application and MongoDB database exists on-premises and will be migrated to use Oracle Database 23ai as the database. It describes the future state architecture, its
 benefits, how it can be deployed, and what additional features can be used to augment the
 existing workload.
 

 
This reference architecture focuses on deploying the migrated workload, and
 not the migration process. To learn more about the migration process, see the Explore
 More section.
 

 
One of the key features used in this architecture is the Oracle Database API for MongoDB , which lets applications interact with collections of JSON documents in Oracle Database using MongoDB commands. This enables existing application code to work with data stored in Oracle Database 23ai, without the need to refactor code.
 

 
The following diagram illustrates a typical application composed of a
 database, back-end tier, and front-end tier.

 
 Description of the illustration mongodb-logical-arch-migration.png 

 mongodb-logical-arch-migration.zip 

 
A popular stack used to implement this pattern is the MEAN stack:

 
 
- MongoDB : Document database
 
 
- Express: Back-end framework 
 
- Angular: Front-end framework 
 
- Node.js: Back-end server 
 
 
This architecture uses a MEAN stack as an example of an existing deployment
 to migrate to Oracle Database 23ai. The migration of this workload to Oracle Database 23ai consists of the following high-level steps:
 

 
 
- Deploy a highly available Oracle Database 23ai instance in Exadata across several database nodes, using Oracle Real Application Clusters (Oracle
 RAC) .
 
 
- Migrate metadata and data from MongoDB to Oracle Database 23ai.
 
 
- Install and configure the back-end tier compute, whether that is VMs,
 containers, or Oracle REST Data Services. 
 
- Configure Oracle REST Data Services to enable the MongoDB API so the application can communicate with the database using MongoDB drivers.
 
 
- Configure the application to use the new database connection
 string. 
 
- Connect the backend application to Oracle Database 23ai using the same MongoDB tools and drivers used on the current application.
 
 
 
After migrating the workload to Oracle Database , you can enhance functionality by enabling additional features - such as improved
 security, operational reporting, analytics, and machine learning - without copying data
 out of the database. Oracle Database 23ai is a multi-model, multi-workload platform, which enables you to seamlessly
 integrate features that utilize relational, spatial, graph, or vector data types
 alongside your existing application.
 

 
To improve workload scalability, allocate more compute and memory to the
 database. Since Oracle Database 23ai is a multi-model, multi-workload database technology, additional features that
 rely on relational, spatial, graph, or vector data types can be added, working alongside
 the existing application.
 

 

 

 
 
Physical Architecture

 

 

 The physical architecture for this migrated workload to Oracle Database 23ai supports the following: 
 
 

 
 Front-end tier 

 
 
- The current deployment is used. 
 
- Users can connect from the internet or the corporate network. 
 
- DNS capability is configured to route requests to the standby data
 center in the event of failover. 
 
 
 Back-end tier 

 
 
- Existing applications are deployed and used with the same compute
 instances. 
 
- Customer-managed Oracle REST Data Services are colocated and deployed on
 the application servers. The application code can connect to Oracle Database 23ai through Oracle REST Data Services.
 
 
- Back-end tier scalability is achieved using the current scalability
 mechanism in place, implicitly scaling Oracle REST Data Services installed in each
 application server. 
 
 
 Database tier 

 
 
- Oracle Database 23ai is deployed in Exadata, and is used to store and serve JSON documents to the
 back-end tier.
 
 
- The Oracle Database API for MongoDB is enabled using Oracle REST Data Services, which allows existing
 application code to be used without changes to code.
 
 
 
 Business continuity 

 
 
- Achieved using an Oracle Data Guard disaster recovery strategy.
 
 
- A warm disaster recovery strategy is assumed, with the back-end tier
 and associated resources already deployed and running. 
 
 
The following diagram illustrates this reference architecture.

 
 Description of the illustration mongodb-exadata-machine-physical-arch.png 

 mongodb-exadata-machine-physical-arch.zip 

 
The design for the physical architecture:

 
 Business continuity 

 
 
- There are two data centers with identical deployments: one active, the
 other on standby. 
 
- DNS traffic steering directs user requests to the active data center. If the DNS
 health check probes executed on the application tier recurrently fail, DNS is
 reconfigured to route traffic to the standby data center workload. 
 
- A load balancer distributes incoming requests across multiple back-end
 tier VMs, preventing a single point of failure. 
 
- The back-end tier has several VMs handling user requests. 
 
- Customer-managed Oracle REST Data Services is deployed and configured on the
 back-end tier VMs. As you add VMs, both the application server and Oracle REST Data
 Services scale automatically. 
 
- The recovery time objective (RTO) is dependent not only on the database
 failover, but on complete failover to the rest of the workload components in the
 standby data center. 
 
- Database RTO and RPO (recovery point objective) depend on the
 configured Oracle Data Guard protection mode.
 
 
- Databa
