# Run a quantized GGUF large language model on an Ampere A2 cluster

- Source: https://docs.oracle.com/en/solutions/run-quantized-gguf-llm-ampere-cluster/index.html
- Date: 2025-06
- Type: reference-architecture
- Services: compute
- Tags: ai-ml

## Summary (catalog)

CPU-based LLM inference on Ampere A2 shapes using quantized GGUF models. Cost-efficient for moderate throughput requirements. llama.cpp for model serving without GPU dependency.

## Architecture (fetched from source)

Architecture

 

 
This Arm-based architecture offers an LLM implementation at exceptional
 value, running at a fraction of the traditional AI infrastructure cost. Use this
 architecture for a budget-friendly approach to getting started with AI.

 
An OCI public load balancer sits at the front, distributing incoming traffic to a
 pool of compute instances. There is an instance pool of Ampere A2 nodes.
 Each node is a 2-core, Arm-based compute instance running Ubuntu. The nodes
 are managed in an OCI instance pool, making it easy to scale horizontally as
 traffic grows. An internet gateway enables public access to both the load
 balancer and the backend instances when needed.

 
Each Ampere A2 compute instance runs Ubuntu 22.04 (Arm), a quantized
 GPT-Generated Unified Format (GGUF) LLM (like TinyLlama or Phi-2) served
 locally using llama.cpp, a simple HTML/JS landing page served via NGINX, and
 a Python-based backend wired into llama-cpp-python that handles prompts from
 the UI and streams model output back to the page.

 
Each compute node in the pool is designed to be lightweight yet fully
 self-sufficient. Upon launch, it bootstraps itself using a cloud-init script
 that installs and runs everything needed to serve an LLM from scratch. The
 nodes are configured as follows:

 
 
- Installs Dependencies : Dependencies such as
 build-essential, cmake, git, NGINX, and python3-pip are installed
 automatically. llama-cpp-python is compiled from the source to
 ensure full ARM64 compatibility.
 
 
- Builds : Nodes pull the latest version of llama.cpp
 from GitHub, and builds it using OpenBLAS for optimized CPU
 inference, while keeping everything local - no external runtime
 dependency on GPUs, or inference APIs.
 
 
- Downloads the Model : A quantized GGUF model
 (TinyLlama or similar) is fetched directly from Hugging Face and
 placed in the models directory.
 
 
- Serves a Landing Page : A minimal HTML/JavaScript UI is served via
 NGINX on port 80. The UI lets users submit prompts and view LLM
 responses directly from their browser.
 
 
- Handles Inference via Python : A small Python backend
 uses llama-cpp-python to interact with the local model. It exposes a
 /generate endpoint which the landing page
 sends a POST request to when a user submits a question.
 
 
- Starts on Boot : Everything is wrapped in a
 systemd service, so inference automatically
 restarts on instance reboot or failure - no manual touch
 required.
 
 
 
The following diagram illustrates this reference architecture.

 
 Description of the illustration gen-ai-ampere-gguf-llm-arch.png 

 gen-ai-ampere-gguf-llm-arch.zip 

 
The architecture has the following components:

 
 
- Region 
An OCI
 region is a localized geographic area that
 contains one or more data centers, hosting
 availability domains. Regions are independent of
 other regions, and vast distances can separate
 them (across countries or even
 continents).

 
 
- Availability domains 
Availability
 domains are standalone, independent data centers
 within a region. The physical resources in each
 availability domain are isolated from the
 resources in the other availability domains, which
 provides fault tolerance. Availability domains
 don’t share infrastructure such as power or
 cooling, or the internal availability domain
 network. So, a failure at one availability domain
 shouldn't affect the other availability domains in
 the region.

 
 
- Fault domains 
A
 fault domain is a grouping of hardware and
 infrastructure within an availability domain. Each
 availability domain has three fault domains with
 independent power and hardware. When you
 distribute resources across multiple fault
 domains, your applications can tolerate physical
 server failure, system maintenance, and power
 failures inside a fault domain.

 
 
- Virtual cloud network (VCN) and subnets 
A
 VCN is a customizable, software-defined network
 that you set up in an OCI region. Like traditional
 data center networks, VCNs give you control over
 your network environment. A VCN can have multiple
 non-overlapping classless inter-domain routing
 (CIDR) blocks that you can change after you create
 the VCN. You can segment a VCN into subnets, which
 can be scoped to a region or to an availability
 domain. Each subnet consists of a contiguous range
 of addresses that don't overlap with the other
 subnets in the VCN. You can change the size of a
 subnet after creation. A subnet can be public or
 private. 

 
 
- Load balancer 
 Oracle Cloud
 Infrastructure Load Balancing provides automated traffic distribution from a
 single entry point to multiple servers.
 

 
 
- Internet
 gateway 
An
 internet gateway allows traffic between the public
 subnets in a VCN and the public internet.

 
 
- Instance
 pool 
An
 instance pool is a group of instances within a
 region that are created from the same instance
 configuration and managed as a group.

 
 
 

 

 
 
Considerations

 

 
Before implementing this architecture, consider the following. 

 
 
- Ampere A2 compute instance costs 
Each node runs Ampere A2 with
 2 OCPUs and 16GB of RAM. The pricing for this OCPU
 is currently $0.01 per OCPU per hour. The monthly
 cost works out to $14.40 with 1 node always
 on.

 
 
- Load balancer costs 
A public load balancer (small shape) is
 priced currently at approximately $0.029 per hour. The monthly cost works out to
 approximately $21. You can further reduce costs by setting up a custom load
 balancer on another Ampere instance.

 
 
- Storage costs 
Each node stores the OS, llama.cpp, and the model
 which is approximately 5-6GB. The default boot
 volume is approximately 50GB. Note the first 200GB
 per month are free.

 
 
 

 

 
 
Explore More

 

 
Learn more about running a GGUF LLM on an Ampere A2 cluster in Oracle Cloud
 Infrastructure .
 

 
Review these additional resources: 

 
 
- Oracle Cloud
 Infrastructure Documentation 
 
- Well-architected framework
 for Oracle Cloud Infrastructure 
 
- Oracle Cloud Cost Estimator 
 
 

 

 
 
Acknowledgments

 

 
 
- Author : Badr Tharwat 
 
 

 

 

 

 

 
 Title and Copyright Information 

 

 
Run a quantized GGUF large language model on an Ampere A2 cluster

 
G35514-01

 
June 2025

 
 Copyright © 2025, 

Oracle and/or its affiliates.
