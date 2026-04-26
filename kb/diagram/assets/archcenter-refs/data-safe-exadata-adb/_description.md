# Implement Oracle Data Safe for Exadata and Autonomous Databases

- Source: https://docs.oracle.com/en/solutions/data-safe-exadata-adb/index.html
- Date: 2025-06
- Type: reference-architecture
- Services: data-safe, exacs, adb-s
- Tags: security, database

## Summary (catalog)

Data Safe deployment for ExaCS and ADB. Security assessment, user assessment, activity auditing, data masking, and data discovery. Private endpoint connectivity for databases in private subnets.

## Architecture (fetched from source)

Architecture

 

 

 
 
This reference architecture outlines the following target databases
 and the way Data Safe connects to these databases:

 
 
 
- Exadata Database Service or Exadata Cloud@Customer / Regional
 Cloud@Customer / Dedicated Region 
 
- Autonomous Databases 
 
 
 

 
This reference architecture only discusses databases with private IP addresses. To
 configure a database with a public IP address is from a security perspective not
 advised. 

 
For each different deployment of Data Safe discussed here, you should also
 deploy a landing zone in your tenancy. The following resources provide best practices
 for security and compliance, landing zone concepts and deployment of a landing zone on
 Oracle Cloud Infrastructure using terraform scripts: 
 
 
- Well-architected framework for Oracle Cloud Infrastructure 
 
- Deploy a secure landing zone that meets the CIS Foundations
 Benchmark for Oracle Cloud 
 
- CIS Compliant OCI Landing Zones (GitHub repository) 
 
 

 
Note:
Please refer to the Explore
 More topic below for access to these resources.
 

 

 
 Exadata Database Service or Exadata Cloud@Customer 

 
Oracle Exadata Database Service provides the Oracle Exadata Database Machine
 as a service in an Oracle Cloud Infrastructure (OCI) data center. 

 
Exadata Cloud@Customer, a managed service, provides an Exadata Database
 Service that is hosted in the on-premises data center. 

 
 Exadata Database Service 

 
The Exadata Database Service does not need to connect to the on-premises
 network because it is deployed on OCI and can therefor use the Private end-point
 directly. After setting up the necessary connectivity, the databases can be configured
 as targets in Data Safe using the wizard.

 
 Exadata Cloud@Customer 

 
To connect a Exadata Cloud@Customer target database there are two options : 
 
 
- On-premises connector 
 
- Private end-point 
 
 

 
In the following diagram, the connections are shown between the Oracle Cloud
 and the on-premises data center. The diagram shows the options to choose from. If there
 is a site-to-site VPN or OCI FastConnect connection you can use a private endpoint to
 connect to your Exadata Cloud@Customer target Data Safe databases. If there is no VPN or
 OCI FastConnect, then you can deploy an on-premises connector to connect to your Exadata
 Cloud@Customer target Data Safe databases. This on-premises connector will then connect
 to Data Safe via a TLS tunnel.

 

 
 
 Description of the illustration data-safe-exa-adb.png 

 
 

 

 data-safe-exa-adb-oracle.zip 
 
 

 
Be aware that as shown in the diagram, an outgoing, persistent, secure automation tunnel
 connects the CPS infrastructure in the on-premises data center to the Oracle-managed
 admin VCN in the OCI region for delivering cloud automation commands to the VM clusters.
 This is a outgoing tunnel for the CPS infrastructure and can not be used for Data Safe
 connections. For more information see the link below on 'Architecture Exadata
 Cloud@Customer'.

 
The Exadata Cloud@Customer environment is supported by Oracle using the
 Oracle Operator Access Control (OpCtl). OpCtl is an OCI privileged access management
 (PAM) service that gives customers a technical mechanism to better control how Oracle
 staff can access their Exadata Cloud@Customer (ExaC@C) infrastructure. For a detailed
 reading on this see the link Oracle Operator Access Control link below. The following
 resources describe the architectures and setup in detail:
 
 
- Architecture Exadata Cloud@Customer 
 
- Architecture Exadata Database Service 
 
- Setup Cloud@Customer database using private endpoint 
 
- Setup Cloud@Customer database using the wizard 
 
- Simplify Security for your on-premises Oracle Databases with Oracle
 Data Safe 
 
- Exadata Database Service Security Controls 
 
 

 
Note:
Please refer to the Explore
 More topic below for access to these resources.
 

 

 
 Autonomous Databases 

 
Autonomous database on shared infrastructure is available with Data Safe.
 Autonomous databases can be registered through the wizard or by a single click from the
 Autonomous database details page. The steps to connect the autonomous database for the
 Dedicated Region Cloud@Customer are discussed in this part of the Data Safe
 documentation. 

 
 Architecture Components 

 
These architectures have the following components:
 
 
- Tenancy 
 
 
Oracle Autonomous Transaction Processing is a self-driving,
 self-securing, self-repairing database service that is optimized for
 transaction processing workloads. You do not need to configure or manage any
 hardware, or install any software. Oracle Cloud Infrastructure handles
 creating the database, as well as backing up, patching, upgrading, and
 tuning the database. 

 
 
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
 they can perform. 

 
 
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

 
 
- Security list 
For each subnet, you can create security rules that
 specify the source, destination, and type of traffic that must be allowed in
 and out of the subnet.

 
 
 
- NAT gateway 
 
 
The NAT gateway enables private resources in a VCN to access hosts on the
 internet, without exposing those resources to incoming internet
 connections.

 
 
- Service gateway 
 
 
The service gateway provides access from a VCN to other
 services, such as Oracle Cloud Infrastructure Object Storage. The traffic
 from the VCN to the Oracle service travels over the Oracle network fabric
 and never traverses the internet. 

 
 
- Cloud Guard 
 
 
You can use Oracle Cloud Guard to monitor and maintain the
 security of your resources in Oracle Cloud Inf
