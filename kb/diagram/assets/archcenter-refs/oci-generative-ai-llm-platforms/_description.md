# Enable secure and scalable self-service platforms for generative AI and LLMs within OCI

- Source: https://docs.oracle.com/en/solutions/oci-generative-ai-llm-platforms/index.html
- Date: 2025-06
- Type: reference-architecture
- Services: genai, oke, compute, api-gateway, data-science
- Tags: ai-ml, security

## Summary (catalog)

Enterprise GenAI platform with AI CoE governance. NVIDIA MIG for fractional GPU allocation, OCI DevOps for CI/CD, Oracle Database 23ai for vector storage. IAM-based environment segmentation per team.

## Architecture (fetched from source)

Architecture

 

 
This architecture illustrates how Oracle Cloud
 Infrastructure (OCI) supports end-to-end generative AI workflows across development, integration, and
 user interaction.
 

 
Flow A: Integration

 
 
- Customer applications 
 
- Oracle Integration 
 
- OCI Object Storage (buckets)
 
 
- OCI Events detection
 
 
- OCI Streaming and OCI Connector Hub 
 
- OCI Functions (logic execution)
 
 
- Oracle Process Cloud
 Service (inference by GPUs)
 
 
- Data layer ( Oracle AI Database 23ai and buckets)
 
 
 
Flow B: User interaction

 
 
- End-user interfaces (Apex) 
 
- Applications ( OCI GenAI Agents , OCI Speech , Oracle Digital Assistant )
 
 
- Oracle Process Cloud
 Service (inference by GPUs)
 
 
- Data layer ( Oracle AI Database 23ai and buckets)
 
 
 
Flow C: Development and sandbox

 
 
- External model sources 
 
- Code security validation 
 
- Development and testing 
 
- Automation pipeline to production 
 
 
The following diagram illustrates this reference architecture.

 
 Description of the illustration ai-llm-workflow-architecture.png 

 ai-llm-workflow-architecture-oracle.zip 

 
 Architecture overview by functional domains 

 
 
- Development and training (self-service workspace)
 
The
 architecture is structured under a centralized compartment for LLM
 operations:

 
 
- Data
 Science provides an integrated workspace for model development, Jupyter
 notebooks, and pre-built ML frameworks. Includes quick action tools for
 model deployment and job execution.
 
 
- Model deployment hosts virtual machines (VMs) for model testing
 and deployment. Users can validate models here before moving them into
 production. 
 
- Playground is a GPU-accelerated environment (Flex VMs, A10,
 A100, LS40) offering isolated and high-performance compute resources for
 custom and third-party models (for example, Hugging Face). It serves as the
 experimentation zone for Bring Your Own LLM (BYOLLM) workflows. 
 
 
 
- Application and function layer
 
 
- OCI Speech and language APIs offer ready-to-consume services for transcription, NLU,
 and entity extraction.
 
 
- OCI Functions is used for real-time transcription, NLP, and serverless execution of AI
 pipelines.
 
 
- APEX front-end and monitoring tools provide interfaces for user
 interaction, analytics, and governance. 
 
- OCI GenAI Agents and Digital Assistant enable conversational experiences using enterprise data and integrated
 LLMs. 
 
 
 
 
- Processing (production layer)
 
 
- OCI Kubernetes Engine (OKE) supports containerized deployment of production models and
 inference services.
 
 
- OCI Generative AI provides API-based access to Oracle-hosted or custom, fine-tuned LLMs,
 supporting secure and scalable enterprise use cases.
 
 
 
 
- GPU infrastructure (H100 and RDMA support)
 
 
- Bare metal GPU instances (H100 with RDMA) enable multi-node,
 distributed training and inference with high-throughput, low-latency
 communication, ideal for massive LLM workloads. 
 
- Optimized for Kubernetes and NVIDIA Multi-Instance GPU (MIG)
 technology, this setup enables GPU orchestration and dynamic resource
 sharing, allowing fractional GPU allocation and multi-user scheduling across
 teams. 
 
 
 
