# Deploy LLM using AMD Instinct accelerators in OCI

- Source: https://docs.oracle.com/en/solutions/deploy-llm-amd-instinct-oci/index.html
- Date: 2025-07
- Type: reference-architecture
- Services: compute
- Tags: ai-ml, hpc

## Summary (catalog)

LLM inference on AMD Instinct MI300X GPUs in OCI. ROCm software stack for model serving. Cost-effective alternative to NVIDIA for specific model architectures.

## Architecture (fetched from source)

About Deploying Large Language Models in OCI 
 
 
 
 
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
 
 

 

 
 
 
About Deploying Large Language
 Models in OCI

 

 

 
Deploying a Large Language Model (LLM) efficiently
 and at scale is a challenging and resource intensive task. Oracle Cloud
 Infrastructure (OCI) offers AMD Instinct™ MI300X GPU in bare metal offering running LLama2 70B model . 
 
vLLM is a fast
 and easy-to-use library for LLM inference and serving. PagedAttention , which is central to vLLM, enhances the efficiency of
 Attention mechanism by managing it as virtual memory. It enhances the GPU memory
 utilization, enables processing of longer sequences, and supports working within the
 hardware resource constraints. In addition, vLLM enables continuous batching to improve
 throughput and reduce latency.
 
In this solution playbook, you learn how to
 deploy an LLM using AMD Instinct™ MI300X GPU s in OCI.
 

 

 
 
Solution Workflow

 

 

 
 

 Hugging Face is a collaborative platform and hub for machine learning
 that provides pre-trained AI models, development tools, and
 hosting infrastructure for AI applications, making advanced
 machine learning accessible to developers
 worldwide.
 

 
 
The following workflow diagram shows how model artifacts can be
 pulled from the Hugging Face GitHub open-source library and stored in OCI Object Storage .
 

 
 

 
 Description of the illustration deploy-llm-amd-instinct-oke.png 

Images built from the model can be stored in the OCI Registry for model image management, version control, and secured access management. Oracle Cloud Infrastructure Kubernetes Engine enhanced cluster in the OCI with AMD BM GPU instance can be launched using a CLI or
 from the console. Finally, a model inference endpoint can be served secured over the
 network or internet.
 

 
The following lists the third-party components:

 
 
- AMD Instinct™ GPUs 
 AMD Instinct™ MI300X GPU with AMD ROCm™ open software power OCI Compute Supercluster instances called BM.GPU.MI300X.8 .
 AMD Instinct MI300X GPUs and ROCm 
 software power the most critical OCI AI workloads.
 

 
The inference capabilities of AMD Instinct
 MI300X GPUs add to OCI's extensive selection of
 high-performance bare metal instances to remove the overhead
 of virtualized compute commonly used for AI
 infrastructure.
 

 
 
- Inference Endpoints 
Inference Endpoints
 offers a secure production solution to easily deploy any
 Transformers, Sentence-Transformers and Diffusers models
 from the Hub on dedicated and autoscaling infrastructure
 managed by Inference Endpoints.

 
 
 
The following lists the OCI components:

 
 
- OCI region 
An OCI region
 is a localized geographic area that contains one
 or more data centers, hosting availability
 domains. Regions are independent of other regions,
 and vast distances can separate them (across
 countries or even continents).

 
 
- OCI virtual cloud
 network and subnet 
A virtual cloud
 network (VCN) is a customizable, software-defined
 network that you set up in an OCI region. Like
 traditional data center networks, VCNs give you
 control over your network environment. A VCN can
 have multiple non-overlapping classless
 inter-domain routing (CIDR) blocks that you can
 change after you create the VCN. You can segment a
 VCN into subnets, which can be scoped to a region
 or to an availability domain. Each subnet consists
 of a contiguous range of addresses that don't
 overlap with the other subnets in the VCN. You can
 change the size of a subnet after creation. A
 subnet can be public or private. 

 
 
- OCI Block Volumes 
With Oracle Cloud
 Infrastructure Block Volumes , you can create, attach, connect, and move
 storage volumes, and change volume performance to
 meet your storage, performance, and application
 requirements. After you attach and connect a
 volume to an instance, you can use the volume like
 a regular hard drive. You can also disconnect a
 volume and attach it to another instance without
 losing data.
 

 
 
