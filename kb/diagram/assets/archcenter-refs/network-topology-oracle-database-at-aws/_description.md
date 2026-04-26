# Learn about network topologies for Oracle Database@AWS

- Source: https://docs.oracle.com/en/solutions/network-topology-oracle-database-at-aws/index.html
- Date: 2025-07
- Type: reference-architecture
- Services: vcn, drg, aws
- Tags: networking, multicloud, aws

## Summary (catalog)

Network topology patterns for Database@AWS. VPC-to-ODB network peering, Transit Gateway integration, and on-premises connectivity via AWS Direct Connect alongside OCI FastConnect.

## Architecture (fetched from source)

Architecture

 

 

 Oracle Database@AWS extends Oracle Database capabilities into AWS as a native service. The following architecture diagram shows
 the primary topology for Oracle Database@AWS with application resources within a VPC of an AWS region in the same availability
 zone. 
 
 

 
 Description of the illustration db-aws-main-arch.png 

 db-aws-main-arch-oracle.zip 

 
 Oracle Exadata Database Service on Dedicated
 Infrastructure or Oracle Autonomous Database on Dedicated Exadata Infrastructure reside inside the OCI child site within the ODB network which hosts Oracle Database@AWS . An application hosted within the VPC communicates with Oracle Database@AWS within the ODB network using the ODB peering connection in the same availability zone. This
 configuration enables a direct, secure, and low latency connection between applications
 in the VPC and Oracle Database@AWS .
 

 
 Amazon S3 represents an Oracle-managed backup. See Explore More for
 the link to Oracle-managed backup to Amazon S3 in the OCI
 documentation.
 

 

 

 

 

 

 
 Title and Copyright Information 

 

 
Learn about network topologies for Oracle Database@AWS

 
G18329-04

 
July 2025

 
 Copyright © 2024,2025, 

Oracle and/or its affiliates.
