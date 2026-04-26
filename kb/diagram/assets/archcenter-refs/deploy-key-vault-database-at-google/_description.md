# Deploy Oracle Key Vault with Oracle Exadata Database Service (Oracle Database@Google Cloud)

- Source: https://docs.oracle.com/en/solutions/deploy-key-vault-database-at-google/index.html
- Date: 2025-01
- Type: reference-architecture
- Services: exacs, vault, google-cloud
- Tags: database, multicloud, security

## Summary (catalog)

Oracle Key Vault deployment for TDE key management on ExaCS in Database@Google Cloud. Centralized encryption key lifecycle management across multiple database deployments.

## Architecture (fetched from source)

Architecture

 

 
This architecture shows how to deploy Oracle Key Vault on a Google Cloud virtual machine (VM) as a secure long-term external key management storage for Oracle Exadata Database
 Service encryption keys in Oracle Database@Google Cloud .
 

 
The architecture diagram depicts the recommended Oracle Key Vault multi-master cluster in Google Cloud to provide continuously available, extremely scalable, and fault-tolerant key
 management for the Oracle Database in Oracle Exadata Database
 Service ( Oracle Database@Google Cloud ).
 

 
Two Oracle Key Vault nodes in the same zone form a read/write pair, providing continuous read
 availability. This is because when one of the two nodes is non-operational, then the
 remaining node is set to be in the read-only restricted mode. When a read/write node is
 again able to communicate with its read/write peer, then the node reverts back to
 read/write mode from read-only restricted mode. Four nodes (as shown in the architecture
 diagram) provide continuous read/write availability.
 

 
 Oracle Key Vault can be deployed on-premises, in OCI, Google Cloud , Microsoft Azure , and Amazon Web Services , as long as network connectivity can be established. Stretched Oracle Key Vault clusters (on-premises to cloud, or across cloud providers) are also possible, giving
 you maximum deployment flexibility and local availability of your encryption keys. Oracle Key Vault provides "hold your own key" functionality out of the box, without the need for an
 additional, expensive third-party key management appliance.
 

 
The following diagram illustrates this reference architecture.

 
 Description of the illustration key-vault-database-google-diagram.png 

 key-vault-database-google.zip 

 
The architecture has the following components:

 
 
- Google Cloud Region 
Google and OCI regions are localized geographic
 areas. For Oracle Database@Google Cloud , a Google Cloud region is connected to an OCI region. A zone in Google Cloud is connected to an availability domain in OCI. Google Cloud and OCI region pairs are selected to minimize distance and latency.
 

 
 
- Google Cloud zone 
A zone is a physically separate data center within a
 region that is designed to be available and fault tolerant. Zones are close
 enough to have low-latency connections to other zones.

 
 
- Google Cloud Virtual Private Cloud 
 Google Cloud Virtual Private Cloud (VPC) is the fundamental building block for your
 private network in Google Cloud . VPC enables many types of Google Cloud resources, such as Google virtual machines (VM), to securely communicate with each other, the internet,
 and on-premises networks.
 

 
 
- Exadata Database Service on Dedicated Infrastructure 
 Oracle Exadata Database
 Service delivers proven Oracle Database capabilities on purpose-built, optimized
 Oracle Exadata infrastructure in the public cloud. Built-in cloud automation,
 elastic resource scaling, security, and fast performance for OLTP, in-memory
 analytics, and converged Oracle Database workloads help simplify management and
 reduce costs.
 

 
Exadata Cloud Infrastructure X9M brings more
 CPU cores, increased storage, and a faster network fabric to the public cloud.
 Exadata X9M storage servers include Exadata RDMA Memory (XRMEM), creating an
 additional tier of storage, boosting overall system performance. Exadata X9M
 combines XRMEM with innovative RDMA algorithms that bypass the network and I/O
 stack, eliminating expensive CPU interrupts and context switches.

 
Exadata Cloud Infrastructure X9M increases the throughput of its
 100 Gbps active-active Remote Direct Memory Access over Converged Ethernet
 (RoCE) internal network fabric, providing a faster interconnect than previous
 generations with extremely low-latency between all compute and storage
 servers.

 
 
