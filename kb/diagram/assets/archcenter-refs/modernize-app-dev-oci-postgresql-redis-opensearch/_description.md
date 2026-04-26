# Modernize your application development with OCI-managed PostgreSQL, Redis, and OpenSearch

- Source: https://docs.oracle.com/en/solutions/modernize-app-dev-oci-postgresql-redis-opensearch/index.html
- Date: 2025-05
- Type: reference-architecture
- Services: postgresql, redis, opensearch, oke
- Tags: application

## Summary (catalog)

Open-source database services on OCI for cloud-native apps. PostgreSQL for relational, Redis for caching, OpenSearch for full-text search. OKE for application tier deployment.

## Architecture (fetched from source)

Architecture

 

 
This architecture demonstrates a modern application deployment on OCI. Use
 this architecture to modernize applications through microservices and OCI-managed
 open-source databases, ensuring efficient data retrieval and robust analysis
 capabilities on a scalable and secure platform.

 
In this reference architecture, you will modernize your application by
 leveraging a microservices deployment coupled with OCI-managed, open-source
 technologies, such as OCI Kubernetes Engine (OKE) for orchestrating and scaling your application frontend, PostgreSQL for data
 persistence, Redis and Valkey as a cache layer for accelerated data retrieval, and
 OpenSearch for fast and accurate search and analysis capabilities. These services
 coupled with OCI's inherent scalability and comprehensive security features, provides a
 solid foundation for modernizing applications on OCI.
 

 
The following diagram illustrates this reference architecture.
 
 Description of the illustration oke-architecture-diagram.png 
 oke-architecture-diagram-oracle.zip 

 
The architecture has the following components:

 
 
- Managed service 
A managed service provides specific functionality without requiring you to perform maintenance tasks related to optimizing performance, availability, scaling, security, or upgrading. A managed service enables you to focus on delivering features for your customers instead of worrying about the complexity of operations. A managed service provides a scalable and secure component for cloud-native development. Use managed services to develop and run your app and to store its data. You get best-in-class solutions without needing expertise in each domain to build and operate your app.

 
 
- Kubernetes Engine 
 Oracle Cloud Infrastructure Kubernetes Engine ( OCI Kubernetes Engine or OKE ) is a fully-managed, scalable, and highly available service that you can use to deploy your containerized applications to the cloud. You specify the compute resources that your applications require, and Kubernetes Engine provisions them on Oracle Cloud
 Infrastructure in an existing tenancy. OKE uses Kubernetes to automate the deployment, scaling, and management of containerized applications across clusters of hosts.
 

 
 
- Cache with Redis 
 Oracle Cloud Infrastructure Cache with Redis is a comprehensive, managed-in-memory caching solution built on the foundation of open source Redis. This fully-managed service accelerates data reads and writes, significantly enhancing application response times and database performance to provide an improved customer experience.
 

 
 
- Database with PostgreSQL 
Oracle Cloud
 Infrastructure Database with PostgreSQL is a managed
 PostgreSQL service that frees up your team from routine
 tasks, such as patching and backups. Its standout feature is
 OCI Database optimized storage, which boosts system
 resilience and performance. OCI Database with PostgreSQL
 allows you to independently scale compute and storage.
 Additionally, it provides enhanced data security with
 end-to-end encryption.

 
 
- Search with OpenSearch 
OCI Search with
 OpenSearch is a managed service that you can use to build
 in-application search solutions based on OpenSearch to
 enable you to search large data sets and return results in
 milliseconds, without having to focus on managing your
 infrastructure. OpenSearch has observability features for
 metrics, traces, and log analysis.

 
 
- Bastion service 
 Oracle Cloud Infrastructure
 Bastion provides restricted and time-limited secure access to resources that don't have public endpoints and that require strict resource access controls, such as bare metal and virtual machines, Oracle MySQL Database Service , Autonomous Transaction
 Processing (ATP), Oracle Cloud Infrastructure Kubernetes Engine ( OKE ), and any other resource that allows Secure Shell Protocol (SSH) access. With OCI Bastion service, you can enable access to private hosts without deploying and maintaining a jump host. In addition, you gain improved security posture with identity-based permissions and a centralized, audited, and time-bound SSH session. OCI Bastion removes the need for a public IP for bastion access, eliminating the hassle and potential attack surface when providing remote access.
 

 
 
- Identity and Access Management 
 Oracle Cloud Infrastructure Identity
 and Access Management (IAM) provides user access control for Oracle Cloud
 Infrastructure (OCI) and Oracle Cloud Applications. The IAM API and the user interface enable you to manage identity domains and the resources within them. Each OCI IAM identity domain represents a standalone identity and access management solution or a different user population.
 

 
 
- Object storage 

 OCI Object Storage provides access to large amounts of structured
 and unstructured data of any content type,
 including database backups, analytic data, and
 rich content such as images and videos. You can
 safely and securely store data directly from the
 internet or from within the cloud platform. You
 can scale storage without experiencing any
 degradation in performance or service reliability.
 
 

 
Use standard storage for
 "hot" storage that you need to access quickly,
 immediately, and frequently. Use archive storage
 for "cold" storage that you retain for long
 periods of time and seldom or rarely
 access.

 
 
- Key Vault 
 Oracle Key Vault securely stores encryption keys, Oracle Wallets, Java KeyStores, SSH key pairs, and other secrets in a scalable, fault-tolerant cluster that supports the OASIS KMIP standard and deploys in OCI, Microsoft Azure, Amazon AWS, and Google Cloud as well as on-premises on dedicated hardware or virtual machines. 
 

 
 
- API Gateway 
 Oracle Cloud Infrastructure API Gateway enables you to publish APIs with private endpoints that are accessible from within your network, and which you can expose to the public internet if required. The endpoints support API validation, request and response transformation, CORS, authentication and authorization, and request limiting.
 

 
 
- Oracle Services Network 
The Oracle Services Network (OSN) is a conceptual network in Oracle Cloud
 Infrastructure that is reserved for Oracle services. These services have public IP addresses that you can reach over the internet. Hosts outside Oracle Cloud can access the OSN privately by using Oracle Cloud
 Infrastructure FastConnect or VPN Connect. Hosts in your VCNs can access the OSN privately through a service gateway.
 

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that contains one or more data centers, hosting availability domains. Regions are independent of other regions, and vast distances can separate them (across countries or even continents).
 

 
 
- Virtual cloud network (VCN) and subnets 
A VCN is a customizable, software-defined network that you set up in an Oracle Cloud
 Infrastructure region. Like traditional data center networks, VCNs give you control over your network environment. A VCN can have multiple non-overlapping CIDR blocks that you can change after you create the VCN. You can segment a VCN into subnets, which can be scoped to a region or to an availability domain. Each subnet consists of a contiguous range of addresses that don't overlap with the other subnets in the VCN. You can change the size of a subnet after creation. A subnet can be public or private. 
 

 
 
- FastConnect 
 Oracle Cloud
 Infrastructure FastConnect creates a dedicated, private connection between your data center and Oracle Cloud
 Infrastructure . FastConnect provides higher-bandwidth options and a more reliable networking experience when compared with internet-based connections.
 

 
 
- Dynamic routing gateway (DRG) 
The DRG is a virtual router that provides a path for private network traffic between VCNs in the same region, between a VCN and a network outside the region, such as a VCN in another Oracle Cloud
 Infrastructure region, an on
