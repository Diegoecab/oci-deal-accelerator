# Monitor a Kubernetes cluster with OCI Logging Analytics

- Source: https://docs.oracle.com/en/solutions/kubernetes-oke-logging-analytics/index.html
- Date: 2025-10
- Type: reference-architecture
- Services: oke, logging
- Tags: observability, application

## Summary (catalog)

Logging Analytics for OKE cluster monitoring. Automated log collection from pods, nodes, and control plane. Pre-built dashboards for cluster health, resource utilization, and application logs.

## Architecture (fetched from source)

Architecture

 

 
This architecture shows how you can use Oracle Log Analytics to monitor a Kubernetes platform and cloud native applications.
 

 
The following diagram is a sample topology of a Kubernetes Cluster
 in a single Oracle Cloud Infrastructure (OCI) region. It shows the
 infrastructure tier and the second diagram highlights the kubernetes and
 application tiers.
 
 Description of the illustration kubernetes-master-worker-nodes.png 
 kubernetes-master-worker-nodes-oracle.zip 
 
 

 
The following diagram illustrates Kubernetes monitoring for your on-premises Kubernetes clusters and Oracle Cloud Infrastructure Kubernetes Engine (also known as Kubernetes Engine or OKE ) with Oracle Log Analytics . This solution offers a collection of various logs of a Kubernetes cluster into Oracle Log Analytics and offers rich analytics on top of the collected logs. You can customize the log collection by modifying the out-of-the box configuration. 
 
 
 Description of the illustration k8s-oke-monitoring.png 
 k8s-oke-monitoring-oracle.zip 
 
 

 
The architecture has the following components:

 
 
- Tenancy 
A tenancy
 is a secure and isolated partition that Oracle
 sets up within Oracle Cloud when you sign up for
 OCI. You can create, organize, and administer your
 resources on OCI within your tenancy. A tenancy is
 synonymous with a company or organization.
 Usually, a company will have a single tenancy and
 reflect its organizational structure within that
 tenancy. A single tenancy is usually associated
 with a single subscription, and a single
 subscription usually only has one
 tenancy.

 
 
- Region 
An OCI region
 is a localized geographic area that contains one
 or more data centers, hosting availability
 domains. Regions are independent of other regions,
 and vast distances can separate them (across
 countries or even continents).

 
 
- Compartment 
Compartments
 are cross-regional logical partitions within an
 OCI tenancy. Use compartments to organize, control
 access, and set usage quotas for your Oracle Cloud resources. In a given compartment, you define
 policies that control access and set privileges
 for resources.
 

 
 
- Virtual cloud network (VCN) and subnets 
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

 
 
- Load balancer 
 Oracle Cloud
 Infrastructure Load Balancing provides automated traffic distribution from a single entry point to multiple servers.
 

 
 
- Service
 gateway 
A
 service gateway provides access from a VCN to
 other services, such as Oracle Cloud
 Infrastructure Object Storage . The traffic from the VCN to the Oracle service
 travels over the Oracle network fabric and does
 not traverse the internet.
 

 
 
- Oracle Log Analytics 
 
 Oracle Log Analytics is a fully managed SaaS regional service available in more than 27 regions that provides collection, indexing, enrichment, query, visualization, and alerting for logs from any IT component running on on-premises, OCI or 3rd party cloud.
 

 
 
- Oracle Log Analytics Source 
 Oracle Log Analytics Source is a configuration resource that provides specifications for parsing, extractions, labeling, data masking, and other enrichment to ensure logs are properly ingested and indexed for analysis and monitoring. This architecture uses more than 30 pre-defined sources for Kubernetes services, applications, and objects. These sources are continuously enhanced to provide deeper analytics capabilities.
 

 
 
- Kubernetes System Pods 
Kubernetes
 System Pods are small deployable units of computing that you
 can create and manage in Kubernetes. A Pod is one or more
 containers, with shared storage and network resources, and
 rules for running the containers. 

 
 
- User Pods 
Applications launched on the
 Kubernetes cluster. All the logs from application pods
 writing STDOUT/STDERR are typically
 available under /var/log/containers/ .
 Applications that have custom log handlers may route their
 logs differently, but in general are available on the node
 (through a volume).
 

 
 
- Control Plane Services & Pods 
Kubernetes platform Control Plane Services and pods. The
 Control Plane manages the worker nodes and the Pods in the
 Kubernetes cluster. The worker nodes run the containerized
 applications. Every cluster has at least one worker node.
 The worker node(s) host the Pods that are the components of
 the application workload. 

 
 
- Node OS Services 
Linux services
 running on the instance on which Kubernetes is installed.
 Logs are collected on OS services.

 
 
- Log and Object Collector Pods 
Log and
 Object Collector Pods are made up of replica sets, FluentD,
 and daemon sets.

 
 
- FluentD Collector 
FluentD is an open-source data collector that provides a unified logging layer between data sources and backend systems. It allows unified data collection and consumption for a building data processing pipelines. This architecture uses containerized FluentD container that runs as daemon set and replicat set on kubernetes cluster. It uses log analytics fluentd output plugin to upload logs to Oracle Log Analytics .
 

 
 
- Oracle Log Analytics FluentD Plugin 
The FluentD output plugin that connects to Oracle Log Analytics service in your tenancy to upload or ingest logs collected by FluentD collector.
 

 
 
- Kubernetes Objects 
Kubernetes objects are persistent entities in the
 Kubernetes system. Kubernetes uses these entities
 to represent the state of your cluster. In this
 architecture, the following kubernetes object
 states are collected as logs for historical
 analysis and troubleshooting: 

 
 
- Kubernetes Daemon Set 
A Kubernetes DaemonSet is a type
 of workload that runs on Kubernetes and ensures
 that all (or some) Nodes run a copy of a Pod. As
 nodes are added to the cluster, Pods are added to
 them. As nodes are removed from the cluster, those
 Pods are garbage collected. 
 

 
 
- Kubernetes Replica Set 
A Kubernetes
 ReplicaSet is a type of workload
 that runs on Kubernetes. It maintains a stable set
 of replica Pods running at any given time. As
 such, it is often used to guarantee the
 availability of a specified number of identical
 Pods
 

 
 
 
 
- OCI Kubernetes Engine 
 Oracle Cloud Infrastructure Kubernetes Engine ( OCI Kubernetes Engine or OKE ) is a fully-managed, scalable, and highly available service that you can use to deploy your containerized applications to the cloud. You specify the compute resources that your applications require, and OKE provisions them on OCI in an existing tenancy. OKE uses Kubernetes to automate the deployment, scaling, and management of containerized applications across clusters of hosts.
 

 
 
- Service connectors 
Service Connector
 Hub is a cloud message bus platform. You can use it to move
 data between services in Oracle Cloud Infrastructure. Data
 is moved using service connectors. A service connector
 specifies the source service that contains the data to be
 moved, the tasks to perform on the data, and the target
 service to which the data must be delivered when the
 specified tasks are completed. One service connector is
 provisioned in this architecture to collect network and
 load-balancer logs.

 
 
- OCI Services 
Oracle Cloud Infrastructure (OCI) services are a
 platform of cloud services that enable you to build and run
 a wide range of applications in a highly-available,
 consistently high-performance environment
