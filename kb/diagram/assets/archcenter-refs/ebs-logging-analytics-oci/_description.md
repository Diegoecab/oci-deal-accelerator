# Integrate, manage and secure E-Business Suite applications using Logging Analytics

- Source: https://docs.oracle.com/en/solutions/ebs-logging-analytics-oci/index.html
- Date: 2025-10
- Type: reference-architecture
- Services: logging, compute
- Tags: observability, ebs, security

## Summary (catalog)

Logging Analytics for EBS log management. Centralized collection of Apache, WebLogic, and Concurrent Manager logs. Security analytics for unauthorized access detection.

## Architecture (fetched from source)

Architecture

 

 
 Oracle Log Analytics uses Management Agents to securely collect logs from Oracle E-Business Suite components, such as database servers, application servers, and applications. Oracle Log Analytics uses a service-connector to ingest logs from Oracle Cloud
 Infrastructure services. 
 

 
 The Oracle E-Business Suite environment consists of the database instance, application tier hosts, and Oracle WebLogic Server . The Oracle E-Business Suite entity model comprises the following:
 

 
 
- 
 
 Oracle E-Business Suite : This is a top-level grouping of the entities and has a few metrics associated with the packaged application that it represents.
 

 
 
- 
 
Concurrent manager: This is a composite entity that has hosted entities under it, and has metrics available for monitoring.

 
 
- 
 
Forms system: This is a system entity which provides metrics for the forms database sessions.

 
 
- 
 
Workflow group: The workflow group has three key hosted entities: Background Engine, Notification Mailer, and Agent Listener, which provide availability metrics.

 
 
 
This architecture assumes an Oracle E-Business Suite deployment with the following characteristics:
 

 
 
- A single compartment configuration for deploying Oracle E-Business Suite 
 
- Different subnets host application instances. For example, web servers are in a public subnet and databases are in a private subnet, with additional subnets for redundancy 
 
- Oracle Log Analytics components consist of various agents installed in each subnet to send logs to Oracle Log Analytics 
 
 
Management Agent can automatically discover the Oracle E-Business Suite environment and send that data to Oracle Log Analytics to create an application and infrastructure entity topology. The management agent must be installed on the same VCN as Oracle E-Business Suite and be able to access Oracle E-Business Suite database. After discovery, you can view and verify the entity topology in Log Explorer's scope filter. You can then associate resources to enable log collection. Management Agents must be installed on all the host nodes identified during discovery. It is installed by default on all Oracle Cloud
 Infrastructure instances as a Oracle Cloud Agent plugin.
 

 
The following architecture diagram shows the functional view of how Oracle Log Analytics uses management agents to monitor Oracle Cloud
 Infrastructure 

 
 Description of the illustration ebs-logging-analytics-oci.png 

 ebs-logging-analytics-oci-oracle.zip 

 
The architecture has the following components:

 
 
- Region 
An OCI region
 is a localized geographic area that contains one
 or more data centers, hosting availability
 domains. Regions are independent of other regions,
 and vast distances can separate them (across
 countries or even continents).

 
 
- Availability domains 
Availability domains are standalone, independent data centers within a region. The physical resources in each availability domain are isolated from the resources in the other availability domains, which provides fault tolerance. Availability domains don’t share infrastructure such as power or cooling, or the internal availability domain network. So, a failure at one availability domain shouldn't affect the other availability domains in the region.

 
 
- Fault domains 
A
 fault domain is a grouping of hardware and
 infrastructure within an availability domain. Each
 availability domain has three fault domains with
 independent power and hardware. When you
 distribute resources across multiple fault
 domains, your applications can tolerate physical
 server failure, system maintenance, and power
 failures inside a fault domain.

 
 
- Virtual cloud network and subnets 
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

 
 
- Route tables 
Virtual
 route tables contain rules to route traffic from
 subnets to destinations outside a VCN, typically
 through gateways.

 
 
- Dynamic routing gateway
 (DRG) 
The DRG is a
 virtual router that provides a path for private
 network traffic between VCNs in the same region,
 between a VCN and a network outside the region,
 such as a VCN in another OCI region, an
 on-premises network, or a network in another cloud
 provider.

 
 
- Service
 gateway 
A
 service gateway provides access from a VCN to
 other services, such as Oracle Cloud
 Infrastructure Object Storage . The traffic from the VCN to the Oracle service
 travels over the Oracle network fabric and does
 not traverse the internet.
 

 
 
- Management Agent 
Allows a management service plug-in to monitor and collect data from the sources that reside on the hosts or virtual hosts where the Management Agent is installed. The Management Agent can connect to Oracle Cloud
 Infrastructure directly using the Management Agent service. 
 

 
 
- Management Agent service 
An Oracle Cloud
 Infrastructure service that manages the Management Agents and their lifecycle. Management Agents allow Oracle Cloud services to interact and collect data from the entities that they manage.
 

 
 
- Oracle Cloud Agent 
A lightweight process that manages plug-ins running on compute instances residing on Oracle Cloud
 Infrastructure . You can deploy Management Agents to compute instances by using the Oracle Cloud Agent.
 

 
 
- Service Connector Hub 
 Oracle Cloud
 Infrastructure cloud message bus platform that offers a single pane of glass for describing, executing, and monitoring movement of data between services in Oracle Cloud
 Infrastructure . A service connector specifies a source service, a target service, and optional tasks.
 

 
 
- Logging 
Provides access to logs from Oracle Cloud
 Infrastructure resources.
 

 
 
- Oracle Log Analytics 
 Oracle Log Analytics is a fully managed SaaS regional service available in more than 27 regions that provides collection, indexing, enrichment, query, visualization, and alerting for logs from any IT component running on-premises, on Oracle Cloud
 Infrastructure , or on a third-party cloud. 
 

 
 
- Application discovery 
A stack management service that allows management agents to discover the components of Oracle E-Business Suite or other applications including their hierarchy or topology and to share with Oracle Log Analytics for log collection.
 

 
 
- Entity 
An IT or business service that you want to monitor such as Storefront Service, Oracle E-Business Suite , Oracle WebLogic Server , or a Linux (Host). Entities can be logically linked with each other in Oracle Log Analytics to build application and infrastructure topology for log exploration.
 

 
 
- Log group 
A resource for log data in Oracle Log Analytics that supports role-based access control (RBAC). A log group is the logical destination for a log record ingested in Oracle Log Analytics and is different from Oracle Cloud
 Infrastructure logging service log group.
 

 
 
- Log source 
Specifies where the log files are located, how to collect them, how to apply data masks, parse the data, extract the data using extended field definitions, enrich the data using labels and enrichment function definitions, and extract the metric data from a log file. Log sources can be used to collect logs continuously from an Oracle Cloud
 Infrastructure Management Agent or can be provided when you perform on-demand upload of a log file to Oracle Log Analytics or Oracle Cloud
 Infrastructure Object Storage collection rules. Whe
