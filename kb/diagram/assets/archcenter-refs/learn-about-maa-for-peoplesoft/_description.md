# Learn about maximum availability architecture for PeopleSoft

- Source: https://docs.oracle.com/en/solutions/learn-about-maa-for-peoplesoft/index.html
- Date: 2024-08
- Type: reference-architecture
- Services: exacs, adg, load-balancer, compute
- Tags: application, ha-dr, peoplesoft

## Summary (catalog)

MAA for PeopleSoft on OCI. Active Data Guard for database HA/DR, multi-instance PIA behind Load Balancer, Process Scheduler on multiple nodes for batch processing resilience.

## Architecture (fetched from source)

Architecture

 

 
The following architecture diagrams show PeopleSoft and Oracle
 Maximum Availability Architecture (Oracle MAA). 

 
PeopleSoft Maximum Availability Architecture is a PeopleSoft high
 availability architecture layered on top of the Oracle Database and Oracle Fusion
 Middleware Oracle MAA, including a secondary site to provide business continuity in the
 event of a primary site failure.

 
The following shows a full-stack Oracle MAA architecture, including primary
 and secondary sites. The secondary site is a replica of the primary. 
 
 Description of the illustration peoplesoft-maa-arch.png 

 peoplesoft-maa-arch-oracle.zip 
 
 

 
Each site consists of the following:

 
 
- An HTTPS load balancer for web-based application services 
 
- Two servers that host the PeopleSoft Pure Internet Architecture (PIA)
 domain 
 
- Two servers that host both the PeopleSoft Application Server and the
 Process Scheduler domains 
 
- A shared file system for PeopleSoft application software and report
 repository 
 
- An Oracle Real Application Clusters (Oracle
 RAC) database, with two database servers and shared storage
 
 
- Oracle Active Data Guard , which allows routing of “mostly read operations” to the standby database while
 keeping the standby database current with the primary
 
 
 
Both the application tier shared file system and the database are replicated
 to the secondary site – the application tier using rsync, and the database tier using
 Oracle Data Guard .
 

 
The data at the second site is kept in sync with the primary by using
 appropriate replication mechanisms.

 
 
- For the database itself, Oracle Active Data Guard ensures the standby database is kept in sync and transactionally consistent.
 
 
- For file system output generated during the operation of the
 application, rsync is used to frequently replicate the output to
 another region. There will be a small gap to resolve by identifying missing file
 system components and determining the action to take for each.
 
 
 

 

 

 

 

 
 Title and Copyright Information 

 

 
Learn about maximum availability architecture for PeopleSoft

 
F87909-01

 
August 2024

 
 Copyright © 2024, 

Oracle and/or its affiliates.
