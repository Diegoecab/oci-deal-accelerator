# Load Oracle Fusion Cloud ERP data into Snowflake

- Source: https://docs.oracle.com/en/solutions/load-fusion-erp-data-snowflake/index.html
- Date: 2025-10
- Type: reference-architecture
- Services: oic, object-storage
- Tags: data-platform, integration, multicloud

## Summary (catalog)

Fusion ERP to Snowflake data pipeline. OIC adapter for Fusion data extraction, Object Storage as staging area, Snowflake COPY INTO for loading. Incremental extraction for ongoing synchronization.

## Architecture (fetched from source)

About Loading Oracle Cloud ERP Data into Snowflake 
 
 
 
 
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
 
 

 

 
 
 
About Loading Oracle Cloud
 ERP Data into Snowflake
 

 

 

 
 
You can load data from Oracle Fusion Cloud
 Enterprise Resource Planning (ERP) or other Oracle Fusion Cloud
 Applications into various cloud storage solutions, such as Snowflake, using intermediaries like
 Amazon S3, Azure Blob, or Google Cloud Storage. You can implement a multicloud strategy
 and have the flexibility to utilize any data warehouse or cloud service provider for
 your organizational needs.
 

 
 
In this solution, you consider the advantages and disadvantages of three
 architecture options, and identify and implement the architecture with the least
 tradeoffs in your organization.

 
 

 
 
Before You Begin

 

 

 The primary tool for extracting data from Oracle Cloud
 ERP is the Business Intelligence Cloud Connector (BICC), which loads the data into OCI Object Storage . 
 
 

 

 
 
Before you begin configuring BICC, you must first set up BICC access using the
 Security Console in Oracle Fusion Cloud
 Applications .
 

 
 

 
 
- Sign in to Oracle Fusion Cloud
 Applications . 
 
- From the Navigator , click Tools ,
 Security Console. 
 
- In the Roles tab, click
 Create . 
 
- On the Basic Information page, enter the following
 values. 
 
 
 Field 
 Value 
 
 
 
 
 Role Name 
 BIACM_ADMIN 
 
 
 Role Code 
 BIACM_ADMIN 
 
 
 Role Category 
 BI - Abstract Roles 
 
 
 
 
 
- Click Next . 
 
- On the Role Hierarchy page, click Add
 Role . 
 
- On the Add Role Membership dialog box, search for the
 following roles: 

 
 
 
- ESS Administrator 
 
- ORA_ASM_APPLICATION_IMPLEMENTATION_ADMIN_ABSTRACT 
 
 
 

 
 
- Click Add Role Membership to add them. 
 
 
 
- Click Close . 
 
- Click Next . 
 
- On the Segregation of Duties page, click
 Next to skip entering details. 
 
- On the Users page, click Add
 User . 
 
- Click Add Selected Users . 
 
- Close the dialog box. 
 
- Click Next . 
 
- Review the summary and click Save and Close . 
 
 

 

 
 
About Required Services and
 Roles

 

 
This solution requires the following services and roles:

 
 
- Oracle
 Fusion Cloud Applications 
 
- OCI GoldenGate 
 
- OCI Object Storage 
 
- OCI Vault 
 
- Oracle Data Transforms 
 
- Data Flow 
 
- Data
 Science 
 
- Snowflake 
 
 
These are the roles needed for each service.

 

 
 
 
 Service Name: Role 
 Required to... 
 
 
 
 
 Oracle
 Fusion Cloud Applications : Security Manager
 
 Access the Security Console of Oracle
 Fusion Cloud Applications .
 
 
 
 Oracle
 Fusion Cloud Applications : ESS Administrator 
 
 Create and manage schedules for global data extracts or jobs. 
 
 
 Oracle
 Fusion Cloud Applications : ORA_ASM_APPLICATION_IMPLEMENTATION_ADMIN_ABSTRACT
 
 Access global offerings and data stores or jobs. 
 
 
 
 

 
See Oracle Products, Solutions, and Services to get what you need.
 

 

 

 

 

 

 
 Title and Copyright Information 

 

 
Load Oracle Fusion Cloud ERP data into Snowflake

 
G22493-04

 
April 2026

 
 Copyright © 2025,2026, 

Oracle and/or its affiliates.
