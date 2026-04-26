# Deploy multicloud generative AI retrieval augmented generation (RAG)

- Source: https://docs.oracle.com/en/solutions/oci-multicloud-genai-rag/index.html
- Date: 2025-02
- Type: reference-architecture
- Services: genai, adb-s, object-storage
- Tags: ai-ml, multicloud, autonomous

## Summary (catalog)

Multicloud RAG architecture with OCI GenAI. Document ingestion to ADB-S vector store, embedding generation with OCI GenAI, retrieval and generation pipeline. Cross-cloud connectivity for data sources.

## Architecture (fetched from source)

Architecture

 

 
This multicloud solution sources data from both Microsoft Azure and Oracle Cloud
 Infrastructure (OCI), enabling Oracle Cloud Infrastructure Generative AI Agents to access a broader range of up-to-date information.
 

 
 OCI GenAI Agents and Oracle Integration together support retrieve, augment, and generate (RAG) services to provide highly
 contextualized results. 
 

 
 OCI GenAI Agents specifically focus on using generative AI to respond to user queries by retrieving
 relevant information from knowledge bases or documents to generate answers. The agent
 provides enriched, context-aware responses by leveraging advanced AI techniques,
 embeddings, and document chunking to understand and generate relevant content:
 

 
 
- Retrieve: Extract relevant data from the knowledge sources, usually
 through advanced hybrid search, combining lexical and semantic search. 
 
- Augment: Use the retrieved data to provide context for a query,
 ensuring that the generative AI model has the necessary information. 
 
- Generate: Use large language models (LLMs) to generate contextual responses to user
 questions, often enhanced by the data retrieved in the previous steps. 
 
 
 Oracle Integration , on the other hand, provides integration services that connect various applications
 and systems, allowing for orchestration of data flows across multiple environments:
 

 
 
- Retrieve: Facilitates data retrieval from different sources by using
 connectivity agents to privately connect to various data sources or services
 (database, REST APIs, cloud storage, and so on) on Azure or other hyperscalers. 
 
- Orchestrate/Augment: Orchestrates workflows and integrates data from
 multiple sources, augmenting processes by enriching data through preconfigured or
 dynamic transformations. 
 
- Manage Data Flow: Unlike the RAG agent, Oracle Integration is not focused on generating responses from data but rather on enabling the
 smooth movement and transformation of data between systems and applications,
 ensuring that all the relevant data is available for different services.
 
 
 

 
 
 
 Functional Area 
 OCI GenAI Agents 
 Oracle Integration 
 
 
 
 
 Purpose 
 Designed to provide AI-driven responses by retrieving data,
 augmenting it, and using an LLM for generating responses. 
 Designed to integrate and orchestrate data across multiple
 applications, providing seamless data connectivity but without the
 LLM-driven generation capabilities. 
 
 
 Data Handling 
 Uses data to generate natural language responses in a context-aware
 manner. 
 Handles data flow between applications, acting as a bridge between
 systems without generating content in the same way a LLM does. 
 
 
 Generative Capabilities 
 Has generative AI capabilities and uses LLMs to generate
 conversational responses or other output. 
 Does not have generative AI capabilities and is used to connect,
 retrieve, and transform data across services. 
 
 
 
 

 
The following diagram illustrates the data flow through the architecture:

 
 Description of the illustration multicloud-genai-rag-process.png 

 multicloud-genai-rag-process-oracle.zip 

 
 
- The user interacts with either Oracle Digital Assistant or OCI GenAI Agents , depending on the implementation, to deliver user queries and prompts.
 
 
- Oracle Integration orchestrates calls among different components: pulling from data sources,
 handling doc ingestion, and passing user prompts downstream.
 
 
- Data sources include:
 
 
- Oracle Interconnect for Microsoft Azure provides a high-bandwidth link between OCI and Azure for document
 repositories, Oracle AI Database@Azure , and so on.
 
 
- Local file repositories provide on-premises or local files for
 ingestion. 
 
