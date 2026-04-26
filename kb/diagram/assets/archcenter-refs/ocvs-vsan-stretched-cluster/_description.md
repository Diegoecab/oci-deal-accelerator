# Deploy a VMware vSAN Stretched Cluster across OCI Regions with Oracle Cloud VMware Solution

- Source: https://docs.oracle.com/en/solutions/ocvs-vsan-stretched-cluster/index.html
- Date: 2025-07
- Type: reference-architecture
- Services: ocvs
- Tags: vmware, ha-dr

## Summary (catalog)

vSAN Stretched Cluster across OCI regions for VMware HA/DR. Synchronous storage replication between sites, automatic VM restart on site failure. Witness host in third location.

## Architecture (fetched from source)

Architecture

 

 
This architecture shows how you can deploy custom VMware vSAN stretched
 clusters across multiple OCI regions.

 
The high-level topology consists of:

 
 
- Primary Site : Oracle Cloud VMware Solution SDDC deployed in OCI Dedicated Region A.
 
 
- Secondary Site : Oracle Cloud VMware Solution SDDC deployed in OCI Dedicated Region B.
 
 
- Witness Site : A regionally separate location for deploying the
 VMware vSAN Witness Appliance.
 
 
 
Communication across these sites is established through OCI’s private
 backbone and OCI FastConnect , both of which are mandatory to meet the low-latency and high-bandwidth requirements
 of a stable VMware vSAN stretched cluster.
 

 

 
Note:
IPSec VPN is not supported for this configuration.
 

 
The following diagram illustrates this architecture.

 
 Description of the illustration ocvs-vsan-stretched-cluster.png 

 ocvs-vsan-stretched-cluster-oracle.zip 

 
The following sections outline the key technical considerations that
 influence a successful deployment of a VMware vSAN stretched cluster in Oracle Cloud VMware Solution across OCI Dedicated Region s.
 

 
 Networking Considerations 

 
A key enabler of this architecture is the robust OCI backbone network 
 that interconnects OCI Dedicated Region s within a customer tenancy. This backbone ensures the high-speed, low-latency
 communication necessary for VMware vSAN replication traffic and heartbeat signaling
 between sites.
 

 
Key factors to plan for:

 
 
- Establish Remote Peering Connections (RPCs) between the VCNs in
 OCI Dedicated Region A and OCI Dedicated Region B using Dynamic Routing Gateways (DRGs) . This enables full mesh
 connectivity across all VMware ESXi hosts.
 
 
- Use OCI FastConnect (not IPSec VPN) to connect both OCI Dedicated Region s to the public OCI region hosting the Witness. This ensures consistent
 low-latency and reliable throughput to support witness communication.
 
 
- Reference documentation: Remote Peering , Managing DRGs , OCI FastConnect 
 
 
 Compute and Storage Considerations 

 
Infrastructure planning across all three regions involves several
 decisions:

 
 
- Region Selection 
 
- Choose two OCI Dedicated Region s with < 5 ms RTT latency between them.
 
 
- Select a public OCI region with < 200 ms RTT latency
 to both OCI Dedicated Region s for Witness deployment.
 
 
 
 
- Shape Selection 
 
- Use Dense Bare Metal shapes (e.g., BM.DenseIO.E5.128)
 with local NVMe storage for VMware vSAN.
 
 
- Avoid Standard shapes that use Block Volumes, as they are
 not suitable for stretched vSAN deployments.
 
 
 
 
- Minimum Host Requirements 
 
- Primary Region : Minimum three Dense Bare Metal hosts
 
 
- Secondary Region : Minimum three Dense Bare Metal
 hosts
 
 
- Witness Region : One Bare Metal host
 
 
 
 
- Witness Appliance Guidelines 
 
- Follow vSAN Witness Design
 guidance .
 
 
- Always refer to the official documentation from Broadcom to get
 the latest updates as the requirements could change. Below are some
 references:
 
 
- Stretched cluster
 considerations in VCF 5.1.2 
 
- Minimum host count
 for vSAN stretched clusters 
 
 
 
 
 
 
 Stretched Cluster Requirements 

 
 
