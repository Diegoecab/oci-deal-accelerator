# Learn About Storage Modernization with Oracle Cloud Infrastructure Object Storage

- Source: https://docs.oracle.com/en/solutions/oci-object-storage-modernization/index.html
- Date: 2024-11
- Type: reference-architecture
- Services: object-storage
- Tags: data-platform

## Summary (catalog)

Object Storage modernization patterns. Tiered storage (Standard, Infrequent Access, Archive), lifecycle policies for cost optimization, and data lake integration with ADB and Data Integration.

## Architecture (fetched from source)

Architecture

 

 
This architecture shows the design and execution to move long term storage to
 OCI Object Storage , helping to reduce cost and apply retention, lifecycle rules, and pre-authenticated
 requests as added features.
 

 
The following images depict the architecture "before" and "after"
 implementation. Oracle File System Service (FSS) is used for a large shared filesystem.
 On this filesystem, which had been migrated from an on-premises datacenter, the
 application components use batch processing to generate archive files on an ongoing
 basis. Thus, the same NFS filesystem holds both the application elements required to do
 the intermediate processing (scripts, temp files, and so on) and the actual file
 archive, stored in a hierarchy that must be maintained for up to 10 years, per business
 requirements. 
 

 
Once set up, OCI Object Storage buckets are used to host the archive portion of what NFS was doing. Permissions for
 reading and writing the bucket are narrowly defined, and retention and lifecycle rules
 are established, in order to be prepared for a large influx of data. The large hierarchy
 of archive files is copied to OCI Object Storage , and the batch processing is refactored to place new archives on the new object
 bucket. Access mechanisms were also refactored slightly in order to access the files
 from object storage, in a way which prevented the rest of the application and end
 customers from having to make changes to how they access these archives.
 

 
The following diagram illustrates the architecture before
 implementation:

 
 Description of the illustration oci-object-storage-modernization_arch_before.png 

 oci-object-storage-modernization-arch-oracle1.zip 

 
The following diagram illustrates the architecture after implementation:

 
 Description of the illustration oci-object-storage-modernization_arch_after.png 

 oci-object-storage-modernization-arch-oracle.zip 

 
 a: Default OSS Policy: 
 
- Tenancy Admins - Full Access 
 
- App Admins - Limited Access without object read 
 
- Read only - Bucket inspect without object read 
 
 

 
 b: Dynamic Group IAM Policy: 
 
- Statements added per dynamic group 
 
- Narrowly defined for specific resources 
 
 

 
 c: Dynamic Group Definition (either of): 
 
- List of instance OCIDs 
 
- Instance compartment OCID 
 
 

 
 d: Retention Rules: 
 
- 3650 days (10 years) 
 
- locked 
 
 

 
 e: Lifecycle Rules: 

 
 
- After 90 days - Infrequent storage 
 
- After 180 days - Archive storage 
 
- After 3651 days - Delete 
 
 
 This architecture supports the following components:

 
 
- Object storage 
 Oracle Cloud
 Infrastructure Object Storage provides quick access to large amounts of structured and unstructured data of any content type, including database backups, analytic data, and rich content such as images and videos. You can safely and securely store and then retrieve data directly from the internet or from within the cloud platform. You can scale storage without experiencing any degradation in performance or service reliability. Use standard storage for "hot" storage that you need to access quickly, immediately, and frequently. Use archive storage for "cold" storage that you retain for long periods of time and seldom or rarely access.
 

 
 
- File storage 
The Oracle Cloud Infrastructure File
 Storage service provides a durable, scalable, secure, enterprise-grade network file system. You can connect to a File Storage service file system from any bare metal, virtual machine, or container instance in a VCN. You can also access a file system from outside the VCN by using Oracle Cloud
 Infrastructure FastConnect and IPSec VPN.
 

 
 
- Identity and Access Management (IAM) 
 Oracle Cloud Infrastructure Identity
 and Access Management (IAM) is the access control plane for Oracle Cloud
 Infrastructure (OCI) and Oracle Cloud Applications. The IAM API and the user interface enable you to manage identity domains and the resources within the identity domain. Each OCI IAM identity domain represents a standalone identity and access management solution or a different user population.
 

 
 
 

 

 
 
Considerations for Identity
 Management

 

 
Using private object storage buckets implies setting up proper permissions
 for use. By default, user groups and dynamic groups are not typically granted access to wide
 permission sets, such as object-family , unless it is scoped to a compartment. 
 

 
Before embarking on this solution, it is worth ensuring that only the groups
 you want to have access to objects storage have permissions. One thing that is extremely
 helpful here is following the CIS Landing Zone methodology
 around restricting access. When implementing this solution, we discuss the creation of
 dynamic groups, so it is worth understanding both the compartment structure of your
 tenancy, as well as the concepts that the landing zone discusses. It is also worth
 reading up on OCI Policy Syntax , including how
 to narrowly define a dynamic group and a policy statement.
 

 
Although both RCLONE and OCIFS support standard OCI API Keys as an
 authentication mechanism, we chose Instance Principals and Dynamic Groups to
 authenticate. This improves the overall security posture - it is not required to create,
 distribute, or rotate keys. Instead, separate dynamic groups are utilized, in order to
 ensure the most narrow permissions possible for each dynamic group. For example,
 allowing bucket creation could be allowed by policy for the RCLONE dynamic group,
 whereas only object read is allowed for the Apache dynamic group.

 

 

 
 
Considerations for Archive
 Storage

 

 
To save on costs and utilize the lowest cost tier of OCI Object Storage , this solution implemented Lifecycle Rules, which move objects to the Infrequent Tier,
 and then to the Archive tier after a period of time after creation.
 

 
Once the objects are archived, they cannot be directly reclassified to Standard Tier.
 Because of the offline nature of Archived Object Storage, a process needs to be
 developed in which an audit (business process) could be requested, certain files pulled
 from the archive, and then the files become accessible for a time-bound period.

 
Once again, using the inherent features of object storage, files can be recalled
 temporarily, copied out to a temporary location (another bucket), and exposed externally
 using Pre-authenticated Requests (PARs). These are obscure URLs (security by obscurity)
 that allow access to specific files in a bucket, and can expire after a set amount of
 time, revoking access.

 
During the recall period, the files can be copied to new standard-tier buckets, and then
 they automatically revert back to Archive mode, and no maintenance is needed. RCLONE and
 OCI CLI, Java, REST or Python can be used similarly for the main solution, again given
 access to a specific audit bucket.

 

 

 

 

 

 
 Title and Copyright Information 

 

 
Learn About Storage Modernization with Oracle Cloud Infrastructure Object Storage

 
G11832-01

 
November 2024

 
 Copyright © 2024, 

Oracle and/or its affiliates.
