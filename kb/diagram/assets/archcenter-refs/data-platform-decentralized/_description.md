# Data platform - decentralized data platform

- Source: https://docs.oracle.com/en/solutions/data-platform-decentralized/index.html
- Date: 2025-03
- Type: reference-architecture
- Services: adw, data-catalog, data-integration, object-storage
- Tags: data-platform, autonomous

## Summary (catalog)

Decentralized data lakehouse with domain-level ADB-S instances sharing data via Cloud Links or Delta Sharing. Centralized catalog, IaC onboarding per domain. Hub-spoke model with OCI backbone routing.

## Architecture (fetched from source)

Data Platform - Decentralized Data Platform 
 
 
 
 
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
 
 

 

 
 
 
- Data platform - decentralized data platform 
 
- Data Platform - Decentralized Data
 Platform 
 
 
 
 
Data Platform - Decentralized Data
 Platform

 
 

 

 
Use a data lakehouse to collect and analyze event and streaming data from
 devices in real time and correlate it with a broad range of enterprise data resources to
 gain the insights you want.

 
How best to support and empower your organization’s various teams, such as
 marketing, finance, or logistics, with the flexibility to work with their
 domain-specific data while also enabling secure cross-domain data sharing and
 consumption without duplicating data and creating data silos?

 
Adopt a domain-driven data architecture that provides teams and departments
 across the organization with the agility and flexibility needed to efficiently use their
 data and develop the data products essential for their business.

 
This reference architecture positions the technology solution within the
 overall business context, where strategic intents drive the creation of measurable
 strategic outcomes. These outcomes generate new strategic intents, effectively
 delivering continuous, data-driven business improvements.

 
 Description of the illustration decentralized-business-context.png 

Each domain independently follows the high-level process shown above to
 create its domain data products. Domain-driven data architectures provide the
 flexibility that organizations require by avoiding reliance on a single point of
 contention, such as a fully centralized data platform and IT team, and by fostering
 agile innovation to produce trusted data products within each domain.

 
 Description of the illustration decentralized-data-platform-overview.png 

 decentralized-data-platform-overview-oracle.zip 

 
The objective of each domain is to acquire domain-related data and then to
 produce data products that are consumed by other domains or final data consumers.

 
The domains can be:

 
 
- Source-aligned: Sources data directly from relevant domain data
 sources, such as enterprise applications, and produces data products that are
 consumed by aggregate or consumer-aligned domains. These data products represent the
 source of truth for a particular domain. The data is granular, curated, and
 foundational within and across domains. 
 
- Aggregate: Consumes and combines source-aligned data, creating
 aggregated and added-value data products that foster reuse, reduce duplication, and
 comprise foundational business logic needed by consumer-aligned domains. 
 
- Consumer-aligned: Consumes data from source-aligned and aggregate
 domains to create data products that serve specific use cases and address data
 consumer's needs within a given domain. 
 
 
The data domain teams and their subject matter experts (SMEs) have the
 flexibility to choose the technology needed to curate their data products, reducing the
 friction and complexity of long technology selection processes, and reducing the time to
 deliver data products.

 
The chosen technology is usually determined at an enterprise level so that
 it adheres to security, scalability, resilience, and high-availability requirements.
 This architecture assumes that any Oracle Cloud
 Infrastructure (OCI) service used with a data lakehouse can be leveraged by any domain.
 

 
Data domain teams often use automation to deploy domain archetypes, making
 preconfigured technologies available to quickly onboard new domains while ensuring that
 enterprise-level requirements, such as security, are enforced.

 
After they are created, data products are then served to other domains or end
 users and applications. Data products are continuously curated to provide information
 and insights.

 
Data products can be of several types. A single data product can be served by
 using more than one interface.
 
 
- Data sets 
 
- APIs 
 
- Dashboards 
 
- Streams 
 
- AI and machine learning (ML) models that address a specific need 
 
 

 
This reference architecture uses primarily data sharing as the underlying
 mechanism to provide and consume data products between domains.

 
 Oracle Autonomous Data Warehouse enables data sharing and allows live sharing of data between Autonomous Data
 Warehouse instances or with versioned data from any technology that is compliant with the Delta
 Sharing open protocol.
 

 

 
 
Functional Architecture

 

 
This architecture depicts a decentralized platform where each domain is a
 subset of the overall data platform and where each domain can choose the technologies and
 services used.

 
 The architecture uses a data lakehouse to store and provide data,
 regardless of its shape or form. For simplicity's sake, the architecture will depict a
 few domains that use a subset of the available data lakehouse services.

 
A decentralized data platform that uses a data lakehouse architecture
 provides:

 
 
- An interoperable and modular lakehouse architecture where data domains
 can ingest and curate any type of data for any use case 
 
- Flexibility for each data domain to use the Oracle Cloud
 Infrastructure (OCI) services needed to support the creation of their data products
 
 
- Curation of data products that can be shared securely by using data
 sharing, streaming, APIs, dashboards, or applications 
 
- Agility in creating data products, reducing interdomain dependencies
 except those required for exchange of data products 
 
- Increased data domain isolation and reduced data interchange complexity
 by using accepted data interchange mechanisms and contracts to exchange data between
 domains 
 
- Increased data governance and data trust because knowledgeable subject
 matter experts (SMEs) curate data and data products for their domains 
 
- Ease of onboarding new data domains using infrastructure as code (IaC)
 to automate deployment using prebuilt and tested Terraform stacks 
 
- Resource and cost efficiency as data domain teams right-size the
 specific services they use to create data products 
 
- Appropriate cost accountability for each data domain with the option of
 fine-grained cost control within the specific domains 
 
 
The following diagram illustrates the functional architecture. For
 simplicity's sake, only four data domains are shown and only some of the data lakehouse
 capabilities that can be used by data domains are shown.

 
 Description of the illustration decentralized-data-platform-logical.png 

 decentralized-data-platform-logical-oracle.zip 

 
Because the particular industry and organization that deploys a decentralized
 data platform determines the data domains, this reference architecture doesn't prescribe
 how data domains should be defined. The data domains depicted are just one example.

 
The architecture focuses on the following logical divisions used by all
 domains:

 
 
- Connect, Ingest, Transform 
Connects to data sources and
 ingests and refines their data for use in each of the data layers in the
 architecture.

 
Source-aligned data domains source data from
 internal and external data sources and from other domains consuming their data
 products. Aggregate and Consumer-aligned data domains usually source their data
 from other domains data products. All domains can source relevant domain data
 from external sources.

 
 
- Persist, Curate, Create 
Facilitates access and
 navigation of the data to show the current business view. For relational
 technologies, data may be logically or physically structured in simple
 relational, longitudinal, dimensional or OLAP forms. For non-relational data,
 this layer contains one or more pools of data, either output from an analytical
 process or data optimized for a specific analytical task.

 
In
 this layer, ea
