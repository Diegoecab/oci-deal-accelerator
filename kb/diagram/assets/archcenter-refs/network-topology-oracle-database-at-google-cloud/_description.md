# Learn about selecting network topologies for Oracle Database@Google Cloud

- Source: https://docs.oracle.com/en/solutions/network-topology-oracle-database-at-google-cloud/index.html
- Date: 2025-10
- Type: reference-architecture
- Services: vcn, drg, google-cloud
- Tags: networking, multicloud

## Summary (catalog)

Network topology options for Database@Google Cloud. Covers VPC-to-VCN peering, shared VPC, and Private Service Connect patterns. Guidance on DNS resolution and IP address management.

## Architecture (fetched from source)

Architecture

 

 
This architecture shows a detailed topology for
 Oracle AI Database@Google
 Cloud :
 

 
 Description of the illustration google-detailed-arch.png 

 google-detailed-arch-oracle.zip 

 
The architecture displays application resources within a
 VPC of a Google Cloud project, located in a single zone of a Google Cloud region. An application subnet in the VPC connects to Oracle AI Database@Google
 Cloud using the ODB network in the OCI child site, located in the same Google Cloud region. The client subnet of the Oracle Autonomous AI Database Serverless , the Oracle Exadata Database Service on Dedicated
 Infrastructure client subnet, and the backup subnets of Oracle Database Autonomous
 Recovery Service are defined in the ODB network . The VCN extends into the OCI region to enable connections to other resources within
 OCI. The OCI region hosts the following OCI services: OCI Vault , OCI Object Storage , and control plane.
 

 

 

 
 
Considerations for
 Networking

 

 
When selecting a network topology, consider the following
 requirements:

 
 
- Select or create an ODB network to associate your Oracle Autonomous AI Database or Oracle Exadata Database
 Service .
 
 
- Carve out a non-overlapping CIDR range with the VPC subnets. 
 
- Define one CIDR for the client and backup subnet to accommodate future
 growth. 
 
 

 
Note:
 Oracle Autonomous AI Database is automatically configured for local backups in the OCI region. Both the backup and
 restore processes are initiated through Oracle Database Autonomous
 Recovery Service .
 

 

 

 

 

 

 
 Title and Copyright Information 

 

 
Learn about selecting network topologies for Oracle AI Database@Google Cloud

 
G13167-06

 
April 2026

 
 Copyright © 2024,2026, 

Oracle and/or its affiliates.
