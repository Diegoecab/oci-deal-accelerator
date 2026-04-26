# Multi-tenant application deployment model on OCI

- Source: https://docs.oracle.com/en/solutions/multi-tenant-app-deploy/index.html
- Date: 2025-11
- Type: reference-architecture
- Services: oke, adb-s, load-balancer, api-gateway, functions, mysql, nosql
- Tags: application, autonomous, security

## Summary (catalog)

Three-layer security: IAM auth with JWTs, per-request middleware with tenant context, ORM-based data isolation. Tiered strategies: discriminator columns (standard), dedicated schemas (premium), separate DBs (enterprise).

## Architecture (fetched from source)

Architecture

 

 
This architecture represents a multi-tenant application deployment model on OCI, at a high level. 

 
The following diagram illustrates this reference architecture:

 
 Description of the illustration multi-tenant-app-oci.png 

 multi-tenant-app-oci-oracle.zip 

 
This flexible architecture is organized into three layers:

 

 
 
 
 Layer 
 Purpose 
 Key Action 
 
 
 
 
 Initial Authentication (OCI IAM) 
 Verify global identity 
 Issue JSON Web Token (JWT) after credential validation 
 
 
 Authentication Middleware 
 Verify per-request identity 
 Extract tenant and user context from JWT 
 
 
 Data Access Layer or ORM Hooks 
 
 Enforce data isolation 
 Automatically filter all queries by tenant_id 
 
 
 
 

 
Each layer is described below:

 
 Initial Authentication and Tenant Context Establishment 

 
 
- Authentication Service: The user logs in, typically by using a tenant-specific URL (for example mycompany.app.com) or by selecting a tenant during login.
 
 
- OCI Identity and Access Management (OCI IAM) as the Identity Provider: OCI IAM (specifically, a dedicated Identity Domain ) validates the user's credentials. Crucially, it confirms the user is not only valid but is also a member of the specific tenant group (for example, mycompany-users) they are trying to access.
 
 
- JWT Issuance: Upon successful authentication, the OCI IAM Identity Domain issues a signed JSON Web Token (JWT). This token includes the following critical claims:
 
 
- sub : The user's unique identifier.
 
 
- groups : An array of OCIDs for the IAM groups the user belongs to. This is the key to identifying the tenant.
 
 
- A custom claim such as tenant_id or tenant_name can be added by using custom attributes in OCI IAM. (Optional) 
 
 
 
 
 
 Authentication Middleware – "Who" layer 

 
The backend must be designed to extract and propagate the tenant context securely. This architecture supports using either OCI API Gateway or OCI Load
 Balancer to perform per-request authentication and tenant context propagation.
 

 
 
- OCI API Gateway : This is the recommended entry point . It can perform JWT validation itself, offloading this responsibility from your application code. You configure it to validate the signature against the JWKS endpoint of your OCI IAM Identity Domain.
 
 
- OCI Load Balancer: Can handle SSL termination and routing but would pass the JWT to the authentication middleware for validation.
 
 
 
 Action: OCI API Gateway validates the JWT's signature and expiry. If invalid, it rejects the request immediately. If valid, it forwards the request to the upstream service, often passing the validated token or extracted claims in headers (for example, X-USER-ID , X-TENANT-ID ).
 

 
If you are using OCI Load
 Balancer instead of OCI API Gateway , the first component of your application backend must be authentication middleware.
 

 
 Action: Extract the JWT from the Authorization: Bearer <token> header, verify its signature using OCI IAM's public keys, decode the claims, and inject the user_id and tenant_id (derived from the groups claim) into the request context for all subsequent layers to use.
 

 
 Data Access Layer or Object-Relational Mapper (ORM) Hook – "What" Layer 

 
This layer automatically injects the tenant ID into every SQL query.

 
 
- Example: A call to getAllInvoices() is transformed into SELECT * FROM invoices WHERE tenant_id = :tenant_id .
 
 
- Enforcement: This is best enforced by a centralized data access layer or an ORM (such as Hibernate) hook or "tenant-aware" connection pool to avoid human error.
 
 
- ORM Hooks: The mechanism that enables true implicit tenant isolation by intercepting and modifying database operations at the application framework level.
 
 
 
 Tenant Data Isolation Strategies: 

 
This architecture supports two options for isolating and protecting your tenants' data:

 
 Option 1: Application Level 

 
 ORM Hooks/Scopes: Frameworks such as Hibernate (Java), Django ORM (Python), or Eloquent (PHP) allow you to define global scopes that automatically add the tenant filter to all queries for a specific model.
 

 
or

 
 Option 2: Database Level 

 
You can use a discriminator column, a separate schema per tenant, or a separate database per tenant:

 
 
- Discriminator Column (Most Common): 
 A tenant_id column is added to every tenant-specific table or document.
 

 
The application's Data Access Layer (DAL) or ORM is responsible for automatically appending the WHERE tenant_id = ? clause to every query. This is achieved through:
 

 
 
- Repository Pattern: All database access flows through a central class or set of classes. This repository automatically adds the tenant filter to every SELECT, INSERT, UPDATE, and DELETE operation based on the tenant_id in the current request context.
 
 
- Connection Context: For some SQL databases (such as Oracle HeatWave MySQL ), the application can set a session variable (for example, SET @tenant_id = 'mycompany123'; ) and then use it in views or stored procedures. However, the application layer is still responsible for setting this value per connection.
 
 
 
 
- Schema Per Tenant: 
Each tenant has a dedicated database schema within the same database instance.

 
The application logic, based on the tenant ID, must switch the database connection's current schema.

 
 
- Connection Pool Per Tenant: Maintain a separate connection pool for each tenant, where each connection is pre-configured to use the tenant's schema (for example, USE tenant_mycompany; ).
 
 
- Dynamic Connection Switching: Use a connection pool that sets the schema on checkout based on the current tenant_id (for example, using a SET search_path TO tenant_mycompany; command for PostgreSQL).
 
 
 
 
- Database Per Tenant: 
Each tenant has its own physically separate database instance with Bring Your Own Keys Encryption for Enterprises.

 
The application needs a tenant data lookup service to map a tenant_id to the correct database connection string.
 

 
 
- The application holds connection pools to multiple databases. 
 
- The DAL uses the tenant ID from the request context to get the correct connection from the pool and execute the query on the dedicated tenant database. 
 
 
This option has advantages and disadvantages:

 
 
- Pros: Maximum isolation, security, and performance. Tenants can even be on different database versions or engine types.
 
 
- Cons: Highest operational overhead, cost, and complexity. Database migrations and patches must be run on every tenant database.
 
 
 
 
 
This architecture implements the following components:

 
 
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

 
 
- OCI Identity and Access Management 
 Oracle Cloud Infrastructure Identity
 and Access Management (IAM) provides user access control for OCI and Oracle Cloud Applications. The IAM API and the user interface enable you to manage identity domains and the resources within them. Each OCI IAM identity domain represents a standalone identity and access management solution or a different user population.
 

 
 
- Load balancer 
 Oracle Cloud
 Infrastructure Load Balancer provides automated traffic distribution from a single entry point to multiple servers.
 

 
 
- OCI API Gateway 
 Oracle Cloud Infrastructure API Gateway enables you to publish APIs with private endpoints that are accessible from within your network, and which you can expose to the public internet if required. The endpoints support API validation, request and response transformation, CORS, authenticati
