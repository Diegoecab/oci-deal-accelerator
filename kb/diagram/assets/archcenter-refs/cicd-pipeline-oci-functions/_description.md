# Build a CI/CD pipeline for OCI Functions deployment using GitHub Action

- Source: https://docs.oracle.com/en/solutions/cicd-pipeline-oci-functions/index.html
- Date: 2024-10
- Type: reference-architecture
- Services: functions
- Tags: devops

## Summary (catalog)

GitHub Actions workflow for OCI Functions deployment. Automated build, test, and deploy pipeline. Container image build and push to OCI Container Registry, function deployment via OCI CLI.

## Architecture (fetched from source)

Architecture

 

 
This architecture uses GitHub Actions as an external continuous integration
 and deployment system to build code, containerize it, and deploy Oracle Cloud Infrastructure
 Functions. Instead of GitHub Action, you can use other integrated development environment
 (IDE) tools, such as GitLab, or Azure DevOps.

 
The following diagram illustrates this reference architecture.
 
 Description of the illustration cicd-deploy-oci-functions.png 
 cicd-deploy-oci-functions-oracle.zip 

 
The architecture includes the following external systems:

 
 
- External System (CI/CD) 
The external system for
 CI/CD includes the integrated development environment (IDE), the code
 repository, and pipeline. 

 
This architecture uses GitHub
 Actions as an external continuous integration and deployment code repository
 system. It is used to build code and then containerize it using Docker. When the
 containerized image is ready, GitHub Actions pushes the image to an OCI Registry . After completing the transfer to the registry, it kicks off the OCI
 Functions deployment. You can use other continuous integration or deployment
 systems like OCI DevOps, Azure DevOps, Gitlab, or Jenkins based on your
 requirements.
 

 
 
- External System (SIEM/ITSM/OTHER) 
The external
 system for SIEM and ITSM represents other third-party systems or non-OCI
 services. 

 
Aggregating and enriching OCI Audit logs, service
 logs, and security events are foundational requirements to external SIEM or ITSM
 systems. Centralizing this data allows organizations to analyze, monitor, and
 secure their tenancies.

 
 
 
The architecture has the following components:

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that
 contains one or more data centers, called
 availability domains. Regions are independent of
 other regions, and vast distances can separate
 them (across countries or even
 continents).
 

 
 
- Virtual cloud network (VCN) and subnets 
A VCN is a customizable,
 software-defined network that you set up in an Oracle Cloud
 Infrastructure region. Like traditional data center networks,
 VCNs give you control over your network
 environment. A VCN can have multiple
 non-overlapping CIDR blocks that you can change
 after you create the VCN. You can segment a VCN
 into subnets, which can be scoped to a region or
 to an availability domain. Each subnet consists of
 a contiguous range of addresses that don't overlap
 with the other subnets in the VCN. You can change
 the size of a subnet after creation. A subnet can
 be public or private. 
 

 
 
- Registry 
 Oracle Cloud Infrastructure
 Registry is an Oracle-managed registry that enables you
 to simplify your development-to-production
 workflow. Registry makes it easy for you to store,
 share, and manage development artifacts, like
 Docker images. The highly available and scalable
 architecture of Oracle Cloud
 Infrastructure ensures that you can deploy and manage your
 applications reliably.
 

 
 
- Functions 
 Oracle Cloud Infrastructure
 Functions is a fully managed, multitenant, highly
 scalable, on-demand, Functions-as-a-Service (FaaS)
 platform. It is powered by the Fn Project open
 source engine. Functions enable you to deploy your
 code, and either call it directly or trigger it in
 response to events. Oracle Functions uses Docker
 containers hosted in Oracle Cloud Infrastructure
 Registry .
 

 
 
- Service
 connectors 
 Oracle Cloud
 Infrastructure Service Connector Hub is a cloud message bus
 platform that orchestrates data movement between
 services in OCI. You can use service connectors to
 move data from a source service to a target
 service. Service connectors also enable you to
 optionally specify a task (such as a function) to
 perform on the data before it is delivered to the
 target service.
 

 
You can
 use Oracle Cloud
 Infrastructure Service Connector Hub to quickly build a
 logging aggregation framework for security
 information and event management (SIEM) systems.
 
 

 
 
- Logging 
Logging is a
 highly scalable and fully managed service that
 provides access to the following types of logs
 from your resources in the cloud:
 
 
- Audit logs : Logs related to
 events emitted by the Audit service.
 
 
- Service logs : Logs emitted
 by individual services such as API Gateway,
 Events, Functions, Load Balancing, Object Storage,
 and VCN flow logs. 
 
 
- Custom logs : Logs that
 contain diagnostic information from custom
 applications, other cloud providers, or an
 on-premises environment.
 
 
 

 
 
- Streaming 
 Oracle Cloud
 Infrastructure Streaming provides a fully managed, scalable,
 and durable storage solution for ingesting
 continuous, high-volume streams of data that you
 can consume and process in real time. You can use
 Streaming for ingesting high-volume data, such as
 application logs, operational telemetry, web
 click-stream data; or for other use cases where
 data is produced and processed continually and
 sequentially in a publish-subscribe messaging
 model.
 

 
 
- Notifications 
The Oracle Cloud Infrastructure
 Notifications service broadcasts messages to distributed
 components through a publish-subscribe pattern,
 delivering secure, highly reliable, low latency,
 and durable messages for applications hosted on
 Oracle Cloud
 Infrastructure .
 

 
 
 

 

 
 
Recommendations

 

 
 Use the following recommendations as a starting point.
 Your requirements might differ from the architecture described here. 
 

 
 
- VCN 
When you create a VCN, determine the number of CIDR blocks required and the size of each block based on the number of resources that you plan to attach to subnets in the VCN. Use CIDR blocks that are within the standard private IP address space.

 
Select CIDR blocks that don't overlap with any other network (in Oracle Cloud
 Infrastructure , your on-premises data center, or another cloud provider) to which you intend to set up private connections.
 

 
After you create a VCN, you can change, add, and remove its CIDR blocks.

 
When you design the subnets, consider your traffic flow and security requirements. Attach all the resources within a specific tier or role to the same subnet, which can serve as a security boundary.

 
Use regional subnets.

 
 
- Security lists 
Use security lists to define ingress and egress rules that apply to the entire subnet.

 
 
- Network security groups (NSGs) 
You can use NSGs to define a set of ingress and egress rules that apply to specific VNICs. We recommend using NSGs rather than security lists, because NSGs enable you to separate the VCN's subnet architecture from the security requirements of your application.

 
 
- Cloud Guard 
Apply Cloud Guard at
 the tenancy level to cover the broadest scope and to reduce
 the administrative burden of maintaining multiple
 configurations.

 
You
 can also use the Managed List feature to apply certain
 configurations to detectors.

 
 
- Security Zones 
For resources that require maximum security, Oracle recommends that you use security zones. A security zone is a compartment associated with an Oracle-defined recipe of security policies that are based on best practices. For example, the resources in a security zone must not be accessible from the public internet and they must be encrypted using customer-managed keys. When you create and update resources in a security zone, Oracle Cloud
 Infrastructure validates the operations against the policies in the security-zone recipe, and denies operations that violate any of the policies.
 

 
 
- OCI Functions 
Applications deployed through the OCI Functions service are highly available, scalable, secure, and
 monitored. With OCI Functions , you can write code in Java, Python, Node, Go, Ruby, and
 C# (and for advanced use cases, bring your own Dockerfile,
 and Graal VM). You can then deploy your code, call it
 directly or trigger it in response to events.
 

 
 
- OCI Registry 
This architecture deploys a public D