- Oracle Database@Google Cloud 
 Oracle Database@Google Cloud is the Oracle Database service ( Oracle Exadata Database Service on Dedicated
 Infrastructure or Oracle Autonomous Database Serverless ) running on Oracle Cloud
 Infrastructure (OCI), deployed in Google Cloud data centers. The service offers features and price parity with OCI. Users
 purchase the service on Google Cloud Marketplace.
 

 
 Oracle Database@Google Cloud integrates Oracle Exadata Database
 Service , Oracle Real Application Clusters (Oracle
 RAC) , and Oracle Data Guard technologies into the Google Cloud platform. Oracle Database@Google Cloud offers the same low latency as other Google -native services and meets mission-critical workloads and cloud-native
 development needs. Users manage the service on the Google console and with Google automation tools. The service is deployed in Google Virtual Private Cloud (VPC) and integrated with the Google identity and access management system. The OCI and Oracle Database metrics and audit logs are natively available in Google . The service requires that users have an Google tenancy and an OCI tenancy.
 

 
 
- Key Vault 
 Oracle Key Vault securely stores encryption keys, Oracle Wallets, Java KeyStores, SSH key
 pairs, and other secrets in a scalable, fault-tolerant cluster that supports the
 OASIS KMIP standard and deploys in Oracle Cloud
 Infrastructure , Google Cloud , Microsoft Azure , and Amazon Web Services as well as on-premises on dedicated hardware or virtual machines.
 

 
 
 

 

 
 
Recommendations

 

 
 Use the following recommendations as a starting point.
 Your requirements might differ from the architecture described here. 
 

 
 
- Oracle Key Vault ISO 
To build the right Oracle Key Vault solution, make sure to use the latest Oracle Key Vault installation medium. See Explore More for the Oracle Software
 Delivery Cloud link.
 

 
 
- Oracle Key Vault Image Building 
To build the Oracle Key Vault image from the ISO, do so on a local system with at least 1 TB of storage
 with at least 32 GB in RAM. Create the virtual hard disk as
 Fixed size and in the VHD 
 format.
 

 
 
- Multi-Master Cluster 
Deploy Oracle Key Vault as a multi-node cluster to achieve maximum availability
 and reliability with read/write pairs of Oracle Key Vault nodes.
 

 
 Oracle Key Vault multi-master cluster is created with a first node, then
 additional nodes can be subsequently inducted to eventually
 form a multi-node cluster with up to 8 read/write pairs.
 
 

 
The initial node is in read-only
 restricted mode and no critical data can be added to it.
 Oracle recommends to deploy a second node to form a
 read/write pair with the first node. After which, the
 cluster can be expanded with read/write pairs so that both
 critical and non-critical data can be added to the
 read/write nodes. Read-only nodes can help with load
 balancing or operation continuity during maintenance
 operations.

 
Refer to the documentation to
 learn how a multi-master cluster affects endpoints, both in
 the way an endpoint connects and with restrictions.

 
For large deployments, install at least four Oracle Key Vault servers. Endpoints should be enrolled by making them
 unique and balanced across the four servers to ensure high
 availability. For example, if a data center has 1,000
 database endpoints to register, and you have four Oracle Key Vault servers to accommodate them, then enroll 250 endpoints
 across each of the four servers.
 

 
Ensure
 that the system clocks of the endpoint host and the Oracle Key Vault server are in sync. For Oracle Key Vault server, setting up NTP is required.
 

 
 
- Read/Write Pair 
A pair of nodes that operates with
 bidirectional synchronous replication. The read/write pair
 by is created by pairing a new node with a read-only node.
 Data can be updated, including the endpoint and wallet data,
 in either node by using the Oracle Key Vault management console, or Oracle Key Vault client software. The updates are replicated immediately
 to the other node in the pair. Updates are replicated
 asynchronously to all other nodes.
 

 
A node
 can be a member of at most one bi
