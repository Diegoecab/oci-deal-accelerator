# Implement disaster recovery with local and regional standbys on Oracle Database@AWS

- Source: https://docs.oracle.com/en/solutions/dr-local-regional-standby-db-at-aws/index.html
- Date: 2025-09
- Type: reference-architecture
- Services: exacs, adg, aws, fsdr
- Tags: database, multicloud, aws, ha-dr

## Summary (catalog)

Local standby for HA within same AWS region, regional standby for DR. Active Data Guard with Fast-Start Failover for automated failover. Full Stack DR service for cross-service failover orchestration.

## Architecture (fetched from source)

Architecture

 

 

 
 
This architecture shows Oracle Exadata Database
 Service on Oracle Database@AWS in a disaster recovery topology using two standby databases:
 

 
 
 
- A local standby in the same region as the primary but in a different availability
 zone. 
 
- A remote standby in a different region. 
 
 
 

 
 Description of the illustration exadb-dbaws-dr-arch.png 

 exadb-dbaws-dr-arch-oracle.zip 

 
Oracle Database runs in an Exadata VM cluster in the primary Region
 1 . For data protection and disaster recovery, Active Data Guard replicates the data to the following two Exadata VM clusters:
 

 
 
- One in the same region but in a different availability zone (local
 standby). A local standby is ideal for failover scenarios, offering zero data loss
 for local failures while applications continue to operate without the performance
 overhead of communicating with a remote region. 
 
- A second standby in a different region (remote standby). A remote
 standby is typically used for disaster recovery or to offload read-only
 workloads. 
 
 
Although Active Data Guard network traffic can traverse the AWS backbone, Oracle recommends this architecture
 which routes it over OCI for optimized throughput and latency.
 

 
The Oracle Exadata Database
 Service on Oracle Database@AWS network is connected to the Exadata client subnet using a Dynamic Routing Gateway
 (DRG) managed by Oracle. A DRG is also required to create a peer connection between VCNs
 in different regions. Because only one DRG is allowed per VCN in OCI, a second VCN with
 its own DRG is required to connect the primary and standby VCNs in each region.
 

 
 
- The primary Exadata VM cluster is deployed in Region
 1 , availability zone 1 in VCN1 with CIDR
 10.10.0.0/16 and client subnet CIDR
 10.10.1.0/24 .
 
 
- VCN1 has Local Peering Gateways (LPGs) LPG1
 remote and LPG1 local .
 
 
- The Hub VCN in the primary Region 1 is Hub
 VCN1 with CIDR 10.11.0.0/16 .
 
 
- The first standby Exadata VM Cluster is deployed in Region
 1 , availability zone 2 in VCN2 with
 CIDR 10.20.0.0/16 and client subnet CIDR
 10.20.1.0/24 .
 
 
- VCN2 has two LPGs LPG2 remote and
 LPG2 local .
 
 
- The Hub VCN is the same as the Hub VCN for the Primary database,
 Hub VCN1 as it resides in the same region.
 
 
- Hub VCN1 has LPG Hub LPG1 and
 Hub LPG2 and DRG1 .
 
 
- The second standby Exadata VM cluster is deployed in Region
 2 in VCN3 with CIDR 10.30.0.0/16 and
 client subnet CIDR 10.30.1.0/24 .
 
 
- VCN3 has a LPG LPG3 remote .
 
 
- The Hub VCN in the remote standby Region 2 is
 Hub VCN3 with CIDR 10.33.0.0/16 .
 
 
- Hub VCN3 has a LPG Hub LPG3 and DRG
 DRG3 .
 
 
- No subnet is required for the hub VCNs to enable transit routing.
 Therefore, these VCNs can use very small IP CIDR ranges. 
 
 
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
 

 
 
 

 

 
 
Recommendations

 

 
 Use the following recommendations as a starting point
 when performing disaster recovery for Oracle Exadata Database
 Service on Oracle Database@AWS . Your requirements might differ from the architecture described here. 
 

 
 
- Use Active Data Guard for comprehensive data corruption prevention with automatic block repair, online
 upgrades and migrations, and to offload the workload to standby with read-mostly
 scale-out.
 
 
- Enable Application Continuity to mask database outages during planned and unplanned events from end-users.
 
 
- Configure automatic backups to Oracle Database Autonomous
 Recovery Service in OCI. Although data is protected by Oracle Data Guard , minimize the backup workload on the database by implementing the
 incremental-forever backup strategy that eliminates weekly
 full backups. Alternatively, use Amazon Simple Storage Service for automatic b
