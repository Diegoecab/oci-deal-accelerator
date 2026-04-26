# Use remote synchronous block replication on Oracle Cloud Infrastructure

- Source: https://docs.oracle.com/en/solutions/remote-synchronous-block-replication-oci/index.html
- Date: 2024-10
- Type: reference-architecture
- Services: block-storage, compute
- Tags: ha-dr

## Summary (catalog)

Block volume cross-region replication for non-database workloads. Synchronous replication for RPO=0 within same metro, asynchronous for cross-region DR with configurable RPO.

## Architecture (fetched from source)

Architecture

 

 
This architecture implements a highly available block device on Oracle Cloud
 Infrastructure (OCI), fully tolerant to a failure at the level of business application. Use this
 architecture for performance-sensitive applications that require continuity at the same
 time.
 

 
This architecture will provide a single entity, iSCSI block device to users. This device
 will be always available, regardless of single-component failures. Any other
 architecture components will be hidden from users. The architecture is fully automated
 in case of a failure or switchover. The only effect users will notice in case of failure
 or switchover will be performance degradation of the iSCSI device by around 50% for one
 or two seconds.

 
Implementation of a single, always-available block devices requires the following.

 
 
- Three compute instances, virtual machines, or bare metal (BM). The
 latter may be preferable as they have stable performance. 
 
- Two VCNs: one public, one private. 
 
- Two block volumes of your target always-available device. 
 
- (Recommended) Have the block volumes at least 10 VPU. You may want to
 consider an even higher level of IOPS, depending on the aggressiveness of your I/O
 throughput, and the distance between the mirrored hosts (and block volumes). 
 
 
Therefore, the cost of implementing an always-available block device is three
 times the cost of the compute instance plus two times the cost of the device itself.

 
The following diagram illustrates this reference architecture.

 
 Description of the illustration remote-synchronous-block-replication-diagram.png 

 remote-synchronous-block-replication-diagram-oracle.zip 

 
The architecture has the following components:

 
 
- Distributed Replicated Block Device 
Distributed
 Replicated Block Device (DRBD) is a Linux kernel driver that maintains network
 connection between two block devices on remote Linux instances, and replicates
 I/O operations from the source instance to the destination instance.

 
 
- Pacemaker 
Pacemaker is an open-source high-availability cluster
 resource manager, commonly used in Linux environments. It ensures that
 applications, services, or resources run continuously with minimal downtime by
 detecting failures and automatically restarting or relocating services on other
 nodes in a cluster.

 
 
- Corosync 
Corosync is an open source software
 product that extends Pacemaker with semantics of restoration in the case of
 split brain.

 
 
- iSCSI initiator and target 
iSCSI is a client and
 server software component that provides an SCSI device over a network.

 
 
 

 

 
 
Recommendations

 

 
 Use the following recommendations as a starting point to <rest of sentence.> Your requirements might differ from the architecture described here. 
 

 
 
- VCN 
When you create a VCN, determine the number of CIDR blocks required and the size of each block based on the number of resources that you plan to attach to subnets in the VCN. Use CIDR blocks that are within the standard private IP address space.

 
Select CIDR blocks that don't overlap with any other network (in Oracle Cloud
 Infrastructure , your on-premises data center, or another cloud provider) to which you intend to set up private connections.
 

 
After you create a VCN, you can change, add, and remove its CIDR blocks.

 
When you design the subnets, consider your traffic flow and security requirements. Attach all the resources within a specific tier or role to the same subnet, which can serve as a security boundary.

 
 
- Cloud Guard 
Clone and customize the default recipes provided by Oracle to create custom detector and responder recipes. These recipes enable you to specify what type of security violations generate a warning and what actions are allowed to be performed on them. For example, you might want to detect Object Storage buckets that have visibility set to public. 

 
Apply Cloud Guard at the tenancy level to cover the broadest scope and to reduce the administrative burden of maintaining multiple configurations.

 
You can also use the Managed List feature to apply certain configurations to detectors.

 
 
- Security Zones 
For resources that require maximum security, Oracle recommends that you use security zones. A security zone is a compartment associated with an Oracle-defined recipe of security policies that are based on best practices. For example, the resources in a security zone must not be accessible from the public internet and they must be encrypted using customer-managed keys. When you create and update resources in a security zone, Oracle Cloud
 Infrastructure validates the operations against the policies in the security-zone recipe, and denies operations that violate any of the policies.
 

 
 
- Network security groups (NSGs) 
You can use NSGs to define a set of ingress and egress rules that apply to specific VNICs. We recommend using NSGs rather than security lists, because NSGs enable you to separate the VCN's subnet architecture from the security requirements of your application.

 
 
- Load balancer bandwidth 
While creating the load balancer, you can either select a predefined shape that provides a fixed bandwidth, or specify a custom (flexible) shape where you set a bandwidth range and let the service scale the bandwidth automatically based on traffic patterns. With either approach, you can change the shape at any time after creating the load balancer. 

 
 
 

 

 
 
Considerations

 

 
Consider the following when deploying this reference
 architecture.

 
 
- Performance 
You should plan two times N of nominal
 IOPS on your always-available device in order to provide N IOPS to your users.
 This is caused by the fact that half of the performance is spent on real-time
 mirroring.

 
 
- Security 
We strongly recommend isolating
 implementation details by splitting the solution to public and private
 networks.

 
 
- Availability 
We recommend implementing
 always-available device as iSCSI for this technology is OS-agnostic, so users
 can enjoy true fault tolerance whether they run Linux or Windows on their
 machines.

 
All the software components of the solution are publicly
 available as open-source products. In particular, the DRBD driver is an integral
 component of the vanilla Linux kernel and is available in any Linux
 distro.

 
 
 

 

 
 
Explore More

 

 
Learn more about the products and technologies used in this reference
 architecture.

 
Review these additional resources:

 
 
- Best practices framework
 for Oracle Cloud Infrastructure 
 
- DRBD technology 
 
- Pacemaker 
 
- Corosync 
 
 

 

 
 
Acknowledgments

 

 
 
- Authors : Andrea Del Monaco, Yuri Rassokhin 
 
- Contributors : Alessio Comisso, Deepak Soni, John
 Sulyok 
 
 

 

 

 

 

 
 Title and Copyright Information 

 

 
Use remote synchronous block replication on Oracle Cloud Infrastructure

 
G10241-01

 
October 2024

 
 Copyright © 2024, 

Oracle and/or its affiliates.
