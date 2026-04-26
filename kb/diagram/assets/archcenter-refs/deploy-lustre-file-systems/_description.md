# Deploy Lustre file systems in Oracle Cloud

- Source: https://docs.oracle.com/en/solutions/deploy-lustre-file-systems/index.html
- Date: 2025-04
- Type: reference-architecture
- Services: compute, file-storage
- Tags: hpc

## Summary (catalog)

Lustre parallel file system on OCI for HPC workloads. High-throughput storage for compute-intensive applications. Bare metal instances for Lustre servers, RDMA networking for low-latency I/O.

## Architecture (fetched from source)

Architecture

 

 
This architecture shows Lustre communications within a virtual cloud
 network (VCN). All Lustre components are deployed in the same
 availability domain across multiple fault domains for high availability. Lustre file
 systems can be mounted from OCI compute instances (both virtual machines and bare metal
 instances) and containerized environments such as Oracle Cloud Infrastructure Kubernetes Engine (OKE).
 

 
The following diagram illustrates the high-level architecture of the underlying
 Lustre components deployed and managed by Oracle Cloud, and the customer managed
 components.

 
 Description of the illustration lustre-file-system-oci-arch.png 

 lustre-file-system-oci-arch.zip 

 
The architecture has the following OCI components:

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that contains one or more data centers, hosting availability domains. Regions are independent of other regions, and vast distances can separate them (across countries or even continents).
 

 
 
- Availability domains 
Availability domains are standalone, independent data centers within a region. The physical resources in each availability domain are isolated from the resources in the other availability domains, which provides fault tolerance. Availability domains don’t share infrastructure such as power or cooling, or the internal availability domain network. So, a failure at one availability domain shouldn't affect the other availability domains in the region.

 
OCI File Storage with Lustre is deployed in a single
 availability domain.

 
 
- Fault domains 
A fault domain is a grouping of hardware and infrastructure within an availability domain. Each availability domain has three fault domains with independent power and hardware. When you distribute resources across multiple fault domains, your applications can tolerate physical server failure, system maintenance, and power failures inside a fault domain.

 
OCI File Storage with Lustre components are deployed in
 multiple fault domains to provide redundancy and high availability.

 
 
- Virtual cloud network (VCN) and subnets 
A VCN is a customizable, software-defined network that you set up in an Oracle Cloud
 Infrastructure region. Like traditional data center networks, VCNs give you control over your network environment. A VCN can have multiple non-overlapping CIDR blocks that you can change after you create the VCN. You can segment a VCN into subnets, which can be scoped to a region or to an availability domain. Each subnet consists of a contiguous range of addresses that don't overlap with the other subnets in the VCN. You can change the size of a subnet after creation. A subnet can be public or private. 
 

 
OCI File Storage with Lustre is accessed via VCN,
 and is deployed in a customer managed subnet.

 
 
 
The architecture has the following Lustre components. All components except
 MGT are added as more capacity is needed:

 
 
- Lustre storage volume (object storage target, or OST) 
These are the volumes where file data is stored.

 
 
- Meta data volume (meta data target, or MDT) 
File
 meta data such as file names and attributes get stored on these
 volumes.

 
 
- Lustre management volume (management target, or MGT) 
Only one exists for a file system. This is a volume used for storing
 configuration information of the Lustre file system.

 
 
- Storage server hosting one or more storage targets (OSS) 
These are virtual or bare metal compute instances.

 
 
- Meta data server hosting one or more meta data targets (MDS) 
These are virtual or bare metal compute instances.

 
 
- LNet (Lustre networking) 
LNet is a virtual networking layer which allows
 Lustre nodes (including clients) to communicate with each other. LNet hides the
 complexities of underlying network protocols, allowing Lustre to operate
 transparently across various network types like Ethernet and
 InfiniBand.

 
 
- VCN and subnets 
Lustre file system's core data
 communication relies on VCNs and subnets. This includes communication between
 client and servers as well as server to server.

 
 
 

 

 
 
About Required Services and
 Policies

 

 
This solution requires the following services and policies:

 
 
- Oracle Cloud Infrastructure File Storage with Lustre 
 
- Oracle Cloud Infrastructure Identity
 and Access Management 
 
- Oracle Cloud
 Infrastructure Virtual Cloud Network
 
 
 
The policies required for each service are listed below. To get started quickly, you
 may consider implementing the following policies and security rules in the subnet. To
 adhere to the principle of least privilege, the specific policies needed will vary
 depending on your organization's security needs. See the Lustre documentation for a full
 list of policies required to manage Lustre file systems in OCI.

 

 
 
 
 Service Name: OCI IAM Policy Group 
 Required to... 
 
 
 
 
 Oracle Cloud Infrastructure File Storage with Lustre:
 lustre-admin-group 
 
 
 
 
- Create and manage Lustre file system. 
 
- Use and access VCN resources. 
 
- Manage and access components such as VNICs and OCI Vault. 
 
- Access OCI Vault keys when encryption at rest is required. 
 
 
 
 
 
 
 

 
The following permissions are required for File Storage with Lustre:

 allow service lustrefs to use virtual-network-family in tenancy 

The following rule is required for security list ingress:

 Stateful ingress from source workload subnet CIDR, source port 512-1023 and destination Lustre subnet CIDR, destination TCP port 988 

The following rule is required for security list egress:

 Egress to 0.0.0.0/0 to all protocols 

See Oracle Products, Solutions, and Services to get what you need.
 

 

 

 
 
About OCI File Storage with Lustre
 Shared Responsibility Model

 

 

 OCI provides APIs, SDKs, a command line interface, the OCI Console,
 and file system metrics to manage Lustre file systems. 
 
 

 
OCI File Storage with Lustre enables you to create, manage, and monitor the
 file system. The service will automate the provisioning and management of the required
 Lustre components such as Lustre storage servers and Lustre storage targets. OCI is
 responsible for the provisioning and managing the back-end components such as storage
 servers and storage volumes. As illustrated in the architecture diagram, the storage
 servers are interconnected using a customer's subnet for Lustre communication. The
 security lists, routing tables, security groups and other VCN related configurations are
 managed by you, the customer.

 

 

 
 
Considerations for Subnet Security
 Lists, IAM Policies, and Lustre Clients

 

 
When implementing File Storage with Lustre, review the following
 considerations. These must be in place before creating Lustre file
 systems.

 
 
- Storage capacity and service limits 
Ensure your
 tenancy has service limit quota to support creating new file
 systems.

 
 
- Sufficient IP addresses 
Ensure the Lustre subnet
 has sufficient IP addresses to assign to file system
 resources. See the Configure Lustre Connectivity section to
 learn more.

 
 
- Subnet security and IAM policies 
If the following
 are not configured correctly, the file system creation will
 fail after timing out during the provisioning stage.

 
 
- The security rules and/or security groups
 must be configured to allow port 988 communication
 between Lustre servers and clients. 
 
- Ensure that lustrefs has
 permissions to use
 virtual-network-family in the
 tenancy.
 
 
 
See the About Required Services and Policies
 section to learn more.

 
 
- Lustre client packages 
Use Lustre
 client version 2.15.5 with Ubuntu running 5.14.x kernel and
 Oracle Linux 8 or 9 running a Redhat Compatible Kernel
 (RHCK) version 4.18.x or 5.15.x. The Lustre DKLM modules
 make the Lustre client package flexible to run in different
 kernel versions. If you have questions about the Lustre
 client, contact OCI support.

 
 
- Firewalls on Lustre clients 
By 
