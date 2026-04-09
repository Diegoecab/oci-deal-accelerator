# WA Review Output Format

This document defines how option 5 (Well-Architected Review) presents its results.
Referenced from `SKILL.md` § Welcome Flow → Behavior Rules → option 5.

The WA review MUST produce **two layers of output**: (a) the formatted terminal scorecard shown to the user, and (b) the structured YAML files saved to disk. The terminal output is the primary deliverable — the YAML is the backing data. Never produce YAML-only output without the formatted scorecard.

## Terminal scorecard banner

```
══════════════════════════════════════════════════════
✅ OCI WELL-ARCHITECTED REVIEW — [Customer Name]
══════════════════════════════════════════════════════
Overall: [STATUS] — X/Y checks passed
HIGH: N │ MEDIUM: N │ LOW: N
══════════════════════════════════════════════════════

[emoji] SECURITY & COMPLIANCE          X/Y passed
[emoji] RELIABILITY & RESILIENCE       X/Y passed
[emoji] PERFORMANCE & COST             X/Y passed
[emoji] OPERATIONAL EFFICIENCY         X/Y passed
[emoji] DISTRIBUTED CLOUD              X/Y passed | N/A
```

Pillar emoji: 🟢 all passed, 🟡 medium gaps only, 🔴 any HIGH gap, ⬜ N/A

## HIGH severity gaps table

Present all HIGH gaps grouped by pillar in a markdown table:

```
### HIGH severity gaps that must be addressed:

**[Pillar Name] (N HIGH)**
| ID | Gap | Fix |
|---|---|---|
| CHECK-ID | Finding description | Recommended action |
```

## MEDIUM and LOW gaps

- **MEDIUM gaps:** List as a compact bullet list grouped by pillar (ID + one-line finding + fix). Skip the table format to keep it concise.
- **LOW gaps:** Mention count only, list individual items only if ≤ 5.

## Analysis section

After the gap tables, add a "Why so many gaps?" paragraph if total gaps > 20, explaining the root cause (e.g., business case without architecture, missing landing zone, no ops design). This contextualizes the score for the SA.

## Recommended Path Forward

3-5 numbered, actionable recommendations that directly map to closing the highest-impact gaps. Reference skill options where applicable (e.g., "Generate the architecture — option 1 or 2").

## Files Generated

Always list the files saved at the end of the review:

```
📁 Files saved:
- examples/<customer>-wa-scorecard.yaml
- examples/<customer>-wa-architecture.yaml
- examples/<customer>-wa-workload-profile.yaml
```

## After WA Review menu

```
What do you want to do?
→ [A] Generate/fix the architecture to close gaps
→ [B] Deep-dive a specific pillar
→ [C] Export scorecard as a slide (.pptx)
→ [D] Re-run after changes
```

## Option [A] behavior — CRITICAL

When the user picks [A], remediate the EXISTING architecture by adding the minimum changes needed to close gaps (e.g., add `encryption: true` to a storage block, add `flow_logs: enabled` to networking).

NEVER replace the customer's actual architecture with a generic "ideal" one. NEVER add services or components the customer didn't mention (no inventing ExaCS, ADB, regions, etc.). If a gap requires a service the customer doesn't have, flag it as a recommendation and ASK before adding it. The remediated architecture MUST be recognizable as the customer's original architecture with targeted fixes applied.
