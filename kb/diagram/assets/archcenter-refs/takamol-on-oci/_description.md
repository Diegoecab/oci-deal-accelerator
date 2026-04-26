# Takamol: Deploy Kubernetes and microservices for a government HR platform on Oracle Cloud

- Source: https://docs.oracle.com/en/solutions/takamol-on-oci/index.html
- Date: 2024-11
- Type: built-deployed
- Services: oke, adb-s
- Tags: application

## Summary (catalog)

Government HR platform on OKE. Microservices architecture with ADB-S for data persistence. Container-based deployment for scalability and operational efficiency.

## Architecture (fetched from source)

Architecture

 

 
Takamol Holding engineers connect to a zero-trust, network access tool and are authenticated through their own single sign-on before gaining access to the virtual cloud network (VCN).

 
Platform users are routed through Oracle Cloud
 Infrastructure Load Balancing which administers user requests across three separate fault domains. User requests are then sent to the Oracle Cloud Infrastructure Kubernetes Engine (OKE) ingress controller, where they are inspected before being routed to their final destination.
 

 
Within the Kubernetes cluster, Takamol uses multiple, open-source tools to process
 user requests, including NGINX, a reverse proxy server, a load balancer, and an API
 gateway. These services are scaled across the Kubernetes cluster by using horizontal pod
 autoscaling (HPA) to meet high demands during peak hours. Takamol also uses a layer 7
 app protect denial of service (DoS) app, along with an app protect WAF by F5 NGINX. Most
 of Takamol's applications are stateless, following the 12 factors model, so they don't
 require in-application caches or storage. Instead, Takamol's applications use external
 storage services, which makes them easily to deploy, auto scale, and manage within the
 Kubernetes cluster.

 
Takamol also uses Argo CD, a declarative, GitOps, continuous delivery tool for Kubernetes. Using Argo CD, Takamol can deploy its workloads declaratively, without providing direct access to the cluster, which makes it possible to have its cluster deployed to a private subnet. Rather than developers updating applications, Argo CD reads from a Gitlab repository to deploy new services, without providing Gitlab direct access to update the cluster. For its stateful components, Takamol uses PostgreSQL for its database and RabbitMQ for message queuing. 

 
The load balancer, Kubernetes cluster, and open-source tools are each located in separate subnets. Although these are isolated from each other, they can send and receive information through communications ports. Using the Oracle VCN flow logs and a SEIM security operations center (SOC), Takamol can virtualize communications between the different subnets without having to install additional tools. In the coming months, Takamol plans to send its VCN flow logs through Oracle Cloud Infrastructure
 Functions to deliver network logs to the SEIM solution.
 

 
 
- Roughly 90% of Takamol's architecture was built by using infrastructure as code (IaC) from the open-source Oracle Cloud
 Infrastructure Terraform Provider with their own in-house built modules. This approach reduces the human effort needed to deploy and manage the infrastructure, enabling faster changes with significantly reduced risk of human error.
 
 
- All of the services in Takamol's development, testing, and preproduction environments are replicated as its production environment. None of these environments are interconnected. This ensures consistency between the environments. 
 
- Database backups are done using pgbackrest, which archives and stores backups in Oracle Cloud
 Infrastructure Block Volumes . This allows long term storage for the database while supporting point-in-time (PIT) recovery.
 
 
- Oracle Cloud
 Infrastructure Object Storage is used by microservices, metrics, OKE logs, and GitLab runners to cache data. It also provides cost-effective, long term, database backups of their PostgreSQL databases.
 
 
- Oracle Cloud Infrastructure
 Registry and Oracle Cloud Infrastructure Identity
 and Access Management policies help Takamol control user access to the repositories. Previously, the company used Docker Hub, which did not provide as fine-grained control as does OCI. Moreover, with OCI Registry, Takamol uses the built-in security scan feature.
 
 
- Takamol uses Loki, a time-series database for logs, Prometheus for metrics collection, Tempo for traces, and Grafana for visualization which are all centralized in the single OKE cluster. 
 
 
The following diagram illustrates this reference architecture.

 
 Description of the illustration takamol-oci-arch.png 

 takamol-oci-arch-oracle.zip 

 
For a future state and roadmap Takamol is looking to move more services to managed and cloud-native services:

 
 
- Run a disaster recovery site out of the Oracle Cloud region in Neom.
 
 
- Leverage Oracle Cloud
 Infrastructure Search with OpenSearch for a distributed, fully managed, and maintenance-free full-text search engine.
 
 
- Leverage Oracle Autonomous Data Warehouse for database workloads.
 
 
- Use Oracle Cloud
 Infrastructure Vulnerability Scanning Service to scan for vulnerabilities, particularly in docker images.
 
 
 
The architecture has the following components:

 
 
- Tenancy 
A tenancy is a secure and isolated partition that Oracle sets up within Oracle Cloud when you sign up for Oracle Cloud
 Infrastructure . You can create, organize, and administer your resources in Oracle Cloud within your tenancy. A tenancy is synonymous with a company or organization. Usually, a company will have a single tenancy and reflect its organizational structure within that tenancy. A single tenancy is usually associated with a single subscription, and a single subscription usually only has one tenancy.
 

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that contains one or more data centers, called availability domains. Regions are independent of other regions, and vast distances can separate them (across countries or even continents).
 

 
 
- Compartment 
Compartments are cross-regional logical partitions within an Oracle Cloud
 Infrastructure tenancy. Use compartments to organize, control access, and set usage quotas for your Oracle Cloud resources. In a given compartment, you define policies that control access and set privileges for resources.
 

 
 
- Availability domain 
Availability domains are standalone, independent data centers within a region. The physical resources in each availability domain are isolated from the resources in the other availability domains, which provides fault tolerance. Availability domains don’t share infrastructure such as power or cooling, or the internal availability domain network. So, a failure at one availability domain shouldn't affect the other availability domains in the region.

 
 
- Fault domain 
A fault domain is a grouping of hardware and infrastructure within an availability domain. Each availability domain has three fault domains with independent power and hardware. When you distribute resources across multiple fault domains, your applications can tolerate physical server failure, system maintenance, and power failures inside a fault domain.

 
 
- Virtual cloud network (VCN) and subnets 
A VCN is a customizable, software-defined network that you set up in an Oracle Cloud
 Infrastructure region. Like traditional data center networks, VCNs give you control over your network environment. A VCN can have multiple non-overlapping CIDR blocks that you can change after you create the VCN. You can segment a VCN into subnets, which can be scoped to a region or to an availability domain. Each subnet consists of a contiguous range of addresses that don't overlap with the other subnets in the VCN. You can change the size of a subnet after creation. A subnet can be public or private. 
 

 
 
- Security list 
For each subnet, you can create security rules that specify the source, destination, and type of traffic that must be allowed in and out of the subnet.

 
 
- Route table 
Virtual route tables contain rules to route traffic from subnets to destinations outside a VCN, typically through gateways.

 
 
- Internet gateway 
The internet gateway allows traffic between the public subnets in a VCN and the public internet.

 
 
- Service gateway 
The service gateway provides access from a VCN to other services, such as Oracle Cloud
 Infrastructure Object Storage . The traffic from the VCN to the Oracle service travels over the Oracle network f
