# Incorporate Cyber-Resilience Capabilities Into Your OCI Tenancy

- Source: https://docs.oracle.com/en/solutions/oci-tenancy-cyber-resilience-architecture/index.html
- Date: 2025-08
- Type: reference-architecture
- Services: cloud-guard, vault, data-safe
- Tags: security

## Summary (catalog)

Cyber-resilience architecture for OCI tenancies. Immutable backups, isolated recovery environments, threat detection with Cloud Guard, and database activity monitoring with Data Safe.

## Architecture (fetched from source)

Learn About Cyber Resilient Architectures that Protect Data from Ransomware 
 
 
 
 
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
 
 

 

 
 
 
Learn About Cyber Resilient
 Architectures that Protect Data from Ransomware

 

 

 

 Ransomware attacks are among the most egregious cybercrimes facing
 businesses today. They can disrupt operations, damage your reputation, and lead to
 escalating recovery and remediation costs. 
 
 

 
Ransomware is an advanced form of malware that uses complex algorithms to
 encrypt your data and lock you out of your systems. Threat actors demand a
 ransom—usually in cryptocurrency to protect their identity—in exchange for a decryption
 key to restore access.

 
Modern ransomware attacks often use a double extortion method: not
 only is your data encrypted, but it is also exfiltrated, with attackers threatening to
 publicly release it if you do not pay.
 

 
In this solution playbook, you learn about Cybersecurity measures to "Protect and Detect" your environment, and Cyber Resilience strategies to "Respond and Recover" your data
 from ransomware.
 

 

 
 
About the NIST Cybersecurity
 Framework

 

 

 The NIST cybersecurity framework which calls out defensive
 best practices centered around the security continuum and the CIA (Confidentiality,
 Integrity, and Availability) Triad, and is best described using the
 following: 
 
 

 
 
- Protect : Prevent a threat to either data confidentiality,
 integrity, or availability.
 
 
- Detect : Detect anomalous activity that may be construed as
 evidence of attempted and/or successful malicious activity.
 
 
- Respond : Address, deter, and counteract a successful
 compromise.
 
 
- Recover : Assume that the compromise has occurred and use
 mechanisms to restore an environment to a known good state.
 
 
 

 

 
 
About the Cyber Triad

 

 

 
 
In the early days of cybersecurity, the focus was primarily on preventing
 attackers from entering networks. However, as threats became more sophisticated with the
 rise of advanced viruses and malware, it became clear that prevention alone was not
 enough. In addition to prevention strategies, detection techniques were introduced to
 identify and flag attackers that breached the firewall.

 
 
Today's antivirus and malware solutions can't keep up. Attackers
 increasingly make their way into the internal networks where they sit dormant, move
 laterally, and orchestrate sophisticated ransomware attacks.

 
 

 
 Description of the illustration oci-cyber-triad-venn-diagram.png 

To avoid being a victim of extortion, supply chain disruptions, and
 operational shutdowns that often accompany ransomware breaches, Oracle recommends that
 your cloud architecture addresses the cyber triad:

 
 
- Cybersecurity 
 
- Cyber resilience 
 
- Disaster recovery 
 
 
By considering all three aspects of the cyber triad, your organization will
 be well positioned to recover from ransomware while meeting your organization's RTO
 (Recovery Time Objective) and RPO (Recovery Point Objective) requirements.

 
While enhancing your OCI environment security, retain focus on the core
 security fundamentals and disaster recovery methods to ensure availability of your
 workloads. For example, if you replicate data that has been compromised, your recovery
 site will be affected in the same way as your primary site and does not address the
 problem of preventing deletion, encryption or modification by threat actors.

 
Designing a cyber resilient architecture protects your backups and ensures
 that you determine if a threat actor modified, deleted, or tampered with the data before
 restoring it.

 
Bringing together the cyber triad, traditional security measures, and
 disaster recovery helps you ensure cyber resilience and better prepare your organization
 to recover from ransomware.

 

 
Note:
High availability and disaster recovery
 are important parts of your architecture, but they are outside the scope of this
 solution playbook. 
 

 

 

 
 
Ask the Architect

 

 
Replay the Ask the Architect episode:
 

 

 

 

 
The following lists the various points (mins:secs) in the video where
 these topics begin:
 

 
 
- 00:00 - Opening 
 
- 02:54 - Introducing the Cyber Triad 
 
- 10:00 - Enclaves and Cyber Resilient Architecture (CRA) 
 
- 17:31 - Understanding Cybersecurity Pillar 
 
- 25:00 - Understanding Cyber Resilience - Concepts and Controls 
 
- 38:15 - Oracle Database Zero Data Loss Autonomous Recovery Service - details and demo
 
 
- 44:26 - Demo of the CRA Terraform stack for Unstructured Data 
 
- 49:34 - Summary 
 
 

 

 
 
Before You Begin

 

 
 Before you can begin setting up cybersecurity, deploy
 the foundational Core Landing Zone using the Deploy a secure landing
 zone that meets the CIS OCI Foundations Benchmark reference architecture.
 

 
Review these related resources:

 
 
- OCI
 IAM 
 
 
 
- 
 
 
 Overview of security best practices in OCI tenancy blog
 

 
 
 
- 
 
 
 Oracle
 Database Cloud Best Practices 

 
 
 
- 
 
 
 OCI
 Zero-Trust Security Model site
 

 
 
 
- 
 
 OCI Core Landing Zone documentation
 

 
 
 

 

 

 

 

 
 Title and Copyright Information 

 

 
Incorporate cyber resilience capabilities into your OCI tenancy

 
F85043-05

 
August 2025

 
 Copyright © 2023,2025, 

Oracle and/or its affiliates.
