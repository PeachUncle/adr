# ADR-0005: Logging, Monitoring & Observability

## Status
Accepted

## Date
2025-11-17

## Context
PolyShop consists of distributed microservices that must be monitored, traced, and logged consistently.

Observability requirements:
- Trace requests end-to-end (auth → gateway → product → order → payment → notification)
- Correlate logs using a shared request ID
- Monitor health and performance
- Detect failures early (payment issues, inventory inconsistencies)
- Provide dashboards for analytics, ops, and engineering teams

A unified observability strategy is required.

---

# Decision

PolyShop adopts a **standardized observability stack**:

- **Logs** → Loki
- **Metrics** → Prometheus
- **Dashboards** → Grafana
- **Tracing** → OpenTelemetry (OTel) + Jaeger
- **Correlation ID** → `X-Request-Id` header passed across services
- **Context propagation** → OTel instrumentation in all services

All services follow the same structure.

---

# 1. Logging Standard

## 1.1 Format
Use **JSON logs**, not plain text.

Each log entry must contain:
- timestamp
- level
- service name
- requestId
- thread
- message
- additional fields (context)

Example:

```json
{
  "timestamp": "2025-11-17T10:38:22Z",
  "level": "INFO",
  "service": "order-service",
  "requestId": "e91bdb3c-95ec-4629-b1f1-1e7d485344af",
  "message": "Order created",
  "orderId": "12345"
}
````

## 1.2 Request ID Injection

Every service uses the shared `RequestIdFilter`:

* Extract `X-Request-Id` if provided
* Generate one if missing
* Set in MDC
* Add to response header

---

# 2. Metrics (Prometheus)

Each service exposes metrics under `/actuator/prometheus`.

Categories:

* JVM metrics
* HTTP server metrics
* Request latency
* Error counts
* Business metrics (orders created, payments processed)

Prometheus scrapes:

```
http://{service}:port/actuator/prometheus
```

Dashboards in `/monitoring/grafana/dashboards/`.

---

# 3. Distributed Tracing (OpenTelemetry)

### Mandatory instrumentation:

* Microservices instrumented using OTel SDK
* Gateway automatically creates root span
* Trace context propagated using W3C standard headers:

    * `traceparent`
    * `tracestate`

Traces flow:

```
Gateway → Service A → Service B → Database / Kafka
```

### Jaeger backend

* Collects spans
* Offers service dependency maps
* Offers timing heatmaps

Stored under:

```
/monitoring/jaeger/
```

---

# 4. Log Aggregation (Loki)

### Each service logs to stdout.

Kubernetes collects logs with Promtail.

Promtail pushes logs → Loki.

Use Grafana to query via:

```
{ service = "product-service" }
```

---

# 5. Alerting

Alerts defined in:

```
/monitoring/alerts/prometheus-alerts.yaml
```

Key alerts:

* High error rate
* Increased payment failures
* Order Saga stuck in a state
* 5xx spikes in gateway
* Kafka consumer lag growing too much

Notifications sent via:

* Email
* Slack
* SMS (via notification-service)

---

# 6. SLO / Error Budgets

Each service maintains:

* **99.9% uptime** (gateway, auth, order, payment)
* **99.5% uptime** (search, analytics)
* **Error budget alerts** if exceeded

---

# Alternatives Considered

### 1. Elastic Stack (ELK)

Rejected — more heavy & costly.

### 2. Cloud vendor monitoring (AWS CloudWatch)

Rejected — PolyShop must remain cloud-portable.

### 3. No tracing (logs only)

Rejected — microservices without traces are hard to debug.

---

# Consequences

### Positive

* Complete observability pipeline
* Faster debug cycles
* Strong operational visibility
* Distributed tracing simplifies issue triage

### Negative

* Additional infrastructure to manage
* Higher initial complexity
* Requires instrumentation discipline

---

## Final Decision

PolyShop will use:

* Loki for logs
* Prometheus for metrics
* Grafana for dashboards
* OpenTelemetry for tracing
* Jaeger for trace storage & visualization

This ensures a complete observability solution across all microservices.