- OCI Kubernetes Engine 
 

 Oracle Cloud Infrastructure Kubernetes Engine ( OCI Kubernetes Engine or OKE ) is a fully-managed, scalable, and highly
 available service that you can use to deploy your
 containerized applications to the cloud. You
 specify the compute resources that your
 applications require, and OKE provisions them on OCI in an existing tenancy.
 OKE uses Kubernetes to automate the deployment,
 scaling, and management of containerized
 applications across clusters of hosts.
 

 
 
- OCI Object
 Storage 

 OCI Object Storage provides access to large amounts of structured
 and unstructured data of any content type,
 including database backups, analytic data, and
 rich content such as images and videos. You can
 safely and securely store data directly from
 applications or from within the cloud platform.
 You can scale storage without experiencing any
 degradation in performance or service reliability.
 
 

 
Use standard storage for
 "hot" storage that you need to access quickly,
 immediately, and frequently. Use archive storage
 for "cold" storage that you retain for long
 periods of time and seldom or rarely
 access.

 
 
- OCI
 Registry 
 Oracle Cloud Infrastructure
 Registry is an Oracle-managed service that enables you
 to simplify your development-to-production
 workflow. Registry makes it easy for you to store,
 share, and manage development artifacts, like
 Docker images.
 

 
 
 

 

 
 
Before You Begin

 

 

 Before you begin, ensure you set up the following: 
 
 

 
 
- Blog: Early LLM serving experience and performance results with AMD
 Instinct MI300X GPUs 
 
- Learn about vLLM .
 
 
- To launch a BM.GPU.MI300X.8 instance check the
 compute capacity in your tenancy by running Compute Capacity Create . Follow these steps , if you need to reserve a BM.GPU.MI300X.8 instance.
 
 
- To launch a GPU instance in a VCN you can choose either an existing VCN in your
 tenancy and region or you can create one. See the Oracle
 Cloud Infrastructure Networking documentation.
 
 
- If you want to use your own SSH key to connect to the instance using SSH, you need
 the public key from the SSH key pair that you plan to use. The key must be in the
 OpenSSH format, see Managing Key Pair on Linux Instance .
 
 
- For authorization to launch and work with instances, see the Required IAM policy to work with instance 
 documentation.
 
 
 

 

 
 
About Required Products and
 Roles

 

 
This solution requires the following products:

 
 
- Oracle Cloud Infrastructure
 Compute Bare Metal with AMD GPU
 
 
- Oracle Cloud
 Infrastructure Object Storage 
 
- Oracle Cloud
 Infrastructure Block Volumes 
 
- Oracle Cloud Infrastructure Kubernetes Engine 
 
- Oracle Cloud Infrastructure
 Registry 
 
 
These are the roles needed for each product.

 

 
 
 
 Service Name: Role 
 Required to... 
 
 
 
 
 Oracle Cloud Instance Launch Using Custom Image policy
 
 
 
 
 
- Allow group ImageUsers to inspect
 instance-images in compartment
 ABC .
 
 
- Allow group ImageUsers to
 {INSTANCE_IMAGE_READ} in compartment ABC
 where target.image.id='' .
 
 
- Allow group ImageUsers to manage instances in
 compartment ABC.
 
 
- Allow group ImageUsers to read
 app-catalog-listing in tenancy.
 
 
- Allow group ImageUsers to use
 volume-family in compartment ABC.
 
 
- Allow group ImageUsers to use
 virtual-network-family in compartment
 XYZ.
 
 
 
 
 
 
 Oracle Cloud Manage Kubernetes Cluster policy
 
 
 
 
- Allow group <group-name> to manage cluster-family in <location> .
 
 
- Allow group acme-dev-team-pool-admins to use cluster-node-pools in <location> .
 
 To create an OKE cluster in OCI, you must either belong to the
 tenancy's Administrators group, or belong to a group
 to which a policy grants the CLUSTER_MANAGE 
 permission. 
 
See the Policy Configu
