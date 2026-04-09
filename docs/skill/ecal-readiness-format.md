# ECAL Readiness Scorecard Format

This document defines how option 12 (ECAL Readiness Score) presents its results.
Referenced from `SKILL.md` § Welcome Flow → Behavior Rules → option 12.

## Scoring model

Each artefact has a status: ✅ Complete | 🟡 Partial | ❌ Missing | ⬜ Not Applicable (future phase).

Phase scores are calculated as:
- ✅ = 1.0 point, 🟡 = 0.5 point, ❌ = 0 points, ⬜ = excluded from denominator
- Phase score = (sum of points / applicable artefacts) × 100%

Overall ECAL Readiness = weighted average:
- DEFINE: 25% weight
- DESIGN: 50% weight (largest phase, most artefacts)
- DELIVER: 25% weight

## Readiness levels

- 🟢 80-100% — Ready to proceed to next phase
- 🟡 60-79%  — Gaps exist but manageable; proceed with caution
- 🟠 40-59%  — Significant gaps; address before proceeding
- 🔴 0-39%   — Major gaps; phase needs substantial work

## Output format

The ECAL readiness score MUST produce **two layers of output**: (a) the formatted terminal scorecard shown to the user, and (b) the structured YAML file saved to disk. The terminal output is the primary deliverable — the YAML is the backing data. Never produce YAML-only output without the formatted scorecard.

```
══════════════════════════════════════════
📊 ECAL READINESS SCORECARD
══════════════════════════════════════════
Customer: [name]
Date: [date]
Current Phase: [DEFINE/DESIGN/DELIVER]
Overall Readiness: [XX%] [emoji level]

── DEFINE (Ideate → Validate → Plan) ──
Score: XX% [emoji]
✅ Value Story
✅ Workload Profile
🟡 Customer Profile (partial — missing Oracle footprint)
❌ Strategy Map
❌ Joint Engagement Plan
⬜ Business Case (revisited in Confirm)

── DESIGN (Current → Future → Confirm) ──
Score: XX% [emoji]
[artefact list with status...]

── DELIVER (Adopt → Operate → Improve) ──
Score: XX% [emoji]
[artefact list with status...]

── TOP 5 GAPS ──
1. ❌ [artefact] — [why it matters] — [recommended action]
2. ...

── RECOMMENDED NEXT ACTIONS ──
1. [specific action]
2. [specific action]
3. [specific action]

── ENGAGEMENT RACI CHECK ──
Roles identified: [list]
Roles missing: [list]
══════════════════════════════════════════
```

## Files generated

Always list the files saved at the end of the scorecard:

```
📁 Files saved:
- examples/<customer>-ecal-scorecard.yaml
```

## After ECAL scorecard menu

```
What do you want to do?
→ [A] Fix the top gap now (I'll generate the missing artefact)
→ [B] Generate all missing artefacts for current phase
→ [C] Export scorecard as a slide (.pptx)
→ [D] Re-score after updates
```
