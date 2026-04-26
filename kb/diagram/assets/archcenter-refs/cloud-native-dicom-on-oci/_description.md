# Implement a cloud-native DICOM store on Oracle Cloud Infrastructure

- Source: https://docs.oracle.com/en/solutions/cloud-native-dicom-on-oci/index.html
- Date: 2025-12
- Type: reference-architecture
- Services: oke, object-storage, adb-s
- Tags: healthcare, application, autonomous

## Summary (catalog)

Cloud-native DICOM store on OKE with Object Storage for medical images and ADB-S for metadata. DICOMweb API compliance for interoperability with medical imaging systems.

## Architecture (fetched from source)

Architecture

 

 
This architecture implements a DICOM store on Oracle Cloud
 Infrastructure .
 

 
The following diagram illustrates this reference architecture.

 
 Description of the illustration dicom-oci-diagram.png 

 oci-dicom-store-oracle.zip 

 
The architecture has the following components:

 
 
- Oracle Cloud
 Infrastructure 
 Oracle Cloud
 Infrastructure (OCI) is Oracle's cloud computing platform
 that provides a comprehensive suite of services for
 building, deploying, and managing applications in the cloud.
 Designed for enterprise performance and security, OCI offers
 infrastructure as a service (IaaS), platform as a service
 (PaaS), and other cloud services such as AI, machine
 learning, networking, storage, and database solutions.
 

 
OCI provides high performance, scalability, and
 cost-efficiency, supporting a wide range of workloads from
 legacy enterprise applications to cloud-native services. It
 is ideal for businesses seeking robust cloud capabilities
 with strong support for hybrid and multi-cloud
 architectures.

 
 
- Cloud-based data science platform 
 Oracle Cloud Infrastructure Data Science is a fully managed platform that enables data scientists
 to build, train, deploy, and manage machine learning models
 at scale. It provides a collaborative, secure environment
 with integrated tools for the entire data science lifecycle,
 including notebooks, automated model training, model
 evaluation, and deployment.
 

 
 Data
 Science supports popular open-source frameworks like TensorFlow,
 scikit-learn, PyTorch, and XGBoost, and offers seamless
 integration with other OCI services such as Object Storage,
 Data Flow, and AI Services. Backed by a wide selection of
 CPU and GPU shapes, Data
 Science helps organizations accelerate AI development, streamline
 collaboration across teams, and operationalize machine
 learning models efficiently in the cloud.
 

 
 
- AI model training and inference 
AI
 training and inference are the two core stages in the
 lifecycle of an artificial intelligence model:

 
 
- Training is the process by which a model
 learns from large datasets by adjusting its internal
 parameters to recognize patterns, make predictions,
 or perform specific tasks. This phase is
 computationally intensive and requires powerful
 hardware such as GPUs, as well as high-throughput
 storage and networking. 
 
- Inference is the stage where the trained
 model is used to make predictions or decisions based
 on new, unseen data. Inference typically needs to be
 fast and scalable, especially in real-time
 applications like medical imaging, fraud detection,
 or virtual assistants. 
 
 
Chosen by world’s leading AI companies such as
 OpenAI and xAI, OCI Generative AI infrastructure has emerged as a leading platform for AI
 model training and inference, offering a unique combination
 of performance, scalability, and cost-efficiency.
 

 
 
- Security and Compliance 
OCI offers a
 comprehensive set of security and compliance features
 designed to protect data, applications, and workloads across
 the cloud environment. OCI provides built-in security at
 every layer, including network security, identity and access
 management (IAM), data encryption, threat detection, and
 monitoring.

 
Key features include isolated
 network virtualization, customer-controlled encryption keys,
 security zones, and Oracle Cloud Guard for continuous monitoring and automated threat response.
 OCI also supports compliance with major industry and
 regulatory standards such as ISO, SOC, HIPAA, GDPR, and
 FedRAMP, helping organizations meet strict data protection
 and governance requirements.
 

 
These
 capabilities make OCI a trusted platform for running
 sensitive, mission-critical workloads securely and in
 compliance with global standards.

 
 
