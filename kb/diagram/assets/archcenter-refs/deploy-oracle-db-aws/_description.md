# Deploy Oracle Database@AWS

- Source: https://docs.oracle.com/en/solutions/deploy-oracle-db-aws/index.html
- Date: 2025-07
- Type: reference-architecture
- Services: exacs, adb-d, aws
- Tags: database, multicloud, aws

## Summary (catalog)

ExaCS and ADB-D colocated in AWS data centers. ODB peering between VPC and ODB network in same AZ. Default limit of 2 DB servers and 3 storage servers — request increase early.

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
 

 
This architecture supports the following components:
 
 
- AWS region 
AWS regions
 are separate geographic areas. They consist of multiple,
 physically separated, and isolated availability zones that
 are connected with low latency, high throughput, highly
 redundant networking.

 
 
- AWS availability zone 
Availability
 zones are highly available data centers within each AWS
 region.

 
 
- Amazon virtual private cloud and subnet 
 Amazon virtual private cloud (VPC) enables you to launch AWS resources into a virtual
 network you've defined. This virtual network resembles a
 traditional network that you operate in your own data
 center, with the benefits of using the scalable
 infrastructure of AWS. After you create an VPC, you can add
 subnets.
 

 
A subnet
 is a range of IP addresses in your Amazon VPC . You can create AWS resources, such as Amazon EC2 instances, in specific subnets.
 

 
 
- Amazon Simple Storage Service 
 Amazon Simple Storage Service (S3) is a cloud-based object storage service. Amazon S3 provides a scalable, secure, and durable platform for
 storing data. Amazon S3 can be used for managed backups.
 

 
 
- ODB network 
An ODB network is a private network that hosts Oracle Database@AWS in a specified availability zone. You can set up an ODB
 peering connection between an ODB network  and a VPC to connect to your Oracle databases.
 

 
 
- Oracle Exadata Database Service on Dedicated
 Infrastructure 
 Oracle Exadata Database Service on Dedicated
 Infrastructure enables you to leverage the power of Exadata in
 the cloud. Oracle Exadata Database
 Service delivers proven Oracle Database capabilities on purpose-built, optimized Oracle
 Exadata infrastructure in the public cloud.
 Built-in cloud automation, elastic resource
 scaling, security, and fast performance for all
 Oracle Database workloads helps you simplify management and
 reduce costs.
 

 
 
- Oracle Autonomous Database on Dedicated Exadata Infrastructure 
 Oracle Autonomous Database on Dedicated Exadata Infrastructure is a fully-managed, preconfigured database
 environment that you can use for transaction
 processing and data warehousing workloads. OCI
 handles creating, backing up, patching, upgrading,
 and tuning the database. 

 
 
- Oracle Database Autonomous
 Recovery Service 
 Oracle Database Autonomous
 Recovery Service is a fully managed service designed to protect
 Oracle Database s from data loss and cyber threats. It offers
 faster backups with reduced database overhead,
 reliable recovery with validated backups, and
 real-time protection enabling recovery to within
 less than a second of an outage or ransomware
 attack. This service provides a centralized data
 protection dashboard and is recommended for
 backing up Oracle Database s with high resiliency.
 

 
 
- OCI region 
An OCI region
 is a localized geographic area that contains one
 or more data centers, hosting availability
 domains. Regions are independent of other regions,
 and vast distances can separate them (across
 countries or even continents).

 
 
- OCI virtual cloud
 network and subnet 
A virtual cloud
 network (VCN) is a customizable, software-defined
 network that you set up in an OCI region. Like
 traditional data center networks, VCNs give you
 control over your network environment. A VCN can
 have multiple non-overlapping classless
 inter-domain routing (CIDR) blocks that you can
 change after you create the VCN. You can segment a
 VCN into subnets, which can be scoped to a region
 or to an availability domain. Each subnet consists
 of a contiguous range of addresses that don't
 overlap with the other subnets in the VCN. You can
 change the size of a subnet after creation. A
 subnet can be public or private. 

 
 
- Network security group
 (NSG) 
NSGs
 act as virtual firewalls for your cloud resources.
 With the zero-trust security model of OCI you
 control the network traffic inside a VCN. An NSG
 consists of a set of ingress and egress security
 rules that apply to only a specified set of
 virtual network interface cards (VNICs) in a
 single VCN.

 
 
- OCI Object
 Storage 

 OCI Object Storage provides access to large amounts of structured
 and unstructured data of any content type,
 including database backups, analytic data, and
 rich content such as images and videos. You can
 safely and securely store data directly from
 applications or from within the cloud platform.
 You can scale storage without experiencing any
 degradation in performance or service reliability.
 
 

 
Use standard storage for
 "hot" storage that you need to access quickly,
 immediately, and frequently. Use archive storage
 for "cold" storage that you retain for long
 periods of time and seldom or rarely
 access.

 
 
- OCI Vault 
 Oracle Cloud Infrastructure Vault enables you to create and centrally manage the
 encryption keys that protect your data and the
 secret credentials that you use to secure access
 to your resources in the cloud. The default key
 management is Oracle-managed keys. You can also
 use customer-managed keys which use OCI Vault . OCI Vault offers a rich set of REST APIs to manage vaults
 and keys.
 

 
 
 

 

 

 
 
Considerations

 

 
Consider the following points when deploying this reference architecture: 

 
 
- Network 
 
 
Plan your network connectivity in advance to define your network
 address space (CIDR) and topologies. You need at least one AWS Private Cloud
 (VPC) to peer with the ODB network. The CIDR blocks must not overlap with any
 AWS VPC subnet, OCI VCN, or any database clients. 

 
 
- Service Limits 
 
 
Before provisioning, review the OCI service limits to ensure they
 meet your needs. Oracle Database@AWS has a default limit of two database servers and three storage servers. If you
 require additional capacity, please raise a service limit increase request. For
 more information, see OCI Service Limits  and Requesting a Service Limit Increase in Explore More .
 

 
 
 
 

 

 
 
Explore More

 

 
Learn more about Oracle Database@AWS . 
 

 
Review these resources:

 
 
- Learn about network
 topologies for Oracle Database@AWS 
 
- Oracle Cloud
 Infrastructure for Amazon Web Services professionals 
 
- Provision Oracle Exadata Database
 Service in Oracle Database@AWS Tutorial
 
 
- Get Started with Autonomous Database on
 Dedicated Exadata Infrastructure on Oracle
 Database@AWS Tutorial
 
 
 
Review the following documentation:

 
 
- Oracle Database@AWS documentation (Oracle)
 
 
- Oracle Database@AWS documentation (AWS)
 
 
- Oracle-managed backup to Amazon S3
 documentation 
 
- Oracle Exadata Database Service on Dedicated
 Infrastructure 
 
- Oracle Autonomous Database on Dedicated Exadata Infrastructure 
 
- ODB Peering Connection 
 
- Quotas and Service Limits 
 
 
Review these additional resources: 

 
 
- Oracle Database@AWS 
 
- Oracle Multicloud Solutions site 
 
- Getting Started with Exadata
 Database Service on Oracle Data
