# ADR 0002: Retry and Timeout Policy

- Status: Accepted
- Date: 2025-09-06
- Authors: Aimless
- Deciders: Aimless
- Tags: reliability, timeouts, retries, streaming, observability

## Context

llm-fiber targets high-throughput, predictable interactions with multiple LLM providers while keeping the core small and async-first. Reliability controls (timeouts and retries) must:

- Bound latency deterministically (no surprise hangs).
- Avoid duplicating side effects or double-billing.
- Preserve streaming UX (low TTFB, ordered chunks).
- Remain provider-agnostic with small, clear hooks for customization.
- Feed observability with stable metrics and logs.

The library already defines:
- An explicit `Timeouts(connect, read, total)` type.
- A retry hook (`retry_if(exc, attempt, ctx)`) for classification overrides.
- Typed exceptions with provider/model/attempt metadata.

We need a single, concrete policy to ship as the default and to document how it interacts with streaming, budgets, and idempotency.

## Decision

Adopt a conservative, bounded, jittered exponential retry policy coupled with explicit, three-part timeouts:

1) Timeouts (applied to all calls)
- Use `Timeouts(connect, read, total)` with the following defaults unless overridden:
  - connect: 5s
  - read: 30s
  - total: 30s
- Per-call overrides via `timeout_s: float | Timeouts` are supported.
- Semantics:
  - connect bounds connection establishment.
  - read bounds inter-byte/chunk silence (especially relevant to streaming).
  - total bounds the complete call lifecycle across all attempts, including streaming.

2) Retry Policy (non-streaming and pre-stream phases)
- Max attempts: 4 (1 initial + up to 3 retries).
- Backoff: capped exponential with full jitter.
  - base_backoff_ms: 200
  - cap_backoff_ms: 2000
  - delay for attempt n (n ≥ 2): random_uniform(0, min(cap, base * 2^(n-2))).
- Classification (retryable):
  - HTTP 429 (rate limited).
  - HTTP 5xx (server errors).
  - Transient network errors (DNS, connect, reset).
  - Connect/handshake timeouts.
  - Read timeouts occurring before streaming started.
- Classification (non-retryable):
  - Auth errors (401, 403, provider-specific auth failures).
  - 4xx request errors (malformed request, quota exceeded that’s not transient).
  - Provider explicit denials or safety blocks reported as non-transient.
  - Read timeouts after streaming has already begun (see “Streaming”).
- The `retry_if(exc, attempt, ctx)` hook may override classification:
  - Return True/False to force a decision; return None to defer to defaults.

3) Streaming-specific Behavior
- No mid-stream automatic retries. Once the first `chunk` is emitted, the library will not attempt to reconnect or replay automatically. Reasons:
  - Prevent duplicate partial outputs or broken ordering.
  - Avoid hidden cost/billing duplication.
- Read timeouts mid-stream are treated as terminal errors (raise).
- If applications require “resume” semantics, they must implement an application-level protocol with idempotent tools and explicit re-entry points.

4) Idempotency
- Pass `idempotency_key` through to providers that support it.
- Retries are performed only pre-stream for calls with idempotency keys. This prevents duplicated side effects.
- Mid-stream retry is never automatic, even with idempotency keys.

5) Total Timeout Budget
- The `total` timeout bounds the entire call, including retries and any streaming time.
- Backoff delays and network time all consume the `total` budget.
- When the total budget expires, raise `FiberTimeout` with metadata for provider/model/attempt.

6) Defaults Are Configurable
- Client-level defaults (timeouts, max attempts, backoff base/cap) are configurable at construction.
- Per-call overrides: `timeout_s`, and optionally `max_attempts` if exposed.
- The `retry_if` hook provides controlled customization without forking policy.

7) Observability (stable schema)
- Metrics:
  - request_count{provider,model,ok}
  - error_count{provider,model,code}
  - retry_count{provider,model,reason}
  - latency_ms histogram (end-to-end)
  - ttfb_ms histogram (streaming only)
- Logs:
  - Include attempt, backoff_ms, reason, error_kind, http_status (where applicable).
  - Bind context (e.g., run_id, tenant_id) flows into logs/metrics.

## Rationale

