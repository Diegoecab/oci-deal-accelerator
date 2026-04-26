# Deploy Active Data Guard Far Sync to protect data across Oracle Database@AWS regions

- Source: https://docs.oracle.com/en/solutions/dr-active-dg-farsync-db-at-aws/index.html
- Date: 2025-09
- Type: reference-architecture
- Services: exacs, adg, aws
- Tags: database, multicloud, aws, ha-dr

## Summary (catalog)

Far Sync instance for zero data loss protection across AWS regions. Synchronous redo to local Far Sync, asynchronous to remote standby. Requires cross-region AWS networking for redo transport.

## Architecture (fetched from source)

Architecture

 

 

 The following architecture shows a cross-region disaster recovery
 with Active Data Guard Far Sync with two Far Sync instances running in each OCI region: 
 
 

 
 Description of the illustration cross-region-dr-activedg-farsync.png 

 cross-region-dr-activedg-farsync-oracle.zip 

 
Two Active Data Guard Far Sync instances are created in the corresponding Oracle Cloud
 Infrastructure (OCI) regions. The Primary database in Region 1 sends the redo data in SYNC mode to the local Far Sync instance in
 the same region, which forwards the redo data in
 ASYNC mode to the standby database in the remote Region 2.
 

 
After a role switch and the database in Region 2 becomes the primary, it
 sends the redo data in SYNC mode to its local Far
 Sync instance in the same region, which forwards the redo data in
 ASYNC mode to the standby database in the remote Region 1.
 

 
The Oracle Exadata Database
 Service on Oracle Database@AWS network is connected to the Exadata client subnet using a Dynamic Routing Gateway
 (DRG) managed by Oracle. A DRG is also required to create a peer connection between VCNs
 in different regions. Because only one DRG is allowed per VCN in OCI, a second VCN with
 its own DRG is required to connect the primary and standby VCNs in each region.
 

 
The application is replicated across regions to access the database in the same region
 and achieve the lowest latency and highest performance.

 
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

 
 
- Route table 
Virtual
 route tables contain rules to route traffic from
 subnets to destinations outside a VCN, typically
 through gateways.

 
 
- Network security group
 (NSG) 
NSGs act as virtual firewalls for your cloud resources. With the zero-trust security model of OCI you control the network traffic inside a VCN. An NSG consists of a set of ingress and egress security rules that apply to only a specified set of virtual network interface cards (VNICs) in a single VCN.

 
 
- Local
 peering 
Local peering allows two VCNs
 within the same OCI region to communicate directly
 using private IP addresses. This communication
 does not traverse the internet or your on-premises
 network. Local peering is enabled by a Local
 Peering Gateway (LPG), which serves as the
 connection point between VCNs. Configure an LPG in
 each VCN and establish a peering relationship to
 allow instances, load balancers, and other
 resources in one VCN to securely access resources
 in another VCN within the same region.

 
 
- Dynamic routing gateway
 (DRG) 
The DRG is a
 virtual router that provides a path for private
 network traffic between VCNs in the same region,
 between a VCN and a network outside the region,
 such as a VCN in another OCI region, an
 on-premises network, or a network in another cloud
 provider.

 
 
- Remote
 peering 
Remote
 peering enables private communication between
 resources in different VCNs, which can be located
 in the same or different OCI regions. Each VCN
 uses its own Dynamic Routing Gateway (DRG) for
 remote peering. The DRGs securely route traffic
 between the VCNs over OCI's private backbone,
 allowing resources to communicate using private IP
 addresses without routing traffic over the
 internet or through on-premises networks. Remote
 peering removes the need for internet gateways or
 public IP addresses for instances that need to
 connect across regions.

 
 
- Oracle Exadata Database Service on Dedicated
 Infrastructure 
 Oracle Exadata Database Service on Dedicated
 Infrastructure enables you to leverage the power of Exadata in the cloud. Oracle Exadata Database
 Service delivers proven Oracle Database capabilities on purpose-built, optimized Oracle Exadata infrastructure in the public cloud. Built-in cloud automation, elastic resource scaling, security, and fast performance for all Oracle Database workloads helps you simplify management and reduce costs.
 

 
 
- Oracle Data Guard 
 Oracle Data Guard and Active Data Guard provide a comprehensive set of services that
 create, maintain, manage, and monitor one or more
 standby databases and that enable production
 Oracle databases to remain available without
 interruption. Oracle Data Guard maintains these standby databases as copies of
 the production database by using in-memory
 replication. If the production database becomes
 unavailable due to a planned or an unplanned
 outage, Oracle Data Guard can switch any standby database to the
 production role, minimizing the downtime
 associated with the outage. Oracle Active Data
 Guard provides the additional ability to offload
 read-mostly workloads to standby databases and
 also provides advanced data protection
 features.
 

 
 
- Active Data Guard Far Sync 
 Active Data Guard Far Sync is a lightweight Oracle database instance that
 receives redo data
 synchronously from the primary database and
 forwards it asynchronously to one or more standby
 databases. It ensures zero data loss at any
 distance with minimal impact on the primary
 database performance without requiring a local
 synchronous standby database.
 

 
 
 

 

 
 
Recommendations

 

 
 Use the following recommendations as a starting point.
 Your requirements might differ from the architecture described here. 
 

 
 
- Place Far Sync far enough from the primary database to avoid
 common‑cause failures but close enough to minimize latency. 
 
- Deploy two Far Sync instances per region for high availability. If all
 Far Sync instances in the primary region are unavailable, Active Data Guard 
 redo will be shipped directly to the remote standby in
 ASYNC mode. This removes zero‑data‑loss protection and can
 introduce transport lag, impacting Recovery Point Objectives (RPOs).
 
 
- Ensure storage performance for Far Sync is adequate to sustain
 redo write IOPS comparable to or better than the
 primary database's online redo logs.
 
 
- Configure Active Data Guard across regions for the databases provisioned in the Exadata VM cluster on Oracle Database@AWS by using an OCI Managed network.
 
 
 

 

 
 
Considerations for Cross-Region
 Disaster Recovery

 

 

 When performing cross-region disaster recovery for Oracle Exadata Database
 Service on Oracle Database@AWS , consider the following: 
 
 

 
 
- Configure OCI as the preferred network for better performance, lower latency, higher
 throughput, and reduced cost; the first 10 TB/month of data egress is free across
 regions. 
 
- Although Far Sync is lightweight, disk performance is critical because
 it must persist redo before acknowledging commits to the primary
 database, which if undersized can affect application latency.
 
 
- Network performance of the Far Sync instance is critical for heavy
 workloads. 
 
- With multiple standby databases and Far Sync instances, the
 configuration can get complicated. Use the Active Data Guard broker RedoRoutes property to simplify the
 definition of how redo is transported to the various
 dest
