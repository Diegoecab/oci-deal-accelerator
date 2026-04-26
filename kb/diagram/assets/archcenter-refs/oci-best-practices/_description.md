# Well-architected framework for Oracle Cloud Infrastructure

- Source: https://docs.oracle.com/en/solutions/oci-best-practices/index.html
- Date: 2025-05
- Type: reference-architecture
- Services: 
- Tags: security, ha-dr, observability

## Summary (catalog)

OCI Well-Architected Framework covering 5 pillars: security, reliability, performance, cost optimization, and operational excellence. Best practices and review checklists for each pillar.

## Architecture (fetched from source)

Learn About the Well-Architected Framework for Oracle Cloud Infrastructure 
 
 
 
 
- 
 
- 
 
 
 
 
 
- 
 
 
 
 
 
 
 
 
 
- 
 
 
 
 
 
 
 
 
 
- 
 
- 
 
- 
 
- 
 
- 
 
- 
 
- 
 
- 
 
- 
 
- 
 
- 
 
- 
 
 
 
 

 Previous 
 Next 
 JavaScript must be enabled to correctly display this content
 
 

 

 
 
 
Learn About the Well-Architected Framework for Oracle Cloud Infrastructure

 

 

 
 Oracle Cloud
 Infrastructure provides infrastructure and platform services for a wide range of enterprise workloads. In each service, you can choose from a rich array of features based on your goals. Oracle recommends a set of best practices to design and operate cloud topologies that deliver the maximum business value.
 

 
The best practices for Oracle Cloud
 Infrastructure services are organized under five business goals, or pillars:
 
 
- Security and compliance: Secure and protect your systems and information assets in the cloud. 
 
- Reliability and resilience: Build reliable applications by architecting resilient cloud infrastructure. 
 
- Performance and cost optimization: Utilize infrastructure resources efficiently, and derive the best performance at the lowest cost. 
 
- Operational efficiency: Operate and monitor your applications and infrastructure resources to deliver the maximum business value. 
 
- Distributed cloud: Design, integrate, and optimize distributed cloud deployments, spanning public cloud, dedicated regions, hybrid (Oracle Cloud@Customer), edge, and multicloud scenarios. 
 
 

 
For each pillar, the best practices are organized based on key focus areas, as follows:

 

 
 
 
 Pillar 
 Key Focus Areas 
 
 
 
 
 Security and compliance 
 
 
 
- User authentication and authorization 
 
- Resource isolation and access control 
 
- Database security 
 
- Data protection 
 
- Network security 
 
- Environment monitoring and auditing 
 
- Optimizing security postures 
 
 
 
 
 Reliability and resilience 
 
 
 
- Scalability 
 
- Service limits and quotas 
 
- Fault-tolerant network architecture 
 
- Health checks 
 
- Data backup 
 
- Data replication 
 
- Disaster recovery 
 
 
 
 
 Performance and cost optimization 
 
 
 
- Compute sizing 
 
- Storage strategy 
 
- Network monitoring and tuning 
 
- Cost tracking and management 
 
 
 
 
 Operational efficiency 
 
 
 
- Deployment strategy 
 
- Workload monitoring 
 
- OS management 
 
- Operations support 
 
 
 
 
 Distributed cloud 
 
 
 
- Deployment strategy and workload placement 
 
- Seamless integration across environments 
 
- Compliance and sovereignty 
 
- Resilience and disaster recovery 
 
- Unified operations and optimization 
 
 
 
 
 
 

 

 
 
About Personas

 

 
Many of the topics within the articles in this well-architected solution list one or more "personas," intended to map to architect roles within typical Oracle Cloud
 Infrastructure organizations. You can use these personas as a guideline for which members of your organization are responsible for each of the best practices areas described. 
 

 
Each persona is listed in this table with some suggested Oracle Cloud
 Infrastructure certifications offered by Oracle University. The focus areas indicate the pillars that present the most topics directed to that persona.
 

 

 
 
 
 Persona 
 Description 
 Suggested Certifications 
 Focus Areas 
 
 
 
 
 Application Architect 
 Creator and curator of custom applications to be hosted on a cloud
 platform. Goals include understanding the tool set, utilizing the
 platform securely and efficiently, and maintaining stability. Focuses on
 taking advantage of the agility and scalability of a cloud platform to
 enhance the user experience. 
 
 
 
 
