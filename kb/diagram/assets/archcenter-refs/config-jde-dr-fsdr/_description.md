# Configure JD Edwards Disaster Recovery by using OCI Full Stack Disaster Recovery

- Source: https://docs.oracle.com/en/solutions/config-jde-dr-fsdr/index.html
- Date: 2025-07
- Type: reference-architecture
- Services: compute, fsdr, base-db
- Tags: ha-dr, application

## Summary (catalog)

JD Edwards DR with Full Stack DR service. Automated failover of application tier, batch servers, and database. Cross-region block volume replication for JDE binary and config files.

## Architecture (fetched from source)

About Configuring JD Edwards Disaster Recovery by Using OCI Full Stack Disaster Recovery 
 
 
 
 
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
 
 

 

 
 
 
About Configuring JD Edwards
 Disaster Recovery by Using OCI Full Stack Disaster Recovery

 

 

 
To ensure a robust, automated, and scalable disaster recovery (DR) strategy
 for your JD Edwards (JDE) application hosted on Oracle Cloud
 Infrastructure (OCI), use Oracle Cloud Infrastructure Full Stack Disaster Recovery (FSDR) service. FSDR ensures business continuity by orchestrating failover and
 failback processes across regions for both infrastructure and application
 components. 
 

 
This document describes the JD Edwards architecture, and provides
 the configuration and implementation procedures involved with setting up the
 DR environment using OCI FSDR, while accounting for necessary security,
 performance, and compliance requirements. 

 

 
 
JD Edwards Architecture

 

 
This illustration outlines the JD Edwards application's deployment
 architecture, featuring both primary and secondary regions.

 
 Description of the illustration jdr-dr-fsdr.png 

 jde-dr-fsdr-oracle.zip 
 
 

 

 
 
Primary Region

 

 
In the primary region, the JDE environment is deployed within a Virtual
 Cloud Network (VCN) that is segmented into three dedicated subnets, which are
 segregated by application resources functionality, as described below.

 
 
- Load balancer tier 
The load balancer tier hosts
 the OCI load balancer, which provides access to JDE web
 services for end users. 

 
 
- Application tier 
The application tier contains
 the core application components, including the enterprise
 server, the web server, and the Application Interface
 Services (AIS) server 

 
 
- Management tier 
The management tier includes
 tools and services for JDE management and administration,
 such as the deployment server and the Server Manager Console
 server 

 
 
- Database tier 
In the database layer, the JDE
 database is deployed on Autonomous Transaction
 Processing –Shared (ATP-S). Application servers connect to the database using endpoints.
 Oracle Autonomous Data Guard is enabled, creating a standby database in the secondary region and ensuring
 real-time data replication for high availability and disaster recovery.
 

 
 
- Storage and data protection 
The block volume
 groups used by compute instances are protected by
 cross-region volume group replication, with the secondary
 region configured as the replication target. 

 
 
 

 

 
 
Secondary Region

 

 
The secondary region serves as the disaster recovery site and mirrors
 critical components from the primary region.It contains:

 
 
- A replicated VCN structure that matches the primary region’s network layout. 
 
- A replica load balancer to ensure continuity of access during failover. 
 
- A standby ATP-S database that is kept in sync with the primary by using Autonomous
 Data Guard. 
 
- Replicas of volume groups, which ensures data availability in the event of a primary
 region failure. 
 
 

 

 

 
 
Understand JD Edwards
 Configuration-related Files

 

 
 JDE relies on multiple configuration
 files to manage connectivity between its components and other participating tiers, such as
 databases and authentication services. These files play a critical role in
 defining connection parameters, runtime settings, and integration behavior. Having a proper
 understanding of these files and its contents is essential while configuring Disaster Recovery
 (DR) scenario to ensure seamless application functionality.
 

 
