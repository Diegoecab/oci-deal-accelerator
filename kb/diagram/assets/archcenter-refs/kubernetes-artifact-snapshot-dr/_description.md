# Use artifact snapshots to protect your OCI Kubernetes Engine clusters from disaster

- Source: https://docs.oracle.com/en/solutions/kubernetes-artifact-snapshot-dr/index.html
- Date: 2025-01
- Type: reference-architecture
- Services: oke, object-storage
- Tags: ha-dr, application

## Summary (catalog)

OKE DR using etcd snapshots and artifact replication. Cross-region backup of Kubernetes state, container images, and persistent volumes. Velero for workload backup and restore.

## Architecture (fetched from source)

Architecture

 

 
This architecture shows the disaster recovery (DR) system's topology for the
 Kubernetes cluster.

 
All runtime, configuration, and metadata information residing in the primary
 database is replicated from Region 1 to Region 2 with Oracle Autonomous Data Guard . The required Kubernetes (K8s) cluster configuration is replicated
 through ETCD snapshots for control plane protection and with YAML snapshots
 for application configuration protection. You can use artifact snapshots or
 You can use etcd copies or artifact snapshots for application-specific
 configuration protection for application-specific configuration protection.
 See Kubernetes clusters
 restore based on etcd snapshots for more details. The images that the container uses are
 hosted in registries, either local to each cluster or in external
 repositories (images are not considered a Kubernetes cluster configuration
 by themselves).
 

 

 
Note:
Setting up Oracle Autonomous Data Guard for the runtime database is out of the scope of this document.
 
 
 Description of the illustration kubernetes-multiregion-dr.png 
 kubernetes-multiregion-dr-oracle.zip 

 
 This architecture supports the following components:

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that contains one or more data centers, called availability domains. Regions are independent of other regions, and vast distances can separate them (across countries or even continents).
 

 
 
- Load balancer 
 Oracle Cloud
 Infrastructure Load Balancing provides automated traffic distribution from a single entry point to multiple servers.
 

 
 
- Dynamic routing gateway (DRG) 
The DRG is a virtual router that provides a path for private network traffic between VCNs in the same region, between a VCN and a network outside the region, such as a VCN in another Oracle Cloud
 Infrastructure region, an on-premises network, or a network in another cloud provider.
 

 
 
- Data Guard 
 Oracle Data Guard and Oracle Active Data Guard provide a comprehensive set of services that create, maintain, manage, and monitor one or more standby databases and that enable production Oracle databases to remain available without interruption. Oracle Data Guard maintains these standby databases as copies of the production database by using in-memory replication. If the production database becomes unavailable due to a planned or an unplanned outage, Oracle Data Guard can switch any standby database to the production role, minimizing the downtime associated with the outage. Oracle Active Data Guard provides the additional ability to offload read-mostly workloads to standby databases and also provides advanced data protection features.
 

 
 
- Oracle Real Application Clusters (Oracle
 RAC) 
Oracle RAC enables you to run a single Oracle Database
 across multiple servers to maximize availability and enable horizontal
 scalability, while accessing shared storage. User sessions connecting to Oracle
 RAC instances can failover and safely replay changes during outages, without any
 changes to end user applications.

 
 
- Registry 
 Oracle Cloud Infrastructure
 Registry is an Oracle-managed registry that enables you to simplify your development-to-production workflow. Registry makes it easy for you to store, share, and manage development artifacts, like Docker images. The highly available and scalable architecture of Oracle Cloud
 Infrastructure ensures that you can deploy and manage your applications reliably.
 

 
 
- Kubernetes Engine 
 Oracle Cloud Infrastructure Kubernetes Engine ( OCI Kubernetes Engine or OKE ) is a fully managed, scalable, and highly available service that you can use to deploy your containerized applications to the cloud. You specify the compute resources that your applications require, and Kubernetes Engine provisions them on Oracle Cloud
 Infrastructure in an existing tenancy. OKE uses Kubernetes to automate the deployment, scaling, and management of containerized applications across clusters of hosts.
 

 
 
- Kubernetes cluster 
A Kubernetes cluster is a set of machines that run containerized applications. Kubernetes provides a portable, extensible, open source platform for managing containerized workloads and services in those nodes. A Kubernetes cluster is formed of worker nodes and control plane nodes.

 
 
- Kubernetes worker node 
A Kubernetes worker node is a worker machine that runs containerized applications within a Kubernetes cluster. Every cluster has at least one worker node.

 
 
- Kubernetes control plane 
A Kubernetes control plane manages the resources for the worker nodes and pods within a Kubernetes cluster. The control plane components detect and respond to events, perform scheduling, and move cluster resources.

 
The following are the control plane components:
 
 
- kube-apiserver: Runs the Kubernetes API server. 
 
- etcd: Distributed key-value store for all cluster data. 
 
- kube-scheduler: Determines which node new unassigned pods will run on. 
 
- kube-controller-manager: Runs controller processes. 
 
- cloud-controller-manager: Links your cluster with cloud-specific API. 
 
 

 
 
- Ingress Controller 
An Ingress controller is a
 component that runs in a Kubernetes cluster and manages the Ingress resources.
 It receives traffic from the external network, routes it to the correct service,
 and performs load balancing and SSL termination. The Ingress controller
 typically runs as a separate pod in the cluster and can be scaled independently
 from the services it manages.

 
 
- KUBE-Endpoint API 
The KUBE-Endpoint API is the
 kube-apiserver component of the Kubernetes control plane.
 It runs the Kubernetes API server.
 

 
 
- ETCD Backup 
ETCD Backup is a backup of
 etcd component of the Kubernetes control plane. The
 etcd contains the distributed key-value store for all
 cluster data. It's important to create an ETCD Backup to recover Kubernetes
 clusters for disaster recovery.
 

 
 
- YAML Snapshots 
A YAML snapshot is a point-in-time
 copy of the (yaml) files containing the definition of the
 artifacts in a Kubernetes cluster. The snapshot is a tar
 file that you can use to restore those artifacts in the same
 or a different Kubernetes cluster.

 
 
 

 

 
 
Considerations for Kubernetes
 Disaster Protection

 

 
When implementing disaster protection for Kubernetes, consider the
 following:

 
 
- Symmetric disaster recovery (DR) : Oracle recommends using the
 exact same resource capacity and configuration in primary and secondary. The
 Kubernetes namespaces involved should have similar resources available, such as the
 number of worker nodes (and their hardware capacity) and other infrastructure
 (shared storage, load balancers, databases, and so on). The resources on which the
 Kubernetes cluster in the secondary region depend, must be able to keep up with the
 same workloads as primary. Also, the two systems must be consistent functionally
 with the exact same services on which the restored system depends on, side cars,
 configuration maps (CMs) must be used in both locations. 
 
 
- Images present a similar paradigm to binaries : Images don't
 change as frequently as the Kubernetes configuration and you might not need to
 update images with every Kubernetes cluster replication. The images used by the
 primary system must be the same as the ones used in the secondary system or
 inconsistencies and failure may take place. However, image replication is out of the
 scope of this playbook. There are multiple strategies that you can use to maintain a
 consistent use of images between two locations, including the following:
 
 
- Save images in primary and load to secondary’s worker nodes.
 This approach is very easy to implement but incurs in management overhead.
 Using container registries has considerable benefits and saving images
 locally makes it more difficult to manage versions and updates. 
 
- Images can reside in totally external Container reg
