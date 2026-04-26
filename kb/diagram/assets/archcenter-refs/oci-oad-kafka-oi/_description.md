# Stream Kafka topics to Oracle Autonomous Database using Oracle Integration 3

- Source: https://docs.oracle.com/en/solutions/oci-oad-kafka-oi/index.html
- Date: 2025-02
- Type: reference-architecture
- Services: adb-s, oic3, streaming
- Tags: database, integration, autonomous

## Summary (catalog)

Kafka to ADB-S streaming ingestion via OIC3. Oracle Integration adapter for Kafka topics with schema mapping to ADB-S tables. Near-real-time data pipeline for analytics workloads.

## Architecture (fetched from source)

Architecture

 

 
This architecture shows on-premises Kafka Streams, Oracle Integration 3, Oracle GoldenGate Stream Analytics and Oracle Autonomous Database in an OCI region.
 

 
Use this architecture to capture Kafka streaming messages from an
 on-premises Kafka stream or Oracle GoldenGate Stream Analytics into Oracle Autonomous Database using Oracle Integration 3.
 

 
The OCI region containing Oracle Integration 3 ingests data from the on-premises Kafka streams or Oracle GoldenGate Stream Analytics.
 

 
 Oracle Integration 3 stores the data in a relational table in Oracle Autonomous Database .
 

 
 Description of the illustration oci-oad-kafka-oi.png 

 oci-oad-kafka-oi-oracle.zip 

 
 This architecture supports the following components:

 
 
- Kafka Streams 
Kafka Streams is a client library for building applications and microservices, where the input and output data are stored in Kafka clusters. It combines the simplicity of writing and deploying standard Java and Scala applications on the client side with the benefits of Kafka's server-side cluster technology.

 
 
- Autonomous Database 
 Oracle Autonomous Database is a fully-managed, preconfigured database environment that you can use for transaction processing and data warehousing workloads. You do not need to configure or manage any hardware, or install any software. Oracle Cloud
 Infrastructure handles creating, backing up, patching, upgrading, and tuning the database.
 

 
 
- Oracle Integration 3 
Oracle Integration 3 is a fully managed, preconfigured
 environment that gives you the power to integrate your cloud and on-premises
 applications, automate business processes, develop visual applications, use an
 SFTP-compliant file server to store and retrieve files, and exchange business
 documents with a B2B trading partner.

 
 
- Oracle GoldenGate Stream Analytics 
GoldenGate Stream Analytics allows for
 the creation of custom operational dashboards that provide real-time monitoring
 and analyses of event streams in an Apache Spark-based system. It enables
 customers to identify events of interest in their Apache Spark-based system,
 execute queries against those event streams in real time and drive operational
 dashboards or raise alerts based on that analysis.

 
 
- Oracle SQL Developer 
 Oracle SQL Developer is a free, integrated development environment that simplifies the development
 and management of Oracle Database in both traditional and Cloud deployments. SQL
 Developer offers complete end-to-end development of your PL/SQL applications, a
 worksheet for running queries and scripts, a DBA console for managing the
 database, a reports interface, a complete data modeling solution, and a
 migration platform for moving your 3rd party databases to Oracle.
 

 
 
 

 

 
 
About Required Products and
 Roles

 

 
This solution requires the following products and roles:

 
 
- Oracle Autonomous Database 
 
- Oracle Integration 3
 
 
- Oracle Cloud
 Infrastructure 
 
- Oracle GoldenGate Stream Analytics
 
 
 
These are the roles needed for each service.

 

 
 
 
 Product Name: Role 
 Required to... 
 
 
 
 
 Oracle Autonomous Database : admin
 
 Create the credentials. 
 
 
 Oracle Integration 3: admin
 
 Create the credentials. 
 
 
 Oracle Cloud
 Infrastructure : admin
 
 Create and manage OCI resources. 
 
 
 Oracle GoldenGate Stream Analytics: admin
 
 Configure Kafka producer to ingest data. 
 
 
 
 

 
 
See Oracle Products, Solutions, and Services to get what you need.
 

 

 

 

 

 

 
 Title and Copyright Information 

 

 
Stream Kafka topics to Oracle Autonomous Database using Oracle Integration 3

 
G24768-01

 
February 2025

 
 Copyright © 2025, 

Oracle and/or its affiliates.