- Oracle Cloud
 Infrastructure Foundations Certification
 
 
- Oracle Cloud
 Infrastructure Developer Associate Certification
 
 
- Oracle Cloud
 Infrastructure Architect Associate Certification
 
 
 
 
 
 
 
 
- Security and Compliance 
 
- Reliability and Resilience 
 
 
 
 
 
 Cloud Architect 
 Responsible for taking the needs and requirements of a workload or
 environment and selecting and organizing the best services and solutions
 for the deployed state of the host environment. Can see across the
 different cloud domains and interconnect the policies and requirements
 into a complete solution. 
 
 
 
 
- Oracle Cloud
 Infrastructure Architect Associate Certification
 
 
- Oracle Cloud
 Infrastructure Architect Professional Certification
 
 
- Oracle Cloud
 Infrastructure Operations Associate Certification
 
 
 
 
 
 
 
 
- Security and Compliance 
 
- Operational Efficiency 
 
- Reliability and Resilience 
 
 
 
 
 
 Cloud Operations Manager 
 Accountable for the operational management of cloud infrastructure, ensuring
 optimized performance, security, and scalability of the cloud
 architecture. Oversees IaaC choices and Incident management processes,
 as well as providing continuous feedback on required changed to
 processes and tools. 
 
 
 
- Oracle Cloud
 Infrastructure Architect Associate Certification
 
 
- Oracle Cloud
 Infrastructure Architect Professional Certification
 
 
- Oracle Cloud
 Infrastructure Operations Associate Certification
 
 
 
 
 
 
- Operational Efficiency 
 
- Performance Efficiency and Cost Optimization 
 
- Reliability and Resilience 
 
 
 
 
 DevOps Architect 
 Responsible for identifying the utility of virtualization and
 automation tools from the operations side and the process and skill set
 of the development side. Understands what is happening with a cloud
 application and develops and manages the tools to automatically respond.
 Collects and applies data from monitoring and alerting to establish a
 dynamic, reactive environment. Identifies tools and programs that best
 fit a workload and how best to incorporate them into system that meets
 requirements. 
 
 
 
 
- Oracle Cloud
 Infrastructure Developer Associate Certification
 
 
- Oracle Cloud
 Infrastructure Architect Associate Certification
 
 
- Oracle Cloud
 Infrastructure Architect Professional Certification
 
 
- Oracle Cloud
 Infrastructure Operations Associate Certification
 
 
 
 
 
 
 
 
- Operational Efficiency 
 
- Security and Compliance 
 
- Reliability and Resilience 
 
 
 
 
 
 Enterprise Architect 
 Responsible for an organization's overall technology strategy. Often
 a C-Level executive accountable for budget, service availability, and
 other applicable business metrics. May be responsible for selecting
 cloud providers, sponsoring a cloud business office, and aligning the
 organizational structure to enable cloud deployments. 
 
 
 
 
- Oracle Cloud
 Infrastructure Foundations Certification
 
 
- Oracle Cloud
 Infrastructure Developer Associate Certification
 
 
- Oracle Cloud
 Infrastructure Architect Associate Certification
 
 
- Oracle Cloud
 Infrastructure Operations Associate Certification
 
 
- Oracle Cloud
 Infrastructure Enterprise Workloads Associate Certification
 
 
 
 
 
 
 
 
- Operational Efficiency 
 
- Security and Compliance 
 
- Reliability and Resilience 
 
- Performance Efficiency and Cost Optimization 
 
 
 
 
 
 Network Architect 
 Responsible for ensuring application connectivity is resilient, performant, and secure. Accountable for hybrid cloud connectivity, on-premises/WAN connectivity, ingress/egress connectivity, and lateral (East <-> West) connectivity. May also be responsible for cloud VCN design, security group stategy, load balancer configuration, inter and intra-region peering, and FastConnect connectivity. Ensures capacity is available for steady-state workloads, and spikes caused by migration or data loads. 
 
 
 
 
- Oracle Cloud
 Infrastructure Networking Professional Certification
 
 
- Oracle Cloud
 Infrastructure Architect Associate Certification
 
 
- Oracle Cloud
 Infrastructure Operations Associate Certification
 
 
- Oracle Cloud
 Infrastructure Enterprise Workloads Associate Certification
 
 
 
 
 
 
 
 
- Security and Compliance 
 
- Reliability and Resilience 
 
 
 
 
 
 Security Ar
