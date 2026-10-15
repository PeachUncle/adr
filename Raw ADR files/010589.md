# ADR 0004: Observability Schema and Exporters

- Status: Accepted
- Date: 2025-09-06
- Authors: Aimless
- Deciders: Aimless
- Tags: observability, metrics, logging, tracing, exporters, schema, compatibility

## Context

llm-fiber is designed to be thin, fast, and observable. The library must expose stable, useful metrics and logs that let engineers understand latency, throughput, reliability, and cost across multiple providers and models. Streaming introduces additional timing and lifecycle signals (notably TTFB). Different teams and stacks prefer different backends: OpenTelemetry (OTel) for traces/metrics, StatsD/DogStatsD for metrics, and Python stdlib logging or structlog for logs.

A clear, stable “observability schema” is needed:
- Metric names and label (tag) sets that are consistent across providers and versions.
- Span names and attributes for OTel that correlate with logs and metrics.
- Logging fields that help correlate requests and debug failures without leaking secrets.
- Guardrails for label cardinality and PII/secret redaction.
- A compatibility policy for changes to avoid breaking dashboards and alerts.

The library should ship with always-on in-memory metrics and optional exporters via extras. It must not force heavy dependencies in core.

## Decision

Define a stable, minimal observability schema for metrics, logs, and traces, and ship optional exporters via extras. The schema is provider-agnostic and streaming-aware, and it favors additive evolution after v1.

### 1) Metrics (names and labels)

Emit the following metrics per call (non-streaming and streaming). Always-on in-memory; optionally export to OTel or StatsD/DogStatsD.

- request_count{provider, model, ok, stream?}
  - Counter. Incremented once per completed request (streaming or not).
  - ok: "true" | "false"
  - stream: "true" | "false" (optional label; present where supported)

- error_count{provider, model, code, stream?}
  - Counter. Incremented once per errored request.
  - code: normalized error category (e.g., "timeout", "rate_limited", "auth", "http_5xx", "http_4xx", "parse_error", "budget_exceeded")

- retry_count{provider, model, reason}
  - Counter. Incremented per retry attempt.
  - reason: "rate_limit", "http_5xx", "timeout_connect", "timeout_read", "network", "other"
  - Populated only when a retry occurs.

- latency_ms{provider, model, stream?}
  - Histogram. End-to-end latency of the call (request→final response or stream termination).
  - Units: milliseconds.

- ttfb_ms{provider, model}
  - Histogram. Time-to-first-byte for streaming calls, measured from request start to first `chunk`.
  - Only emitted for streaming.

- tokens_in{provider, model}
  - Counter (or per-call gauge in some backends). Number of prompt tokens consumed, when known.

- tokens_out{provider, model}
  - Counter (or per-call gauge). Number of completion tokens produced, when known.

- tokens_total{provider, model}
  - Counter (or per-call gauge). tokens_in + tokens_out, when known.

- estimated_cost_usd{provider, model}
  - Gauge (one measurement per call). Estimated USD cost when pricing and usage are known.

- cache_hit_count{provider, model, policy} (when cache is enabled)
  - Counter. Count of cache hits.
  - policy: "read_through" | "write_through" | "off" (if present)

- cache_miss_count{provider, model, policy} (when cache is enabled)
  - Counter. Count of cache misses.

- cache_write_count{provider, model}
  - Counter. Successful writes to cache.

- cache_evict_count{adapter}
  - Counter. Evictions due to TTL or capacity (adapter-specific).

Label set constraints
- Required small-cardinality labels only: provider, model, ok/code/reason, stream, policy, adapter.
- No per-request unique IDs as labels.
- Bound context fields (e.g., run_id, tenant_id) DO NOT become metric labels by default. They may appear in tracing/logging, but not metrics, unless explicitly allowlisted by the host app (off by default).

Emissions
- Tokens and cost are emitted when available (provider usage and pricing known). If unknown, metrics are omitted rather than guessed.
- For StatsD backends that lack histograms, use timing or distribution equivalents where possible (implementation detail).

### 2) Logging (fields and levels)

Use stdlib logging by default; support structlog when provided. Logs are structured, concise, and redact secrets.

Typical fields:
- level: INFO on success, WARN on retry, ERROR on failure
- event: "chat_call", "chat_stream", "retry", "error"
- provider, model
- request_id: per-call correlation ID (short, random)
- attempt, total_attempts (on retry) and backoff_ms
- stream: true|false
- latency_ms and ttfb_ms (when streaming)
- finish_reason (normalized) when available
- tokens_in, tokens_out, tokens_total, estimated_cost_usd (when available)
- error_kind (e.g., FiberTimeout, FiberRateLimited, FiberAuthError, FiberAPIError, FiberParsingError)
- http_status (if relevant)
- message: short, actionable description

Context binding:
- Fields bound via `fiber.bind(...)` (e.g., run_id, tenant_id, request_id) are included in logs.
- Redaction is applied where necessary (keys/secrets); avoid logging raw prompts/responses by default.

### 3) Tracing (OpenTelemetry spans and attributes)

When OTel is configured and the extra is installed, emit spans and metrics with stable names and attributes.

