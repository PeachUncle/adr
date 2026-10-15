# ADR 007: Observability Strategy (Logs vs Metrics)

## Status
Accepted

## Context
Modern applications require comprehensive observability to diagnose issues in production. The three pillars of observability are:
1.  **Logs**: Discrete events with context (e.g., "User 123 purchased ticket 456").
2.  **Metrics**: Numerical measurements over time (e.g., "Request rate: 500 req/s").
3.  **Traces**: Request flow across services (e.g., "This request touched API → DB → Cache").

We need a strategy that handles all three pillars without creating redundant or conflicting infrastructure.

## Decision
We decided to use a **dual-stack approach**, separating logs from metrics/traces:

### Stack 1: Logs (ELK)
*   **Serilog**: Structured logging library that captures logs as JSON.
*   **Elasticsearch**: Stores logs in a searchable index (reusing the same Elasticsearch instance used for movie search).
*   **Kibana**: Provides a UI for searching, filtering, and visualizing logs.

**Use Cases**:
- Debugging specific errors ("Show me all exceptions from User 123").
- Auditing ("Who accessed the admin panel?").
- Searching text-based events.

### Stack 2: Metrics & Traces (OpenTelemetry + Prometheus + Grafana)
*   **OpenTelemetry**: Vendor-neutral instrumentation for collecting metrics and traces.
*   **Prometheus**: Time-series database optimized for numerical metrics.
*   **Grafana**: Dashboards for real-time monitoring (latency, throughput, error rates).

**Use Cases**:
- Performance monitoring ("Is the API slow right now?").
- Alerting ("Send alert if error rate > 5%").
- Capacity planning ("How many requests can we handle?").

## Alternatives Considered

### 1. ELK Stack Only (Logs + Metrics)
*   **Description**: Use Elasticsearch for both logs and metrics (via Metricbeat).
*   **Reason for Rejection**: Elasticsearch is not optimized for time-series metrics. Prometheus is purpose-built for this and has better performance and query language (PromQL) for metrics.

### 2. OpenTelemetry Only (Logs + Metrics + Traces)
*   **Description**: Send everything to a single backend (e.g., Grafana Loki for logs, Prometheus for metrics).
*   **Reason for Rejection**: We already have Elasticsearch for movie search. Reusing it for logs is efficient. Adding Loki would be redundant infrastructure.

### 3. Proprietary APM (Application Performance Monitoring)
*   **Description**: Use a vendor solution like Datadog, New Relic, or Dynatrace.
*   **Reason for Rejection**: Vendor lock-in and cost. OpenTelemetry + open-source tools provide the same capabilities without licensing fees.

## Consequences

### Positive
*   **Separation of Concerns**: Logs (text search) and Metrics (numerical analysis) use tools optimized for their respective workloads.
*   **Reuse of Infrastructure**: Elasticsearch serves dual purposes (movie search + logs), reducing operational overhead.
*   **Vendor Neutrality**: OpenTelemetry allows switching backends (e.g., from Prometheus to Datadog) without code changes.
*   **Industry Standard**: Both stacks (ELK and OpenTelemetry) are widely adopted and well-documented.

### Negative
*   **Complexity**: Developers must understand two different stacks (ELK for logs, Prometheus/Grafana for metrics).
*   **Infrastructure Overhead**: Running Elasticsearch, Prometheus, Grafana, and Kibana requires more resources than a single-vendor solution.
*   **Learning Curve**: Team must learn Kibana Query Language (KQL) for logs and PromQL for metrics.

## Implementation Notes
*   **Serilog Configuration**: Use the `Serilog.Sinks.Elasticsearch` package to send logs directly to Elasticsearch.
*   **OpenTelemetry Configuration**: Use `OpenTelemetry.Exporter.Prometheus.AspNetCore` to expose metrics at `/metrics` endpoint.
*   **Grafana Dashboards**: Create dashboards for key metrics (request rate, error rate, P95 latency).
*   **Kibana Index Patterns**: Create index patterns for application logs (e.g., `ticketeer-logs-*`).
