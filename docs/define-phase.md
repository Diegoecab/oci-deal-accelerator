# DEFINE Phase — Detailed Guide

The DEFINE phase identifies the customer's business problem and builds commitment to solve it. Output: a scoped **Value Story** and a **Joint Engagement Plan**.

## Steps

### 1. Ideate

Create a value hypothesis expressed in the customer's business terms — not Oracle features.

**Inputs:**
- Discovery notes (unstructured)
- Customer's public filings, strategy docs, press releases
- Industry patterns from `kb/patterns/business-patterns.yaml`

**Activities:**
- Parse discovery notes into structured Workload Profile
- Identify 1-3 business drivers (cost, risk, growth, compliance, modernization)
- Formulate hypothesis: "If we [technical action], the customer achieves [business outcome]"
- Cross-reference with `kb/patterns/application-patterns.yaml` for proven solutions

**Output:** Draft Value Story (`templates/value-story.yaml`)

### 2. Validate

Test the hypothesis against the customer's reality.

**Activities:**
- Review value story for SMART criteria (Specific, Measurable, Attainable, Relevant, Time-based)
- Identify gaps in discovery data — list what we assumed vs. what we confirmed
- Check: Is the hypothesis bold enough? Is there enough urgency?
- Validate technical feasibility against `kb/services/` and `kb/compatibility/`

**Validation checklist:**
```
- [ ] Business driver clearly identified and quantifiable
- [ ] Desired outcome is SMART
- [ ] Technical feasibility confirmed (no blockers in feature matrix)
- [ ] Customer sponsor identified
- [ ] Urgency driver exists (EOL, contract, compliance deadline, competitive threat)
```

**Output:** Validated Value Story with confidence flags

### 3. Plan

If the hypothesis is compelling, create a Joint Engagement Plan for the DESIGN phase.

**Activities:**
- Define engagement tier (small/standard/complex) — see [engagement-tiers.md](engagement-tiers.md)
- Timebox the DESIGN phase (typically 2-6 weeks)
- Identify resources needed (SA, specialists, customer stakeholders)
- Define success criteria for the DESIGN phase itself

**Output:** Joint Engagement Plan (`templates/joint-engagement-plan.yaml`)

## Engagement Tier Selection

The tier determines artifact depth. Select based on:

| Signal | Small | Standard | Complex |
|--------|-------|----------|---------|
| # Applications | 1-2 | 3-10 | 10+ |
| Compliance | None | 1 framework | Multiple |
| Regions | 1 | 1-2 | 3+ |
| Integration points | 0-2 | 3-5 | 5+ |
| Budget sensitivity | Low | Medium | High |
| Timeline | < 4 weeks | 4-12 weeks | 12+ weeks |

See [engagement-tiers.md](engagement-tiers.md) for full tier definitions and artifact mapping.

## Iterative Checkpoint

Before moving to DESIGN, verify:
```
- [ ] Value Story approved by architect (and ideally customer sponsor)
- [ ] Workload Profile has < 3 critical gaps
- [ ] Engagement tier selected
- [ ] Joint Engagement Plan agreed (timebox, resources, success criteria)
```

If the value story isn't compelling, iterate: refine the hypothesis or pick another one.
