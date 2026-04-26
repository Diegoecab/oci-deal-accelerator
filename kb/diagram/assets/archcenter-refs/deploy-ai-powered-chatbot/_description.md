# Deploy an AI-powered chatbot

- Source: https://docs.oracle.com/en/solutions/deploy-ai-powered-chatbot/index.html
- Date: 2025-08
- Type: reference-architecture
- Services: genai, functions, adb-s
- Tags: ai-ml, application, autonomous

## Summary (catalog)

AI chatbot with OCI GenAI and Functions. RAG for knowledge-grounded responses, ADB-S for conversation history and vector search. Serverless architecture with OCI Functions for cost efficiency.

## Architecture (fetched from source)

Architecture

 

 

 This reference architecture outlines how to configure and deploy an
 AI-powered chatbot on your own OCI tenancy. This chatbot can generate or summarize
 content, answer questions, translate languages, and more. 
 
 

 
This AI-powered chatbot leverages Oracle Digital Assistant and OCI Generative AI large language models (LLMs). Oracle Visual Builder is used to embed the chatbot in a web application. Users can interact with OCI Generative AI through natural language questions and receive responses from the LLM by using the
 chatbot interface.
 

 
The following diagram illustrates this reference architecture.

 
 Description of the illustration deploy-ai-chatbot-arch.png 

 deploy-ai-chatbot-arch.zip 

 
The flow for users and developers using this architecture resembles:

 
 
- Developers and chatbot users authenticate with OCI Identity and Access Management .
 
 
- Users access the chatbot using the Oracle Visual Builder app where it is embedded. Developers can configure the app from the Oracle Visual Builder service home page.
 
 
- Developers configure the chatbot using the Oracle Digital Assistant service console.
 
 
- Developers access OCI Generative AI LLMs using APIs. 
 
 
 
The architecture has the following components:

 
 
- Region 
An Oracle Cloud
 Infrastructure region is a localized geographic area that contains one or more data centers, hosting availability domains. Regions are independent of other regions, and vast distances can separate them (across countries or even continents).
 

 
 
- Identity and Access Management 
 Oracle Cloud Infrastructure Identity
 and Access Management (IAM) provides user access control for Oracle Cloud
 Infrastructure (OCI) and Oracle Cloud Applications. The IAM API and the user interface enable you to manage identity domains and the resources within them. Each OCI IAM identity domain represents a standalone identity and access management solution or a different user population.
 

 
 
- Oracle Visual Builder 
 Oracle Visual Builder is an intuitive development experience on top of a development and hosting
 platform that empowers you to create engaging responsive applications. Focusing
 on ease of use and a visual development approach, it provides an easy way for
 you to create applications that are hosted in Oracle’s secure and scalable cloud
 platform.
 

 
 
- Digital Assistant 
 Oracle Digital Assistant is a platform that allows you to create and deploy digital assistants for your users. With Oracle Digital Assistant , you can create AI-driven interfaces (or chatbots) for business applications through text, chat, and voice interfaces. Each digital assistant has a collection of one or more specialized skills to help users complete a variety of tasks in natural language conversations. For example, an individual digital assistant might have skills that focus on specific types of tasks such as tracking inventory, submitting time cards, and creating expense reports.
 

 
 
- Generative AI 
 Oracle Cloud Infrastructure Generative AI is a fully-managed OCI service that provides a set of state-of-the-art, customizable, large language models (LLMs) that cover a wide range of use cases for text generation, summarization, semantic search, and more. Use the playground to try out the ready-to-use pretrained models, or create and host your own fine-tuned custom models based on your own data on dedicated AI clusters.
 

 
 
 

 

 
 
Considerations

 

 
When deploying this AI-powered chatbot, consider the following. 

 
 
- Region Availability 
Oracle hosts its OCI services in regions
 and availability domains. A region is a localized geographic area, and an
 availability domain is one or more data centers in that region. AI services are
 not always available in all regions. To learn more, see Regions with
 Generative AI in the Explore More section.
 

 
 
- Document Processing 
The document processing feature used in this
 architecture is intended for smaller documents. For solutions that analyze
 larger documents, see the other LiveLabs in the Explore More 
 section.
 

 
 
 

 

 
 
 Deploy 

 

 
To deploy this architecture, follow the instructions in this Live
 Lab:

 

 
 
 Deploy ATOM (AI Powered) Chatbot 

 
 

 

 

 
 
Explore More

 

 
Learn more about deploying an AI-powered chatbot.

 
Review these additional resources: 

 
 
- Deploy an ODA Chatbot powered by Generative
 AI Agents (LiveLab)
 
 
- Deploy a Chatbot powered by
 Generative AI Agents using 23ai Vector DB 
 (LiveLab)
 
 
- OCI Generative
 AI 
 
- Overview of Digital Assistants and Skills 
 
- Regions with Generative AI 
 
- Well-architected framework
 for Oracle Cloud Infrastructure 
 
 

 

 
 
Acknowledgments

 

 
 
- Authors : Luke Farley, Abhinav Jain 
 
- Contributor : Kaushik Kundu 
 
 

 

 

 

 

 
 Title and Copyright Information 

 

 
Deploy an AI-powered chatbot

 
G27457-02

 
August 2025

 
 Copyright © 2025, 

Oracle and/or its affiliates.
