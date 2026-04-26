# Implement retrieval augmented generation by using Oracle Integration

- Source: https://docs.oracle.com/en/solutions/implement-rag-oci/index.html
- Date: 2024-09
- Type: reference-architecture
- Services: genai, oic, adb-s
- Tags: ai-ml, integration, autonomous

## Summary (catalog)

RAG implementation using OIC for document ingestion pipeline. Pre-built OIC adapters for SaaS data sources, ADB-S for vector storage, GenAI for embedding and generation.

## Architecture (fetched from source)

Architecture

 

 
This reference architecture shows how you can implement a RAG framework using
 semantic search technique to answer a user query on a corporate data using low-code or
 no-code integration platform such as Oracle Integration (OIC) services.
 

 
In this architecture, Oracle Cloud Infrastructure Generative AI is used to create embeddings and generates optimized or helpful answers/responses
 based on the context specific corporate data. Oracle Autonomous Database 23ai is used to store the vector embeddings, create indexes and allows to do a
 semantic search based on the similarity or distance instead of keyword-based search. OCI Functions is used to perform a chunking of corporate documents or data using the standard
 LangChain python packages. OIC services handles the entire orchestration and automation
 process from receiving the corporate data to storing/querying those as vector embeddings
 and generate the optimized and creative context specific answers for the user queries in
 real or near-time fashion. 
 

 
The following diagrams illustrate two processes supported by this reference
 architecture:
 
 
- Retrieval process: 

 
 
 Description of the illustration rag-oic.png 

 
 

 

 rag-oic-oracle.zip 
 
 

 
In this process, the following occurs:

 
 
- Corporate or company data is received to Oracle Integration Retriever service in various formats such as PDF, TXT, CSV, XML,
 JSON,and so on by way of REST, File or sFTP, or any other
 protocols.
 
 
- The Retriever service chunks the documents or data by using
 OCI Functions .
 
 
- The Retriever service then gets the vector embeddings for
 each chunk of data by calling the OCI Generative AI Embedding service by using embedding models such as Cohere or
 others.
 
 
- Finally, the Retriever service stores these embeddings in
 the Oracle Autonomous Database 23ai along with the chunked data.
 
 
 
 
- Augmentation and Generation process: 

 
 
 Description of the illustration rag-oic-aug-gen.png 

 
 

 

 rag-oic-aug-gen-oracle.zip 
 
 

 
In this process, the following occurs:

 
 
- Corporate or company users through front end applications
 ask queries or questions about company data, such as polices, HR, sales,
 purchase history, financial reports, issues, and so on. 
 
- OIC's Generate service receives the query data and invokes
 its local integration's Augment service to get the context for that
 query. 
 
- OIC's Augment service, once invoked, calls OCI Generative AI 's Embedding service to get the vector embeddings of the query data. 
 
 
- OIC's Augment service gets the context stored in the Oracle Autonomous Database 23ai, based on the semantic search of the query data vector
 embeddings. Retrieved context is sent back as a response to the Generate
 service. 
 
 
- The Generate service, with the received context and query,
 invokes the OCI Generative AI Generation service to generate the appropriate response. 
 
 
- Finally, the Generate service replies with the generated
 response to the user. 
 
 
 
 

 
OIC helps customers automate the end-to-end RAG process. Customers or
 companies can benefit from using a low-code, no-code integration platform to implement
 RAG on their corporate data. Building RAG by using a low-code, no-code platform enables
 development and go-to-market within hours or days rather than months.

 
The architecture has the following components:

 
 
- Autonomous
 Database 

 Oracle Autonomous Database is a fully managed, preconfigured database
 environments that you can use for transaction
 processing and data warehousing workloads. You do
 not need to configure or manage any hardware, or
 install any software. Oracle Cloud
 Infrastructure handles creating the database, as well as
 backing up, patching, upgrading, and tuning the
 database.
 

 
 
- Autonomous Transaction
 Processing 
 Oracle Autonomous Transaction
 Processing is a self-driving, self-securing,
 self-repairing database service that is optimized
 for transaction processing workloads. You do not
 need to configure or manage any hardware, or
 install any software. Oracle Cloud
 Infrastructure handles creating the database, as well as
 backing up, patching, upgrading, and tuning the
 database. 
 

 
 
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
 

 
 
- Integration 
 Oracle Integration is a fully managed service that allows you to
 integrate your applications, automate processes,
 gain insight into your business processes, and
 create visual applications.
 

 
 
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

 
 
- Oracle Database 23ai 
Oracle Database 23ai is the next long-term support
 release of Oracle Database. It includes over 300 new features with a focus on
 artificial intelligence (AI) and developer productivity. Features such as AI
 Vector Search enable you to leverage a new generation of AI models to generate
 and store vectors of documents, images, sound, and so on; index them and quickly
 look for similarity while leveraging the existing analytical capabilities of
 Oracle Database. This combined with the already extensive set of Machine
 Learning algorithms enables you to quickly create sophisticated AI-enabled
 applications. Oracle Database 23ai also uses AI to optimize many of the key
 database functions to make more accurate estimates on timings and resource
 costings.

 
 
 

 

 
 
Explore More

 

 
Learn more about implementing RAG by using Oracle Integration.

 
Review these additional resources: 

 
 
- Best practices framework
 for Oracle Cloud Infrastructure 
 
- Oracle Cloud
 Infrastructure Documentation 
 
- Oracle
 Integration 
 
- OCI
 Functions 
 
- About Oracle
 Database 23ai 
 
- Deploy generative AI models to
 OCI 
 
 
Review these OCI Generative AI resources: 
 
 
- Generative AI Documentation Home 
 
 
 
- Generative AI capabilities 
 
 
 
- Press release: Oracle Introduces Integrated Vector Database to Augment
 Generative AI and Dramatically Increase Developer
 Productivity 
 
 
 
- Using
 the Large Language Models (LLMs) in Generative AI (Using the
 Playground)
 
 
- About
 the Generation Models in Generative AI 
 
- About the Summarization Models in Generative AI 
 
- About the
 Embedding Models in Generative AI 
 
 

 

 

 
 
Acknowledgments

 

 
 Author: Pavan Rajalbandi
 

 

 

 

 

 

 
 Title and Copyright Information 

 

 
Implement retrieval augmented generation by using Oracle Integration

 
G14623-01

 
September 2024

 
 Copyright © 2024, 

Oracle and/or its affiliates.
