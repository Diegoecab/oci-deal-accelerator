# Build a secure multicloud architecture for Oracle Database@Azure

- Source: https://docs.oracle.com/en/solutions/secure-db-azure/index.html
- Date: 2025-07
- Type: reference-architecture
- Services: exacs, adb-s, vault, data-safe, cloud-guard, azure
- Tags: database, multicloud, azure, security

## Summary (catalog)

Security architecture for Database@Azure. Covers data encryption with OCI Vault, database activity monitoring with Data Safe, threat detection with Cloud Guard, and network security with NSGs.

## Architecture (fetched from source)

About Building a Secure Multicloud Architecture for Oracle Database@Azure 
 
 
 
 
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
 
 

 

 
 
 
About Building a Secure Multicloud
 Architecture for Oracle Database@Azure 

 

 

 
You want to ensure that your data is always protected from accidental or
 malicious exposure, regardless of where your database is being deployed.

 
 Successfully securing this data requires an understanding of the various attack
 vectors, as well as the tools and services available to you on the relevant
 cloud platform. 

 
Whether you run Oracle databases on Oracle Cloud
 Infrastructure or other cloud service providers such as Microsoft Azure, Google Cloud
 Platform, Amazon Web Services, Oracle provides a robust set of security
 tools that allow administrators to prevent, detect and respond to security
 threats, both inside and outside of your organization.
 

 
 Oracle Autonomous Database Serverless @ Azure includes access to many security features and options.
 

 
All Oracle Autonomous Database Serverless databases are encrypted by default using Transparent Data Encryption
 (TDE). This safeguards your data at rest in the database and prevents bypass
 attacks on this data such as attempts to access the data by using the
 underlying file system without any attempt to authenticate or have the
 necessary database privileges to access the data.
 

 
Encryption keys should be stored and managed separately from the
 database. With Oracle Autonomous Database Serverless @ Azure, this can be achieved by integrating your database with Azure Key
 Vault.
 

 
 Oracle Database Vault implements powerful security controls for your database. These unique
 security controls restrict access to application data by privileged database
 users, reducing the risk of insider and outside threats and addressing
 common compliance requirements.
 

 
 Oracle Data Safe , which is included with Autonomous Database , provides a unified control center that helps you manage the day-to-day
 security and compliance requirements of Oracle databases. Oracle Data Safe helps you to evaluate security controls, assess user security, monitor
 user activity, mitigate risk from compromised accounts, and address data
 security compliance requirements for your database. Oracle Data Safe does this by employing:
 
 
- Security assessment 
 
- User assessment 
 
- Activity auditing 
 
- Sensitive data discovery 
 
- Data masking 
 
 
 

 
A final consideration is to centralize database user authentication
 and authorization by integrating your database with Entra ID.

 
The remainder of this playbook will show how each of these available
 features and services helps you to be confident that your data is adequately
 secured in a public cloud platform.

 

 
 
Replay the Webinar

 

 
Replay the webinar about building a secure multicloud architecture for Oracle Database@Azure : 
 

 

 

 

 

 

 

 

 

 

 

 
 Title and Copyright Information 

 

 
 Build a secure multicloud architecture for Oracle Database@Azure 

 
G36548-01

 
June 2025

 
 Copyright © 2025, 

Oracle and/or its affiliates.
