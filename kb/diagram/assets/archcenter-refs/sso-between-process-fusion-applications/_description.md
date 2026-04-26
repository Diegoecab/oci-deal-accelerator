# Configure single sign-on between Oracle Integration and Oracle Fusion Applications

- Source: https://docs.oracle.com/en/solutions/sso-between-process-fusion-applications/index.html
- Date: 2025-08
- Type: reference-architecture
- Services: oic
- Tags: integration, security

## Summary (catalog)

SSO configuration between OIC and Fusion Applications. SAML-based federation for seamless user experience across integration and application platforms.

## Architecture (fetched from source)

Architecture

 

 

 SSO federation enables you to choose the most suitable approach for
 your enterprise architecture and identity management needs from the available
 approaches. You can configure SSO between Oracle Fusion Applications , Oracle Integration , Microsoft Active Directory Federation Service , and other OCI services like OCI Object Storage . 
 
 

 

 
SSO with Oracle
 Fusion Cloud Applications identity domain
 

 
 
 
The Fusion Applications identity domain can deploy extensions and
 integrations, including provisioning Oracle Integration within the same domain. This approach eliminates the need to create additional
 OCI IAM identity domains, and helps you reduce both licensing costs and
 administrative overhead. Since the Oracle Fusion Applications identity domain is an Oracle App, extension use cases are supported without
 incurring extra costs, which minimizes operational and governance overhead. This
 involves provisioning Oracle Integration within the Oracle Fusion Applications identity domain.
 

 
 
The following diagram illustrates this authentication flow:

 

 
 Description of the illustration sso-fusion-apps-idm.png 

 
 

 

 
SSO with Oracle Fusion Applications identity domain and an external identity provider
 

 
 
 
If you already use an external identity provider (such as, Microsoft
 Entra ID or Okta) for your applications you can extend it as the identity provider
 for Oracle Fusion Applications and Oracle Integration . This approach centralizes user and access management, and also reduces
 duplication and administrative effort. You configure SSO with Oracle Fusion Applications identity domain as the service provider and your external identity provider. Oracle Integration is provisioned with Oracle Fusion Applications identity domain.
 

 
 
The following diagram illustrates this authentication flow:

 

 
 Description of the illustration sso-fusion-apps-idm-external-idp.png 

 
 

 

 
SSO between Oracle Fusion Applications identity domain, an OCI IAM identity domain, and an external identity
 provider
 

 
 
 
The Oracle Fusion Applications identity domain can act as the identity store for managing users and groups
 specific to Oracle Fusion Applications and Oracle Integration . At the same time, a separate OCI identity domain can function as a centralized
 identity store to manage users and groups that require controlled access to OCI
 services such as OCI Object Storage , OCI Logging , and OCI Functions .
 

 
 
The following diagram illustrates this authentication flow:

 

 
 Description of the illustration sso-fusion-apps-idm-oci.png 

 
 

 

 

 
 
Considerations for Oracle
 Fusion Cloud Applications 

 

 
All Fusion
 Applications environments are provisioned with an OCI Identity and Access Management identity domain.
 

 
 This identity domain is pre-integrated with Fusion
 Applications internal identity system and acts as the identity backbone for tools like Oracle Visual Builder Studio . Users created in Fusion
 Applications are automatically synchronized with this domain.
 

 
By default, federated SSO is configured, with Fusion
 Applications serving as the identity provider (IdP) and the Fusion
 Applications identity domain as the service provider.
 

 

 
 Oracle
 Fusion Cloud Applications Identity Domain and Identity Upgrade
 

 
 
 
 Oracle
 Fusion Cloud Applications are upgrading their user identity service to Oracle Cloud Infrastructure Identity
 and Access Management , with this transition being rolled out to existing Oracle customers over the
 coming quarters. 
 

 
 
The new Oracle
 Fusion Cloud Applications identity domain in OCI will provide enhanced capabilities for authentication,
 sign-on policies, SSO, multifactor authentication, and identity lifecycle
 management. This upgrade designates the Oracle
 Fusion Cloud Applications identity domain as the identity provider for Oracle
 Fusion Cloud Applications .
 

 
 
For more information, see Identity Upgrade
 Overview in the Explore More section.
 

 
 

 

 

 
 
About Required Services, Products, and Roles

 

 
This solution requires the following services, products, and roles:

 
 
- 
 Oracle
 Fusion Cloud Applications 
 
- Oracle Integration 
 
- Oracle Cloud Infrastructure Identity
 and Access Management 
 
 
These are the roles needed for each service.

 

 
 
 
 Service Name: Role 
 Required to... 
 
 
 
 
 Oracle Fusion Applications : Application Administrator
 
 Configure and test federated
 SSO configuration for Oracle Fusion Applications .
 
 
 
 Oracle Integration : Service Administrator
 
 Configure and test federated SSO configuration for Oracle Integration .
 
 
 
 Identity Domain Administrator 
 
 
 
- Configure SSO between Oracle Fusion Applications identity domain and Microsoft Entra
 ID .
 
 
- Configure SSO between Oracle Cloud Infrastructure Identity
 and Access Management and Microsoft Entra
 ID .
 
 
 
 
 
 
 

 
See Oracle Products, Solutions, and Services to
 get what you need.
 

 

 

 

 

 

 
 Title and Copyright Information 

 

 
Configure single sign-on between Oracle Integration and Oracle Fusion Applications

 
F17402-02

 
August 2025

 
 Copyright © 2019,2025, 

Oracle and/or its affiliates.
