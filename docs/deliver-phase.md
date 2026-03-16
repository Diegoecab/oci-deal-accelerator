# DELIVER Phase — Detailed Guide

The DELIVER phase ensures an efficient handover from pre-sales to implementation and tracks value realization. These are **lightweight artifacts** — the SA does not replace the implementation team.

> ECAL DELIVER describes the solution implementation at high level. It provides just enough guidance and templates to deliver. It dovetails with the customer or implementation partner framework (e.g., Oracle Consulting True Cloud Method).

## Steps

### 1. Adopt

Ensure a clean handover so the implementation team doesn't rework previous steps.

**Activities:**
- Produce Handover Document (`templates/handover-document.yaml`)
  - Summarizes all DEFINE + DESIGN artifacts in one place
  - Lists key decisions made and their rationale (from ADRs)
  - Identifies open items and assumptions to verify
- Define MVP scope
  - What ships in Phase 1 vs. later phases
  - Prioritize by customer value, not technical convenience
  - Example: "Phase 1: migrate core OLTP to ADB-S with local HA. Phase 2: activate cross-region DR. Phase 3: modernize reporting with ADW."
- Establish governance
  - Steering committee cadence (bi-weekly for standard, weekly for complex)
  - Escalation path
  - Change control process

**Output:** Handover Document + MVP Definition

**Guidelines:**
- Look for a Minimum Viable Product that delivers real customer benefits early
- Incremental delivery phases should maximize customer value per the roadmap
- Consider how to help the customer with adoption and ownership

### 2. Operate

Define what "running well" looks like after go-live.

**Activities:**
- Produce Go-Live Checklist (`templates/go-live-checklist.yaml`)
  - Pre-go-live verification items
  - Monitoring and alerting confirmation
  - Runbook availability
  - Rollback readiness
- Define Success Criteria (`templates/success-criteria.yaml`)
  - Quantitative metrics tied to the Value Story
  - Example: "P95 latency < 15ms", "Monthly cost < $X", "Zero unplanned downtime in first 90 days"
  - Measurement method and cadence
- Operational handover
  - Confirm ops team has access and training
  - Validate monitoring dashboards are active
  - Confirm backup/recovery has been tested

**Output:** Go-Live Checklist + Success Criteria

**Guidelines:**
- Regular governance checks should continue beyond go-live
- Data must be collected to validate business outcomes
- Results should be reported back to the business sponsor

### 3. Improve

Capture learnings and validate value delivery.

**Activities:**
- Produce Lessons Learned (`templates/lessons-learned.yaml`)
  - What worked well (reuse in future engagements)
  - What didn't work (improve process or templates)
  - Suggestions for ECAL/skill improvements
- Value realization check (30/60/90 days post go-live)
  - Compare actual metrics against Success Criteria
  - Determine if the original hypothesis from DEFINE delivered value
  - Identify next hypothesis to tackle
- Feed improvements back
  - Update `kb/field-knowledge/` with new findings
  - Update patterns if architecture evolved during delivery
  - Share customer success story if applicable

**Output:** Lessons Learned + Value Realization Report

**Guidelines:**
- Grab any opportunity to capture a successful outcome as a customer story
- Look back at every project for what you could do better
- Keep in touch with the customer and track how the project is going
- Share learnings with the team

## Artifact Summary by Tier

| Artifact | Small | Standard | Complex |
|----------|-------|----------|---------|
| Handover Document | 1-page summary | Full template | Full + appendices |
| MVP Definition | Inline in handover | Separate section | Phased roadmap |
| Go-Live Checklist | 10-15 items | 20-30 items | 30-50 items |
| Success Criteria | 3-5 metrics | 5-8 metrics | 8-12 metrics |
| Lessons Learned | Brief notes | Full template | Full + retro |

## Iterative Checkpoint

The DELIVER phase feeds back into DEFINE for next phases:
```
- [ ] Handover document complete and reviewed with implementation team
- [ ] MVP scope agreed with customer
- [ ] Go-live checklist validated (all items green)
- [ ] Success criteria baselined (measurements started)
- [ ] Lessons learned captured within 2 weeks of go-live
- [ ] Value realization check scheduled (30/60/90 days)
- [ ] Next hypothesis identified (return to DEFINE if applicable)
```
