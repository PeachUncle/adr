# ADR-014: Phase Definitions and Trust Gates

**Status:** Accepted
**Date:** 2026-01-02
**Decision Makers:** TechTrend Federal - Digital Twin Team
**Category:** Process
**Supersedes:** None

---

## Context

RANGER development has used the terms "demo" and "pilot" loosely, creating ambiguity around:
- What infrastructure is required for each phase
- Who the intended audience is
- What success criteria must be met before advancing
- What compliance posture applies

This ADR codifies the phase boundaries, success criteria, and trust gates that govern progression from initial validation through production deployment.

## Decision

We adopt a **four-phase deployment model** with explicit trust gates between each phase:

| Phase | Name | Duration | Audience | Data | Compliance |
|-------|------|----------|----------|------|------------|
| 0 | Foundation | Complete | Internal team | Fixtures | None |
| 1 | **Demo** | 6 weeks | Partner stakeholders | Fixtures (Cedar Creek) | None |
| 2 | **Pilot** | 8-12 weeks | 2-3 Forest Supervisors | Live IRWIN (read-only) | Research Agreement |
| 3 | Production | Ongoing | All authorized FS users | Live + Historical | FedRAMP ATO |

### Phase 1: Demo (Current)

**Objective:** Prove multi-agent coordination, Proof Layer transparency, and cross-domain synthesis work with simulated data.

**Audience:**
- TechTrend Federal internal team
- Google Cloud partner stakeholders (showcase)
- Selected USFS technical contacts (preview)

**Infrastructure:**
| Component | Status | Notes |
|-----------|--------|-------|
| Cloud Run Services | ✅ Active | ranger-console, ranger-coordinator, ranger-mcp-fixtures |
| Vertex AI RAG | ❌ Disabled | Uses embedded fixtures to avoid Spanner costs |
| Session Persistence | ❌ In-memory | No database required |
| Authentication | ❌ None / IAP | Basic protection only |

**Data:**
- Cedar Creek Fire fixtures (`data/fixtures/cedar-creek/`)
- Embedded regulatory templates (`agents/*/skills/template_lookup.py`)
- Simulated IRWIN/NIFC responses via MCP fixtures server

**Success Criteria (Trust Gate 1→2):**
| Criterion | Metric | Validation Method |
|-----------|--------|-------------------|
| Multi-agent cascade | Coordinator successfully delegates to 3+ specialists | Automated test suite |
| Proof Layer visibility | Reasoning chains render in UI with ≥3 steps | Manual QA |
| Citation accuracy | 100% of citations link to valid sources | Spot-check 10 queries |
| Cross-domain synthesis | Briefing correctly correlates burn→trail→NEPA | Scenario test |
| Export compatibility | TRACS CSV validates against schema | Unit tests |
| Performance | End-to-end briefing < 30 seconds | Load test |
| Stakeholder approval | Google Cloud partner sign-off | Demo presentation |

### Phase 2: Pilot

**Objective:** Validate that RANGER provides decision value with real incident data under controlled conditions.

**Audience:**
- 2-3 Forest Supervisors (Region 5 or 6)
- BAER team leads (as technical validators)
- USFS IT security liaison (compliance observer)

**Infrastructure:**
| Component | Status | Notes |
|-----------|--------|-------|
| Cloud Run Services | ✅ Active | Same as Demo |
| Vertex AI Search | ✅ Enabled | Pay-per-query model (avoids Spanner) |
| Session Persistence | ✅ Cloud SQL | PostgreSQL for audit trail |
| Authentication | ✅ USDA eAuth | Research agreement basis |
| Monitoring | ✅ Cloud Logging | Full audit trail |

**Data:**
- Live IRWIN incidents (read-only API access)
- NIFC perimeter feeds (current season fires)
- RAG corpus: GCS bucket with 34 Tier 1+2 documents
- User feedback logged for iteration

**Success Criteria (Trust Gate 2→3):**
| Criterion | Metric | Validation Method |
|-----------|--------|-------------------|
| Real incident triage | Supervisors complete triage in <5 min | Timed observation |
| User trust | ≥4/5 rating on "I trust the AI recommendations" | Survey |
| Decision influence | ≥50% of AI recommendations reviewed (not ignored) | Usage analytics |
| Audit trail complete | 100% of agent actions logged with timestamps | Log inspection |
| No critical errors | Zero P0 incidents during pilot window | Incident tracking |
| FedRAMP readiness | Preliminary security assessment complete | ISSO review |
| Stakeholder approval | Forest Supervisor sign-off for production | Written approval |

**Compliance Posture:**
- Operate under USDA Research Agreement (not ATO)
- No PII beyond user authentication tokens
- Data stays within GCP project boundary
- 12-month evaluation window

### Phase 3: Production

**Objective:** Scale RANGER to general availability for authorized Forest Service personnel.

