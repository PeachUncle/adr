# ADR-0008: Centralized Logging & Distributed Tracing

## Status
Accepted

## Date
2025-11-17

## Context
PolyShop is a distributed microservices system with:
- Java Spring Boot services
- Node.js (Payment)
- Python (Notification / Analytics)
- API Gateway
- Kafka event-driven flows

Debugging across services requires:
- Centralized logs
- Correlation IDs
- Distributed tracing
- Support for high-volume traffic
- Standard formatting for analysis

A unified logging and tracing standard is needed.

---

# Decision

PolyShop uses a unified **OpenTelemetry-based** observability strategy.

Components:

1. **Centralized logging**
2. **Distributed tracing**
3. **Correlation ID propagation**
4. **Structured JSON log format**
5. **Service-level log enrichment**
6. **Trace export to Jaeger / Tempo / OTLP collector**

---

# 1. Logging Standard

### Format
All services log exclusively in **structured JSON**.

Example log entry:
```json
{
  "timestamp": "2025-01-17T12:00:00Z",
  "level": "INFO",
  "service": "order-service",
  "traceId": "abc-123",
  "spanId": "def-456",
  "requestId": "xyz-789",
  "message": "Order created",
  "metadata": {
    "orderId": "123",
    "userId": "987"
  }
}
````

### Requirements

* No plain text logs
* No console formatting
* Mandatory fields: timestamp, level, service, message
* Optional metadata allowed

### Java Implementation

Spring Boot:

* Logback with JSON encoder (Logstash encoder)
* RequestIdFilter injects MDC values

### Node.js (Payment)

* Pino logger with pino-http
* Inject requestId and traceIds

### Python (Notification/Analytics)

* Structlog with OpenTelemetry instrumentation

---

# 2. Correlation ID Strategy

PolyShop uses:

* `X-Request-Id` for external correlation
* `traceId` and `spanId` from OpenTelemetry

Rules:

1. Gateway generates requestId if missing from client.
2. All services must forward:

    * `X-Request-Id`
    * W3C trace context headers:

        * `traceparent`
        * `tracestate`
3. All Kafka events include:

    * `context.traceId`
    * `context.requestId`

---

# 3. Distributed Tracing

PolyShop uses **OpenTelemetry SDKs** for:

* Java
* Node.js
* Python

### Exporters

Preferred exporters:

* Jaeger
* Grafana Tempo
* OTLP (Collector)

Tracing requirements:

* Every inbound HTTP request creates a new trace or joins existing one
* Every outbound HTTP call creates a span
* Kafka produce/consume creates spans
* DB operations traced with auto-instrumentation

Example trace:

```
Client → Gateway → Auth-Service → Order-Service → Inventory-Service → Payment-Service
```

---

# 4. Log Aggregation

Logs are shipped via:

* Fluent Bit → Loki (primary)
* Optional Elasticsearch

### Log Structure Keys

```
timestamp
severity
service
environment
requestId
traceId
userId (optional)
message
metadata.*
```

### Retention policy

* Application logs: 7–30 days
* Audit logs: 1 year minimum

---

# 5. Service-Level Enrichment

Each service attaches its own metadata:

* `orderId` for Order Service
* `productId` for Product Service
* `paymentId` for Payment Service
* `eventType` for Kafka handlers
* `email` / `userId` for Auth Service

Enrichment must not:

* Expose passwords
* Expose tokens
* Log PII or secrets

---

# 6. Alternatives Considered

### 1. Zipkin

Rejected: legacy, limited features.

### 2. Vendor-locked services (Datadog / New Relic)

Rejected: costs + lock-in.

### 3. No structured logs

Rejected: impossible to debug at microservice scale.

---

# Consequences

### Positive

* Full service-to-service traceability
* Faster debugging
* Scalable with Grafana stack
* Cloud-neutral architecture

### Negative

* Slight overhead from instrumentation
* More storage needed for logs

---

# Final Decision

PolyShop uses:

* **OpenTelemetry for tracing**
* **Structured JSON for logs**
* **X-Request-Id + W3C Trace Headers** for correlation
* **Centralized aggregation** using Loki or Elasticsearch

This observability foundation supports all future scaling and debugging needs.
