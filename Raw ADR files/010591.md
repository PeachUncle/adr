# ADR-0002: vLLM Memory Model Assumptions

Date: 2025-09-05

## Status

Accepted

## Context

The v1 calculator must estimate per-GPU VRAM usage for locally hosted vLLM deployments. Accuracy hinges on the KV cache formula, how tensor parallel (TP) shards weights and KV, how multiple deployments share GPUs, and how safety headroom is modeled. We also need to decouple weight dtype from KV cache dtype and account for partially replicated parameters.

## Decision

- Decouple dtypes:
  - Weights dtype: bf16/fp16 (2B), fp32 (4B), q8≈1B, q4≈0.5B (weight quant optional in v1 UI).
  - KV cache dtype: bf16/fp16 (2B), fp8/int8 (1B).
- GQA-aware KV formula:
  - `headDim = hiddenSize / heads`
  - `kvBytesPerTokPerGpu = 2 × layers × numKeyValueHeads × headDim × bytesPerKvElem(kvDtype) / tp × (1 + kvOverheadPct)`
- Weights per-GPU (with replication overhead):
  - `weightBytesPerGpu = (paramsB×1e9 × bytesPerParam(weightDtype) / tp) × (1 + replicationOverheadPct)`
  - Default `replicationOverheadPct = 0.02` (2%).
- Budget per GPU with headroom and reserve:
  - `budgetBytesPerGpu = utilization × capacityBytes − reserveBytes`
  - Default `utilization = 0.90` (adjustable [0..1]), default `reserveBytes = 2 GB`.
- Overlapping deployments:
  - Allow multiple deployments to share GPUs. Per-GPU used memory is the sum of all deployments’ weights and KV on that GPU.
- Suggestions for vLLM flags per deployment d on GPU g:
  - `max_model_len = floor(budgetLeft / (kvPerTok_dg × numSeq))`
  - `max_num_seqs = floor(budgetLeft / (kvPerTok_dg × modelLen))`
  - where `budgetLeft = max(budgetBytesPerGpu − Σ_d weights_dg, 0)`.

## Alternatives Considered

- Single “dtype” for both weights and KV: simpler but unrealistic; rejected.
- Disallow GPU sharing across deployments: simpler visualization, but not representative of real multi-model colocations; rejected.
- Exact paged-attention block accounting: higher fidelity, but requires loader specifics; deferred to v2.

## Consequences

- The domain layer needs model metadata with `numKeyValueHeads` and must expose separate dtypes for weights vs KV.
- The app must aggregate per-GPU usage across deployments and run fit checks at the GPU level.
- UI bars must segment by deployment and component (weights/KV/reserve/unallocated/free).
- Defaults (U=0.90, reserve=2GB, replication=2%) provide conservative sizing and are configurable.

## Follow-up

- Extend model catalog to include `numKeyValueHeads` for GQA-aware sizing.
- Add validations: `tp ≤ assignedGpuIds.length`; warn when mixed GPU capacities are used within a TP group.
- Add unit tests covering formula sanity checks and overlapping deployment aggregation.
