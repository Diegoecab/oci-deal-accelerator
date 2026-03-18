# DESIGN Phase — Detailed Guide

The DESIGN phase produces a complete, defensible architecture. Output: agreed architecture, cost estimate, operations model, and solution proposal.

## Steps

### 1. Current State (People, Process, Technology)

Capture enough about the current state to architect the future. Frame the problem — don't gather exhaustive requirements.

**Artefacts:**
- Discovery Questionnaire (`templates/discovery-questionnaire.yaml`) — structured customer data collection
- Business & Security Constraints — time, funding, legal, compliance, technology constraints
- Current State Apps & Tech Portfolio — systems, assets, integrations
- Prioritization Matrix — score apps by criticality, fit, potential, risk (in discovery questionnaire)
- Current State Architecture — diagrams of current environment

**Technology** (existing in Workload Profile):
- Databases, compute, middleware, messaging, storage, networking, identity, integration
- Use `config/workload-profile-schema.yaml` for field definitions

**People** (new — added to Workload Profile):
- Team size and roles (DBAs, cloud engineers, DevOps, security)
- Skill gaps relevant to the proposed solution
- Managed services preference (self-managed → fully managed)
- Change management readiness (how resistant is the org to change?)

**Process** (new — added to Workload Profile):
- Deployment process (manual, CI/CD, IaC maturity)
- Change management process (CAB, lightweight, none)
- Incident response process (NOC, on-call rotation, outsourced)
- Backup/recovery testing frequency

**Guidelines:**
- Frame the problem — don't gather exhaustive requirements
- Be collaborative — share everything with the customer
- Use whatever works — top-down and bottom-up
- Understand business context, drivers, and desired outcomes
- Be very clear about scope — which systems are in and out

**ECAL Artefacts:** See `kb/patterns/ecal-artefacts-catalog.yaml` DES-01 through DES-09
**Engagement RACI:** See `kb/patterns/engagement-raci.yaml` design.current

### 2. Future State (Solution Design)

Given the Workload Profile and Current State, compose a complete architecture. This step produces multiple design artifacts:

#### Solution Design
Core architecture composition — the existing Phase 2 workflow:
1. Select services from `kb/services/`
2. Dimension using `kb/sizing/` rules
3. Compose topology from `kb/patterns/` blocks
4. Estimate costs with explicit assumptions
5. Validate against Well-Architected Framework (`kb/well-architected/`)

#### Deployment Design
How the solution gets built and deployed:
- Environment strategy (dev, test, staging, prod)
- IaC approach (Terraform, Resource Manager, Ansible)
- CI/CD pipeline design
- Non-production environment sizing (typically 50% of prod for test, 25% for dev)

#### Transition Design
How to get from current state to future state:
- Migration strategy per component (lift-and-shift, re-platform, re-architect)
- Migration tooling (DMS, GoldenGate, RMAN, Data Pump, ZDM)
- Phased migration plan with dependencies
- Parallel run requirements and cutover strategy
- Rollback plan for each phase

#### Operations Model
How the solution will be operated day-to-day:
- Use `templates/operations-model.yaml` as the artifact template
- Monitoring and alerting strategy (OCI Monitoring, Logging Analytics, 3rd party)
- Patching and maintenance windows
- Backup and recovery procedures
- Incident response and escalation
- Capacity management and scaling triggers

**Guidelines:**
- Always look for a quick win the customer can see early
- The operational model is just as important as the architecture
- Don't forget non-production environments
- Security and data locality must be understood early

### 3. Confirm (Solution Proposal)

Assemble all design work into a solution proposal for stakeholder decision.

**Activities:**
- Assemble the slide deck with all architecture artifacts
- Prepare the business case: costs, benefits, timeline, risks
- Ensure all propositions are SMART:
  - **S**pecific: "Migrate 3 Oracle databases to ADB-S" not "Move to cloud"
  - **M**easurable: "Reduce DB admin effort by 60%" not "Improve efficiency"
  - **A**ttainable: Validated against feature matrix and field findings
  - **R**elevant: Tied to the business driver from the Value Story
  - **T**ime-based: "8-week migration" not "as soon as possible"
- Include competitive positioning if relevant (`kb/competitive/`)

**Output artifacts by tier:**

| Artifact | Small | Standard | Complex |
|----------|-------|----------|---------|
| Slide deck (.pptx) | 6-8 slides | 10-12 slides | 12-15 slides |
| Architecture diagram | Single-page | Single-page | Multi-page |
| Cost estimate | In-deck table | Separate .xlsx | Detailed .xlsx |
| ADRs | 2-3 inline | 4-6 in appendix | Full ADR docs |
| Migration plan | 1 slide | 2-3 slides | Separate doc |
| Operations model | In-deck summary | 1-page summary | Full template |
| Risk register | Top 3-5 | Top 5-8 | Full register |
| WA scorecard | Traffic lights | With recommendations | Full report |

**Guidelines:**
- Don't say anything you cannot back up with evidence
- The roadmap must be achievable
- Think about the person you are presenting to — what does it mean for them
- Quality of the presentation matters — it must look professional

## Iterative Checkpoint

Before moving to DELIVER (or presenting to customer):
```
- [ ] Architecture validated against WA Framework (no critical gaps)
- [ ] Cost estimate reviewed with explicit assumptions
- [ ] Migration plan is achievable within stated timeline
- [ ] Operations model addresses day-2 concerns
- [ ] All propositions are SMART
- [ ] Risk register has mitigations for all HIGH items
- [ ] Feature compatibility checked (no blockers)
- [ ] Field findings reviewed (no known issues unaddressed)
```
