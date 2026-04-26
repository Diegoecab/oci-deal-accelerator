# Move to Oracle Database@Azure with Oracle Zero Downtime Migration

- Source: https://docs.oracle.com/en/solutions/oracle-db-at-azure-migration/index.html
- Date: 2024-12
- Type: reference-architecture
- Services: exacs, azure, goldengate
- Tags: database, multicloud, azure, migration

## Summary (catalog)

Zero Downtime Migration to Database@Azure using logical or physical online migration. GoldenGate for continuous replication during cutover. Supports on-premises Oracle DB to ExaCS on Database@Azure.

## Architecture (fetched from source)

Architecture

 

 
This reference architecture describes Oracle Database migrations from on-premises to Oracle Exadata Database Service on Dedicated
 Infrastructure on Oracle Database@Azure using the physical online migration workflow based on Oracle Data Guard and direct data transfer, providing simplicity, automation, and business
 continuity during your database migrations to Oracle Database@Azure .
 

 
The Oracle Zero Downtime Migration service host is installed on a separate on-premises virtual machine (VM)
 next to the source database. The target Oracle Exadata Database Service on Dedicated
 Infrastructure is provisioned in Azure ’s data center within the Azure Virtual Network (VNet) in a delegated subnet to Oracle Database@Azure . The on-premises data center is connected to Azure ’s data center via Azure ExpressRoute or site-to-site VPN. The Oracle Zero Downtime Migration physical online workflow based on direct data transfer creates the target
 database by using the restore from a service method and avoids backing up
 the source database to an intermediate storage location. Oracle Zero Downtime Migration automatically leverages Oracle Data Guard to replicate the data from the on-premises database to the target
 database. Oracle Zero Downtime Migration automatically sets up Oracle Data Guard , maintains it, and cleans up the configuration after the migration
 completes. Hence, knowledge in setting up and maintaining Oracle Data Guard is not required. After the migration completes, the target database can
 use the Automatic Backup feature to back up the database into Oracle Database Autonomous
 Recovery Service .
 

 
The following diagram illustrates this reference architecture.

 
 Description of the illustration oracle-db-azure-zdm.png 

 oracle-db-azure-zdm-oracle.zip 

 
 Microsoft Azure provides the following components:
 

 
 
- Azure VNIC 
The services in Azure data centers have physical network interface cards
 (NICs). Virtual machine instances communicate using virtual
 NICs (VNICs) associated with the physical NICs. Each
 instance has a primary VNIC that's automatically created and
 attached during launch and is available during the
 instance's lifetime.
 

 
 
- Azure Virtual Network Gateway 
 Azure Virtual Network Gateway is a service that establishes
 secure, cross-premises connectivity between an Azure virtual network and an on-premises network. It allows you
 to create a hybrid network that spans your data center and
 Azure .
 

 
 
- Azure Delegated subnet 
Subnet delegation is
 Microsoft's ability to inject a managed service,
 specifically a platform-as-a-service service, directly into
 your virtual network. This means you can designate or
 delegate a subnet to be a home for an external managed
 service inside your virtual network. In other words, that
 external service will act as a virtual network resource,
 even though it technically is an external
 platform-as-a-service service.

 
 
- Azure Virtual Network 
 Azure Virtual Network (VNet) is the fundamental building block
 for your private network in Azure . VNet enables many Azure resources, such as Azure virtual machines, to securely communicate with each
 other, the internet, and on-premises networks.
 

 
 
 
 Oracle Cloud
 Infrastructure provides the following components:
 

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that contains one or more data centers, called availability domains. Regions are independent of other regions, and vast distances can separate them (across countries or even continents).
 

 
 
- Virtual cloud network (VCN) and subnets 
A VCN is a customizable, software-defined network that you set up in an Oracle Cloud
 Infrastructure region. Like traditional data center networks, VCNs give you control over your network environment. A VCN can have multiple non-overlapping CIDR blocks that you can change after you create the VCN. You can segment a VCN into subnets, which can be scoped to a region or to an availability domain. Each subnet consists of a contiguous range of addresses that don't overlap with the other subnets in the VCN. You can change the size of a subnet after creation. A subnet can be public or private. 
 

 
 
- On-premises network 
This network is the local network used by your organization. It is one of the spokes of the topology.

 
 
- Service gateway 
The service gateway provides access from a VCN to other services, such as Oracle Cloud
 Infrastructure Object Storage . The traffic from the VCN to the Oracle service travels over the Oracle network fabric and does not traverse the internet.
 

 
 
- Data Guard 
 Oracle Data Guard and Oracle Active Data Guard provide a comprehensive set of services that create, maintain, manage, and monitor one or more standby databases and that enable production Oracle databases to remain available without interruption. Oracle Data Guard maintains these standby databases as copies of the production database by using in-memory replication. If the production database becomes unavailable due to a planned or an unplanned outage, Oracle Data Guard can switch any standby database to the production role, minimizing the downtime associated with the outage. Oracle Active Data Guard provides the additional ability to offload read-mostly workloads to standby databases and also provides advanced data protection features.
 

 
 
- Exadata Database Service 
 Oracle Exadata Database
 Service enables you to leverage the power of Exadata in the cloud. You can provision
 flexible Exadata X9M systems that allow you to add database compute servers and
 storage servers to your system as your needs grow. Exadata X9M systems offer
 RDMA over Converged Ethernet (RoCE) networking for high bandwidth and low
 latency, persistent memory (PMEM) modules, and intelligent Exadata software. You
 can provision Exadata X9M systems by using a shape that's equivalent to a
 quarter-rack X9M system, and then add database and storage servers at any time
 after provisioning.
 

 
 Oracle Exadata Database Service on Dedicated
 Infrastructure provides Oracle Exadata Database Machine as a service in an Oracle Cloud
 Infrastructure (OCI) data center. The Oracle Exadata Database Service on Dedicated
 Infrastructure instance is a virtual machine (VM) cluster that resides on Exadata racks in
 an OCI region.
 

 
 Oracle Exadata Database Service
 on Cloud@Customer provides Oracle Exadata Database
 Service that is hosted in your data center.
 

 
 
- Zero Downtime Migration service host 
The Oracle Zero Downtime Migration service host should be a dedicated system, but it can be
 shared for other purposes.
 

 
 Oracle Zero Downtime Migration software requires a standalone Oracle Linux host running on any one of the following platforms: Oracle Linux 7, Oracle Linux 8, or Red Hat Enterprise Linux 8.
 

 
The
 Oracle Zero Downtime Migration service host must be able to connect to the source and
 the target database servers; as long as connectivity is
 guaranteed, the service host can be located
 anywhere.
 

 
 
- Oracle Database Autonomous
 Recovery Service 
 Oracle Database Autonomous
 Recovery Service is an Oracle Cloud service that protects Oracle databases. With backup automation and enhanced data protection capabilities for OCI databases, you can offload all backup processing and storage requirements to Oracle Database Autonomous
 Recovery Service , thereby eliminating backup infrastructure costs and manual administration overhead.
 

 
 
 
 Oracle Zero Downtime Migration migration workflows 

 

 
Note:
For each migration worklfow listed, see Explore More for more details.
 

 
You can perform the following workflows to migrate your Oracle Database to Oracle Exadata Database Service on Dedicated
 Infrastructure on Oracle Database@Azure .
 

 
 
- Physical online migration 
The physical online migration
 workflow supports migrations between the same database
 versions and platforms. It uses direct data tra
