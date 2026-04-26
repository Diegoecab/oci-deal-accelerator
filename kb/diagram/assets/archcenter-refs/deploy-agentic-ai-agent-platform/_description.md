# Deploy agentic AI with Oracle Cloud Infrastructure AI Agent Platform

- Source: https://docs.oracle.com/en/solutions/deploy-agentic-ai-agent-platform/index.html
- Date: 2025-12
- Type: reference-architecture
- Services: genai, adb-s, functions
- Tags: ai-ml, autonomous

## Summary (catalog)

Enterprise AI chatbot integrating Visual Builder, Digital Assistant, and OCI AI Agent Platform. RAG from unstructured data, structured queries via ADB-S, custom business logic through serverless Functions.

## Architecture (fetched from source)

Architecture

 

 

 This is an enterprise-grade OCI architecture for building advanced
 generative AI chatbots that blend conversational AI, secure data access, RAG, and
 extensible business logic. 
 
 

 
Users interact with a web application built using Oracle Visual Builder . The application integrates with Oracle Digital Assistant , which manages conversational interactions and routes user queries to the appropriate backend services. The Digital Assistant connects to the OCI Generative AI Agent Platform, which intelligently orchestrates requests to different tools:
 

 
 
- The RAG Tool retrieves relevant information from OCI Object Storage for context-aware responses.
 
 
- The SQL Tool queries structured data in the Oracle Autonomous AI Database ( Oracle Autonomous Transaction
 Processing ) to answer specific data-driven questions.
 
 
- The Custom Tool invokes serverless functions for specialized tasks like
 document understanding or integrating external data (e.g., weather).
 
 
 
Together, these services leverage Oracle Cloud Infrastructure to deliver an intelligent,
 responsive, and extensible AI-driven experience that combines conversational AI,
 real-time data access, and custom functionality.

 
The following diagram illustrates this reference architecture.

 
 Description of the illustration agentic-ai-oci-ai-agent-arch.png 

 agentic-ai-oci-ai-agent-arch-oracle.zip 

 
The architecture has the following components:

 
 
- Region 
An OCI region
 is a localized geographic area that contains one
 or more data centers, hosting availability
 domains. Regions are independent of other regions,
 and vast distances can separate them (across
 countries or even continents).

 
 
- Oracle Services Network 
The Oracle Services Network (OSN) is a conceptual network on OCI that is reserved for Oracle services. These services have public IP addresses that you can reach over the internet. Hosts outside Oracle Cloud can access the OSN privately by using Oracle Cloud
 Infrastructure FastConnect or VPN Connect. Hosts in your VCNs can access the OSN privately through a service gateway.
 

 
 
- Oracle Visual Builder 
 Oracle Visual Builder is an intuitive development experience on top of a development and hosting
 platform that empowers you to create engaging responsive applications. Focusing
 on ease of use and a visual development approach, it provides an easy way for
 you to create applications that are hosted in Oracle’s secure and scalable cloud
 platform.
 

 
 
- Oracle Digital Assistant 
 Oracle Digital Assistant is a platform that allows you to create and deploy digital assistants for your users. With Oracle Digital Assistant , you can create AI-driven interfaces (or chatbots) for business applications through text, chat, and voice interfaces. Each digital assistant has a collection of one or more specialized skills to help users complete a variety of tasks in natural language conversations. For example, an individual digital assistant might have skills that focus on specific types of tasks such as tracking inventory, submitting time cards, and creating expense reports.
 

 
 
- OCI AI Agent Platform 
Oracle Cloud Infrastructure (OCI) AI
 Agent Platform provides a fully managed, cloud native solution that lets you
 build, deploy, and manage AI agents. By leveraging state-of-the-art large
 language models (LLMs), the AI agents you create can revolutionize the way you
 interact with customers, perform complex tasks autonomously, automate workflows,
 approach business problems. The service integrates across the Oracle stack,
 including databases and cloud infrastructure, enabling efficient data retrieval
 and API interactions. 

 
 
- OCI Object Storage 
 OCI Object Storage provides access to large amounts of structured and unstructured data of any content type, including database backups, analytic data, and rich content such as images and videos. You can safely and securely store data directly from applications or from within the cloud platform. You can scale storage without experiencing any degradation in performance or service reliability. 
 

 
 
- Oracle Autonomous Transaction
 Processing 
 Oracle Autonomous Transaction
 Processing is a self-driving, self-securing, self-repairing database service that is optimized for transaction processing workloads. You do not need to configure or manage any hardware, or install any software. OCI handles creating, backing up, patching, upgrading, and tuning the database.
 

 
 
- Oracle AI Database 26ai 
 Oracle AI Database 26ai with AI Vector Search lets you query data
 by meaning rather than keywords. Vector
 representations (embeddings) capture the semantics
 of text, images, audio, and more so you can find
 similar content efficiently. Built-in SQL distance
 functions allow similarity searches using vectors.
 You can combine semantic similarity and other
 search criteria to ground large language models
 (RAG) for more accurate and relevant
 answers.
 

 
 
- OCI Functions 
 Oracle Cloud Infrastructure
 Functions is a fully-managed, multitenant, highly scalable, on-demand, Functions-as-a-Service (FaaS) platform. It is powered by the Fn Project open source engine. OCI Functions enables you to deploy your code, and either call it directly or trigger it in response to events. OCI Functions uses Docker containers hosted in Oracle Cloud Infrastructure
 Registry .
 

 
 
 

 

 
 
 Deploy 

 

 

 To deploy this architecture, follow the instructions in this Live
 Lab: 
 
 

 
 Build Agentic AI Solution with Multi-Tool Capabilities powered by
 OCI AI Agent Framework 

 

 

 
 
Explore More

 

 
Learn more about deploying AI agents using Oracle Cloud
 Infrastructure .
 

 
Review these additional resources: 

 
 
- Deploy an ODA Chatbot powered by Generative AI
 Agents (LiveLab)
 
 
- Deploy a Chatbot powered by
 Generative AI Agents using 23ai Vector DB (LiveLab)
 
 
- OCI AI Agents 
 
- OCI AI Agents
 Documentation 
 
- Overview of Digital Assistants and
 Skills 
 
- Oracle Cloud
 Infrastructure Documentation 
 
- Well-architected framework
 for Oracle Cloud Infrastructure 
 
 

 

 
 
Acknowledgments

 

 
 
- Authors : Luke Farley, Abhinav Jain 
 
- Contributor : Kaushik Kundu 
 
 

 

 

 

 

 
 Title and Copyright Information 

 

 
Deploy agentic AI using Oracle Cloud Infrastructure AI Agent Platform

 
G39281-01

 
December 2025

 
 Copyright © 2025, 

Oracle and/or its affiliates.
