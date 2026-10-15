# 5. Alerting Strategy for Key Service Level Objectives

*   **Status:** Accepted
*   **Date:** 2025-11-4

## Context

With the implementation of a comprehensive observability stack (TDT-11), the EzraTask API now produces detailed metrics, logs, and traces. However, this data is currently passive. To operate the service reliably and pr
oactively, we need a formal strategy for how to use this data to alert operators of potential or actual user-impacting issues.

A common anti-pattern is to alert on *causes* (e.g., "CPU is at 80%"). This often leads to alert fatigue and may not correlate with actual user-facing problems. A more mature approach, aligned with Site Reliability Eng
ineering (SRE) principles, is to alert on *symptoms*—specifically, when the service is failing to meet its promises to users. These promises are formally defined as Service Level Objectives (SLOs).

## Decision

We will adopt an **SLO-based alerting strategy**. Our alerts will fire when user-facing metrics indicate that we are at risk of violating our defined SLOs for availability and latency. This ensures that every alert is 
meaningful, actionable, and directly related to the user experience.

## Service Level Objectives (SLOs)

Our SLOs are based on the standard metrics exposed by the OpenTelemetry ASP.NET Core instrumentation. We define separate SLOs for read and write paths to provide more granular insight into system health.

### 1. Availability SLOs

*   **Service Level Indicator (SLI):** The ratio of successful requests (HTTP status code `< 500`) to total requests, measured by the `http.server.request.count` metric.

#### 1.1. Read Availability: 99.95%
*   **Description:** Over a rolling 28-day period, 99.95% of all legitimate read requests (`GET`) should be successful.
*   **Rationale:** Users being unable to view their data is a critical outage. We set a higher target for reads as they are typically more frequent and less complex than writes.

#### 1.2. Write Availability: 99.9%
*   **Description:** Over a rolling 28-day period, 99.9% of all legitimate state-changing requests (`POST`, `PUT`, `PATCH`, `DELETE`) should be successful.
*   **Rationale:** This focuses on critical user actions that modify data. A 99.9% target allows for approximately 43 minutes of downtime per month, a reasonable starting point for a production service.

### 2. Latency SLOs

*   **Service Level Indicator (SLI):** The distribution of API request durations, measured by the `http.server.request.duration` histogram metric.

#### 2.1. Write Latency: 95% of requests < 300ms
*   **Description:** 95% of `POST`, `PUT`, and `PATCH` requests should complete in under 300ms.
*   **Rationale:** Write operations can be more complex (validation, data persistence). This target ensures a responsive feel without being overly sensitive to necessary processing time.

#### 2.2. Read Latency (Paginated List): 95% of requests < 150ms
*   **Description:** 95% of `GET /api/v1/todos` requests should complete in under 150ms.
*   **Rationale:** Listing data is a core, high-frequency operation. A snappy response is critical for the user experience.

#### 2.3. Read Latency (Singleton): 95% of requests < 100ms
*   **Description:** 95% of `GET /api/v1/todos/{id}` requests should complete in under 100ms.
*   **Rationale:** Fetching a single item should be extremely fast. This sets a high bar for a key read path.

### 3. Future Business-Level SLIs

While technical HTTP metrics are a necessary starting point, a mature observability strategy also includes custom metrics tied to business outcomes. We should plan to introduce business-level SLIs in the future.

*   **Example:** A `todo_creation_success_rate` SLO could be based on a custom metric incremented within the `TodoService` itself. This would measure whether a `201 Created` response truly resulted in a persisted item,
 protecting against subtle bugs that technical metrics might miss.

## Proposed Implementation

### Tooling

*   **Metrics Storage & Querying:** **Prometheus**. The application already exposes a `/metrics` endpoint in the Prometheus format.
*   **Alerting Logic:** **Prometheus Alertmanager**. Alertmanager will be configured with rules that query Prometheus based on our SLOs.
*   **Notification Channels:** A combination of tools for different severity levels.

### Alert Severities

We will use a multi-tiered alerting strategy based on how quickly our "error budget" (the small percentage of requests allowed to fail) is being consumed.

*   **Severity: P2 / Warning**
    *   **Trigger:** The error rate over the last hour is high enough that, if it continues, we will exhaust our 28-day error budget in 3 days.
    *   **Notification Channel:** A message to a low-priority channel (e.g., **#ezratask-alerts** in Slack).
    *   **Expected Action:** An engineer should acknowledge and begin investigating during business hours. This is not a pageable event.

*   **Severity: P1 / Critical**
    *   **Trigger:** The error rate over the last 5 minutes is so high that we will exhaust our 28-day error budget in the next 6 hours. This indicates a severe, immediate user-facing outage.
    *   **Notification Channel:** An urgent notification to an on-call rotation management tool (e.g., **PagerDuty** or **Opsgenie**). The chosen tool must support accessible notification methods (e.g., text, phone cal
l, mobile app push) to accommodate all on-call responders.
    *   **Expected Action:** The on-call engineer is paged and must immediately acknowledge and begin incident response.

### Operational Considerations

*   **Security:** The `/metrics` endpoint and the Prometheus/Alertmanager UIs expose internal operational data and must not be publicly accessible. They should be deployed within a secure network boundary (e.g., a priv
ate VNet) and protected by authentication and authorization.
*   **FinOps (Cost):** Self-hosting Prometheus and Alertmanager incurs infrastructure and operational costs. Commercial tools like PagerDuty have subscription fees. These costs must be weighed against managed cloud alt
ernatives like Azure Monitor, which trades higher direct costs for lower operational overhead. For this project, a self-hosted stack is a reasonable and cost-effective starting point.

## Validation Strategy

An alerting pipeline is a critical production system and must be treated as testable code to prevent silent failures. We will validate our alerting configuration to ensure it functions as expected before a real inciden
t occurs.

**Proposed Test:**
1.  **Setup:** Add a lightweight "test alert receiver" service to the `docker-compose.yml` environment. This service will expose an endpoint that simply logs any alerts it receives.
2.  **Test Case:** Create a new integration test suite (`AlertingTests.cs`).
3.  **Action:** The test will programmatically generate a high volume of `500` error responses from a test endpoint, deliberately breaching the Availability SLO in a short window.
4.  **Assertion:** The test will then poll the test alert receiver's endpoint to assert that the expected "P1 / Critical" alert was correctly fired by Alertmanager and received.

This approach validates the entire pipeline—from metric generation in the API, to rule evaluation in Prometheus, and finally to notification via Alertmanager—ensuring our safety net is actually in place and functional.

## Consequences

### Positive:

*   **Proactive Response:** We will be notified of problems before our users are significantly impacted.
*   **Reduced Alert Fatigue:** Every alert is tied to a user-facing SLO, making them meaningful.
*   **Data-Driven Decisions:** Provides a framework for discussing reliability and making data-informed trade-offs.
*   **Increased Confidence:** The validation strategy ensures our alerting system is reliable.

### Negative:

*   **Implementation Overhead:** Requires setting up and maintaining a Prometheus and Alertmanager stack. This is a standard and acceptable cost for operating a production service.
