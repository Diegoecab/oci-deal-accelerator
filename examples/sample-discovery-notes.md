# Discovery Call — Banco Pacífico (fake name) — 2024-11-14

Attendees: Maria (SA), Jorge (CTO), Ana (DBA lead), Mike (infra mgr)
45 min call, mostly Jorge talking

---

## Current State (what I could gather)

- 3x Oracle 19c databases on Exadata X8M on-prem
  - largest one is ~4TB, OLTP workload (core banking txns)
  - second is ~1.2TB — reporting/analytics, runs batch overnight
  - third is smaller, ~300GB, "auxiliary services" — Jorge was vague here ??
- GoldenGate replication between prod and DR site (San Jose DC)
- Ana mentioned 99.95% availability SLA — "contractual, can't go lower"
- PCI DSS compliance — mandatory, they process card transactions
- ~~2 RAC nodes~~ correction: 3 RAC nodes on the big DB, 2 on the others

## Licensing / Cost

- current Oracle licensing spend ~$2M/year  (Jorge said "around two million, maybe a bit more")
- they have 8 processor licenses — BYOL eligible??  need to confirm with Oracle LMS
- Mike mentioned support renewal coming up in Q2 — leverage point
- also paying for GoldenGate licenses separately, didn't get the number

## App Tier

- WebLogic 14c — 6 bare metal servers (BM)
  - running core banking APIs + some internal portals
  - ~~Java 8~~ Java 11 actually, Ana corrected
- MQ Series for async messaging between services
  - how tightly coupled?? need to dig into this
- some .NET stuff too but "not critical" per Mike

## Peaks & Performance

- seasonal peaks — Black Friday is 3x normal traffic
  - "el último Black Friday casi nos tumba" — Jorge
  - need autoscaling story for this
- end of month batch processing also heavy
- latency requirements: <50ms for API responses (p99)

## Team & Skills

- 2 Oracle DBAs — Ana + one other person
  - NO cloud experience, "nunca hemos tocado la nube"
  - will need training / enablement plan
  - Ana seemed nervous about ADB automation — "qué pasa si algo sale mal?"
- 6 app developers, mostly Java
- 1 infra person (Mike) who does "everything else"

## Timeline & Competition

- el CTO quiere migrar en 6 meses  ("Jorge: necesitamos estar en cloud antes de julio")
  - aggressive but not impossible if we start in Dec
  - phased approach? non-critical DB first??
- COMPARING WITH AWS — they got an Aurora pitch last week
  - Jorge: "AWS nos ofreció créditos pero no sé si Aurora aguanta nuestro workload"
  - we need to counter with BYOL savings + Exadata compatibility story
  - also mention: ADB on Exadata = same engine, zero refactoring

## Key Concerns (verbatim from Jorge)

1. "No quiero downtime en la migración"  — zero downtime migration, GG + ADB
2. "¿Pueden garantizar el mismo performance?" — need benchmarks
3. Cost — wants to see TCO comparison vs staying on-prem vs AWS
4. Security — "el regulador nos audita cada trimestre"
5. What happens to our GoldenGate investment?

## My Notes / TODO

- [ ] build TCO model: on-prem vs OCI (BYOL) vs AWS (Aurora)
- [ ] architecture diagram: ADB-S with ADG for HA + cross-region DR
- [ ] check if MQ Series → OCI Streaming is feasible or if they need to keep MQ
- [ ] training plan for Ana's team — OCI certs? hands-on workshop?
- [ ] ~~ask about Kubernetes~~ — Mike confirmed they're interested in OKE
- [ ] get exact GoldenGate version — need 21c for full ADB integration
- [ ] PCI compliance mapping — OCI compliance docs
- [ ] set up reference call with similar banking customer?

## Random bits

- Jorge keeps mentioning "el board quiere resultados rápidos"
- they had a failed Azure POC last year — "mala experiencia" — don't bring it up
- Ana asked about autonomous features — "¿se parchea solo de verdad?"
  she seemed skeptical but interested
- DR site is 500km away — FastConnect already in both DCs?? need to check
- budget: Jorge hinted at $1.5M first year target — doable with BYOL

---

Next steps: follow-up call Thursday, bring pricing estimate + draft architecture
