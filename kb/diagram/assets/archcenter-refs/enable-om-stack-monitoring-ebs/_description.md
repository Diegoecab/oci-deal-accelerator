# Enable observability and management stack monitoring for Oracle E-Business Suite

- Source: https://docs.oracle.com/en/solutions/enable-om-stack-monitoring-ebs/index.html
- Date: 2024-10
- Type: reference-architecture
- Services: monitoring, compute
- Tags: observability, ebs

## Summary (catalog)

Stack Monitoring for EBS infrastructure and application health. Automatic discovery of EBS components, pre-built metrics and alarms for proactive monitoring.

## Architecture (fetched from source)

Understand Oracle Cloud Observability and Management Platform Stack Monitoring Service for Oracle E-Business Suite 
 
 
 
 
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
 
 

 

 
 
 
- Enable observability and management stack monitoring for Oracle E-Business Suite 
 
- Understand Oracle Cloud Observability and
 Management Platform Stack Monitoring Service for Oracle E-Business Suite 
 
 
 
 
Understand Oracle Cloud Observability and
 Management Platform Stack Monitoring Service for Oracle E-Business Suite 

 
 

 

 
The Stack Monitoring services in Oracle Cloud Observability and
 Management Platform for Oracle E-Business Suite deliver essential insights into application health, including real-time performance
 tracking and out-of-box metrics. These services offer integrated visibility across your E-Business Suite stack, enabling efficient troubleshooting, performance optimization, and proactive issue
 resolution to ensure seamless and reliable operation of your enterprise applications. 
 

 

 
 
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

 

 

 
 
Considerations for Monitoring a
 Stack

 

 
To ensure a successful experience when enabling observability and management
 stack monitoring for Oracle E-Business Suite 

 

 
 
 
- You do not need Oracle
 Application Management Pack (AMP) licenses for Stack Monitoring. Instead, the Stack
 Monitoring service is priced under APM Stack Monitoring in Oracle Cloud Observability and
 Management Platform .
 
 
- When running E-Business Suite on OCI Compute , ensure the Management Agent is enabled within the Oracle Cloud Agent.
 
 
- If you are running an E-Business Suite application on-premises, you'll need to manually install the Management Agent. You can
 download the Management Agent installation key and RPMs from the OCI Console.
 
 
- Once the agent is installed, both
 on-premises or on an OCI Compute instance, Stack Monitoring automatically creates a job to promote the compute to full
 monitoring. To do so:
 
 
- Click the promote link in the Promotion UI. 
 
- Ennsure the hostname to be discovered is using the FQDN, and within minutes Stack
 Monitoring will collect metrics and monitoring begins. 
 
- With the host now being monitored, next discover the Oracle Database where the E-Business Suite schema resides.
 
 
- Once you've discoverd Oracle Database , ensure all prerequisites are met. For a full set of prerequisites see "Discovering
 Oracle E-Business Suite", in Oracle Application Management Pack for Oracle
 E-Business Suite Guide , which you can access from "Explore More", elsewhere
 in this playbook.
 
 
 
 
- You can successfully discover E-Business Suite and Oracle Database by using DNS names or IP addresses.
 
 
- Once E-Business Suite resources has been discovered in Stack Monitoring, the out-of-box EBS metrics are
 exposed to OCI Monitoring service.
 
 
- To create alarms for the metrics,
 navigate to the OCI console and from the menu, select
 Observability , then Monitoring , then
 Alarm Definitions , then Create
 Alarm .
 

 
Note:
Stack Monitoring provides a list of recommended alarm rules. For
 details, see "Setting Up Alarms", in the Oracle Cloud
 Infrastructure documentation, which you can access from "Explore More".
 

 
 
 
 

 

 

 

 

 

 
 Title and Copyright Information 

 

 
Enable observability and management stack monitoring for Oracle E-Business Suite

 
G16566-01

 
October 2024

 
 Copyright © 2024, 

Oracle and/or its affiliates.
