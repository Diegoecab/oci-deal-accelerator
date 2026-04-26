# Connect Oracle Data Safe to Oracle databases on multicloud and hybrid cloud environments

- Source: https://docs.oracle.com/en/solutions/data-safe-multicloud-ods-hybrid/index.html
- Date: 2025-06
- Type: reference-architecture
- Services: data-safe, exacs, adb-s
- Tags: security, database, multicloud

## Summary (catalog)

Data Safe for database security assessment across multicloud and hybrid deployments. Covers Database@Azure, Database@AWS, on-premises, and OCI-native databases.

## Architecture (fetched from source)

Architecture

 

 

 
 
This reference architecture outlines the following target databases
 and these Data Safe connection scenarios:

 
 
 
- Data Safe connecting to multicloud database deployments in non
 Microsoft Azure cloud environments 
 
- Data Safe connecting to databases in Microsoft Azure using Database
 Service (ODSA) 
 
 
 

 
For all the different deployments of Data Safe discussed here a deployment
 of a landing zone in your tenancy is advised. The following resources provide best
 practices for security and compliance, landing zone concepts and deployment of a landing
 zone on Oracle Cloud Infrastructure using terraform scripts: 
 
 
- Well-architected framework for Oracle Cloud Infrastructure 
 
 
 
- Deploy a secure landing zone that meets the CIS Foundations
 Benchmark for Oracle Cloud 
 
 
 
- CIS Compliant OCI Landing Zones (GitHub repository) 
 
 

 
Note:
Please refer to "Explore
 More", below, for access to these resources.
 

 

 
 Data Safe connecting to databases in a multicloud environment 

 
When Oracle Databases are deployed in a multicloud environment then they can
 be seen as databases deployed on-premises. Either the private end-point or on-premises
 connector can be used. The following diagram shows the connection options for databases
 deployed on e.g. AWS and/or Microsoft Azure. Any cloud provider that can host Oracle
 databases can be used in this setup. By connecting to the databases deployed in a cloud
 provider using either private endpoint or the on-premises Data Safe connector enables
 Data Safe to inspect the databases. 

 

 
 
 Description of the illustration datasafe-multi-odsa-01.png 

 
 

 

 datasafe-multi-odsa-01-oracle.zip 
 
 

 
 Data Safe connecting to databases in Microsoft Azure using Database
 Service (ODSA) 

 
Connecting Data Safe to the databases that are part of Oracle Database
 Service for Azure (ODSA) is the same as for other OCI based databases. There are however
 some details you should consider when using the ODSA service. The following diagram
 illustrates the architecture for ODSA: 

 

 
 
 Description of the illustration datasafe-multi-odsa-02.png 

 
 

 

 datasafe-multi-odsa-02-oracle.zip 
 
 

 
Because the databases are setup in a separate ODSA compartment some
 adjustments to policies may be necessary to provide access to these resources. 

 
With Oracle Database Service for Microsoft Azure (ODSA) the database
 resources reside in an OCI tenancy that is linked to a Microsoft Azure account. In OCI,
 the databases and infrastructure resources are maintained in an ODSA compartment. This
 compartment is automatically created for ODSA resources during the sign up process. The
 ODSA Multicloud NetworkLink (see the diagram ) and account linking will be setup during
 the sign up process as well. 

 
One of the prerequisites for ODSA is that your tenancy must support Identity
 Domains. Additionally, regional availability must be checked. The ODSA database
 resources need to be provisioned in these regions.

 
See The Multicloud Service Model , accessible from the Explore
 More topic, below for additional information on ODSA.
 

 
This architecture has the following components:
 
 
- Tenancy 
 
 
A tenancy is a secure and isolated partition that Oracle sets up
 within Oracle Cloud when you sign up for OCI . You can create, organize, and
 administer your resources in Oracle Cloud within your tenancy. A tenancy is
 synonymous with a company or organization. Usually, a company will have a
 single tenancy and reflect its organizational structure within that tenancy.
 A single tenancy is usually associated with a single subscription, and a
 single subscription usually only has one tenancy.

 
 
- Region 
 
 
An Oracle Cloud Infrastructure region is a localized geographic
 area that contains one or more data centers, called availability domains.
 Regions are independent of other regions, and vast distances can separate
 them (across countries or even continents).

 
 
 
- Compartment 
 
 
Compartments are cross-region logical partitions within an
 Oracle Cloud Infrastructure tenancy. Use compartments to organize your
 resources in Oracle Cloud, control access to the resources, and set usage
 quotas. To control access to the resources in a given compartment, you
 define policies that specify who can access the resources and what actions
 they can perform.. 

 
 
- Availability domains 
 
 
Availability domains are standalone, independent data centers
 within a region. The physical resources in each availability domain are
 isolated from the resources in the other availability domains, which
 provides fault tolerance. Availability domains don’t share infrastructure
 such as power or cooling, or the internal availability domain network. So, a
 failure at one availability domain is unlikely to affect the other
 availability domains in the region. 

 
 
- Fault domains 
 
 
A fault domain is a grouping of hardware and infrastructure
 within an availability domain. Each availability domain has three fault
 domains with independent power and hardware. When you distribute resources
 across multiple fault domains, your applications can tolerate physical
 server failure, system maintenance, and power failures inside a fault
 domain. 

 
 
- Virtual cloud network (VCN) and subnets 
 
 
A VCN is a customizable, software-defined network that you set up
 in an Oracle Cloud Infrastructure region. Like traditional data center
 networks, VCNs give you complete control over your network environment. A
 VCN can have multiple non-overlapping CIDR blocks that you can change after
 you create the VCN. You can segment a VCN into subnets, which can be scoped
 to a region or to an availability domain. Each subnet consists of a
 contiguous range of addresses that don't overlap with the other subnets in
 the VCN. You can change the size of a subnet after creation. A subnet can be
 public or private.

 
 
- Load balancer 
The Oracle Cloud
 Infrastructure Load Balancing service provides automated traffic
 distribution from a single entry point to multiple servers in the back end.
 The load balancer provides access to different applications. 

 
 
- Service gateway 
 
 
The service gateway provides access from a VCN to other
 services, such as Oracle Cloud Infrastructure Object Storage. The traffic
 from the VCN to the Oracle service travels over the Oracle network fabric
 and never traverses the internet. 

 
 
- Cloud Guard 
 
 
You can use Oracle Cloud Guard to monitor and maintain the
 security of your resources in Oracle Cloud Infrastructure. Cloud Guard uses
 detector recipes that you can define to examine your resources for security
 weaknesses and to monitor operators and users for risky activities; for
 example, Cloud Guard can notify you when you have a database in your tenancy
 that is not registered with Data Safe. When any misconfiguration or insecure
 activity is detected, Cloud Guard recommends corrective actions and assists
 with taking those actions, based on responder recipes that you can
 configure. 

 
 
- FastConnect 
 
 
Oracle Cloud Infrastructure FastConnect provides an easy way to
 create a dedicated, private connection between your data center and Oracle
 Cloud Infrastructure. FastConnect provides higher-bandwidth options and a
 more reliable networking experience when compared with internet-based
 connections; for example, Cloud Guard can notify you if you have a database
 in your tenancy that is not registered with Data Safe. 

 
 
- Autonomous Transaction Processing 
Autonomous
 Transaction Processing delivers a self-driving, self-securing,
 self-repairing database service that can instantly scale to meet demands of
 a variety of applications: mission-critical transaction processing, mixed
 transactions and analytics, IoT, JSON documents, and so on. When you create
 an Autonomous Database, you can deploy it to one of three kinds of Exadata
 infrastructure:
 
 
- Shared ; a simple and elas
