# Deploy a multi-agent AI fraud detection system on OCI

- Source: https://docs.oracle.com/en/solutions/ai-fraud-detection/index.html
- Date: 2025-06
- Type: reference-architecture
- Services: genai, streaming, adb-s
- Tags: ai-ml, autonomous

## Summary (catalog)

Multi-agent AI system for real-time fraud detection. Streaming ingestion of transaction data, ML models for anomaly detection, GenAI agents for investigation and decision support.

## Architecture (fetched from source)

Architecture

 

 
This architecture shows a multi-agent AI fraud detection system on Oracle Cloud
 Infrastructure (OCI).
 

 
This design uses multiple AI agents to provide key insights, gather evidence,
 and produce a comprehensive fraud analysis.

 
At the core is a model context protocol (MCP) server that orchestrates agent
 interactions. Specialized agents handle distinct tasks. For example, a data retrieval
 agent queries enterprise data sources and a fraud analyzer agent evaluates and explains
 anomalies. The flow begins when an event, such as a suspicious transaction alert or an
 investigator’s query, triggers the orchestrator. The orchestrator then delegates
 subtasks to the agents and consolidates their results by using a fan-in and fan-out
 design pattern. Each agent uses OCI-native services to perform tasks (database queries,
 LLM inference, and so on), and the orchestrator translates between agent and Oracle
 system contexts, ensuring that each agent gets the information it needs in the format it
 expects. 

 
The following diagram shows process flow overview:

 
 Description of the illustration ai-fraud-detection-flow.png 

 ai-fraud-detection-flow-oracle.zip 

 
 
- MCP orchestrator server 
The model context protocol
 (MCP) server is the coordinating hub that orchestrates agent actions and
 maintains the overall context or state of an investigation. It uses MCP to
 standardize how agents invoke tools and exchange data. Acting as a “central
 brain,” it receives the initial request (fraud alert or analysis query) and
 calls the appropriate agents in sequence. It also translates high-level agent
 intents into low-level operations on Oracle systems, such as converting an
 agent’s request for customer information into an SQL query, and converting SQL
 results into a natural language response. This approach decouples agents from
 direct system calls by using the orchestrator as a bridge between the agent
 logic and enterprise data, enabling flexible updates and centralized control. In
 the first phase of this architecture, the server is a lightweight server derived
 from Google’s Gen AI Toolbox running on Oracle Cloud Infrastructure
 Compute or OCI Kubernetes Engine .
 

 
 
- Data retrieval agent 
The data retrieval agent is
 a specialized agent responsible for fetching relevant data from enterprise
 sources. For example, upon receiving a customer ID or transaction ID from the
 orchestrator, it queries the Oracle Autonomous Database or other OCI data stores for information such as recent transactions, account
 profiles, claims history, and so on. You can implement this agent by using OCI Functions (serverless) to call tools hosted on an MCP server for Autonomous Database . The agent contains all data-access logic. The orchestrator server may use a
 predefined tool for this agent, such as a YAML-configured
 LookupTransaction or GetCustomerProfile 
 tool that knows how to run the proper SQL on the Autonomous Database . Similar to how Google Gen AI Toolbox uses YAML-defined tools to let agents
 perform database operations, this design defines database queries as
 configuration-driven tools. In the first phase, the data agent simply executes
 these queries without AI decision-making involvement and returns the results to
 the orchestrator.
 

 
 
- Fraud analyzer agent 
The fraud analyzer agent is
 the cornerstone agent that assesses the data for signs of fraud and generates
 insights. This agent ingests the context, such as the transaction details,
 customer info, or historical patterns provided by the orchestrator and applies
 AI/ML logic to determine if the scenario is likely fraudulent. In phase 1, this
 could be a rule-based engine or an OCI Anomaly Detection model to provide a
 quick, deterministic response. For example, it might flag anomalies such as a
 transaction far outside normal range or multiple claims in a short time span.
 The agent then produces a fraud score or classification and possibly an
 explanation. 

 
In phase 2, the fraud analyzer agent is
 augmented with LLM capabilities by using OCI Generative AI or Oracle pretrained models to generate human-readable investigative
 narratives. In this way, generative AI automatically creates a concise report of
 the findings, summarizing why a transaction was flagged and referencing the data
 directly such as how a customer’s recent transactions show unusual high-value
 purchases overseas, which deviates from their normal pattern by 5σ (5 sigma),
 indicating high fraud likelihood. Oracle’s own Financial Services division has
 highlighted the value of such generative narratives in accelerating
 investigations. In phase 2, the fraud analyzer agent can use an OCI LLM to both
 analyze the data and explain the results. For example, it might use a prompt
 that incorporates the data and asks the model to analyze the fraud risk, or it
 could perform tool-assisted reasoning by first calling a calculation tool, and
 then having the LLM elaborate on the results.
 

 
 
- Additional agents (as needed) 
The architecture
 supports the ability to plug in other agents to enrich the analysis. For
 example, an external check agent could call third-party services, such as
 sanctions lists or credit bureaus, to gather more evidence on the entity
 involved. Another could be a notification and case management agent that, after
 fraud is confirmed, logs the case in a system or triggers an alert to a human
 investigator. The orchestrator’s ability to manage multiple agents and
 coordinate complex workflows allows new agents to be added without disturbing
 existing ones. This modularity makes the system extensible for demo showcases
 that can start with two agents and later attach more for other demo scenarios
 such as compliance checks, customer messaging, and so on.

 
 
 

 

 

 

 

 
 Title and Copyright Information 

 

 
Deploy a multi-agent AI fraud detection system on OCI

 
G34124-01

 
June 2025

 
 Copyright © 2025, 

Oracle and/or its affiliates.
