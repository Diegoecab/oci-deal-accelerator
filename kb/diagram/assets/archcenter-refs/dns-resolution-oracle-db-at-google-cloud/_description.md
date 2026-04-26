# Configure DNS resolution in Oracle Database@Google Cloud

- Source: https://docs.oracle.com/en/solutions/dns-resolution-oracle-db-at-google-cloud/index.html
- Date: 2025-11
- Type: reference-architecture
- Services: dns, google-cloud, exacs
- Tags: networking, multicloud

## Summary (catalog)

DNS configuration for Database@Google Cloud. Cloud DNS forwarding zones for OCI service resolution, private DNS for VCN name resolution from Google Cloud applications.

## Architecture (fetched from source)

Architecture

 

 

 During deployment, a Google Cloud DNS Zone is created to map Oracle Database@Google Cloud resources to FQDNs as follows: 
 
 

 
 
- *.oraclevcn.com for Oracle Exadata Database
 Service , Oracle Exadata Database Service on Exascale Infrastructure , and Oracle Base Database Service .
 
 
- *.oraclecloud.com and
 *.oraclecloudapps.com for Oracle Autonomous Database .
 
 
 
An OCI Private DNS listener endpoint is created during Oracle Database@Google Cloud deployment, associated with the private resolver, default private view, and a private
 zone to the OCI VCN to resolve names and IPs in the OCI DNS service.
 

 
The following architecture shows the Google Cloud DNS Zone forwarded to the OCI Private DNS listener endpoint:
 

 
 Description of the illustration resolve-dns-oci-google-cloud.png 

 resolve-dns-oci-google-cloud-oracle.zip 

 
The architecture enables private, controlled connectivity from an application
 in Google Cloud to Oracle Database@Google Cloud with DNS resolution handled by OCI DNS through a private listener.
 

 
The architecture has the following components:

 
 
- OCI virtual cloud
 network and subnet 
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

 
 
- Security list 
For
 each subnet, you can create security rules that
 specify the source, destination, and type of
 traffic that is allowed in and out of the
 subnet.

 
 
- Network security group
 (NSG) 
NSGs act as virtual firewalls for your cloud resources. With the zero-trust security model of OCI you control the network traffic inside a VCN. An NSG consists of a set of ingress and egress security rules that apply to only a specified set of virtual network interface cards (VNICs) in a single VCN.

 
 
- Private DNS resolver 
A
 private DNS resolver answers DNS queries for a
 VCN. A private resolver can be configured to use
 views, zones, and conditional forwarding rules to
 define how queries are resolved.

 
 
- Listener endpoint 
A listener endpoint
 receives queries from within the VCN, from other
 VCN resolvers, or from an on-premises network's
 DNS. After creation, no further configuration is
 needed.

 
 
- Forwarder endpoint 
A forwarder endpoint
 forwards DNS queries to the listener endpoint for
 resolvers in other peered VCNs or an on-premises
 DNS. Forwarding decisions are governed by resolver
 rules.

 
 
- Resolver rules 
Resolver rules define how to
 respond to queries not answered by a resolver's
 view. They are processed in order and can have
 optional conditions to limit which queries they
 apply to. When a condition matches, the forwarding
 action is performed.

 
 
- Google Virtual Private Cloud 
Google
 Virtual Private Cloud (VPC) provides networking
 functionality to Compute Engine virtual machine (VM)
 instances, Google Kubernetes Engine (GKE) containers,
 database services, and serverless workloads. VPC provides
 global, scalable, and flexible networking for your
 cloud-based service.

 
 
- Google Cloud DNS 
Cloud
 DNS provides both public zones and privately managed DNS
 zones. Public zones are visible on the internet; private
 zones are visible only within specified VPC
 networks.

 
 
- Google Cloud DNS forwarder 
Google Cloud supports
 inbound and outbound DNS forwarding for private zones. You
 can configure DNS forwarding by creating a forwarding zone
 or a Cloud DNS server policy.

 
 
- Google Cloud project 
A Google
 Cloud Project is required to use Google Workspace APIs and
 build Google Workspace add-ons or apps. A Cloud Project
 forms the basis for creating, enabling, and using all Google
 Cloud services, including managing APIs, enabling billing,
 adding and removing collaborators, and managing
 permissions.

 
 
- ODB network 
The ODB network creates a metadata construct around the Google Virtual Private Cloud (VPC), serving as the foundation for all database provisioning. The ODB network enables support for Shared VPC by abstracting and centralizing network configuration - such as subnets, CIDR ranges, and routing. This allows network administrators to manage connectivity independently of database deployment workflows.

 
 
 

 

 
 
Before You Begin

 

 
 To implement the DNS use cases, ensure you have the following roles and
 permissions: 

 
 
- Cloud DNS supports IAM permissions at both the project and individual
 DNS zone levels. See the Google Cloud DNS permissions
 documentation .
 
 
- OCI DNS supports IAM; see the OCI IAM permissions documentation .
 
 
 

 

 

 

 

 
 Title and Copyright Information 

 

 
Configure DNS resolution in Oracle Database@Google Cloud

 
G44531-02

 
November 2025

 
 Copyright © 2025, 

Oracle and/or its affiliates.
