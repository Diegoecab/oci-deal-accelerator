# Deploy JD Edwards EnterpriseOne with Oracle Autonomous Database on Dedicated Exadata Infrastructure

- Source: https://docs.oracle.com/en/solutions/oracle-adb-jde-exadata/index.html
- Date: 2025-03
- Type: reference-architecture
- Services: adb-d, exacs, compute
- Tags: application, database

## Summary (catalog)

JDE on ADB-D for maximum database performance and isolation. Dedicated Exadata infrastructure for JDE database, compute instances for JDE application and batch servers.

## Architecture (fetched from source)

Architecture

 

 
This reference architecture delineates a high availability JD Edwards
 deployment in a single Availability Domain in an OCI region with Oracle Autonomous Database on Dedicated Exadata Infrastructure . The emphasis of this architecture is to provide detailed information when you
 are planning to deploy your JD Edwards EnterpriseOne workload on Oracle Autonomous Database on Dedicated Exadata Infrastructure .
 

 

 
Note:
Although it is a JD Edwards specific deployment, this reference architecture
 can be a good starting point for any workload with Oracle Autonomous Database on Dedicated Exadata Infrastructure .
 

 
The following diagram illustrates this reference architecture.

 
 Description of the illustration oracle-adb-jde-exadata-arch.png 

 oracle-adb-jde-exadata-arch-oracle.zip 

 
This deployment has a Production and two Non-Production environments.
 All the instances in the Production as well as Non-Production environments
 including load balancer, web tier, application and database are deployed in
 a private subnet.

 
In the Production environment, Presentation tier or Web tier contains
 four instances which are load balanced by a single Production load
 balancer.

 
Each Web tier instance consists of a single Application Interface
 Services (AIS) Server, Standard HTML Server (Standard HTML), and Dedicated
 HTML Server (Dedicated HTML). As per the recommendation, all the Web tier
 components are installed in each Web tier instances (or VM) and scaled
 horizontally by deploying redundant instances of every component. High
 availability can be achieved by spreading the multiple VMs across different
 fault domains.

 
The Application or middle tier contains four logic servers and batch
 servers. The logic server and the batch server can be hosted on the same
 enterprise server instance. However, it is recommended to set up the logic
 server and the batch server on separate enterprise server instances.

 
The JD Edwards EnterpriseOne application server connects to the
 Autonomous Database. Within the Production Autonomous VM cluster, it has a
 single container database and one pluggable database. Note that you can have
 a maximum number of five schemas distributed across one or many database
 instances. You can provision the database server instance with the available
 schemas as required. The following schemas are available for the database
 instance: Production (for example, PD920), Prototype (for example, PY920),
 Development (for example, DV920), Pristine (for example, PS920) and Shared
 (required).

 
One-Click is a Provisioning automation for OCI to accelerate the
 customers path to cloud. Using 'One-Click', customers must install all four
 namely Production, Prototype, Development and Pristine path codes along with
 'Shared data source'. There is no automated way to add additional path codes
 post deployment. However, you can add other path codes as required using
 traditional On-Premise methodology. 

 
The Non-Production section of the architecture has two environments.
 One is a multi-instance deployment and another is a single instance
 deployment for both Presentation and Middle or Application tier. Within the
 Non-Production Autonomous VM Cluster, we have a single container database
 and two pluggable databases for two Non-Production environments.

 
Additionally, One-Click Provisioning Server and Deployment Server
 are deployed in the Admin subnet. It also has an OCI Bastion which can be
 used for a secure SSH connectivity. Depending on your requirement, you can
 use either 'Self Service Bastion' or 'Bastion as a Service'. Optional JD
 Edwards EnterpriseOne components are hosted in the Admin subnet. Optional
 components are not deployed by One-Click provisioning. However, the web
 components can be manually added through server manager and the development
 client can be added in a new Microsoft Windows instance using the
 traditional On-Premise methodology.

 
This section explores the technical Architecture for Oracle Autonomous Database on Dedicated Exadata Infrastructure . 
 

 
 Rack Overview 

 
The following image illustrates the rack overview for Oracle Autonomous Database on Dedicated Exadata Infrastructure .
 

 
 Description of the illustration oracle-adb-jde-exadata-rack-overview.png 

 oracle-adb-jde-exadata-rack-overview-oracle.zip 

 
Each instance of Dedicated Exadata Infrastructure contains multiple
 database servers and Exadata storage servers that are connected by
 high-speed, low-latency network fabric. The Exadata database and storage
 server rack reside in an OCI region.

 
With elastic expansion in Exadata X8M and later series (X9M, X11M),
 the starting configuration is similar to a quarter rack (2 database servers
 and 3 storage servers), which can be expanded to up to 32 database servers
 and 64 storage servers to support workloads of different sizes.

 

 
Note:
Unlike the Oracle Exadata Database Service on Dedicated
 Infrastructure instance, Oracle Autonomous Database on Dedicated Exadata Infrastructure only needs to have a client subnet within the customer VCN. Oracle
 internally uses its service tenancy to route the backup traffic, as shown in
 the diagram above. Oracle also manages the infrastructure through the
 management network, which connects the database and storage server
 hardware.
 

 
 VM Clusters Overview 

 
The following diagram illustrates the VM Clusters overview on
 Dedicated Exadata Infrastructure.

 
 Description of the illustration oracle-adb-jde-vm-clusters.png 

 oracle-adb-jde-vmclusters-oracle.zip 

 
You can create multiple VM clusters on a single Oracle Exadata Cloud Infrastructure . This enables you to choose a specific database server within the
 infrastructure to host VM from the cluster. The same Oracle Exadata Cloud Infrastructure can host VM clusters supporting both the Oracle Exadata Database Service on Dedicated
 Infrastructure and the Oracle Autonomous Database ( Oracle Autonomous Transaction
 Processing and Oracle Autonomous Data Warehouse ). You can host up to eight VM clusters across all the database servers in
 your Oracle Exadata Database Service on Dedicated
 Infrastructure .
 

 
This diagram has two VM clusters (Production and Non-Production) with
 resources allocated across two database servers that are connected to three
 storage servers.

 
 VMs and Database Servers Overview 

 
The following diagram illustrates the hypervisor and database
 servers.

 
 Description of the illustration oracle-adb-jde-vms-db-servers.png 

 oracle-adb-jde-vms-db-servers-oracle.zip 

 
Each Oracle Exadata database server contains one or more virtual
 machine guests running on a hypervisor. Oracle manages the hypervisors
 through the management network. Each hypervisor uses minimal resources: only
 2 CPU cores (OCPUs) and 16 GB of RAM.

 
The client and backup networks connect to the VM guest through
 bonded network interfaces to maximize performance and availability, where
 the backup network for Autonomous VM Clusters as specified before is managed
 by Oracle internally.

 
Each VM guest has a complete Oracle Database installation including
 all the Enterprise Edition options, such as Oracle Database In-Memory and
 Oracle Real Application Clusters (RAC), as well as Oracle Grid
 Infrastructure. In the Autonomous cluster, we will have Autonomous
 Management tools. In this diagram we have shown two Autonomous Container
 databases (ACD1 and ACD2). One Autonomous Database (ADB1) in ACD1 and two
 Autonomous Databases (ADB2 and ADB3) in ACD2. Oracle manages the
 infrastructure through the management network, which connects the database
 and storage server hardware.

 
The architecture has the following components:

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that contains one or more data centers, hosting availability domains. Regions are independent of other regions, and vast distances can separate them (across countries o