Below is a summary of key configuration files: 
 
 
 sqlnet.ora 
 
 
 
 
 
 Purpose: Stores Oracle Wallet
 configuration used by the application to securely
 connect to the database. 
 

 
 
 Location: JDE Enterprise/Batch servers.
 DR 
 

 
 
 Consideration: Ensure the wallet path
 points to the valid wallet location of the DR
 database. 
 

 
 
 File path: 
 Oracle_ClientHome /network/admin 

 
 
 
 
 tnsnames.ora 
 
 
 
 
 
 Purpose: Stores Net Service Names, which
 act as aliases for database network addresses. 
 

 
 
 Location: JDE Enterprise, Batch, and Web
 servers. 
 

 
 
 DR Consideration: Update with the
 correct network address (FQDN/IP) of the DR
 database. 
 

 
 
 File path on Enterprise/Batch Servers: 
 Oracle_ClientHome /network/admin
 

 
 
 File path on Web Servers: 
 SM_Agent_Home /SCFHA/Target/ Managed
 Instance /config 

 
 
 
 
 
 jde.ini 
 
 
 
 
 
 Purpose: Stores runtime configuration
 for the JDE application, including database
 connection details and security settings. 
 

 
 
 Location: JDE Enterprise and Batch
 servers. 
 

 
 
 DR Consideration: Update the DB
 SYSTEM SETTINGS section with the correct
 server name for the DR environment. 
 

 
 
 File path:
 JDE_HOME /e920/ini 
 
 

 
 
 
 
 
 jdbj.ini 
 
 
 
 
 
 Purpose: Contains JDBj driver settings
 and database connection parameters for JDE
 applications. 
 

 
 
 Location: JDE Web and AIS servers. 
 

 
 
 DR Consideration: Ensure the correct
 server name is specified in the
 JDBj-BOOTSTRAP DATA SOURCE 
 section. 
 

 
 
 File path: 
 SM_Agent_Home /SCFHA/Target/ Managed
 Instance/ config 

 
 
 
 
 
 jas.ini 
 
 
 
 
 
 Purpose: Stores configuration for the
 HTML Server component of EnterpriseOne web
 clients. 
 

 
 
 Location: JDE Web servers. 
 

 
 
 DR Consideration: Update the
 following:
 
 
- FORMSERVICE section with the
 correct AIS host and port. 
 
 
- Security section
 with the appropriate OracleAccessSSOSignOffURL if SSO is
 enabled.
 
 
 File path: 
 SM_Agent_Home /SCFHA/Target/ Managed
 Instance /config 

 
 
 
 
 rest.ini 
 
 
 
 Purpose: Holds configuration for the AIS
 Server, including REST API paths, authentication
 settings, and JAS server links. 
 

 
 
 Location: JDE AIS servers. 
 

 
 
 DR Consideration: Update the
 following:
 
 
- BASIC CONFIG section with the
 correct JAS host and port. 
 
 
- Security section
 with the updated IDCSSSOSignOffURL if SSO is enabled. 
 
 
 File path: 
 SM_Agent_Home /SCFHA/Target/ Managed
 Instance /config 

 
 
 
 
 management-console.xml 
 
 
 
 Purpose: This XML file has information
 about the different servers, their configurations,
 and user access permissions. 
 

 
 
 Location: Server Manager Server 
 

 
 
 DR Consideration: Ensure
 the correct hostname is specified in the management-console.xml 
 
 

 
 
 File path: 
 SM_Console_Home /SCFMC/targets/home 

 
 
 
 
 agent. properties 
 
 
 
 Purpose: Configuration file that has
 settings for the Management Agent, a component
 that interacts with the Management Console and
 manages EnterpriseOne servers 
 

 
 
 Location: Server Manager Server 
 

 
 
 DR Consideration: Ensure the correct
 server name is specified in the
 agent.properties section.
 

 
 
 File path:
 SM_Console_Home /
 SCFMC/config 

 
 
 
 
 Additional System-Level Updates 
 
 
 
In addition to application configuration files,
 the following system files should also be reviewed
 and updated during a DR implementation: 
 
 
- Linux hosts and fstab files: Ensure
 valid IP addresses and FQDNs are defined. 
 
 
- Windows hosts file: Update with current
 IP and FQDN mappings as required. 
 
 
- WebLogic wallet files: Must be updated
 to reflect DR-specific database wallet to ensure
 connectivity if database is Autonomous. 
 
 Properly maintaining and updating these
 configuration files ensures that JDE continues to
 function correctly in a Disaster Recovery
 environment, minimizing downtime and maintaining
 secure, consistent application connectivity.
 

 
 
 
 
 

 

 

 
 
Understand Full Stack Disaster
 Recovery Concepts

 

 
When configuring and implementing FSDR, you will need to understand the
 following concepts and terminologies.

 
 
- 
 DR Protection Group 
 
 
 
- Definition: A DR
 protection group inclu
