# Deploy a secure landing zone that meets the CIS OCI Foundations Benchmark

- Source: https://docs.oracle.com/en/solutions/cis-oci-benchmark/index.html
- Date: 2025-02
- Type: reference-architecture
- Services: cloud-guard, vault, vcn, bastion
- Tags: security

## Summary (catalog)

CIS-compliant OCI landing zone with compartment-based organization, segregation of duties through IAM groups/policies. Supports standalone, hub-spoke, and DMZ VCN patterns. Zero Trust Packet Routing enabled.

## Architecture (fetched from source)

Architecture

 

 
 The architecture starts with the compartment
 design for the tenancy, along with groups and policies for the segregation of duties.
 In OCI Core Landing Zone, provisioning of landing zone compartments within a
 designated parent compartment is supported. Each of the landing zone compartments is
 assigned a group with the appropriate permissions for managing resources in the compartment
 and for accessing required resources in other compartments.
 

 
OCI Core Landing Zone has the ability to provision multiple VCNs, either in
 standalone mode or as constituent parts of a hub-and-spoke architecture, or connected
 through a DMZ VCN. The VCNs can either follow a general-purpose, three-tier network
 topology or be oriented toward specific topologies for supporting OCI Kubernetes Engine (OKE) or Oracle Exadata Database
 Service deployments. They are configured out-of-the-box with the necessary routing, with
 their inbound and outbound interfaces properly secured.
 

 
The landing zone includes various pre-configured security services that can
 be deployed in tandem with the overall architecture for a strong security posture. These
 services are Oracle Cloud Guard , VCN flow logs, OCI Connector Hub , OCI Vault with customer-managed keys, OCI Vulnerability Scanning Service, Security Zones, and
 Zero Trust Packet Routing (ZPR). Notifications are set using Topics and Events for
 alerting administrators about changes in the deployed resources.
 

 
The following diagram illustrates this reference architecture.

 
 Description of the illustration oci-core-landingzone.png 

 oci-core-landingzone-oracle.zip 

 
The architecture has the following components:

 
 
- Tenancy 
A tenancy is a secure and isolated partition that Oracle sets up within Oracle Cloud when you sign up for Oracle Cloud
 Infrastructure . You can create, organize, and administer your resources in Oracle Cloud within your tenancy. A tenancy is synonymous with a company or organization. Usually, a company will have a single tenancy and reflect its organizational structure within that tenancy. A single tenancy is usually associated with a single subscription, and a single subscription usually only has one tenancy.
 

 
 
- Identity domain 
An identity domain is a container
 for managing users and roles, federating and provisioning users, securing
 application integration through single sign-on (SSO) configuration, and
 SAML/OAuth-based identity provider administration. It represents a user
 population in Oracle Cloud Infrastructure and its associated configurations and
 security settings (such as MFA).

 
 
- Policies 
An Oracle Cloud Infrastructure Identity
 and Access Management policy specifies who can access which resources, and how. Access is granted at the group and compartment level, which means you can write a policy that gives a group a specific type of access within a specific compartment, or to the tenancy.
 

 
 
- Compartments 
Compartments are cross-regional logical partitions within an Oracle Cloud
 Infrastructure tenancy. Use compartments to organize, control access, and set usage quotas for your Oracle Cloud resources. In a given compartment, you define policies that control access and set privileges for resources.
 

 
The resources in this landing zone template are
 provisioned in the following compartments:
 
 
- A recommended enclosing compartment containing all
 compartments listed below. 
 
- A Network compartment for all the networking resources,
 including the required network gateways. 
 
- A Security compartment for the logging, key management, and
 notifications resources. 
 
- An App compartment for the application-related services,
 including compute, storage, functions, streams, Kubernetes nodes, API
 gateway, and so on. 
 
- A Database compartment for all database resources. 
 
- An optional compartment for Oracle Exadata Database
 Service infrastructure.
 
 
 

 
The grayed out icons in the diagram indicate services
 that are not provisioned by the template.

 
This compartment
 design reflects a basic functional structure observed across different
 organizations, where IT responsibilities are typically separated among
 networking, security, application development, and database
 administrators.

 
 
- Virtual cloud network (VCN) and subnets 
A VCN is a customizable, software-defined network that you set up in an Oracle Cloud
 Infrastructure region. Like traditional data center networks, VCNs give you control over your network environment. A VCN can have multiple non-overlapping CIDR blocks that you can change after you create the VCN. You can segment a VCN into subnets, which can be scoped to a region or to an availability domain. Each subnet consists of a contiguous range of addresses that don't overlap with the other subnets in the VCN. You can change the size of a subnet after creation. A subnet can be public or private. 
 

 
The template can deploy VCNs for different workload types,
 including three-tier VCNs for typical three-tier web-based applications, OCI Kubernetes Engine applications and Oracle Exadata Database
 Service .
 

 
 
- Internet gateway 
An internet gateway allows traffic between the public subnets in a VCN and the public internet.

 
 
- Dynamic routing gateway (DRG) 
The DRG is a
 virtual router that provides a path for private network traffic between
 on-premises networks and VCNs and can also be used to route traffic between VCNs
 in the same region or across regions.

 
 
- NAT gateway 
A NAT gateway enables private resources in a VCN to access hosts on the internet, without exposing those resources to incoming internet connections.

 
 
- Service gateway 
The service gateway provides access from a VCN to other services, such as Oracle Cloud
 Infrastructure Object Storage . The traffic from the VCN to the Oracle service travels over the Oracle network fabric and does not traverse the internet.
 

 
 
- Oracle services network 
The Oracle Services Network (OSN) is a conceptual network in Oracle Cloud
 Infrastructure that is reserved for Oracle services. These services have public IP addresses that you can reach over the internet. Hosts outside Oracle Cloud can access the OSN privately by using Oracle Cloud
 Infrastructure FastConnect or VPN Connect. Hosts in your VCNs can access the OSN privately through a service gateway.
 

 
 
- Network security groups (NSGs) 
NSGs act as virtual firewalls for your cloud resources. With the zero-trust security model of Oracle Cloud
 Infrastructure you control the network traffic inside a VCN. An NSG consists of a set of ingress and egress security rules that apply to only a specified set of VNICs in a single VCN.
 

 
 
- Events 
 Oracle Cloud
 Infrastructure services emit events, which are structured messages that describe the changes in resources. Events are emitted for create, read, update, or delete (CRUD) operations, resource lifecycle state changes, and system events that affect cloud resources.
 

 
 
- Notifications 
 OCI Notifications broadcasts messages to distributed components by using a low latency publish-subscribe pattern, delivering secure, highly reliable, durable messages for applications hosted on Oracle Cloud
 Infrastructure .
 

 
 
- Vault 
 Oracle Cloud Infrastructure Vault enables you to centrally manage the encryption
 keys that protect your data and the secret
 credentials that you use to secure access to your
 resources in the cloud. You can use the Vault
 service to create and manage vaults, keys, and
 secrets.
 

 
 
- Logs 
 Oracle Cloud Infrastructure Logging is a highly-scalable and fully-managed service that provides access to the following types of logs from your resources in the cloud:
 
 
- Audit logs: Logs related to events produced by OCI Audit .
 
 
- Service logs: Logs published by individual services such as OCI API Gateway , OCI Events , OCI Functions , OCI Load Balancing , OCI Object Storage , and VCN flow logs. 
 
 
- Custom logs: Logs th
