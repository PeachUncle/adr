# ADR-004: Vendor Integration Strategy

**Status:** Accepted  
**Date:** January 2026  
**Author:** Liem Vo-Nguyen  
**Reviewers:** [Security Architecture Team]

---

## Context

AgentGuard addresses multiple capability domains. For each domain, we must decide whether to build custom solutions, buy/integrate vendor products, or extend existing tools.

This ADR documents the systematic build/buy/extend analysis for each capability.

## Decision Framework

### Evaluation Criteria

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Market gap | 30% | Does a solution exist that meets our requirements? |
| Core differentiator | 25% | Is this capability central to AgentGuard's value proposition? |
| Total cost of ownership | 20% | Build + maintain vs. license + integrate costs |
| Time to market | 15% | Impact on delivery timeline |
| Strategic control | 10% | Risk of vendor dependency |

### Decision Matrix

| Score | Decision |
|-------|----------|
| Build score > 70 | Build from scratch |
| Build score 50-70 | Build core, integrate edges |
| Build score < 50 | Buy/Integrate |

---

## Capability Analysis

### 1. LLM Observability

**Requirement:** Trace collection, storage, and visualization for AI agent execution.

| Criterion | Score | Rationale |
|-----------|-------|-----------|
| Market gap | 20/30 | Multiple vendors (Langfuse, LangSmith, Arize) |
| Core differentiator | 10/25 | Commodity capability, not our unique value |
| TCO | 15/20 | Significant build cost, mature OSS available |
| Time to market | 5/15 | Building delays roadmap significantly |
| Strategic control | 5/10 | OTEL standards reduce lock-in risk |

**Build Score:** 55/100  
**Decision:** **INTEGRATE** (Langfuse) + **BUILD** security enrichment layer

**Rationale:** Base telemetry is solved. Our value is security-specific signals layered on top.

---

### 2. Prompt Injection Detection

**Requirement:** Detect and block prompt injection attempts in real-time.

| Criterion | Score | Rationale |
|-----------|-------|-----------|
| Market gap | 10/30 | Lakera Guard, Rebuff, AWS Guardrails exist |
| Core differentiator | 15/25 | Important but not unique methodology |
| TCO | 8/20 | ML models expensive to train/maintain |
| Time to market | 3/15 | 6+ months to build competitive detection |
| Strategic control | 4/10 | Can swap providers if needed |

**Build Score:** 40/100  
**Decision:** **BUY** (Lakera Guard)

**Rationale:** Lakera has best-in-class detection (<50ms latency, >95% accuracy). Building ML models is not our core competency.

**Integration Architecture:**
```
User Input → AgentGuard SDK → Lakera Guard API → Score + Decision
                                    │
                              ┌─────┴─────┐
                              │           │
                         Score < 0.7   Score ≥ 0.7
                              │           │
                              ▼           ▼
                         Continue      Block + Log
```

---

### 3. Control Framework Mapping

**Requirement:** Map NIST AI RMF to NIST 800-53 and ISO 42001 with gap analysis.

| Criterion | Score | Rationale |
|-----------|-------|-----------|
| Market gap | 30/30 | No vendor provides AI-specific crosswalks |
| Core differentiator | 25/25 | Central to AgentGuard value proposition |
| TCO | 18/20 | Manual effort but no external dependencies |
| Time to market | 10/15 | Can build incrementally |
| Strategic control | 10/10 | Full ownership of methodology |

**Build Score:** 93/100  
**Decision:** **BUILD**

**Rationale:** This is our primary differentiator. No vendor has published authoritative NIST AI RMF crosswalks. We own the methodology and can update as frameworks evolve.

---

### 4. Policy Engine (Tool Access Control)

**Requirement:** Enforce policies on agent tool access, data flow, and behavior.

| Criterion | Score | Rationale |
|-----------|-------|-----------|
| Market gap | 25/30 | No agent-specific policy solutions exist |
| Core differentiator | 22/25 | Critical for enterprise governance |
| TCO | 12/20 | OPA is battle-tested, policies are custom |
| Time to market | 10/15 | OPA integration is well-documented |
| Strategic control | 8/10 | Own policies, OPA is OSS |

**Build Score:** 77/100  
**Decision:** **BUILD** policies on **OPA** (Open Policy Agent)

**Rationale:** OPA provides the engine; we build the agent-specific policy language and enforcement points. Vendor guardrails (AWS, Azure) are content-focused, not agent-behavior-focused.

---

### 5. Threat Modeling

**Requirement:** Generate threat models specific to agentic AI systems.

