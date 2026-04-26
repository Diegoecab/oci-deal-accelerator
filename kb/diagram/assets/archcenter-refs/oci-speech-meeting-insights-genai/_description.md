# Get actionable meeting insights with Oracle Autonomous AI Database and GenAI

- Source: https://docs.oracle.com/en/solutions/oci-speech-meeting-insights-genai/index.html
- Date: 2025-12
- Type: reference-architecture
- Services: genai, adb-s, ai-services
- Tags: ai-ml, autonomous

## Summary (catalog)

Meeting transcription and insights using OCI Speech + GenAI. Audio processing with OCI Speech service, summarization and action item extraction with GenAI, storage in ADB-S for analytics.

## Architecture (fetched from source)

Architecture

 

 
 This architecture uses OCI Speech , an embedding model, Oracle AI Database 26ai vector search, OCI Generative AI , and Oracle APEX to transcribe meeting audio, enrich it with semantic search, and enable you to
 summarize meetings from recordings. 
 

 
The following architecture shows this deployment topology:

 
 Description of the illustration oci-speech-adb-ai-arch.png 

 oci-speech-adb-ai-arch-oracle.zip 

 
The solution ingests meeting content, creates transcripts, stores and analyzes text, and
 surfaces insights using managed services on Oracle Cloud
 Infrastructure (OCI).
 

 
 
- Oracle APEX Service connects to Oracle Autonomous AI Database .
 
 
- Oracle Autonomous AI Database reads from and writes to OCI Object Storage .
 
 
- OCI Speech reads audio from and writes transcripts to OCI Object Storage .
 
 
- Oracle Autonomous AI Database calls OCI Generative AI and OCI
 Language for text analytics.
 
 
- OCI Identity and Access Management authorizes all interactions.
 
 
- Oracle Services Network exposes listed services to workloads. 
 
 
This architecture uses the following components:

 
 
- OCI
 Language 
 Oracle Cloud Infrastructure Language is a fully managed, serverless AI service for
 analyzing unstructured text using pretrained and
 custom models. It supports sentiment analysis,
 entity extraction, key phrase extraction,
 personally identifiable information (PII)
 detection, language detection, and text
 classification, with options for custom
 classifiers and custom entities. Access using REST
 APIs and SDKs with sophisticated text analysis at
 scale. Customer data is encrypted in transit and
 at rest, and tenant isolation is enforced.
 Pretrained models are regularly improved to
 enhance quality without customer retraining
 effort.
 

 
 
- OCI Speech 
 Oracle Cloud Infrastructure Speech harnesses the power of spoken language,
 enabling you to easily convert media files
 containing human speech into highly accurate text
 transcriptions stored in the JSON 
 format. You can access using the Console, REST
 API, CLI, and SDK.
 

 
 
- OCI Object Storage 
 OCI Object Storage provides access to large amounts of structured and unstructured data of any content type, including database backups, analytic data, and rich content such as images and videos. You can safely and securely store data directly from applications or from within the cloud platform. You can scale storage without experiencing any degradation in performance or service reliability. 
 

 
Use standard storage for "hot" storage that you need to access quickly, immediately, and frequently. Use archive storage for "cold" storage that you retain for long periods of time and seldom or rarely access.

 
 
- Oracle Autonomous AI Database 
 Oracle Autonomous AI Database provides an easy-to-use, fully autonomous
 (self-governing) database that scales elastically
 and delivers fast query performance. As a service,
 it doesn't require database administration. You
 don't need to configure or manage any hardware, or
 install any software. It automatically handles
 provisioning, backing up, patching and upgrading,
 and growing or shrinking the database and is an
 elastic service. Develop scalable AI-powered apps
 with any data using built-in AI capabilities. Use
 your choice of large language model (LLM) and
 deploy in the cloud or your data center.
 

 
 
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
 

 
 
- OCI Generative AI 
 Oracle Cloud Infrastructure Generative AI is a fully-managed OCI service that provides a set of state-of-the-art, customizable, large language models (LLMs) that cover a wide range of use cases for text generation, summarization, semantic search, and more. Use the playground to try out the ready-to-use pretrained models, or create and host your own fine-tuned custom models based on your own data on dedicated AI clusters.
 

 
 
- Oracle APEX Application
 Development 
 Oracle APEX Application
 Development is a low-code development platform that enables you to build scalable, feature-rich, secure, enterprise apps that can be deployed anywhere that Oracle AI Database is installed. You don't need to be an expert in a vast array of technologies to deliver sophisticated solutions. APEX Service includes built-in features such as user interface themes, navigational controls, form handlers, and flexible reports that accelerate the application development process.
 

 
 
- OCI Identity and Access Management 
 Oracle Cloud Infrastructure Identity
 and Access Management (IAM) provides user access control for OCI and Oracle Cloud Applications. The IAM API and the user interface enable you to manage identity domains and the resources within them. Each OCI IAM identity domain represents a standalone identity and access management solution or a different user population.
 

 
 
 

 

 
 
About Required Services and Roles

 

 
This solution requires the following services:

 
 
- Oracle Cloud Infrastructure Speech 
 
- Oracle Cloud Infrastructure Generative AI 
 
- Oracle Autonomous Database with Oracle AI
 Database 26ai
 
 
- Oracle APEX Application
 Development 
 
 
These are the roles needed for each service.

 

 
 
 
 Service Name: Role 
 Required to... 
 
 
 
 
 Oracle Cloud Infrastructure Speech : manage ai-service-speech-family 
 Create and manage transcription jobs. 
 
 
 Oracle Cloud Infrastructure Generative AI : manage generative-ai-family 
 Manage AI models, text generation, and
 summarization. 
 
 
 APEX Service : administrator 
 Manage APEX workspace permissions, development team, and
 developer permissions. 
 
 
 APEX Service : developer 
 Develop the APEX application. 
 
 
 
 

 
See Oracle Products, Solutions, and Services to
 get what you need.
 

 

 

 

 

 

 
 Title and Copyright Information 

 

 
Get actionable meeting insights with Oracle Autonomous AI Database and GenAI

 
G24622-01

 
December 2025

 
 Copyright © 2025, 

Oracle and/or its affiliates.
