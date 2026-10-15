# ADR-001: Grounding Status over Confidence Scores

**Status:** Accepted  
**Date:** 2025-01-05  
**Deciders:** Steve (PM)  
**Context:** Compliance Retrieval Assistant — Module 4 of Regulated AI Workflow Toolkit

---

## Context

The Compliance Retrieval Assistant generates answers based on retrieved passages from an approved corpus. Before returning a response, the system must communicate to users how trustworthy the answer is — specifically, whether the answer is supported by the source material.

Two approaches were considered:

1. **Confidence Score** — Return a numeric value (e.g., 0.87) representing model confidence
2. **Grounding Status** — Return a categorical status (FULLY_GROUNDED, PARTIALLY_GROUNDED, REFUSED)

This decision has significant implications for:
- User trust and behavior
- Audit defensibility
- Compliance review
- Support escalations

---

## Decision

**We will use categorical Grounding Status, not numeric confidence scores.**

Every response includes one of three statuses:

| Status | Meaning |
|--------|---------|
| `FULLY_GROUNDED` | All claims are supported by retrieved passages |
| `PARTIALLY_GROUNDED` | Some claims are supported; unsupported portions are explicitly marked |
| `REFUSED` | Cannot provide a grounded answer; refusal code explains why |

Confidence scores are **not** exposed to users or included in responses.

---

## Rationale

### 1. Numeric confidence invites unproductive debate

A score of 0.87 immediately prompts:
- "Why not 0.92?"
- "Is 0.87 good enough to act on?"
- "What's the threshold?"

These questions have no good answers. The number creates false precision and shifts focus from "Is this grounded?" to "Is this number high enough?"

### 2. Categorical status is audit-defensible

When a regulator asks "Why did the system provide this answer?", we can respond:

> "The answer was FULLY_GROUNDED — every claim maps to a citation from the approved corpus, version v2025.01.06."

This is defensible. Explaining why a confidence score was 0.87 vs 0.82 is not.

### 3. Grounding is verifiable; confidence is not

Grounding status can be independently verified:
- Check each claim against its citation
- Confirm the citation exists in the corpus
- Validate the passage supports the claim

Confidence scores emerge from model internals (logprobs, attention weights) and cannot be independently verified or audited.

### 4. Users need actionable signals, not probabilities

Users in regulated environments need to know:
- Can I trust this answer? → **FULLY_GROUNDED**
- Should I verify something? → **PARTIALLY_GROUNDED** (with specific warnings)
- Do I need to escalate? → **REFUSED** (with guidance on next steps)

A numeric score doesn't map cleanly to any action.

### 5. Partial grounding is more useful than a lower score

When some claims can be grounded but others cannot, `PARTIALLY_GROUNDED` with explicit warnings is more useful than a middling confidence score. The user knows exactly which parts to trust and which parts need verification.

---

## Consequences

### Positive

- **Simpler user experience** — Clear, actionable status instead of ambiguous numbers
- **Audit-ready** — Every status is explainable and verifiable
- **No threshold debates** — Removes "what confidence is good enough?" discussions
- **Consistent behavior** — Same criteria applied to every response

### Negative

- **Less granularity** — We cannot express "barely grounded" vs "strongly grounded" within a category
- **Engineering complexity** — Requires robust grounding validation logic rather than simply exposing model outputs
- **Potential for edge cases** — Borderline cases must be handled by threshold configuration

### Mitigations

- `policy-constraints.yaml` defines grounding thresholds that can be tuned
- `PARTIALLY_GROUNDED` status with explicit warnings handles borderline cases
- Evaluation scorecard monitors grounding quality over time

---

## Alternatives Considered

### Alternative A: Expose confidence scores alongside grounding status

**Rejected.** This gives users two conflicting signals. If grounding is FULLY_GROUNDED but confidence is 0.72, what should the user do? Mixed signals create confusion and undermine trust.

### Alternative B: Use confidence scores with defined thresholds

**Rejected.** Thresholds (e.g., >0.8 = high confidence) still require explaining what the number means. They also create cliff effects where 0.79 and 0.81 are treated very differently despite being nearly identical.

### Alternative C: Show confidence scores only to internal users

**Rejected.** Creates two different user experiences and risks information leaking to contexts where it's misinterpreted. Simpler to have one consistent approach.

---

## Related Artifacts

- [docs/response-contract.md](../docs/response-contract.md) — Defines the grounding_status field
- [config/policy-constraints.yaml](../config/policy-constraints.yaml) — Grounding thresholds
- [architecture/component-design.md](../architecture/component-design.md) — Grounding Checker component
- [evaluation/scorecard.md](../evaluation/scorecard.md) — Grounding Integrity dimension

---

## References

- Internal design discussions
- Enterprise RAG deployment patterns in regulated industries
- Model Risk Management (SR 11-7) documentation requirements