# Stream fraud detection with NVIDIA Morpheus on Oracle Compute Cloud@Customer

- Source: https://docs.oracle.com/en/solutions/fraud-detection-nvidia-morpheus-compute-cloud/index.html
- Date: 2025-08
- Type: built-deployed
- Services: compute
- Tags: ai-ml, security

## Summary (catalog)

Real-time fraud detection with NVIDIA Morpheus on Compute Cloud@Customer. GPU-accelerated ML pipeline for transaction monitoring. On-premises deployment for data sovereignty requirements.

## Architecture (fetched from source)

Learn About Streaming Fraud Detection 
 
 
 
 
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
 
- 
 
 
 
 

 Previous 
 Next 
 JavaScript must be enabled to correctly display this content
 
 

 

 
 
 
Learn About Streaming Fraud
 Detection

 

 

 
 
 Oracle Compute Cloud@Customer , a key component of the Oracle Roving Edge Infrastructure portfolio, provides organizations a scalable solution to process sensitive data
 securely, with low latency—close to its source. 
 

 
 
In this solution playbook, you learn how to use the NVIDIA Morpheus cybersecurity framework to deploy real-time, AI-driven fraud detection using a
 GPU-accelerated Morpheus pipeline, and publish the results using Compute Cloud@Customer . The solution enables instant fraud detection without waiting for batch jobs and
 keeps your data secure by locally processing it at the edge.
 

 
 

 
 
Before You Begin

 

 

 Ensure you perform the deployment on a host machine with the
 following environment settings: 
 
 

 
 
- Operating System : Ubuntu 24.04 LTS
 
 
- Platform : NVIDIA AI Enterprise on a single-node Oracle Compute Cloud@Customer instance equipped with an NVIDIA L40S GPU.
 
 
 
Before you begin, ensure the following tools are installed on the host machine:

 
 
- Docker and Docker Compose ( docker compose V2 )
 
 
- Git and Git LFS ( git-lfs )
 
 
- Python 3 and Pip 
 
 

 

 
 
Workflow

 

 
The workflow leverages the NVIDIA Morpheus cybersecurity framework to perform GPU-accelerated inference on a stream of financial
 transaction data. 
 

 
The following diagram shows a workflow through three swimlanes; Host
 environment, Apache Kafka , and the Morpheus pipeline:
 

 
 Description of the illustration ai-driven-fraud-detection-workflow-arch.png 

The pipeline ingests live transaction data through Apache Kafka , performs graph-based contextual analysis using a pre-trained Graph Sample and Aggregate ( GraphSAGE ) model, and executes final fraud classification using XGBoost . All stages are accelerated using NVIDIA 
 RAPIDS libraries (cuDF, cuML), making the entire workflow GPU-optimized for high throughput.
 The following is how the process flows:
 

 
 
- Transaction data (.csv) is produced by a Python producer.
 
 
- Data goes into Kafka topic INPUT stream.
 
 
- Data is processed through the Morpheus pipeline in steps: reading from Kafka source, deserializing, constructing a graph, interfacing with Graph Neural Network (GNN) interface ( GraphSAGE ), classifying with
 XGBoost , serializing results, and writing to Kafka sink.
 
 
- Results are sent to Kafka topic OUTPUT stream.
 
 
- A Python consumer receives output and provides live fraud prediction.
 
 
 
 Model Provenance 

 
The inference pipeline at the core of this architecture uses two pre-trained
 machine learning models: a GraphSAGE GNN and an XGBoost classifier. These models were generated using a separate training pipeline, which is
 included in the Morpheus repository for reference.
 

 
 
- Training Script Location: 
 examples/gnn_fraud_detection_pipeline/training.py .
 
 
- Process: The script processes a labeled historical dataset to
 train the GNN on graph-based features and the XGBoost model on
 the resulting embeddings.
 
 
 
In this solution, you don't have to run the training script becausethe
 pre-trained models are already provided. Focus on deploying and running the real-time
 inference pipeline.

 
This architecture supports the following components:

 
 
- Oracle Compute Cloud@Customer 
 Oracle Compute Cloud@Customer is fully-managed, rack-scale infrastructure
 that lets you use OCI Compute anywhere. Gain the benefits of cloud automation
 and economics in your data center by running OCI Compute and GPU shapes with storage and networking
 services on Compute Cloud@Customer . You can run applications and harness the power
 of GenAI on cloud infrastructure in your data
 center while helping address data residency,
 security, and low-latency connections to local
 resources and real-time operations.
 

 
 
- RAPIDS 
 cuDF/cuML 
 RAPIDS cuDF/cuML are a suite of GPU-accelerated libraries for high-performance data
 manipulation and machine learning utilities within the Morpheus
 pipeline.
 

 
 
- Docker + Conda 
 Docker + Conda provide a layered approach to dependency management, using Docker for OS-level isolation and Conda for managing the complex Python environment inside the container.
 

 
 
 

 

 
 
Considerations for
 Production

 

 
When implementing this solution in a production environment, consider the
 scalability and resilience that Kubernetes can provide. You can migrate this solution to OCI Kubernetes Engine ( OKE ) by:
 

 
 
- Containerizing the producer and consumer helper scripts. 
 
- Deploying Kafka using a production-grade Kubernetes operator.
 
 
- Deploying the Morpheus pipeline as a Kubernetes job or deployment.
 
 
 

 

 
 
About Required Services and
 Roles

 

 
This solution requires the following services and roles:

 
 
- Oracle Compute Cloud@Customer 
 
- NVIDIA AI Enterprise 6.0
 
 
- 
 
Ubuntu Linux (or a compatible Linux distribution)

 
 
- Docker 
 
- NVIDIA Morpheus 25.02
 
 
 
These are the roles needed for each service.

 

 
 
 
 Service Name: Role 
 Required to... 
 
 
 
 
 Oracle Compute Cloud@Customer : administrator 
 Configure and deploy the NVIDIA AI Enterprise virtual machine instance, manage network resources, and ensure access
 to the NVIDIA L40S GPU.
 
 
 
 Ubuntu Linux: root or user with sudo 
 privileges
 
 Install prerequisite software ( Docker , Git), manage system services, and execute Docker commands.
 
 
 
 NVIDIA AI Enterprise : Account User
 
 Pull the required NVIDIA Morpheus container image from the NVIDIA GPU Cloud ( NGC ) catalog.
 
 
 
 
 

 
See Oracle Products, Solutions, and Services to get what you need.
 

 

 

 

 

 

 
 Title and Copyright Information 

 

 
Fraud detection with NVIDIA Morpheus on Compute Cloud@Customer and Private Cloud Appliance

 
G38649-02

 
August 2025

 
 Copyright © 2025, 

Oracle and/or its affiliates.
