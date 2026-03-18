# Engagement Tiers

Engagement tiers scale artifact depth to match engagement complexity. Not every deal needs a 15-slide deck and full ADR set.

## Tier Definitions

### Small (Rapid Innovation)

**Profile:** Single workload, single region, minimal compliance, short timeline.

**Examples:**
- Autonomous Database + Analytics Cloud dashboard
- Single app migration to OKE
- PoC or pilot deployment

**Characteristics:**
- 1-2 applications in scope
- No compliance frameworks
- Single OCI region
- 0-2 integration points
- Budget < $10K/month
- Timeline < 4 weeks design

**Artifact depth:** Highly templated, minimal customization. The Value Story can be a single paragraph. The deck is 6-8 slides. No separate operations model — include a "Day-2" slide.

### Standard (Extend Capabilities)

**Profile:** Multi-component architecture, moderate complexity, typical enterprise engagement.

**Examples:**
- Oracle DB migration with HA/DR to ADB-S
- Multi-tier application modernization
- Hybrid cloud with FastConnect

**Characteristics:**
- 3-10 applications in scope
- 1 compliance framework (PCI, SOC2, HIPAA)
- 1-2 OCI regions
- 3-5 integration points
- Budget $10K-100K/month
- Timeline 4-12 weeks design

**Artifact depth:** Full template set. 10-12 slide deck. Separate cost spreadsheet. Operations model as 1-page summary. 4-6 ADRs.

### Complex (Business Transformation)

**Profile:** Enterprise-wide transformation, multi-region, multiple compliance, long timeline.

**Examples:**
- Full data center migration (50+ workloads)
- Multi-cloud architecture with OCI as primary
- Regulated industry platform (banking, healthcare)

**Characteristics:**
- 10+ applications in scope
- Multiple compliance frameworks
- 3+ OCI regions
- 5+ integration points
- Budget > $100K/month
- Timeline 12+ weeks design

**Artifact depth:** Full customized artifacts. 12-15 slide deck (possibly multi-deck). Full operations model. Detailed migration plan as separate document. Full risk register. Comprehensive WA report.

## Artifact Matrix

| Artifact | Small | Standard | Complex |
|----------|-------|----------|---------|
| **DEFINE** | | | |
| Value Story | 1 paragraph | Full template | Full + executive summary |
| Workload Profile | Minimal fields | Standard fields | All fields + appendix |
| Joint Engagement Plan | Email/verbal | 1-page template | Full template |
| **DESIGN** | | | |
| Slide deck | 6-8 slides | 10-12 slides | 12-15 slides |
| Architecture diagram | Single-page simple | Single-page detailed | Multi-page |
| Cost estimate | In-deck table | Separate .xlsx | Detailed .xlsx with scenarios |
| ADRs | 2-3 inline in deck | 4-6 separate | Full ADR documents |
| Migration plan | 1 slide | 2-3 slides | Separate document |
| Operations model | 1 "Day-2" slide | 1-page summary | Full template |
| Transition design | Inline in migration | Separate section | Separate document |
| Risk register | Top 3-5 in deck | Top 5-8 in deck | Full register document |
| WA scorecard | Traffic lights only | With recommendations | Full WA report |
| **DELIVER** | | | |
| Handover document | 1-page summary | Full template | Full + appendices |
| MVP definition | Inline in handover | Separate section | Phased roadmap |
| Go-live checklist | 10-15 items | 20-30 items | 30-50 items |
| Success criteria | 3-5 metrics | 5-8 metrics | 8-12 metrics |
| Lessons learned | Brief notes | Full template | Full + retrospective |

## Tier Selection Logic

Select tier based on the **highest complexity signal**. If 8 out of 10 signals say "small" but compliance says "complex", use **standard** (not complex — let the single complex dimension drive up one tier, not two).

```
IF any signal is "complex" AND 2+ signals are "complex":
  → Complex tier
ELIF any signal is "complex" OR 3+ signals are "standard":
  → Standard tier
ELSE:
  → Small tier
```