- Orthanc 
Orthanc is an open-source,
 lightweight DICOM server designed to manage, store, and
 share medical imaging data. It is widely used in hospitals
 and research labs, and by developers to build imaging
 workflows without relying on heavy commercial PACS (Picture
 Archiving and Communication Systems).

 
Orthanc seamlessly integrates with OCI Object Storage and OCI Database with PostgreSQL , providing a DICOMweb API endpoint that enables users to
 store, retrieve, and query DICOM images by using RESTful
 APIs.
 

 
In this reference architecture,
 Orthanc is deployed on OCI Container Instances or OCI Container Instances (OKE), eliminating the infrastructure management overhead
 for our healthcare customers.
 

 
 
- OCI Object Storage 
Actual DICOM images are stored in an
 OCI Object Storage bucket.
 

 
 OCI Object Storage offers highly durable, infinitely scalable, and secure
 storage for any type of data—structured or unstructured.
 Whether you're archiving medical images, serving media
 files, or backing up enterprise workloads, OCI Object Storage provides low-latency access, built-in redundancy, and
 tiered pricing to optimize cost and performance. It is
 designed for modern cloud applications, integrates natively
 with AI, analytics, and DevOps tools, and offers seamless
 data lifecycle management, all with no up-front hardware
 investment.
 

 
 
- OCI Database with PostgreSQL 
In this reference architecture, Orthanc
 is integrated with OCI Database with PostgreSQL to manage and index the non-image metadata associated
 with DICOM files. While Orthanc can run without an external
 database (using its built-in SQLite engine), integrating
 with a managed and more powerful database such as OCI Database with PostgreSQL is recommended for scalability and performance.
 

 
 
- OCI Kubernetes Engine 
 Oracle Cloud Infrastructure Kubernetes Engine ( OCI Kubernetes Engine or OKE ) is a fully managed, enterprise-grade Kubernetes service
 that simplifies container orchestration on Oracle Cloud.
 With OKE, you get automated provisioning, scaling, and
 updates, so you can deploy, run, and manage cloud-native
 applications with less overhead.
 

 
Running
 AI workloads on OKE gives you the best of both worlds: the flexibility of
 containers and Kubernetes, combined with the power of OCI’s
 high-performance infrastructure. Whether you're training
 models on GPU nodes or deploying inference at scale, OKE lets you manage AI pipelines with ease using your
 favorite tools like TensorFlow, PyTorch, or Hugging
 Face.
 

 
With automated scaling, GPU
 support, integrated logging, and cost-efficient pricing, OKE makes it simple to build, run, and scale AI workloads in
 production, all in a secure, enterprise-grade
 environment.
 

 
 
- OCI FastConnect 
 OCI FastConnect offers dedicated, private network connectivity between
 customer’s on-premises facility, such as a hospital, and Oracle Cloud , delivering high throughput, low latency, and predictable
 performance for enterprise workloads. It bypasses the public
 internet entirely, improving security and reliability for
 hybrid and multicloud architectures.
 

 
But
 what sets OCI FastConnect apart is its cost model: OCI doesn’t charge for data
 egress over Oracle Cloud , unlike other cloud providers that often impose steep
 outbound data transfer fees. This creates significant cost
 savings for data-heavy workloads like medical
 imaging.
 

 
 
- OCI Roving Edge Device 
OCI Roving
 Edge Devices (REDs) help facilitate DICOM data transmission
 and provide the necessary infrastructure for local
 inference. They bring the power of Oracle Cloud to the edge: rugged, portable, high-performance nodes
 that let you run applications, process data, and deploy AI
 models in disconnected or remote environments.
 

 
REDs enable low-latency edge computing with
 full compatibility with OCI services. You can preload VMs,
 containers, and data, then synchronize with the cloud when
 connectivity is available.

 
 
 

 

 
 
Recommendations

 

 
 Use the following recommendations as a starting point
 for implementing a DICOM store on Oracle Cloud
 Infrastructure . Your requirements mi
