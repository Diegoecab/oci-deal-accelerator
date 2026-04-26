# Data platform - data lakehouse

- Source: https://docs.oracle.com/en/solutions/data-platform-lakehouse/index.html
- Date: 2024-10
- Type: reference-architecture
- Services: adw, object-storage, data-integration, data-catalog, streaming, goldengate
- Tags: data-platform, autonomous, ai-ml

## Summary (catalog)

Full data lakehouse with ADW + autoscaling, hybrid partitioned tables, Object Storage medallion architecture. Data Integration/Data Flow for ETL, GoldenGate Stream Analytics for real-time, AI/ML with Data Science.

## Architecture (fetched from source)

Data Platform - Data Lakehouse 
 
 
 
 
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
 
 

 

 
 
 
- Data platform - data lakehouse 
 
- Data Platform - Data Lakehouse 
 
 
 
 
Data Platform - Data Lakehouse

 
 

 

 
You can effectively collect and analyze event data and streaming data from internet of things (IoT) and social media sources, but how do you correlate it with the broad range of enterprise data resources to leverage your investment and gain the insights you want?

 
Leverage a cloud data lakehouse that combines the abilities of a data lake
 and a data warehouse to process a broad range of enterprise and streaming data for
 business analysis and machine learning.

 
This reference architecture positions the technology solution within the overall business
 context, where strategic intents drive the creation of measurable strategic outcomes.
 These outcomes generate new strategic intents, effectively delivering continuous,
 data-driven business improvements.

 
 Description of the illustration data-driven-business-context.png 

A data lake enables an enterprise to store all of its data in a
 cost-effective, elastic environment while providing the necessary processing,
 persistence, and analytic services to discover new business insights. A data lake stores
 and curates structured and unstructured data and provides methods for organizing large
 volumes of highly diverse data from multiple sources.

 
With a data warehouse, you perform data transformation and cleansing before
 you commit the data to the warehouse. With a a data lake, you ingest data quickly and
 prepare it on the fly as people access it. A data lake supports operational reporting
 and business monitoring that require immediate access to data and flexible analysis to
 understand what is happening in the business while it is happening.

 

 
 
Functional Architecture

 

 
 You can combine the abilities of a data lake and a data warehouse to provide
 a modern data lakehouse platform that processes streaming and other types of data from a
 broad range of enterprise data resources so that you can leverage the data for business
 analysis, machine learning, data services, and data products.

 
A data lakehouse architecture combines the capabilities of both the data lake and the data warehouse to increase operational efficiency and to deliver enhanced capabilities that allow:

 
 
- Seamless data and information usage without the need to replicate it
 across the data lake and data warehouse 
 
- Diverse data type support in an enhanced multimodel and polyglot
 architecture 
 
- Seamless data ingest from any consumer using real time, streaming, batch,
 application programming interface (API), and bulk ingestion mechanisms 
 
- Continuous intelligence extraction from data using artificial intelligence (AI),
 generative AI, and machine learning (ML) services 
 
- The ability to infuse and serve intelligence to any data consumer by using API, user
 interface, streaming, and integration mechanisms 
 
- Governance and fine-grained data security that leverages a zero-trust
 security model 
 
- The ability to fully decouple storage and compute resources and to
 consume only the resources needed at any point in time 
 
- The ability to leverage multiple compute engines, including open source
 engines, to process the same data for different use cases to achieve maximum data
 repurposing, liquidity, and usage 
 
- The ability to store data using different open file and table formats in the data
 lake 
 
- The ability to leverage Oracle Cloud
 Infrastructure (OCI) native services that are managed by Oracle and that reduce
 operational overhead
 
 
- Better cloud economics with autoscaling that adjusts cloud resources
 infrastructure to match the actual demand 
 
- Modularity so that service use is use-case driven 
 
- Interoperability with any system or cloud that adheres to open
 standards 
 
- Support for a diverse set of use cases including streaming, analytics,
 data science, and machine learning 
 
- Support for different architectural approaches, from a centralized
 lakehouse to a decentralized data mesh 
 
 
The following diagram illustrates the functional architecture. 

 
 Description of the illustration lakehouse-functional.png 

 lakehouse-functional-oracle.zip 

 
The architecture focuses on the following logical divisions:

 
 
- Connect, Ingest, Transform 
Connects to data sources, ingests,
 and refines their data for use in each of the data layers in the
 architecture.

 
 
- Persist, Curate, Create 
Facilitates access and navigation of the data to show the current business view. For relational technologies, data may be logically or physically structured in simple relational, longitudinal, dimensional or OLAP forms. For non-relational data, this layer contains one or more pools of data, either output from an analytical process or data optimized for a specific analytical task.

 
 
- Analyze, Learn, Predict 
Abstracts the logical business view of the data for consumers. This abstraction facilitates agile approaches to development, migration to the target architecture, and the provision of a single reporting layer from multiple federated sources.

 
 
 
The architecture has the following functional components:

 
 
- Batch ingest 
Batch ingest is useful for data that
 can't be ingested in real time or that is too costly to adapt for real-time
 ingestion. It is also important for transforming data into reliable and
 trustworthy information that can be curated and persisted for regular
 consumption. You can use the following services together or independently to
 achieve a highly flexible and effective data integration and transformation
 workflow.

 
 
- 
 
 
 Oracle Cloud Infrastructure Data
 Integration is a fully managed, serverless, cloud-native
 service that extracts, loads, transforms,
 cleanses, and reshapes data from a variety of data
 sources into target Oracle Cloud
 Infrastructure services, such as Autonomous Data
 Warehouse and Oracle Cloud
 Infrastructure Object Storage . Users design data integration processes using
 an intuitive, codeless user interface that
 optimizes integration flows to generate the most
 efficient engine and orchestration, automatically
 allocating and scaling the execution environment.
 
 

 
 
ETL (extract transform
 load) leverages fully-managed, scale-out
 processing on Spark, and ELT (extract load
 transform) leverages full SQL push-down
 capabilities of the Autonomous Data
 Warehouse in order to minimize data movement and to
 improve the time to value for newly ingested data.
 
 

 
 
 Oracle Cloud Infrastructure Data
 Integration provides interactive exploration and data
 preparation, and helps data engineers protect
 against schema drift by defining rules to handle
 schema changes.
 

 
 
 
- 
 
 
 Oracle Data
 Integrator provides comprehensive data integration from
 high-volume and high-performance batch loads, to
 event-driven, trickle-feed integration processes,
 to SOA-enabled data services. A declarative design
 approach ensures faster, simpler development and
 maintenance, and provides a unique approach to
 extract load transform (ELT) that helps guarantee
 the highest level of performance possible for data
 transformation and validation processes. Oracle
 data transforms use a web interface to simplify
 the configuration and execution of ELT and to help
 users build and schedule data and work flows using
 a declarative design approach.
 

 
 
 
- 
 
 
Oracle Data Transforms enable ELT for selected supported
 technologies, simplifying the configuration and execution of data
 pipelines by using a web user interface that allows users to
 declaratively build and schedule data flows and workflows. Oracle Data
 Transforms is available as a fully-managed environment within Oracle A