- Data and knowledge layer
 
 
- Oracle AI Database 23ai, enhanced with support for vector and semantic search, acts as the
 retrieval layer for Retrieval-Augmented Generation (RAG) workflows.
 
 
- OCI Object Storage buckets store unstructured data, embeddings, documents, and model
 artifacts.
 
 
 
 
- MLOps (production model pipeline)
 
 
- The architecture includes a CI/CD pipeline for promoting models
 from the playground environment to production. Currently represented by OCI DevOps is OCI's native, fully-managed, continuous integration and continuous
 delivery (CI/CD) service that enables organizations to automate the
 deployment of machine learning models from experimentation to
 production.
 
 
- Integrated build pipelines with Git. 
 
- Automated deployment to VMs or containers. 
 
- Native integration with OCI Artifacts
 Registry , OCI Functions , and OCI API Gateway . 
 
 
 
 
- Integration and security layer
 
 
- OCI Object Storage buckets act as the central storage for models, training data, inference
 outputs, and embeddings.
 
 
- OCI Events , OCI Streaming , and OCI Connector Hub enable event-driven orchestration and service integration across the
 environment.
 
 
- Oracle Identity Cloud
 Service , IAM policies, OCI Logging , and security lists provide robust governance, authentication, access
 control, and compliance capabilities across all OCI services.
 
 
- Oracle Integration is a pre-built middleware platform that enables secure and seamless
 integration between on-premises systems and cloud services, supporting
 real-time data synchronization, API orchestration, and process automation
 across heterogeneous applications.
 
 
 
 
 
The architecture has the following components:

 
 
- Availability domains 
Availability domains are standalone, independent data centers within a region. The physical resources in each availability domain are isolated from the resources in the other availability domains, which provides fault tolerance. Availability domains don’t share infrastructure such as power or cooling, or the internal availability domain network. So, a failure at one availability domain shouldn't affect the other availability domains in the region.

 
 
- Bare metal 
Oracle’s bare metal servers provide isolation, visibility, and control by using dedicated compute instances. The servers support applications that require high core counts, large amounts of memory, and high bandwidth. They can scale up to 192 cores, 2.3 TB of RAM, and up to 1 PB of block storage. Customers can build cloud environments on Oracle’s bare metal servers with significant performance improvements over other public clouds and on-premises data centers.

 
 
- Compartment 
Compartments
 are cross-regional logical partitions within an
 OCI tenancy. Use compartments to organize, control
 access, and set usage quotas for your Oracle Cloud resources. In a given compartment, you define
 policies that control access and set privileges
 for resources.
 

 
 
- OCI Connector Hub 
 Oracle Cloud Infrastructure Connector Hub is a message bus platform that orchestrates data movement between services on OCI. You can use connectors to move data from a source service to a target service. Connectors also enable you to optionally specify a task (such as a function) to perform on the data before it is delivered to the target service.
 

 
You can use OCI Connector Hub to quickly build a logging aggregation framework for security information and event management (SIEM) systems. 
 

 
 
- Dynamic routing gateway
 (DRG) 
The DRG is a
 virtual router that provides a path for private
 network traffic between VCNs in the same region,
 between a VCN and a network outside the region,
 such as a VCN in another OCI region, an
 on-premises network, or a network in another cloud
 provider.

 
 
- OCI FastConnect 
 Oracle Cloud
 Infrastructure FastConnect creates a dedicated, private connection between your data center and OCI. FastConnect provides higher-bandwidth options and a more reliable networking experience when compared with internet-based connections.
 

 
 
- High-performance
 computing 
High-performance
 computing is designed for workloads that require
 cluster networking and high-speed processor cores
 for massively parallel workloads.

 
 
- Internet
 gateway 
An
 internet gateway allows traffic between the public
 subnets in a VCN and the public internet.

 
 
- On-premises network 
This
 is a local network used by your
 organization.

 
 
- Region 
An OCI region
 is a localized geographic area that contains one
 or more data centers, hosting availability
 domains. Regions are independent of other regions,
 and vast distances can separate them (across
 countries or even continents).

 
 
- Route table 
Virtual
 route tables