- RTT latency < 5 ms between Primary and Secondary Regions 
 
- RTT latency < 200 ms between either site and the Witness node 
 
- All hosts (including Witness) must belong to the same VMware vSAN
 cluster 
 
- Host hardware and configuration must be identical across regions 
 
- Witness must reside in a third, separate location 
 
 
 Operational Considerations 

 
Customers are responsible for completing Day 2 operations manually. Key
 notes:

 
 
- Oracle Cloud VMware Solution environments are deployed separately in each OCI Dedicated Region . The secondary site’s VMware vCenter and VMware NSX Manager must be manually
 detached and integrated with the primary cluster.
 
 
- Manual failover and route updates are required in case of a site
 failure. 
 
- VMware NSX Tier-0 Gateway is active only in one site, implying an
 active-passive model for North-South traffic routing. 
 
 

 

 
 
Design Overview

 

 
Building on the previous sections that covered architecture and requirements
 for a stretched vSAN configuration with Oracle Cloud VMware Solution , this section explains how to implement a highly available design capable of withstanding
 the failure of an OCI Dedicated Region .
 

 
This design uses two VCNs per site , resulting in a total of four VCNs :
 

 
 OCI Dedicated Region A 

 
 
- VCN Primary with two CIDR blocks; for example,
 10.16.0.0/16 as the primary and 172.45.0.0/16 
 as the secondary CIDR (added after VCN creation). The secondary CIDR is required
 only for the initial SDDC deployment.
 
Since an Oracle Cloud VMware Solution SDDC cannot span multiple VCNs, a secondary CIDR block
 ( 172.45.0.0/16 ) is attached to the Primary VCN within OCI Dedicated Region A. This enables VLAN definitions for management and services subnets while
 keeping them logically grouped within a single VCN.
 

 
 
- VCN MGMT Active , using the same CIDR block as
 the secondary CIDR attached to VCN Primary; i.e.,
 172.45.0.0/16 .
 
 
 
 OCI Dedicated Region B 

 
 
- VCN Secondary with a CIDR block distinct from
 and non-overlapping with VCN Primary ; for example,
 10.17.0.0/16 .
 
 
- VCN MGMT Failover , using the same CIDR block as
 VCN MGMT Active ; i.e., 172.45.0.0/16 .
 
 
 
 Oracle Cloud VMware Solution provides flexibility in network provisioning. During SDDC creation, users can
 either:
 

 
 
- Specify a CIDR block and allow Oracle Cloud VMware Solution automation to create required networking components, or
 
 
- Manually create VCNs, subnets, VLANs, route tables, and NSGs beforehand, then select
 these existing resources during deployment. 
 
 
For this stretched vSAN design, the latter approach is necessary. Precise
 control over network segmentation across multiple VCNs and regions requires pre-creation
 of route tables, NSGs, and VLANs. This separation supports clear responsibilities
 between VCNs and enables seamless failover behavior.

 
A critical aspect is that the management subnet
 ( 172.45.0.0/16 ) must be accessible in both OCI Dedicated Region s. To support failover, the design allows this VCN MGMT network to “float” between the
 two sites via manual network updates during failover events, such as modifying route
 tables and re-advertising the subnet through DRG attachments.
 

 
DNS resolution is vital for failover and service availability. Therefore, a dedicated
 services subnet will be created in each VCN to host DNS and supporting
 infrastructure.
 

 
For VLAN tagging simplicity:

 
 
- VLAN tags in the 100 range are region-specific , confined to their
 respective sites.
 
 
- VLAN tags in the 200 range are associated with the
 172.45.0.0/16 subnet and will float between sites .
 
 
 
With the high-level design defined, we now step into the practical configuration of each
 site, starting with the Primary region.

 

 

 

 

 

 
 Title and Copyright Information 

 

 
Deploy a VMware vSAN Stretched Cluster across OCI Regions with Oracle Cloud VMware Solution

 
G36844-01

 
July 2025

 
 Copyright © 2025, 

Oracle and/or its affiliates.