| Criterion | Score | Rationale |
|-----------|-------|-----------|
| Market gap | 28/30 | No AI-specific threat modeling tools |
| Core differentiator | 20/25 | Valuable but not primary value prop |
| TCO | 14/20 | Templates + engine, moderate effort |
| Time to market | 12/15 | Can leverage existing STRIDE/ATLAS |
| Strategic control | 8/10 | Own templates and methodology |

**Build Score:** 82/100  
**Decision:** **BUILD**

**Rationale:** Existing threat modeling tools (OWASP Threat Dragon, Microsoft TMT) don't address AI-specific threats. MITRE ATLAS provides taxonomy but no tooling.

---

### 6. GRC Integration

**Requirement:** Integrate with enterprise GRC platforms (ServiceNow, Archer) for risk workflows.

| Criterion | Score | Rationale |
|-----------|-------|-----------|
| Market gap | 20/30 | GRC platforms exist, AI modules don't |
| Core differentiator | 12/25 | Important for enterprise but not unique |
| TCO | 15/20 | API integration is bounded scope |
| Time to market | 12/15 | Well-documented APIs |
| Strategic control | 6/10 | Dependent on GRC vendor APIs |

**Build Score:** 65/100  
**Decision:** **EXTEND** (Build integration layer)

**Rationale:** Enterprises already have GRC investments. We build adapters that create AI-specific risk types and sync findings/exceptions.

---

### 7. Maturity Assessment

**Requirement:** Assess and benchmark organizational AI security posture.

| Criterion | Score | Rationale |
|-----------|-------|-----------|
| Market gap | 27/30 | No AI-specific maturity models exist |
| Core differentiator | 18/25 | Valuable consulting-style asset |
| TCO | 16/20 | Questionnaire + scoring engine |
| Time to market | 13/15 | Straightforward to implement |
| Strategic control | 9/10 | Full ownership of methodology |

**Build Score:** 83/100  
**Decision:** **BUILD**

**Rationale:** Creates consulting engagement opportunity. No equivalent exists for AI security maturity.

---

## Summary Decision Matrix

| Capability | Decision | Vendor/Approach | Effort |
|------------|----------|-----------------|--------|
| LLM Observability | Integrate + Build | Langfuse + custom enrichment | Medium |
| Injection Detection | Buy | Lakera Guard | Low |
| Control Mapping | Build | Custom (YAML + Go) | Medium |
| Policy Engine | Build on OPA | OPA + custom policies | Medium |
| Threat Modeling | Build | Custom (STRIDE + ATLAS) | Medium |
| GRC Integration | Extend | ServiceNow/Archer APIs | Low |
| Maturity Assessment | Build | Custom questionnaire | Low |

## Vendor Dependency Analysis

```
                         Dependency Level
                    Low ◄─────────────────► High
                    
Lakera Guard     ────●────────────────────────  (Replaceable)
Langfuse         ────────●────────────────────  (OTEL exit path)
OPA              ──────────────●──────────────  (OSS, no vendor)
ServiceNow       ────────────────────●────────  (Optional integration)
Cloud Providers  ────────────────────────●────  (Infrastructure)
```

## Cost Projections

### Year 1 (Build Phase)

| Item | Cost | Notes |
|------|------|-------|
| Langfuse Cloud | $0 | Self-hosted |
| Lakera Guard | $12,000 | ~1M requests/month |
| OPA | $0 | OSS |
| Infrastructure | $24,000 | AKS + managed services |
| Engineering | $200,000 | 1 FTE equivalent |
| **Total** | **$236,000** | |

### Year 2+ (Operate Phase)

| Item | Cost | Notes |
|------|------|-------|
| Lakera Guard | $36,000 | ~3M requests/month scale |
| Infrastructure | $48,000 | Scaled deployment |
| Engineering | $100,000 | 0.5 FTE maintenance |
| **Total** | **$184,000** | |

## Consequences

### Positive
- Focused build effort on differentiators (control mapping, policy, threat models)
- Leverage best-in-class vendors for commodity capabilities
- Reduced time-to-market by avoiding reinventing observability
- OTEL standards enable future flexibility

### Negative
- Lakera dependency for injection detection
- Must maintain integrations as vendor APIs evolve
- Split architecture increases operational complexity

### Risks

| Risk | Mitigation |
|------|------------|
| Lakera pricing increases | Abstract behind interface, maintain fallback |
| Langfuse feature gaps | Contribute to OSS or fork if needed |
| GRC API changes | Version pinning, integration tests |

## References

- [ADR-001: Observability Strategy](ADR-001-observability-strategy.md)
- [ADR-002: Control Framework Selection](ADR-002-control-framework-selection.md)
- [ADR-003: Policy Engine Selection](ADR-003-policy-engine-selection.md)
- [Lakera Guard Documentation](https://docs.lakera.ai/)
- [OPA Documentation](https://www.openpolicyagent.org/docs/latest/)
