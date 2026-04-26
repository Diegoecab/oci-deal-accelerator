# Replicate Oracle Fusion SaaS data to a third-party data warehouse

- Source: https://docs.oracle.com/en/solutions/rep-fusion-saas-third-party-dw/index.html
- Date: 2024-05
- Type: reference-architecture
- Services: oic, data-integration
- Tags: data-platform, integration

## Summary (catalog)

Fusion SaaS data replication to third-party data warehouses (Snowflake, Databricks, BigQuery). OIC for extraction, OCI Data Integration for transformation and loading to target platforms.

## Architecture (fetched from source)

Architecture

 

 
This architecture shows how to replicate data from Oracle Fusion SaaS
 applications to such third-party data warehouses as Snowflake Data Cloud, Azure
 ADLS, or AWS Redshift.

 
The following diagram illustrates this reference architecture.

 

 
 
 Description of the illustration fusion-saas-snowflake-arch.png 

 
 

 

 fusion-saas-snowflake-arch-oracle.zip 
 
 

 
The architecture has the following components:

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that contains one or more data centers, called availability domains. Regions are independent of other regions, and vast distances can separate them (across countries or even continents).
 

 
 
- Virtual cloud network (VCN) and subnets 
A VCN is a
 customizable, software-defined network that you set up in an
 OCI region. Like traditional data center networks, VCNs give
 you complete control over your network environment. A VCN
 can have multiple non-overlapping CIDR blocks that you can
 change after you create the VCN. You can segment a VCN into
 subnets, which can be scoped to a region or to an
 availability domain. Each subnet consists of a contiguous
 range of addresses that don't overlap with the other subnets
 in the VCN. You can change the size of a subnet after
 creation. A subnet can be public or private.In this
 architecture, the autonomous database and a function to set
 up the database are attached to a private subnet. The
 compute instance that hosts the web server and the functions
 that process the streams are deployed in a public
 subnet.

 
 
- Dynamic routing gateway (DRG) 
The DRG is a virtual
 router that provides a path for private network traffic
 between VCNs in the same region, between a VCN and a network
 outside the region, such as a VCN in another OCI region, an
 on-premises network, or a network in another cloud
 provider.

 
 
- Autonomous database 
Oracle Autonomous Data
 Warehouse is a self-driving, self-securing, self-repairing
 database service that is optimized for data warehousing
 workloads. You do not need to configure or manage any
 hardware or install any software. OCI handles creating the
 database, as well as backing up, patching, upgrading, and
 tuning the database.

 
Oracle Autonomous
 Transaction Processing is a self-driving, self-securing,
 self-repairing database service optimized for transaction
 processing workloads. You do not need to configure or manage
 any hardware or install any software. OCI handles creating
 the database, as well as backing up, patching, upgrading,
 and tuning the database.

 
 
- Oracle GoldenGate 
 Oracle GoldenGate is a fully managed service that allows data ingestion
 from sources residing on premises or in any cloud,
 leveraging the GoldenGate CDC technology for a non-intrusive
 and efficient capture of data and delivery to Autonomous Data
 Warehouse in real time and at scale in order to make relevant
 information available to consumers as quickly as
 possible.
 

 
 
- OCI Data Integration 
 
 
Data Integration is a fully managed, multi-tenant
 service that helps data engineers and developers with data
 movement and data loading tasks. Powered by Spark ETL or ELT
 processes, a large volume of data can be ingested from a
 variety of data assets; cleansed; transformed and reshaped;
 and efficiently loaded to OCI target data assets.

 
 
- Oracle Business Intelligence Cloud Connector (BICC) 
Oracle Business
 Intelligence Cloud Connector (BICC) is used to extract business intelligence and
 other Fusion data in bulk and load it into designated external storage
 areas.

 
 
 

 

 
 
Recommendations

 

 
 Use the following recommendation as a starting point
 to replicating Oracle Fusion SaaS data on a third-party data warehouse. 
 These recommendations are useful when sizing your VCN; be aware that your requirements might
 differ from the architecture described here. 
 

 
 
- When you create a VCN, determine the number of CIDR blocks required and
 the size of each block based on the number of resources that you plan to attach to
 subnets in the VCN. Use CIDR blocks that are within the standard private IP address
 space. 
 
- Select CIDR blocks that don't overlap with any other network (for
 example, in Oracle Cloud Infrastructure, your on-premises data center, or another
 cloud provider) to which you intend to set up private connections. After you create
 a VCN, you can change, add, and remove its CIDR blocks. 
 
 

 

 
 
Considerations

 

 
When implementing this architecture, consider your requirements for the
 following parameters:

 
 
- Service limits 
When designing your architecture,
 consider the service limits for the compute instance, block
 storage, file storage, and autonomous database. See the
 Service Limits documentation listed in "Explore More",
 below.

 
 
- Database scalability 
You can manually scale the
 number of CPU cores of the database and Oracle GoldenGate up or down at any time. The autoscaling feature of
 autonomous databases and Oracle GoldenGate allows your database to use up to three times the current
 base number of CPU cores at any time. As demand increases,
 autoscaling automatically increases the number of cores in
 use. Autonomous databases allow you to scale the storage
 capacity at any time without affecting availability or
 performance.
 

 
 
- Application availability 
Fault domains provide the best resilience within
 an availability domain. If you need higher availability, consider using multiple
 availability domains or multiple regions where feasible.

 
 
- Backups 
 
- Database 
OCI automatically backs up
 autonomous databases and retains the backups for
 60 days. You can restore and recover your database
 to any point in time during the retention period.
 You can also create manual backups to supplement
 the automatic backups. Manual backups are stored
 in an OCI Object Storage bucket that you create and are retained for 60
 days.
 

 
 
- Application 
The OCI Block Volumes service lets you create point-in-time backups
 of data on a block volume. You can restore these
 backups to new volumes at any time. You can also
 use the service to make a point-in-time,
 crash-consistent backup of a boot volume without
 application interruption or downtime. Boot and
 block volumes have the same backup
 capabilities.
 

 
 
 
 
- Security: Access control 
Use policies to restrict who can access your
 resources in the cloud and the actions that they can perform.

 
 
 

 

 
 
Explore More

 

 
Learn more about using serverless functions for your workloads in the
 cloud.

 
Review these additional resources: 

 
 
- 
 
 
 Oracle
 Cloud Infrastructure GoldenGate 

 
 
 
- 
 
 
 Data
 Integration (oracle.com) 

 
 
 
- 
 
 
 Service Limits 

 
 
 
- 
 
 
 Oracle Cloud
 Infrastructure Documentation 

 
 
 
- 
 
 
 Oracle
 Cloud Cost Estimator 

 
 
 
- 
 
 
 Best practices framework for Oracle Cloud Infrastructure 

 
 
 
 

 

 
 
Acknowledgments

 

 
 Author : Sunil Vernekar 

 

 

 

 

 

 
 Title and Copyright Information 

 

 
Replicate Oracle Fusion SaaS data to a third-party data warehouse

 
F96187-02

 
May 2024

 
 Copyright © 2024, 

Oracle and/or its affiliates.
