# Implement fine-grained access control on Oracle Integration

- Source: https://docs.oracle.com/en/solutions/integration-access-control/index.html
- Date: 2025-06
- Type: reference-architecture
- Services: oic
- Tags: integration, security

## Summary (catalog)

Fine-grained RBAC for Oracle Integration flows. Project-level access control with custom roles. Separation of duties between integration developers and administrators.

## Architecture (fetched from source)

Architecture

 

 
This architecture outlines a fine-grained access control model for Oracle Integration .
 

 
Architecture details:

 
 
- The OCI API Gateway triggers OCI Functions , which acts as a custom authorizer to handle the authorization logic for the
 incoming request. This request includes an access token intended to grant access to
 Oracle Integration .
 
 
- The authorizer function performs the following steps:
 
 
- It extracts the token from the request and uses it to query OCI Vault for sensitive credentials such as the client ID and client secret.
 
 
- Using these credentials, the function validates the token
 against Oracle Identity Cloud
 Service (IDCS) to ensure its authenticity and integrity.
 
 
- If the token is valid, the function returns a response containing key
 details such as:
 
 
- Token validity status 
 
- Principal (user identity) 
 
- Client ID and client secret 
 
- Scope of access 
 
 
 
 
 
- The OCI API Gateway then uses scope in this response to verify the token’s scope against the required
 access level for the Oracle Integration integration.
 
 
 
If the scope matches, the OCI API Gateway forwards the original request to the Oracle Integration API which is protected by an allowlist, now enriched with validated authorization
 headers, allowing the integration flow to continue securely.
 

 
The following diagram illustrates this reference architecture.

 
 Description of the illustration oracle-integration-rest-oauth-diagram.png 

 oracle-integration-rest-oauth-diagram-oracle.zip 

 
The architecture has the following components:

 
 
- Region 
An OCI region
 is a localized geographic area that contains one
 or more data centers, hosting availability
 domains. Regions are independent of other regions,
 and vast distances can separate them (across
 countries or even continents).

 
 
- Virtual cloud network (VCN) and subnets 
A
 VCN is a customizable, software-defined network
 that you set up in an OCI region. Like traditional
 data center networks, VCNs give you control over
 your network environment. A VCN can have multiple
 non-overlapping classless inter-domain routing
 (CIDR) blocks that you can change after you create
 the VCN. You can segment a VCN into subnets, which
 can be scoped to a region or to an availability
 domain. Each subnet consists of a contiguous range
 of addresses that don't overlap with the other
 subnets in the VCN. You can change the size of a
 subnet after creation. A subnet can be public or
 private. 

 
 
- API Gateway 
 Oracle Cloud Infrastructure API Gateway enables you to publish APIs with private
 endpoints that are accessible from within your
 network, and which you can expose to the public
 internet if required. The endpoints support API
 validation, request and response transformation,
 CORS, authentication and authorization, and
 request limiting.
 

 
 
- Functions 
 Oracle Cloud Infrastructure
 Functions is a fully-managed, multitenant, highly
 scalable, on-demand, Functions-as-a-Service (FaaS)
 platform. It is powered by the Fn Project open
 source engine. OCI Functions enables you to deploy your code, and either
 call it directly or trigger it in response to
 events. OCI Functions uses Docker containers hosted in Oracle Cloud Infrastructure
 Registry .
 

 
 
- Integration 
 Oracle Integration is a fully-managed, preconfigured environment
 that allows you to integrate cloud and on-premises
 applications, automate business processes, and
 develop visual applications. It uses an
 SFTP-compliant file server to store and retrieve
 files and allows you to exchange documents with
 business-to-business trading partners by using a
 portfolio of hundreds of adapters and recipes to
 connect with Oracle and third-party
 applications.
 

 
 
- Identity
 and Access Management 
 Oracle Cloud Infrastructure Identity
 and Access Management (IAM) provides user access control for OCI and
 Oracle Cloud Applications. The IAM API and the
 user interface enable you to manage identity
 domains and the resources within them. Each OCI
 IAM identity domain represents a standalone
 identity and access management solution or a
 different user population.
 

 
 
- Oracle Cloud Infrastructure Vault 
 Oracle Cloud Infrastructure Vault enables you to create and centrally manage the
 encryption keys that protect your data and the
 secret credentials that you use to secure access
 to your resources in the cloud. The default key
 management is Oracle-managed keys. You can also
 use customer-managed keys which use OCI Vault . OCI Vault offers a rich set of REST APIs to manage vaults
 and keys.
 

 
 
 

 

 
 
Explore More

 

 
Learn more about Oracle Integration integrations.
 

 
Review these additional resources:

 
 
- Overview of API Gateway in Oracle Cloud Infrastructure
 Documentation 
 
- Oracle Integration 3 
 
- Configuring OAuth in Oracle
 Cloud Infrastructure Documentation 
 
- Validating Tokens to Add
 Authentication and Authorization to API Deployments in Oracle Cloud
 Infrastructure Documentation 
 
- Oracle Cloud Cost Estimator 
 
- Oracle Cloud
 Infrastructure Documentation 
 
- Well-architected framework
 for Oracle Cloud Infrastructure 
 
 

 

 
 
Acknowledgments

 

 
 
- Authors : Pradyumna Kodgi, Ravi Pinto, Sumit
 Aneja 
 
- Contributors : John Sulyok 
 
 

 

 

 

 

 
 Title and Copyright Information 

 

 
Implement fine-grained access control on Oracle Integration

 
G36317-01

 
June 2025

 
 Copyright © 2025, 

Oracle and/or its affiliates.
