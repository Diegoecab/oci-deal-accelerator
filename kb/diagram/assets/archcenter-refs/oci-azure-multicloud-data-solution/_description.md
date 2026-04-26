# Establish a multicloud data solution between OCI and Microsoft Azure

- Source: https://docs.oracle.com/en/solutions/oci-azure-multicloud-data-solution/index.html
- Date: 2024-08
- Type: reference-architecture
- Services: adb-s, azure, data-integration, object-storage
- Tags: data-platform, multicloud, azure

## Summary (catalog)

Cross-cloud data integration between OCI and Azure. OCI Data Integration for ETL between Azure Blob Storage and OCI Object Storage. ADB-S for analytics with data from both clouds.

## Architecture (fetched from source)

Architecture

 

 
This reference architecture illustrates an enterprise multicloud data
 pipeline that collects and formats data from various sources, transferring it to the
 enterprise data lake or data warehouse. It includes batch integration, data integration, and
 real-time integration scenarios.

 
 Oracle Interconnect for Microsoft Azure links Azure ExpressRoute and Oracle Cloud
 Infrastructure FastConnect to connect two separate cloud networks efficiently.
 

 
 Azure 's Virtual Network (VNet) traffic routes through a private interconnection to OCI's
 virtual cloud network (VCN).
 

 
The following diagram illustrates this reference architecture.

 
 Description of the illustration oci-azure-multicloud-data-solution-diagram.png 

 oci-azure-multicloud-data-solution-diagram-oracle.zip 

 
 OCI Data Integration connects, and extracts data from, on-premises and cloud sources using native
 adapters, accesses Oracle SaaS applications using BICC connector, conducts
 transformations on the data, and loads it into an OCI data lake through adapters ( Oracle Autonomous Database or OCI Object Storage ).
 

 
Oracle application integration services collect real-time data from diverse
 source systems such as Oracle SaaS applications, internet-of-things (IoT), streaming
 services, social media, on-premises systems, and other cloud providers via native
 adapters. It then executes transformation and orchestration processes before loading the
 data into an OCI data lake using adapters ( Oracle Autonomous Database or OCI Object Storage ).
 

 
 OCI GoldenGate captures data from Oracle Autonomous Database and replicates it to Azure Data Lake Gen2 and Azure Synapse Analytics in near real-time via OCI FastConnect . The replication to Synapse involves staging and merging the change data in
 micro-batches in Azure Data Lake Storage Gen2 before merging it into the Synapse target table.
 

 
 Flow of events 

 
 
- Data extraction and transfer 
 
- Customer data is transferred from the data source to OCI Object Storage either directly or via default, source-specific drivers.
 
 
- On-premises flat files are moved to OCI Object Storage using the customer's Python script or by establishing an FTP connection
 with OCI Object Storage for seamless connectivity to Oracle Integration Cloud
 Service .
 
 
- Data is securely uploaded in its raw form to OCI Object Storage buckets with encryption.
 
 
 
 
- Data ingestion and transformation 
 
- OCI Data Integration retrieves data from OCI Object Storage and other sources, transforms it according to business needs using Apache Spark and a proposed architecture flow, then stores the transformed data back
 into OCI Object Storage alongside the autonomous database.
 
 
- This process follows the Delta Lake architecture for active ACID
 properties and compression. The data is now structured, can be queried, and
 is ready for further analytics. 
 
- OCI Logging manages all processing logs.
 
 
 
 
- Orchestration and scheduling 
 
- OCI Data Integration manages data flow processes, scheduling the execution of Data Flow applications and Data
 Science notebooks as necessary.
 
 
- Developers can run Data Flow applications from the UI or Data
 Science service notebooks for flexibility.
 
 
 
 
- Data archival 
 
- OCI Object Storage lifecycle policies, which are defined and implemented by customers, play
 a crucial role in automating the process of data archival. These policies
 facilitate the seamless shifting of data to more cost-effective storage
 tiers or the systematic deletion of outdated information, all in accordance
 with predefined rules and guidelines. This automation is essential for
 ensuring not only efficient data management but also compliance with various
 retention policies that organizations must adhere to.
 
 
- By utilizing these lifecycle policies, customers can optimize
 their storage costs while maintaining control over their data retention
 practices and ensuring that they are aligned with legal and regulatory
 requirements. 
 
 
 
- Data replication to Azure 
 
- OCI GoldenGate is used for data replication to Azure via a dedicated network established with Oracle Interconnect for Microsoft Azure .
 
 
- OCI GoldenGate integrates closely with Azure Data Lake and Azure Synapse Analytics for seamless data loading.
 
 
 
 
- Data analysis and reporting 
 
- Oracle
 Analytics Cloud and Power BI are examples of business intelligence tools that can
 establish a connection with OCI Object Storage or Oracle Autonomous Database .
 
 
- These tools gather the data that has been transformed and
 produce user-friendly dashboards showcasing key business key performance
 indicators (KPIs). 
 
- Through these dashboards, valuable insights can be obtained from
 the data, facilitating well-informed decision-making. 
 
 
 
 
The architecture has the following components:

 
 
- Tenancy 
A tenancy is a
 secure and isolated partition that Oracle sets up
 within Oracle Cloud when you sign up for Oracle Cloud
 Infrastructure . You can create, organize, and administer your
 resources in Oracle Cloud within your tenancy. A
 tenancy is synonymous with a company or
 organization. Usually, a company will have a
 single tenancy and reflect its organizational
 structure within that tenancy. A single tenancy is
 usually associated with a single subscription, and
 a single subscription usually only has one
 tenancy.
 

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that
 contains one or more data centers, called
 availability domains. Regions are independent of
 other regions, and vast distances can separate
 them (across countries or even
 continents).
 

 
 
- Compartment 
Compartments
 are cross-region logical partitions within an Oracle Cloud
 Infrastructure tenancy. Use compartments to organize your
 resources in Oracle Cloud , control access to the resources, and set usage
 quotas. To control access to the resources in a
 given compartment, you define policies that
 specify who can access the resources and what
 actions they can perform.
 

 
 
- Availability domains 
Availability domains
 are standalone, independent data centers within a
 region. The physical resources in each
 availability domain are isolated from the
 resources in the other availability domains, which
 provides fault tolerance. Availability domains
 don’t share infrastructure such as power or
 cooling, or the internal availability domain
 network. So, a failure at one availability domain
 shouldn't affect the other availability domains in
 the region.

 
 
- Virtual cloud network (VCN) and subnets 
A VCN is a customizable,
 software-defined network that you set up in an Oracle Cloud
 Infrastructure region. Like traditional data center networks,
 VCNs give you control over your network
 environment. A VCN can have multiple
 non-overlapping CIDR blocks that you can change
 after you create the VCN. You can segment a VCN
 into subnets, which can be scoped to a region or
 to an availability domain. Each subnet consists of
 a contiguous range of addresses that don't overlap
 with the other subnets in the VCN. You can change
 the size of a subnet after creation. A subnet can
 be public or private. 
 

 
 
- ExpressRoute 
 Azure ExpressRoute lets you set up a private connection between a VNet and another network, such
 as your on-premises network or a network in another cloud provider.
 

 
 Azure ExpressRoute is a more reliable and faster alternative to typical internet connections
 because the traffic over Azure ExpressRoute does not traverse the public internet.
 

 
 
- Autonomous
 Database 

 Oracle Autonomous Database is a fully managed, preconfigured database
 environments that you can use for transaction
 processing and data warehousing workloads. You do
 not need to configure or manage any hardware, or
 install any software. Oracle Cloud
 Infrastructure handles creating the database, as well as
 backing up, patching, upgrading
