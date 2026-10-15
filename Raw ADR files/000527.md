# ADR-002: Judge–AKG Responsibility Boundary

**Date**: 2025-12-28
**Status**: Accepted
**Owner**: AiGov Architecture Team
**Decision Type**: One-Way Door

---

## Context

The AIGov evaluation system uses two AI-powered components:
1. **Judge**: Evaluates transcripts and produces compliance verdicts
2. **AKG (Autonomous Knowledge Graph)**: Provides legal context and article interpretations

As we scale to production (Phase 2), we need clear boundaries between these components to ensure:
- **Accountability**: Who owns the final verdict?
- **Auditability**: Can we trace how legal context influenced decisions?
- **Governance**: How do we validate and update each component independently?

Without clear boundaries, we risk:
- Verdict disputes ("Was it the judge or the knowledge graph that made this call?")
- Untraceable decisions (black-box AI stacking)
- Governance paralysis (can't update AKG without re-validating all judges)

---

## Decision

We establish the following **responsibility boundary**:

### 1. Judge Owns the Verdict
- **Judge responsibility**: Final verdict (VIOLATED | COMPLIANT | UNDECIDED)
- **Judge output**: behaviour_json_v1 with confidence scores, reasoning, and evidence
- **Judge accountability**: All judgements are traceable to specific judge model version
- **Constraint**: Judge MUST NOT defer verdict to AKG (no "ask the knowledge graph" logic)

### 2. AKG Provides Grounding Context (Read-Only)
- **AKG responsibility**: Legal article text, interpretations, and precedents
- **AKG output**: Context snippets included in `akg_context` field of behaviour_json_v1
- **AKG constraint**: MUST NOT produce verdicts or confidence scores
- **AKG role**: "Library" not "decision-maker"

### 3. Judge-AKG Interface Contract
```json
{
  "akg_context": {
    "Art.5(1)(f)": {
      "title": "Integrity and confidentiality",
      "text": "Personal data shall be processed in a manner...",
      "interpretation": "Healthcare providers must implement strict access controls..."
    }
  }
}
```
- **Judge queries AKG**: Provide context for article X
- **AKG response**: Text + interpretation (no verdict)
- **Judge uses context**: Incorporate into reasoning, maintain verdict ownership

### 4. Audit Trail Requirements
- **Judge manifest**: MUST include AKG version used (if any)
- **behaviour_json_v1**: MUST include `akg_context` field showing what context was provided
- **Provenance chain**: run_manifest → judge_manifest → akg_version
- **Third-party review**: Can verify judge verdict against AKG context provided

**One-Way Door Notice**:
> This is a **one-way door** decision. Once implemented, reverting would require:
> - Re-judging all historical runs (verdicts may change if responsibility shifts)
> - Breaking audit trail (provenance chain assumes verdict ownership model)
> - Client contract violations (L2 reports reference this boundary in annexes)
> - Regulatory non-compliance (some jurisdictions require clear AI decision ownership)

---

## Consequences

### Positive Consequences
- **Clear accountability**: Judge owns verdict, AKG owns legal context
- **Independent validation**: Can validate AKG quality separately from judge quality
- **Regulatory compliance**: Clear AI decision ownership (required by EU AI Act drafts)
- **Audit trail**: Full traceability from context to verdict
- **Governance flexibility**: Can update AKG without re-validating judge (context-only changes)

### Negative Consequences / Tradeoffs
- **Judge complexity**: Judge must synthesize AKG context (can't defer to "knowledge graph decides")
- **Duplication risk**: Judge and AKG may have overlapping legal reasoning
- **Interface cost**: Every judge call requires AKG context lookup (latency + API cost)

### Risks
- **Risk**: Judge ignores AKG context (defeats purpose of integration)
  - **Mitigation**: Validate judge reasoning includes AKG citations (automated check)

- **Risk**: AKG context biases judge too strongly (context = verdict)
  - **Mitigation**: Test judge with contradictory AKG context to ensure independence

- **Risk**: Audit trail breaks if AKG version not recorded
  - **Mitigation**: Judge manifest validation enforces AKG version field (fail-closed)

---

## Alternatives Considered

### Option A: AKG Owns Verdict (Judge as Scorer)
**Pros**:
- Centralizes legal reasoning in one place (AKG)
- Judge becomes simpler (just confidence scoring)

**Cons**:
- No AI accountability (knowledge graph isn't a "decider")
- Violates EU AI Act high-risk system requirements (need clear decision maker)
- Can't validate AKG independently (verdicts embedded in graph)

**Rejected because**: Regulatory non-compliance, no clear accountability

### Option B: Judge and AKG Co-Own Verdict (Ensemble)
**Pros**:
- Best of both worlds (judge + AKG agreement = high confidence)
- Robustness through redundancy

**Cons**:
- What happens when they disagree? (need tie-breaker logic)
- Double the cost (two AI calls per verdict)
- Unclear accountability (who owns the final decision?)

**Rejected because**: Governance complexity, cost prohibitive, unclear accountability

### Option C: Judge-Only (No AKG)
**Pros**:
- Simplest architecture
- Clear accountability (judge owns everything)

**Cons**:
- Judge must memorize all legal context (expensive, error-prone)
- No grounding in canonical legal text (hallucination risk)
- Can't update legal interpretations without re-training judge

**Rejected because**: Doesn't leverage structured legal knowledge, higher error rate

---

## Implementation Plan

### Phase 2.1: Define AKG Context Schema
1. Document `akg_context` field schema in data-contracts-v0.2.md
2. Add validation rules (required fields, text length limits)
3. Create test fixtures with known AKG context

**Timeline**: 1 week
**Dependencies**: Phase 2 artefact model complete

### Phase 2.2: Update Judge to Use AKG Context
1. Modify judge system prompt to incorporate AKG context
2. Add AKG version to judge manifest
3. Validate judge reasoning cites AKG context

**Timeline**: 2 weeks
**Dependencies**: AKG integration endpoint available

### Phase 2.3: Audit Trail Validation
1. Add automated check: judge_manifest includes akg_version
2. Add automated check: behaviour_json_v1 includes akg_context
3. Update L2 report template to show AKG context used

**Timeline**: 1 week
**Dependencies**: Phase 2.2 complete

**Rollback Plan**: N/A (one-way door; no rollback)

---

## Validation Criteria

This decision will be considered successful if:
- ✅ 100% of judgements include `akg_context` field (no missing context)
- ✅ Judge manifest includes `akg_version` for all runs
- ✅ Third-party auditors can trace verdict reasoning to AKG context provided
- ✅ AKG context updates don't require judge re-validation (independence verified)
- ✅ Zero verdict disputes due to unclear ownership (accountability clear)

**Review date**: 2026-03-01 (after 3 months of production use)

---

## References

- [Phase 2 system overview](../specs/phase2-system-overview-v0.1.md)
- [Offline judgement spec](../specs/phase2-offline-judgement-v0.1.md)
- [Data contracts v0.1](../specs/data-contracts-v0.1.md) (behaviour_json_v1 schema)
- [AKG project](../../projects/akg/)
- EU AI Act high-risk system requirements (Article 13)

---

## Approval

This is a **one-way door** decision and requires approval from:

- [x] Architecture Lead: @aigov_arch (approved 2025-12-28)
- [x] Engineering Lead: @aigov_eng (approved 2025-12-28)
- [x] Legal Counsel: @aigov_legal (approved 2025-12-28)
- [x] AKG Team Lead: @aigov_akg (approved 2025-12-28)

**Final Status**: Accepted (2025-12-28)
