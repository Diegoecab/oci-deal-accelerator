# Enable Observability and Management Stack Monitoring for PeopleSoft

- Source: https://docs.oracle.com/en/solutions/enable-om-stack-monitoring-psft/index.html
- Date: 2024-12
- Type: reference-architecture
- Services: monitoring, compute
- Tags: observability, peoplesoft

## Summary (catalog)

Stack Monitoring for PeopleSoft. Automatic discovery of PIA, App Server, Process Scheduler, and database components. Metrics and alarms for performance and availability monitoring.

## Architecture (fetched from source)

Understand Oracle Cloud Observability and Management Platform Stack Monitoring Service for PeopleSoft Applications 
 
 
 
 
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
 
 

 

 
 
 
- Enable Observability and Management Stack Monitoring for PeopleSoft 
 
- Understand Oracle Cloud Observability and
 Management Platform Stack Monitoring Service for PeopleSoft Applications 
 
 
 
 
Understand Oracle Cloud Observability and
 Management Platform Stack Monitoring Service for PeopleSoft Applications
 

 
 

 

 
The Stack Monitoring services in Oracle Cloud Observability and
 Management Platform for PeopleSoft applications deliver essential insights into application health, including
 real-time performance tracking and out-of-box metrics. These services offer integrated
 visibility across your PeopleSoft stack, enabling efficient troubleshooting, performance
 optimization, and proactive issue resolution to ensure seamless and reliable operation of
 your enterprise applications. 
 

 

 
 
Configure Your Environment

 

 
Before you can use the Stack Monitoring service, you must set up your Oracle Cloud
 Infrastructure environment to allow communication between the different components and services. This
 section explains the steps to set up Oracle Cloud Infrastructure for Stack
 Monitoring.
 

 

 
Note:
 The full procedures for completing the steps in this topic are beyond the scope of
 this playbook. Please refer "Getting Started" in the Oracle Cloud
 Infrastructure documentation, which you can access from "Explore More", elsewhere in this
 playbook.
 

 
To properly configure your OCI envieronment, you need to complete these three
 steps:
 
 
- Create or Designate a Compartment to Use 
 
 
You can create a new compartment or use an existing compartment
 to install and configure the Stack Monitoring service. Stack Monitoring
 supports the following configurations to create a single-pane of glass for
 monitoring all resources: 
 
 
- All resources are deployed within the monitoring
 compartment. 
 
- Resources deployed in a compartment different than the
 monitoring compartment. 
 
 

 
 
- Install Management Agents 
 
 
Next, you need to install the Management Agent, which is a
 prerequisite for using the Stack Monitoring service. You can learn more
 about the Management Agent in the following topic, "Learn About the
 Management Agent in Oracle Cloud
 Infrastructure ".
 

 
 
- Enable the Stack Monitoring Service 
 
 
Finally, you need to enable the Stack Monitoring service, from
 the Oracle Cloud
 Infrastructure console. Navigate to Stack Monitoring located under Observability
 and Management, Stack Monitoring. Select the compartment you want to
 monitor, and click Enable Stack Monitoring .
 

 
 
 

 

 

 
 
Learn About the Management Agent
 in Oracle Cloud
 Infrastructure 

 

 
 The Management Agent in OCI is a lightweight software component that
 facilitates monitoring and management of on-premises resources and hybrid cloud
 environments. It securely connects these resources to OCI services such as Monitoring,
 Logging, and Operations Insights, enabling centralized visibility and control. As mentioned
 in the previous topic you need to set up this component to deploy stack monitoring. 

 
The key Management Agent features are:
 
 
- Monitoring: Provides detailed metrics and logs from on-premises resources
 to OCI Monitoring. 
 
 
- Logging: Sends log data from on-premises environments to OCI Logging for
 analysis and troubleshooting. 
 
 
- Operations Insights: Enables operational insights and automation for
 hybrid cloud environments. 
 
 
- Security: Ensures secure communication with OCI using encryption and
 authentication mechanisms. 
 
 
 

 
See "Management Agent" in the Oracle Cloud Infrastructure Documentation, which you can
 access from"Explore More".

 

 

 

 

 

 
 Title and Copyright Information 

 

 
Enable Observability and Management Stack Monitoring for PeopleSoft

 
G19528-01

 
December 2024

 
 Copyright © 2024, 

Oracle and/or its affiliates.
