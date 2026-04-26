# Deploy a Data Lake leveraging Power BI on Oracle Database@Azure

- Source: https://docs.oracle.com/en/solutions/analytics-pipeline-db-at-azure/index.html
- Date: 2025-02
- Type: reference-architecture
- Services: adb-s, azure, object-storage
- Tags: data-platform, multicloud, azure, autonomous

## Summary (catalog)

Analytics pipeline combining ADB-S on Database@Azure with Power BI. Data ingestion to Object Storage, transformation in ADB-S, visualization via Power BI DirectQuery or Import mode.

## Architecture (fetched from source)

Deploy a Data Lake Leveraging Power BI on Oracle Database@Azure 
 
 
 
 
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
 
 

 

 
 
 
- Deploy a Data Lake leveraging Power BI on Oracle Database@Azure 
 
- Deploy a Data Lake Leveraging
 Power BI on Oracle Database@Azure 
 
 
 
 
Deploy a Data Lake Leveraging
 Power BI on Oracle Database@Azure 

 
 

 

 
Many businesses leverage Microsoft Power BI with data lakes on Microsoft
 Azure to derive actionable business insights. 

 
You can expand these capabilities by using a medallion architecture
 that includes Azure Data Factory, Azure Data Lake Storage, Azure Compute,
 Oracle Database@Azure (either a fully managed Oracle Autonomous Database or a co-managed Oracle Exadata Database
 Service instance), and Power BI to address several key data challenges faced by
 customers:
 

 
 
- Data Silos and Integration : Azure Data Factory ingests data from
 diverse sources into a unified data lake, breaking down silos and
 providing a single source of truth.
 
 
- Data Quality and Consistency : Autonomous Data
 Warehouse in the Curation Layer ensures clean, consistent, and high-quality
 data through deduplication and quality rules, reducing errors and
 enhancing decision-making.
 
 
- Scalability and Performance : Azure's scalable
 compute resources and Autonomous Data
 Warehouse 's serverless architecture or Oracle Exadata Database
 Service handle large-scale data processing efficiently, while maintaining
 optimal performance as data volumes and user adoption (concurrency)
 grow.
 
 
- Complex Transformations : Azure Compute and Autonomous Data
 Warehouse or Oracle Exadata Database
 Service perform complex transformations and analytics efficiently,
 reducing processing time and focusing on insights.
 
 
- Cost Management : The serverless and pay-as-you-go
 models for Azure services and Autonomous Data
 Warehouse or Oracle Exadata Database
 Service optimize costs, ensuring that you only pay for what you use.
 
 
- Data Governance and Compliance : Structured data management layers
 facilitate better governance, traceability, and regulatory
 compliance.
 
 
- Built-in Analytics : Users are able to apply analytics
 directly to their data by using built-in features such as artificial
 intelligence (AI), machine learning (ML), graph, spatial, and text
 analytics.
 
 
 
 Typical use cases include:

 
 
- Retail Analytics : Integrates data from online sales, in-store
 transactions, and customer feedback, optimizing inventory and
 marketing strategies.
 
 
- Financial Services : Analyzes transaction data for fraud detection
 and regulatory compliance, mitigating risks.
 
 
- Healthcare Analytics : Integrates patient data from EHRs, lab
 results, and wearable devices, improving patient care and health
 management.
 
 
 
This architecture enables enterprise customers across industries to
 leverage data effectively to empower their business users to make informed
 decisions to drive better business outcomes.

 

 
 
Logical Architecture

 

 
 The analytical data lake can ingest data from multiple sources and can
 provide business insights by using Power BI running on Microsoft Azure.

 
 
- Data Sources: The analytical data lake can ingest data from multiple
 sources. Azure Data Factory can ingest data from Microsoft SQL Server and Azure Blob
 Storage. Oracle Database@Azure can ingest data from Oracle Cloud
 ERP , Oracle Cloud
 Infrastructure Object Storage , Azure Cosmos Database, Azure SQL Database, various types of table storage data
 (Azure, PostgresSQL, Azure MariaDB), and other types of on-premises relational
 databases.
 
 