**Audience:**
- All authorized USFS users (Forest Supervisors, Rangers, BAER teams)
- Adjacent agencies (BLM, NPS) via inter-agency agreements

**Infrastructure:**
| Component | Status | Notes |
|-----------|--------|-------|
| Cloud Run Services | ✅ Active | Multi-region deployment |
| Vertex AI RAG Engine | ✅ Enabled | Full corpus with 100+ documents |
| Session Persistence | ✅ Cloud SQL HA | High-availability PostgreSQL |
| Authentication | ✅ USDA eAuth + MFA | Full integration |
| Monitoring | ✅ Cloud Operations Suite | SLOs, alerting, dashboards |

**Data:**
- Full IRWIN/NIFC integration (read + write for field updates)
- Historical incident archive (10+ years)
- Real-time GEE raster integration
- Multi-incident portfolio views

**Success Criteria:**
| Criterion | Metric | Validation Method |
|-----------|--------|-------------------|
| Availability | 99.5% uptime SLO | Cloud Monitoring |
| Adoption | ≥100 active users/month | Usage analytics |
| Decision value | Documented time savings in post-fire reports | Case studies |
| Compliance | FedRAMP High ATO maintained | Annual audit |

## Rationale

### Why Four Phases?

The **Trust Hierarchy** (Data → AI → Recommendations → Behavior Change) requires progressive validation. Users must trust basic data display before accepting AI recommendations. Skipping phases breaks this progression.

### Why Research Agreement Before FedRAMP?

FedRAMP ATO is a 12-18 month process requiring significant investment. A Research Agreement provides:
- Legal basis for pilot operation
- Defined scope and duration
- Lower compliance burden during validation
- Path to ATO based on pilot learnings

### Why Embedded Fixtures for Demo?

Vertex AI RAG Engine auto-provisions Cloud Spanner (~$7/month per corpus region). For a demo that may run intermittently, this creates unnecessary costs. Embedded fixtures provide:
- Zero standing infrastructure cost
- Deterministic responses for demo repeatability
- Proof Layer compatibility (citations still work)
- Clean upgrade path to RAG in Phase 2

## Consequences

### Positive
- Clear boundaries prevent scope creep
- Trust gates enforce quality before scaling
- Cost optimization by phase
- Compliance posture appropriate to risk

### Negative
- Pilot requires USDA coordination (timeline dependency)
- FedRAMP preparation must start during Pilot (parallel workstream)
- Phase 2 infrastructure requires budget approval

### Mitigations
| Risk | Mitigation |
|------|------------|
| USDA coordination delays Pilot | Begin outreach during Demo phase |
| FedRAMP timeline exceeds 18 months | Engage FedRAMP advisor early; consider CISA FedRAMP Ready pathway |
| Pilot users reject AI recommendations | Implement "explain this" affordances; strengthen Proof Layer |

## Alternatives Considered

| Alternative | Verdict | Rationale |
|-------------|---------|-----------|
| Skip Demo, go directly to Pilot | Rejected | Insufficient validation of core functionality; risk of embarrassing failures |
| Run Demo with full RAG infrastructure | Rejected | Unnecessary cost; fixtures provide adequate validation |
| Require FedRAMP before Pilot | Rejected | 12-18 month delay; Research Agreement provides adequate compliance basis |
| Single "MVP" phase | Rejected | Conflates audience, data, and compliance requirements |

## Implementation

### Phase Transition Checklist

**Demo → Pilot:**
- [ ] All Trust Gate 1→2 criteria met
- [ ] USDA Research Agreement signed
- [ ] Pilot participants identified and briefed
- [ ] IRWIN read-only API access provisioned
- [ ] Vertex AI Search corpora created (us-west1)
- [ ] Cloud SQL instance provisioned
- [ ] eAuth integration tested
- [ ] Monitoring dashboards configured

**Pilot → Production:**
- [ ] All Trust Gate 2→3 criteria met
- [ ] FedRAMP ATO granted
- [ ] Multi-region deployment complete
- [ ] SLOs defined and monitoring active
- [ ] User documentation published
- [ ] Training program developed
- [ ] Support escalation path established

## References

- [PRODUCT-SUMMARY-COMPACT.md](../../PRODUCT-SUMMARY-COMPACT.md) — Product vision
- [ADR-005: Skills-First Architecture](./ADR-005-skills-first-architecture.md) — Core pattern
- [ADR-010: Vertex RAG Migration](./ADR-010-vertex-rag-migration.md) — RAG infrastructure
- [PROOF-LAYER-DESIGN.md](../specs/PROOF-LAYER-DESIGN.md) — Transparency requirements
- [USDA Research Agreement Template](https://www.usda.gov/agreements) — Compliance pathway

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-02 | ADR-014 accepted | Codifies phase boundaries discussed in CTO session |
| 2026-01-01 | RAG disabled for Demo | Cost optimization per billing investigation |
| 2025-12-28 | Demo phase initiated | Cedar Creek fixtures validated |
