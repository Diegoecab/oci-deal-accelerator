# Analyze and visualize healthcare data and apply AI on OCI to solve real-world challenges

- Source: https://docs.oracle.com/en/solutions/oci-ai-healthcare/index.html
- Date: 2024-12
- Type: reference-architecture
- Services: genai, adb-s, data-integration
- Tags: healthcare, ai-ml, data-platform

## Summary (catalog)

Healthcare analytics platform with AI on OCI. FHIR data ingestion, clinical NLP with GenAI, predictive analytics for patient outcomes. ADB-S for structured clinical data, Object Storage for imaging.

## Architecture (fetched from source)

Architecture

 

 
OCI supports open-source tools, and its framework makes it seamless to
 implement the architecture using in-house skilled resources while providing
 portability.

 
In this reference architecture, we will discuss a solution design that can
 be implemented for use cases including improving patient care and disease prevention;
 evidence-based decision-making in pre-authorization; and detecting, analyzing, and
 optimizing medical alarm parameters for hospitals and healthcare providers.

 
 Data Analytics and Machine Learning :
 

 
For the healthcare customer, Oracle Autonomous Data Warehouse was an ideal solution since the customer was using streaming data from sensors where
 Oracle Autonomous Data Warehouse ’s scalability and their Lakehouse capabilities were optimal. Oracle Autonomous Data Warehouse ’s easy integration with Oracle Machine Learning helped the customer prepare and understand their data better in the pre-processing
 stage. Oracle Machine Learning also supports exporting data to and from Jupyter Notebooks, enabling data scientists
 to combine Oracle’s in-database ML with other popular data science libraries. Oracle Machine Learning has many benefits, including: ease of install, usage of in-database computing,
 reduced management overhead, cross-purpose powerful and scalable database compute for
 SQL, Python based analytics at scale.
 

 
Using Oracle Machine Learning , the customer was able to install and test a wide variety of Python-based libraries
 (including Panda, NumPy), run the existing Julia application, and analytics at scale.
 Oracle Machine Learning also features Automatic Model Deployment, where models are instantly available for
 scoring within applications or analytics dashboards after training and simplifying the
 deployment process. The customer was able to port the same Python UDFs and UDTFs, and
 the same SQL queries from Snowflake to Oracle Autonomous Data Warehouse without needing to refactor code. For the ML model, customer used the AutoML
 capability, greatly simplifying the model training process, allowing users with minimal
 machine learning experience to achieve desired accuracy and generate insights from
 medical device data.
 

 
 AI application using GPU compute on OCI: 

 
OCI provides optimal performance for AI applications with cutting edge cloud
 infrastructure powered by Nvidia and AMD GPUs. OCI helps to accelerate your AI solution
 with model training, inferencing, and AI analysis. OCI partners with Nvidia to bring
 Nvidia Nemo for end-to-end development of generative AI, and uses Nvidia Inference
 Microservices (NIM) to speed up AI inference of AI models. To run AI applications on OCI
 AI infrastructure, OCI deploys GPU compute instances with either HPC Slurm cluster or
 Oracle Cloud Infrastructure Kubernetes Engine ( OCI Kubernetes Engine or OKE) using our customized and scalable terraform stacks, including various storage
 options.
 

 
AI based medical diagnosis and clinical data management consists of NLP/LLM
 for EHR data, medical imaging, clinical data, and lab results. Nvidia application
 frameworks, such as BioNemo, MONAI, triton inference server, along with Cohere provides
 a solution that speeds up AI adoption.

 
 Data Science Notebooks and integration: 

 
This reference architecture uses the Oracle Cloud Infrastructure Data Science service, a fully managed platform for teams of data scientists to build, train,
 deploy, and manage machine learning (ML) models using Python with built-in framework
 like Pytorch, TensorFlow and other open-source framework of your choice. This service
 can be used to create an open-source Jupyter-based development environment with built-in
 integration with GitHub. Nvidia A10 GPU compute can be used for training the LLM models,
 build MLOps pipeline integrated with mlfow, and, lastly, deploy from Notebook into a
 scalable and low latency inference secured endpoint and monitor model performance. The
 customer could choose from a variety of supported Nvidia GPUs on bare metals or virtual
 instances to train and deploy AI models at scale.
 

 
 Backup and Disaster Recovery: 

 
For healthcare, customer data protection and availability is extremely
 important. Due to various regulations, data must be protected and made available on
 demand. Oracle Autonomous Database provides options of automated backup and recovery and can create a replica database
 using Oracle Cloud Guard . The database replica also can work as a read-only standby copy of database to reduce
 load on the primary database, therefore improve database performance and load
 balancing.
 

 
 Security and Access Management: 

 
This architecture implements OCI Zero Trust security best practice using
 network, data and application security features in all layers of the architecture. For
 network security, compute is implemented in private network using Virtual Cloud Network
 (VCN) and traffic filter is applied using Security List (SLs) and Network Security Group
 (NSGs). Data is always encrypted at rest (AES256) and in transit (TLS 2.0) with easy
 customer provided certificate management.

 
 Oracle Data Safe , which is included with Oracle Autonomous Database , provides a unified control center that helps manage the day-to-day security and
 compliance requirements of Oracle databases. Oracle Data Safe provides advanced data security features required by healthcare such as Data Masking,
 Data Obfuscation, Activity Auditing, and SQL Firewall Management.
 

 
 Oracle Cloud Infrastructure Identity
 and Access Management ( OCI Identity and Access Management ) implements the principle of least privilege and OAuth 2.0 authentication of end user
 access using identity. It securely provides advanced features like Multi Factor
 Authentication and token based authentication (JWT).
 

 
The following diagram illustrates this reference architecture.

 
 Description of the illustration oci-ai-healthcare_arch.png 

 oci-ai-healthcare_arch-oracle.zip 

 
The architecture has the following components:

 
 
- API Gateway 
 Oracle Cloud Infrastructure API Gateway enables you to publish APIs with private endpoints that are accessible from within your network, and which you can expose to the public internet if required. The endpoints support API validation, request and response transformation, CORS, authentication and authorization, and request limiting.
 

 
 
- Object Storage 
 Oracle Cloud
 Infrastructure Object Storage provides quick access to large amounts of structured and
 unstructured data of any content type, including database backups, analytics
 data, and rich content such as images and videos. You can safely and securely
 store and retrieve data directly from the internet or within the cloud platform.
 You can scale storage without experiencing any degradation in performance or
 service reliability. Use standard storage for "hot" storage that you need to
 access quickly, immediately, and frequently. Use archive storage for "cold"
 storage that you retain for long periods of time and seldom or rarely
 access.
 

 
 
- Web Application Firewall (WAF) 
 Oracle Cloud Infrastructure Web
 Application Firewall (WAF) is a payment card industry (PCI) compliant, regional-based and edge enforcement service that is attached to an enforcement point, such as a load balancer or a web application domain name. WAF protects applications from malicious and unwanted internet traffic. WAF can protect any internet facing endpoint, providing consistent rule enforcement across a customer's applications.
 

 
 
- Dynamic routing gateway (DRG) 
The DRG is a virtual router that provides a path for private network traffic between VCNs in the same region, between a VCN and a network outside the region, such as a VCN in another Oracle Cloud
 Infrastructure region, an on-premises network, or a network in another cloud provider.
 

 
 
- Security list 
For each subnet, you can create security rules that specify the source, 