- Predictability: Three-part timeouts plus a hard total cap are straightforward to reason about and tune.
- Safety: Pre-stream retries and idempotency support prevent duplicated side effects while still handling transient errors.
- Streaming UX: Avoiding mid-stream retry preserves ordering and output integrity and eliminates silent duplication risk.
- Simplicity: Full-jitter exponential backoff is robust and low-ceremony; classification rules map cleanly from provider behaviors.
- Extensibility: The `retry_if` hook allows teams to refine behavior without bloating the core with per-provider quirks.

## Consequences

Positive:
- Deterministic upper bound on call time with clear failure modes.
- Good default resilience for transient faults (429/5xx/network).
- Streaming semantics remain simple and trustworthy (no hidden replays).
- Stable observability enables SLOs for latency/TTFB/retries/errors.

Negative:
- No automatic mid-stream recovery; applications that require it must build higher-level protocols.
- Some transient mid-stream failures could succeed under a complex replay scheme, but we intentionally avoid that complexity and ambiguity.

## Details

Classification Table (summary)
- Retryable:
  - HTTP: 429, 5xx
  - Network: DNS failure, connection refused/reset, TLS handshake transient
  - Timeout: connect timeout; read timeout pre-stream
- Non-retryable:
  - HTTP: 400, 401, 403, 404 (unless provider docs classify some as transient)
  - Provider-specific: explicit “invalid request”, “invalid key”, “quota exhausted permanently”
  - Timeout: read timeout post-first-chunk
- Hook:
  - `retry_if(exc, attempt, ctx)` can override per exception.
  - ctx includes provider, model, bound context (e.g., run_id), stream flag.

Backoff Parameters (defaults)
- base_backoff_ms: 200
- cap_backoff_ms: 2000
- max_attempts: 4
- jitter: full jitter
- These defaults are intended for typical SaaS LLM latencies; adjust in high-throughput or highly constrained environments.

Timeouts (defaults)
- connect: 5s
- read: 30s
- total: 30s
- The library will not exceed total even when retries are still “allowed”.

Streaming
- First emitted `chunk` marks TTFB and flips the “streaming-started” flag.
- Any read timeout after that is terminal (no retry).
- Cancellation by caller is respected (break loop; no final `usage` guaranteed).

Idempotency
- If `idempotency_key` is provided and supported by the provider, it is attached to the request.
- Retries remain pre-stream only. The key reduces risk of duplicated billing or server-side effects on retried attempts.

Budgets Interaction
- Budgets (token or cost ceilings) are enforced independently of retries/timeouts.
- Preflight checks may abort before any attempt if ceilings cannot be met.
- Mid-stream budget termination is terminal (no automatic retry).

## Alternatives Considered

1) Mid-stream automatic retries and merging deltas
- Pros: Might recover transient drops.
- Cons: Complex, provider-specific, risks duplicated output or subtle corruption; unclear cost semantics. Rejected.

2) Fixed (non-jittered) backoff
- Pros: Simpler.
- Cons: Herding and contention under bursts; worse fairness. Rejected.

3) Single “overall” timeout only
- Pros: Simpler mental model.
- Cons: Hard to distinguish between connect/read constraints; less actionable tuning. Rejected.

4) Aggressive retry of all 4xx except auth
- Pros: Masks some provider inconsistencies.
- Cons: Risks hammering providers on permanent client errors; wastes budget. Rejected.

## Compatibility and Migration

- The policy codifies behavior already described in the README and feature docs.
- If future provider guidance suggests narrower/wider retry classes, we will evolve defaults conservatively, preserving the `retry_if` escape hatch for early adopters.

## Observability

- Ensure `retry_count{reason}` includes reasons such as rate_limit, http_5xx, timeout_connect, timeout_read, network.
- Log entries should include attempt index, chosen backoff_ms, and final decision (retry/stop).
- Maintain stable names for `latency_ms`, `ttfb_ms`, and error codes for dashboards and alerting.

## How We Will Measure Success

- Reduced tail latency due to bounded timeouts and backoff.
- Lower error rates after transient spikes due to controlled retries.
- No incidents of duplicated outputs reported due to mid-stream replays (by design).
- Clear, actionable metrics and logs in post-incident analysis.

## References

- Project README: Retries and budgets section.
- Docs: docs/features/retries-and-budgets.md, docs/features/streaming.md, docs/features/observability.md.
- “Exponential Backoff And Jitter”: AWS Architecture Blog (guidance for jitter strategies).