Span model:
- Root span per call: "llm_fiber.chat" (non-streaming) or "llm_fiber.chat_stream" (streaming).
- Attributes (representative):
  - llm.provider: "openai" | "anthropic" | "gemini" | custom
  - llm.model: model name (e.g., "gpt-4o-mini")
  - llm.request_id: per-call correlation ID
  - llm.stream: bool
  - llm.finish_reason: normalized finish reason, when available
  - llm.tokens.in, llm.tokens.out, llm.tokens.total (ints, when available)
  - llm.cost.estimated_usd (float, when available)
  - app.run_id, app.tenant_id, etc. from bind() as attributes (optional)
- Events:
  - "retry" with attributes: attempt, reason, backoff_ms
  - "first_chunk" marks TTFB on streaming
  - Errors recorded with status and exception info

Sampling:
- Tracing sampling is configured by the host application (OTel SDK). The library does not impose sampling.

### 4) Schema compatibility policy

- Pre-v1: best-effort stability; breaking changes possible with release notes.
- v1+:
  - Metric names and label keys are stable. Adding new metrics or labels is allowed; removing/renaming requires a major version.
  - Logging field names are stable; adding fields is allowed; removing/renaming requires a major version.
  - Span names and core attributes are stable; adding attributes is allowed; removing/renaming requires a major version.
- Deprecated elements:
  - Mark as deprecated in release notes and docs for at least one minor release before removal in the next major.
- No schema version label is added to metrics to avoid cardinality inflation. Changes are communicated via SemVer and CHANGELOG.

### 5) Exporters and dependencies

- Core:
  - Always-on in-memory metrics.
  - Stdlib logging; redaction on by default.
- Optional extras:
  - "otel": opentelemetry-api, opentelemetry-sdk, opentelemetry-exporter-otlp
  - "statsd": statsd (DogStatsD compatible)
  - "structlog": structlog integration
- The library detects initialization at runtime (e.g., OTel tracer/meter) and annotates accordingly. If not configured, operation continues with in-memory metrics and stdlib logging.

### 6) Cardinality and PII guidance

- Cardinality:
  - Labels limited to provider, model, ok/code/reason, stream, policy, adapter; avoid high-cardinality values.
  - Bound context fields are not metric labels by default; they appear in logs/traces.
- PII/Secrets:
  - Never log secrets (API keys redacted).
  - Avoid logging raw prompts/responses by default in production.
  - Allow users to configure additional redaction or field allowlists as needed.
- Sampling:
  - Use logging/tracing sampling at the host app level if needed.
  - Metrics remain counters/histograms with bounded label sets.

### 7) Streaming semantics

- ttfb_ms emitted only for streaming; measured at first `chunk`.
- latency_ms measures end-to-end, including streaming.
- On cancellation: iterator ends; final `usage` may not be available; emit partial logs/spans; metrics reflect termination without usage.
- If usage/cost not reported by provider for streamed responses, usage and estimated cost are omitted.

## Rationale

- Stable, minimal schema ensures portability and predictable dashboards across providers.
- Optional exporters avoid bloating core and allow teams to choose their stack (OTel vs StatsD).
- Clear cardinality rules prevent metric blow-ups; context belongs in logs/traces, not metric labels.
- Streaming-aware signals (TTFB) reflect user experience for token delivery.
- Compatibility policy aligned with SemVer encourages additive evolution and predictable upgrades.

## Consequences

Positive:
- Easy integration with common observability stacks (OTel, Datadog/StatsD) without heavy core deps.
- Clear SLOs: p95 latency_ms, p99 ttfb_ms, error and retry rates.
- Safe-by-default logs (redaction) and bounded metrics cardinality.

Negative:
- No per-request metrics labeling by default; correlation relies on logs/traces.
- Some backends lack true histograms; implementations must adapt (timing/distribution).

Mitigations:
- Allow host apps to map selected bound fields to metric labels via explicit allowlists (off by default).
- Provide examples and guidance for OTel and StatsD wiring in docs.

## Alternatives Considered

1) Native Prometheus client in core
- Rejected to avoid adding a hard runtime dependency and to keep a single metric emission surface compatible with multiple backends.

2) Rich per-request labels (run_id/request_id) on metrics
- Rejected due to cardinality explosion risks; logs/traces are better suited for this.

3) Trace-only, no metrics
- Rejected; metrics are fundamental for SLOs and alerting. Traces complement metrics.

4) No ttfb_ms
- Rejected; TTFB is critical to streaming UX and should be measured.

## Migration

- Pre-v1: update dashboards as metrics/labels stabilize; track changes in CHANGELOG.
- Post-v1: expect additive changes only; breaking changes require a major version bump.

## Observability Testing

- Unit tests for metric emission on success, error, retries, streaming TTFB.
- Contract tests ensure names/labels remain stable across releases.
- E2E smoke with mock providers: verify logs/spans, TTFB, latency, and error categorization.

## References

- Docs: docs/features/observability.md
- Related ADRs:
  - ADR-0002 Retry and Timeout Policy
  - ADR-0003 Model Registry and Routing
- OTel best practices for attributes and events
- AWS Architecture Blog on jittered backoff (for retry signals)
