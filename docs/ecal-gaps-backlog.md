# ECAL Gaps Backlog

Items identified from ECAL 3.1 Practitioners Guides (01-09) + Big Bets Banking Example PDF that are **not yet implemented** in the KB. Prioritized by impact.

## Priority 1 — High Impact (next sprint)

### B1. Integration Catalog Template
- **Source**: ECAL 05 FUTURE, slide 23
- **What**: Table of all non-OOTB integrations with data flows, volumes, frequency
- **Why**: Directly affects architecture accuracy and implementation scope
- **Action**: Create `templates/integration-catalog.yaml` with fields: use_case, source, target, method (API/file/DB link), protocol, data_volume, frequency, direction, owner

### B2. Cloud Operating Framework (52-week plan)
- **Source**: ECAL 08 OPERATE, slide 14
- **What**: Detailed first-year operational plan covering all 9 operational capability areas
- **Why**: Most customers have never operated cloud — this bridges the gap
- **Action**: Create `kb/patterns/cloud-operating-framework.yaml` with 9 capability areas mapped to weekly cadence
- **9 Capabilities**: Program Management, Cloud Innovation, Platform Enablement, Lifecycle Management, Environments Management, Testing, Management & Monitoring, Adoption & User Support, Issue Management

### B3. OCI Operationalization Framework (5 milestones)
- **Source**: ECAL 08 OPERATE, slide 15
- **What**: 5-milestone methodology for deploying workloads to OCI
- **Milestones**: Preparation & Training → Conceptual & Logical Arch → Physical Arch Execution → Operations → Specific Workloads
- **Action**: Create `kb/patterns/oci-operationalization.yaml`

### B4. POD (Pool of Databases) Pattern
- **Source**: Big Bets PDF, p.23
- **What**: Data platform pattern for large-scale DB consolidation
- **Characteristics**: Self-contained granular unit, standard external connectivity, internally optimized for DB, designed for maintainability/longevity, no prescribed hardware, on-prem/hybrid/cloud
- **Action**: Create `kb/patterns/database-consolidation-pod.yaml`

### B5. Banking/Financial Compliance Pattern
- **Source**: Big Bets PDF, pp.4,19,21
- **What**: EBA, FCA, PRA, ISO 27001/27002, NIST CSF requirements mapped to OCI services
- **Action**: Create `kb/compliance/banking-financial.yaml` with regulation → OCI service mapping

## Priority 2 — Medium Impact

### B6. Extension Catalog Template
- **Source**: ECAL 05 FUTURE, slide 22
- **What**: Custom extensions needed beyond OOTB Oracle products
- **Fields**: Business capability, name, type, technology, developer (customer/partner/Oracle)
- **Action**: Create `templates/extension-catalog.yaml`

### B7. Business Transition Plan Template
- **Source**: ECAL 07 ADOPT, slide 22
- **What**: Managing business change during technology transformation
- **Covers**: Org change, process standardization, policy alignment, value measurement
- **Action**: Create `templates/business-transition-plan.yaml`

### B8. Training & Communication Plan Template
- **Source**: ECAL 07 ADOPT, slide 23
- **What**: Training delivery plan + project communication plan
- **Action**: Create `templates/training-communication-plan.yaml`

### B9. Project Governance Template
- **Source**: ECAL 07 ADOPT, slide 25
- **What**: Governance framework: steering committee, change control, escalation
- **Components**: Steering committee, solution authority, change control board, project board
- **Action**: Create `templates/project-governance.yaml`

### B10. Customer Success Story Template
- **Source**: ECAL 09 IMPROVE, slide 14
- **What**: Single-slide format: who, industry, challenges, approach, value, turning point
- **Action**: Create `templates/customer-success-story.yaml`

### B11. Contracts & Policy Review Checklist
- **Source**: ECAL 07 ADOPT, slide 30
- **What**: Review checklist for all agreements (cloud services, ULA, PULA, partner)
- **Action**: Create `templates/contracts-review-checklist.yaml`

### B12. Readiness Assessment Template
- **Source**: ECAL 07 ADOPT, slide 31
- **What**: Ensure project team has right skills, assets, infrastructure, processes
- **Action**: Create `templates/readiness-assessment.yaml`

## Priority 3 — Lower Impact (nice to have)

### B13. PoC Joint Execution Plan Template
- **Source**: ECAL 05 FUTURE, slide 43
- **What**: Scope, approach, timeline, success criteria, use cases, test plans, ground rules
- **Action**: Create `templates/poc-execution-plan.yaml`

### B14. Information & BI Model Template
- **Source**: ECAL 05 FUTURE, slide 24
- **What**: Data flows, MDM, analytics/BI architecture view
- **Action**: Create `kb/patterns/information-bi-model.yaml`

### B15. Current State Process & Capability Map Guide
- **Source**: ECAL 04 CURRENT, slide 17
- **What**: Guidance for creating business architecture view of current state
- **Note**: This is mostly a customer/BA activity — skill can provide structure
- **Action**: Add guidance to `docs/design-phase.md`

### B16. RFx Response Guide
- **Source**: ECAL 06 CONFIRM, slide 14
- **What**: Process for responding to RFI/RFQ/RFP
- **Note**: Primarily sales/BD activity
- **Action**: Add brief section to `docs/design-phase.md` Confirm step

### B17. Commercial Agreement Guide
- **Source**: ECAL 06 CONFIRM, slide 16
- **What**: BYOL, ELA, PULA, Cloud Credits options and when to use each
- **Action**: Enhance `kb/pricing/` with licensing model guidance

### B18. TCM Alignment Mapping
- **Source**: All ECAL guides — Consulting Guidance slides
- **What**: Map ECAL artefacts to Oracle True Cloud Method (TCM) activities
- **Action**: Add `tcm_alignment` field to ecal-artefacts-catalog.yaml

### B19. ExaCC Managed Service Pattern
- **Source**: Big Bets PDF
- **What**: Complete pattern for ExaCC with ZDLRA, ZFS, OEM, OKV as managed service
- **Action**: Create `kb/patterns/exacc-managed-service.yaml`

### B20. Security Constraints Checklist
- **Source**: ECAL 04 CURRENT, slide 15
- **What**: Structured checklist for security requirements assessment
- **Action**: Create `templates/security-constraints-checklist.yaml`

---

## Completed (this session)

| Item | File Created |
|---|---|
| Engagement RACI (10 roles, all 9 steps) | `kb/patterns/engagement-raci.yaml` |
| Discovery Questionnaire (with prioritization) | `templates/discovery-questionnaire.yaml` |
| Business Drivers Framework (4 pillars + hypothesis families) | `kb/patterns/business-drivers.yaml` |
| ECAL Artefacts Catalog (60 artefacts, skill support classification) | `kb/patterns/ecal-artefacts-catalog.yaml` |
| Customer Profile Template | `templates/customer-profile.yaml` |
| Strategy Map Template | `templates/strategy-map.yaml` |
| Lessons Learned per step | Included in `engagement-raci.yaml` |