- Data Tier: Oracle Database@Azure ingests source data from Azure Data Lake Storage in conjunction with Azure Data
 Factory. 
 
 
- Consumption Tier: Oracle Database@Azure provides insights to Microsoft Power BI running on Microsoft Azure.
 
 
 
The following diagram illustrates the functional architecture:

 
 Description of the illustration data-lake-db-azure-process.png 

 data-lake-db-azure-process-oracle.zip 

 

 

 
 
Medallion Architecture

 

 
This section demonstrates how you can deploy Oracle Database@Azure as the data warehouse within the Azure medallion architecture.
 

 
The medallion architecture is a data management framework that
 structures data handling in a data lakehouse into distinct stages (bronze,
 silver, and gold), representing the different stages of data processing:

 
 
- Bronze stage: Data from various sources is ingested,
 validated, and curated. 
 
- Silver stage: The data is stored and processed for analytics
 and reporting. 
 
- Gold stage: Refined data is delivered for analysis and
 reporting. 
 
 
The following diagram illustrates the architecture:

 
 Description of the illustration data-lake-db-azure-medallion.png 

 data-lake-db-azure-medallion-oracle.zip 

 

 
The medallion stages are further divided into the following
 deployment areas:

 
 
- Ingestion Framework: Ingests data from various data sources
 using Azure Data Factory. Raw data is stored in Azure Data Lake
 Storage Gen 2 and Delta Lake. This framework ensures data
 consistency and accuracy across source and sink systems. This
 framework constitutes a robust set of scripts to ensure quality by
 using audit, balance and control mechanisms across platforms. 
 
- Validation: Raw data is ingested into Oracle Autonomous Data Warehouse Serverless or Oracle Exadata Database
 Service for deduplication and data quality check. This workflow performs
 basic cleansing masking of PII and PHI data along with validation of
 raw files through a rules-driven framework to perform schema checks.
 The validation framework can be implemented using Azure Data
 Factory. 
 
 
- Rejection Workflow: Any record that is rejected during the
 ingestion stage due to validation errors or other processing errors
 is staged on a separate Azure Data Lake Storage path. Automated
 email notifications using Logic App are sent to the support team
 based on defined software license agreements (SLAs). Standardized
 data remains in Oracle Autonomous Data Warehouse Serverless or Oracle Exadata Database
 Service .
 
 
- Orchestration: A scheduling system manages data processing
 jobs, scheduling, and job dependencies. Azure Data Factory can be
 used for the orchestration of ETL jobs. The Orchestration stage
 includes Oracle Autonomous Data Warehouse Serverless or Oracle Exadata Database
 Service , Delta Lake, and Azure Data Lake Storage Gen 2.
 
 
- Reporting/Analytics: The reporting stage includes Power BI
 and data services such as external feeds and data monetization. 
 
 
The architecture has the following infrastructure components:

 
 
- Region 
An Azure region is a
 geographical area in which one or more physical Azure data
 centers, called availability zones, reside. Regions are
 independent of other regions, and vast distances can
 separate them (across countries or even continents).

 
Azure and OCI regions are localized geographic
 areas. For Oracle Database@Azure , an Azure region is connected to an OCI region, with
 availability zones (AZs) in Azure connected to availability
 domains (ADs) in OCI. Azure and OCI region pairs are
 selected to minimize distance and latency.
 

 
 
- Availability zone 
An availability zone
 is a physically separate data center within a region
 designed to be available and fault-tolerant. Availability
 zones are close enough to have low-latency connections to
 other availability zones.

 
 
- Virtual network (VNet) and subnet 
A
 VNet is a virtual network that you define in Azure. A VNet
 can have multiple non-overlapping CIDR blocks subnets that
 you can add after your create the VNet. You can segment a
 VNet into subnets, which can be scoped to a region or to an
 availability zones. Each subnet consists of a contiguous
 range of addresses that
