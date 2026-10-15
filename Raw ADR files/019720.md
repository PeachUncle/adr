# ADR-001: Local Compute Decision Policy

**Status:** Accepted
**Date:** 2025-10-24
**Deciders:** Engineering Team
**Context:** 3 Computer Architecture implementation

---

## Context and Problem Statement

The Vantage Imaging System operates across three compute tiers:
- **Computer 1 (Cloud):** DigitalReality NYC + RunPod DGX
- **Computer 2 (Workstation):** RTX 6000 Pro at retail locations
- **Computer 3 (Edge):** Jetson devices + mobile

We need a **deterministic, auditable policy** to decide where each operation runs. The policy must balance:
- **Latency SLA** (real-time vs batch)
- **Privacy** (PHI must stay local unless explicitly allowed)
- **Connectivity** (retail locations may have poor uplinks)
- **VRAM constraints** (model size vs available GPU memory)
- **Cost** (cloud bursts are expensive; local compute is fixed cost)

**Without a policy:** Engineers make ad-hoc decisions, leading to PHI leaks, SLA violations, and unpredictable costs.

---

## Decision

We adopt a **"Local when sensible"** policy encoded as a pure function: `decideTarget(Context) → Target`.

### Decision Matrix

| Dimension | Edge (Jetson) | Workstation (RTX 6000 Pro) | Cloud (DGX/Colo) |
|:--|:--|:--|:--|
| **Latency SLA** | < 50 ms/frame | 50–500 ms | > 1 s (async) |
| **Connectivity** | Poor/intermittent | Good LAN | Internet required |
| **Data Sensitivity** | Raw frames stay local | PHI stays local; export by policy | De-identified features or encrypted PHI under BAA |
| **Model Size/VRAM** | Tiny (INT8/FP16 TensorRT) | Small–medium (Ollama/vLLM) | Large (multi-GPU) |
| **Compute Cost** | Low, fixed | Medium, fixed | Elastic, $$ per burst |
| **Examples** | Denoise, stabilization | VIS pose, retinal seg, QC | Fusion, training, cohort analytics |

### Five Gates

Policy evaluates per request:

1. **SLA gate:** If latency target < 500 ms and connectivity uncertain → prefer workstation
2. **Privacy gate:** If payload = raw PHI → keep on workstation; send features/masks to cloud
3. **VRAM gate:** If model > local VRAM → cloud
4. **Connectivity gate:** If uplink < 20 Mbps or jitter > 30 ms → local
5. **Cost gate:** If daily budget exceeded → local (degraded mode)

### Implementation

```typescript
// packages/policy/src/execution-policy.ts
export type Target = 'edge' | 'workstation' | 'cloud'

export interface Context {
  slaMs: number
  payloadType: 'raw_image' | 'features' | 'metrics'
  uplinkMbps: number
  jitterMs: number
  vrams: { jetson: number; workstation: number }
  model: { name: string; vramGB: number; tier: 'tiny' | 'small' | 'medium' | 'large' }
  privacy: 'phi_raw' | 'phi_masked' | 'deidentified'
  cost: { dailyGpuBudgetUsd: number; spentUsd: number }
}

export function decideTarget(ctx: Context): Target {
  // Privacy gate: raw PHI stays on workstation if SLA allows
  if (ctx.privacy === 'phi_raw' && ctx.slaMs <= 500) return 'workstation'

  // SLA gate: ultra-low latency → edge
  if (ctx.slaMs <= 50 && ctx.model.tier === 'tiny') return 'edge'

  // VRAM gate: model too large for workstation → cloud
  if (ctx.model.vramGB > ctx.vrams.workstation) return 'cloud'

  // Connectivity gate: poor uplink → local
  if (ctx.uplinkMbps < 20 || ctx.jitterMs > 30) return 'workstation'

  // Cost gate: budget exceeded → local
  if (ctx.cost.spentUsd > ctx.cost.dailyGpuBudgetUsd) return 'workstation'

  // Default: prefer workstation for interactive, cloud for async
  return ctx.slaMs <= 500 ? 'workstation' : 'cloud'
}
```

### Integration with Temporal Workflows

```typescript
// packages/workflows/src/session.workflow.ts
import { decideTarget } from '@vantage/policy'

export async function sessionWorkflow(input: { sessionId: string }) {
  const ctx = await activities.collectRuntimeContext(input)

  // Decide segmentation target
  const t1 = decideTarget({
    ...ctx,
    slaMs: 120,
    payloadType: 'raw_image',
    privacy: 'phi_raw'
  })
  await (t1 === 'workstation' ? activities.segWorkstation : activities.segCloud)(input)

  // Decide fusion target
  const t2 = decideTarget({
    ...ctx,
    slaMs: 3000,
    payloadType: 'features',
    privacy: 'deidentified'
  })
  await (t2 === 'cloud' ? activities.fuseCloud : activities.fuseWorkstation)(input)
}
```

---

## Consequences

### Positive

- **Deterministic:** Same inputs always produce same target; no surprises
- **Testable:** Pure function with zero dependencies; exhaustive unit tests possible
- **Auditable:** Policy version captured in provenance; compliance can verify decisions
- **Flexible:** Override per tenant/location via config without touching workflow code
- **Privacy-safe:** Raw PHI never leaves workstation unless explicitly allowed
- **Cost-predictable:** Budget gate prevents runaway cloud costs

### Negative

- **Context collection overhead:** Must fetch uplink speed, VRAM, budget before every decision
  - *Mitigation:* Cache context for session duration (5-60 minutes)
- **Policy complexity:** Five gates with interactions may be hard to reason about
  - *Mitigation:* Comprehensive unit tests with decision tables; ADR documents rationale
- **Stale context:** Network conditions change mid-session
  - *Mitigation:* Workflows can re-evaluate policy at step boundaries

---

## Alternatives Considered

### Alternative 1: Static Configuration ("Always cloud" or "Always local")

**Pros:** Simple; no runtime logic
**Cons:** Cannot adapt to connectivity changes, budget limits, or per-operation SLA needs

**Decision:** Rejected. Retail locations have variable connectivity; static config leads to failures.

### Alternative 2: Machine Learning-Based Placement

**Pros:** Could optimize over time based on historical data
**Cons:** Non-deterministic; hard to audit; adds ML model ops burden; overkill for 3-tier system

**Decision:** Rejected. Five explicit gates are sufficient and auditable.

### Alternative 3: Manual Developer Choice Per Activity

**Pros:** Maximum flexibility
**Cons:** Error-prone; no enforcement of privacy rules; inconsistent behavior across developers

**Decision:** Rejected. Policy must be centralized and enforced.

---

## Related Decisions

- **ADR-002:** PHI Rings and Data Minimization (defines privacy levels used in policy)
- **ADR-004:** Model Packaging as OCI Artifacts (enables VRAM metadata for decision)

---

## References

- [NVIDIA's Three Computers for Robotics](https://blogs.nvidia.com/blog/three-computers-robotics/)
- Temporal Workflows: [docs/architecture/temporal-integration.md](../temporal-integration.md)
- Development Plan: Week 2 (Policy Library Implementation)

---

**Document Version:** 1.0
**Last Updated:** 2025-10-24
**Maintained By:** Vantage Engineering
