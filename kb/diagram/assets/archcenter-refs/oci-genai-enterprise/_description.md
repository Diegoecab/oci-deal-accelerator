# Build an enterprise level Generative AI stack on Oracle Cloud Infrastructure

- Source: https://docs.oracle.com/en/solutions/oci-genai-enterprise/index.html
- Date: 2024-09
- Type: reference-architecture
- Services: genai, oke, object-storage
- Tags: ai-ml

## Summary (catalog)

Enterprise GenAI stack with model fine-tuning, RAG, and inference. OCI AI Infrastructure for GPU compute, Object Storage for model artifacts, OKE for scalable inference serving.

## Architecture (fetched from source)

Architecture

 

 
This reference architecture describes a four layer AI stack and all the
 different components that are needed to implement an enterprise grade Generative AI solution
 within an enterprise setting.

 
 
- Application Layer 
 
- Access Layer 
 
- Logging and Monitoring across the solution 
 
- AI layer consisting of the following five modules:
 
 
- AI integration 
 
- LLM 
 
- AI Development 
 
- Data Integration 
 
- Context and Data Catalog 
 
 
 
 
The hypothetical flow considered for this reference architecture is
 described in the following section:

 
 
- A request will come in from the application to the API and Access
 layer. 
 
- The layer is protected by WAF and the request is checked for
 authentication using OCI Identity and Access Management and authorization policies.
 
 
- The API gateway then takes the request to the integration layer, this
 layer includes LangChain which is used for AI abstraction and orchestration. This
 layer also includes the prompts repository that have been whitelisted and mapped to
 the proper authorization and the LLM model version. 
 
- The request is sent to the LLM that matches the request class and
 prompt. 
 
- Context and consumer history is loaded from the context database. 
 
- The location of any data that needs to be enriched is accessed from the
 data catalog. 
 
- Let us say some data is still missing, The Data integration layer will
 first check if the data has been cached and if not it will be queried from the
 customer's data. 
 
- LLM will respond through integration. 
 
- The response will pass through the Hallucination checker, the
 Hallucination checker will then run adversarial AI to validate whether the response
 is meaningful. 
 
- Finally it goes through the API gateway back to the application. 
 
 
The following diagram illustrates this reference architecture.

 
 Description of the illustration oci-genai-enterprise-arch.png 

 oci-genai-enterprise-arch-oracle.zip 

 
Let us go through the building blocks that make each block layer:

 
 AI Layer 
 
- Mix and match LLMs within the LLM module with each LLM used for the
 area it is the best fit for. 
 
- Context should be maintained per customer and across different
 conversations, Data Catalog helps the different LLMs know where to find the required data.
 
 
- Data Integration layer accesses the customer data and provides it
 at speed to AI, this includes the required data caching as well as
 integration. 
 
- AI integration module, maintains the prompts Repo, LangChain to
 abstract LLMs, and Oracle Integration for integration.
 
 
- AI development layer allows for model versioning and storage as
 well as the DevOps needed to evolve the solution. 
 
 

 
 Logging and Monitoring Layer 
 
- Hallucination checker runs adversarial AI to run the output of the
 LLM output to validate its veracity. 
 
- Application Performance Monitoring tracks the performance SLA. 
 
- Logging and auditing track how the Generative AI solution is being
 used to observe the system and identify potential issues. 
 
 

 
 API and Access Layer 
 
- API gateway allows controlled access to the AI Stack. 
 
- The policies are maintained centrally to manage access to the LLM
 stack. 
 
- WAF protects the environment from potential attack vectors. 
 
- Access tokens and control are managed with OCI Identity and Access Management .
 
 
 

 
The architecture has the following components:

 
 
- OCI Generative AI Agents 
OCI Generative AI Agents
 is a fully managed service that combines the power of large language models
 (LLMs) with an intelligent retrieval system to create contextually relevant
 answers by searching your knowledge base, making your AI applications smart and
 efficient.OCI Generative AI Agents supports several ways to onboard your data
 and then allows you and your customers to interact with your data using a chat
 interface or API.

 
 
- Generative AI 
Oracle Cloud Infrastructure
 Generative AI is a fully managed OCI service that
 provides a set of state-of-the-art, customizable
 large language models (LLMs) that cover a wide
 range of use cases for text generation,
 summarization, semantic search, and more. Use the
 playground to try out the ready-to-use pretrained
 models, or create and host your own fine-tuned
 custom models based on your own data on dedicated
 AI clusters.

 
 
- Integration 
 Oracle Integration is a fully managed, preconfigured environment that allows you to integrate cloud and on-premises applications, automate business processes, and develop visual applications. It uses an SFTP-compliant file server to store and retrieve files and allows you to exchange documents with business-to-business trading partners by using a portfolio of hundreds of adapters and recipes to connect with Oracle and third-party applications.
 
 
 
 
- API Gateway 
 Oracle Cloud Infrastructure API Gateway enables you to publish APIs with private endpoints that are accessible from within your network, and which you can expose to the public internet if required. The endpoints support API validation, request and response transformation, CORS, authentication and authorization, and request limiting.
 

 
 
- OCI Data Integration 
Oracle Cloud Infrastructure Data Integration is a
 fully managed, serverless, cloud-native service that extracts, loads,
 transforms, cleanses, and reshapes data from a variety of data sources into
 target Oracle Cloud Infrastructure services, such as Autonomous Data Warehouse
 and Oracle Cloud Infrastructure Object Storage. ETL (extract transform load)
 leverages fully-managed scale-out processing on Spark, and ELT (extract load
 transform) leverages full SQL push-down capabilities of the Autonomous Data
 Warehouse in order to minimize data movement and to improve the time to value
 for newly ingested data. Users design data integration processes using an
 intuitive, codeless user interface that optimizes integration flows to generate
 the most efficient engine and orchestration, automatically allocating and
 scaling the execution environment. Oracle Cloud Infrastructure Data Integration
 provides interactive exploration and data preparation and helps data engineers
 protect against schema drift by defining rules to handle schema changes.
 

 
 
- Oracle Exadata Database Service 
 Oracle Exadata Database
 Service enables you to leverage the power of Exadata in
 the cloud. Oracle Exadata Database
 Service delivers proven Oracle Database capabilities on purpose-built, optimized Oracle
 Exadata infrastructure in the public cloud and on
 Cloud@Customer. Built-in cloud automation, elastic
 resource scaling, security, and fast performance
 for all Oracle Database workloads helps you simplify management and
 reduce costs.
 

 
 
- Identity
 and Access Management (IAM) 
 Oracle Cloud Infrastructure Identity
 and Access Management (IAM) is the access control plane for Oracle Cloud
 Infrastructure (OCI) and Oracle Cloud Applications. The IAM
 API and the user interface enable you to manage
 identity domains and the resources within the
 identity domain. Each OCI IAM identity domain
 represents a standalone identity and access
 management solution or a different user
 population.
 

 
 
 

 

 
 
Recommendations

 

 

 Use the following recommendations as a starting point. Your
 requirements might differ from the architecture described here. 
 
 

 
 
- Oracle Cloud
 Infrastructure + Generative AI 
Generative AI can drive innovation, improve processes,
 and help companies accomplish more than ever before, but it requires the right
 approach. Oracle continues to make the best of AI available to enterprises
 everywhere, with a unique focus on high performing models, embedding Generative
 AI across the stack, and data management, security and privacy. By embedding AI
 throughout the entire technology stack - from the infrastructure that businesses
 run on, through to applications for every line of business from finance to
 supply 
