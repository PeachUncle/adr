# ADR-0004: ROI Scoring Model Design

**Date:** 2025-12-29  
**Status:** Accepted  

## Context

When evaluating AI opportunities in regulated industries, organizations typically assess business value and technical feasibility—but regulatory complexity is often treated as a late-stage gate rather than a first-class evaluation criterion. This leads to:

- Promising projects stalled late when compliance concerns surface
- Risky projects proceeding too far without governance guidance
- No shared language between business sponsors and compliance teams

The ROI Decision Engine needs a scoring model that makes regulatory considerations visible alongside value and feasibility from day one.

## Decision

### Three Scoring Dimensions

We will evaluate AI opportunities across three dimensions:

| Dimension | What It Measures | Direction |
|-----------|------------------|-----------|
| **Business Value** | Impact on KPIs, revenue, cost, risk, CX | Higher = stronger |
| **Implementation Feasibility** | Technical complexity, data availability, effort | Higher = more feasible |
| **Regulatory Complexity** | Compliance burden, data sensitivity, controls required | Higher = more complex |

**Rationale:** Three dimensions map to the stakeholder groups providing inputs (Business, Engineering, Governance) and capture key trade-offs without overcomplicating the model.

### Configurable Weights

Weights are configurable per organization, not hardcoded.

- Default: 40% Value / 30% Feasibility / 30% Regulatory
- Organizations can adjust based on risk appetite and strategic priorities

**Rationale:** Fixed weights invite "why those numbers?" challenges. Configurability signals maturity and allows adaptation to organizational context.

### Scoring Scale

All dimensions use a 1–5 scale (Very Low → Very High).

**Rationale:** Familiar, explainable, sufficient granularity without false precision.

### Regulatory Complexity Inversion

For composite calculation, regulatory complexity is inverted (6 - score) so that lower complexity contributes positively.

**Rationale:** "Complexity" naturally reads as "more = harder." Inversion keeps math clean while preserving intuitive scoring direction.

### Declared Assumptions Philosophy

All inputs are treated as "declared assumptions, subject to review"—not ground truth.

**Rationale:** Acknowledges uncertainty, invites validation, supports governance as a partner rather than a gate.

## Consequences

**Benefits:**
- ✅ Regulatory considerations elevated to first-class status
- ✅ Shared language between business and compliance teams
- ✅ Transparent, auditable scoring rationale
- ✅ Configurable to organizational context

**Costs:**
- ⚠️ Weight configuration requires organizational alignment
- ⚠️ Some nuance lost in three-dimension reduction
- ⚠️ 1–5 scale may feel coarse to some evaluators

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Five dimensions (add Time-to-Value, Strategic Fit) | Overcomplicates MVP; can extend later |
| Fixed weights | Reduces adaptability; invites challenges |
| 1–10 scale | False precision; harder to calibrate consistently |
| Regulatory as pass/fail gate | Contradicts "governance as partner" philosophy |

## Links

- ROI Decision Engine: [`/modules/roi-engine/`](../../modules/roi-engine/)
- Sample Decision Memo: [`/modules/roi-engine/samples/ai-assisted-customer-routing/`](../../modules/roi-engine/samples/ai-assisted-customer-routing/)
- Related: [ADR-0003 - Evidence Traceability Standard](ADR-0003%20-%20Evidence%20Traceability%20Standard.md)