- OCI Services, such as Oracle Fusion Cloud
 Enterprise Resource Planning .
 
 
- Oracle AI Database@Azure in a delegated subnet for data sharing across Oracle-managed services on
 Azure.
 
 
 
 
- The document ingestion, chunking, and embedding process can be
 implemented in different ways:
 
 
- Oracle Integration (using embedded JavaScript or custom libraries) performs chunking and
 calls OCI Generative AI to embed.
 
 
- OCI Functions receives documents, chunks them, then calls OCI Generative AI for embeddings.
 
 
- Oracle Autonomous AI Database performs chunking and embedding using vector functionality. 
 
 
 
The standard result is a set of chunk-text plus vector
 embeddings completely managed in the multicloud context.

 
 
- Vectors and chunks are stored in Oracle Autonomous AI Database : 
 
 
- The typical approach is to store embeddings in the vector index
 of Oracle Autonomous AI Database .
 
 
- The chunk text itself can also be stored directly in a database
 CLOB (for quick retrieval), or as references that point to the chunk text in
 OCI Object Storage or in Azure Data Lake.
 
 
- OCI Object Storage can store the original documents if needed, but you don’t necessarily
 need to keep embeddings there if you’re querying the vector store in the
 database.
 
 
 
 
- When the user prompts a question, OCI GenAI Agents (or the Digital Assistant) calls Oracle Autonomous AI Database to perform a vector similarity search using the user prompt’s embedding to
 identify the best matching chunks based on vector similarity scores.
 
 
- OCI Generative AI generates embeddings for questions and document chunks and generates responses
 using LLM models, providing contextually enriched answers. Chunk retrieval and LLM
 response also depends on the implementation:
 
 
- If chunk text is stored in the database, it can be retrieved
 directly. 
 
- If only references are stored, the system quickly fetches the
 actual chunk content from OCI Object Storage , Azure Data Lake, or other repository.
 
 
- The relevant chunks are then fed to the LLM in OCI Generative AI along with the user’s original prompt to produce a contextually enriched
 response.
 
 
 
 
- The final answer is returned either by the Oracle Digital Assistant or by the OCI GenAI Agents interface, depending on the front end to which the user is connected.
 
 
 
The following diagram illustrates the architecture:

 
 Description of the illustration multicloud-genai-rag-architecture.png 

 multicloud-genai-rag-architecture-oracle.zip 

 
Microsoft Azure provides the following components:
 
 
- Microsoft Azure region 
An Azure region is a
 geographical area in which one or more physical Azure data centers, called
 availability zones, reside. Regions are independent of other regions, and
 vast distances can separate them (across countries or even
 continents).

 
Azure and OCI regions are localized
 geographic areas. For Oracle AI Database@Azure , an Azure region is connected to an OCI region, with availability zones
 (AZs) in Azure connected to availability domains (ADs) in OCI. Azure and OCI
 region pairs are selected to minimize distance and latency.
 

 
 
- Microsoft Azure availability zone 
An
 availability zone is a physically-separate data center within a region that
 is designed to be highly available and fault tolerant. Availability zones
 are close enough to have low-latency connections to other availability
 zones.

 
 
- Microsoft Azure Virtual Network 
Microsoft
 Azure Virtual Network (VNet) is the fundamental building block for a private
 network in Azure. VNet enables many types of Azure resources, such as Azure
 virtual machines (VM), to securely communicate with each other, the
 internet, and with on-premises networks.

 
 
- Microsoft Azure Delegated Subnet 
Subnet delegation
 allows you to inject a managed service, specifically a platform-as-a-service
 (PaaS) service, directly into your virtual network. A delegated subnet can
 be a home for an externally managed service inside of your virtual network
 so that the external service acts as a virtual network resource, even though
 it is an external PaaS service.

 
 
- Microsoft Azure Data Lake Storage 
Data Lake Storage is a cloud-based,
 enterprise data lake s
