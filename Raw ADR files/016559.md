# 008: Observability Strategy using OpenShift Built-in Monitoring and Logging

*   **Status:** Proposed
*   **Date:** 2025-09-05

## Context and Problem Statement

As a demo application running on OpenShift 4.18, the project requires a straightforward way to monitor application health, view logs, and perform basic troubleshooting. The solution should prioritize simplicity and leverage platform-native features to avoid unnecessary complexity and setup time.

## Decision Drivers

*   The need to minimize configuration and deployment overhead for a demo environment.
*   The desire to leverage the robust, pre-existing tools provided by the OpenShift platform.
*   The requirement for basic, essential observability (metrics and logs) without the need for advanced features like distributed tracing.

## Considered Options

*   **OpenShift Built-in Stack:** Rely on the default Prometheus for metrics (scraped via `ServiceMonitor`) and the default OpenShift Logging stack (Loki) for log aggregation from container `stdout`.
*   **Deploy a Custom Observability Stack:** Manually deploy and configure a separate Prometheus, Grafana, and Loki stack. This is unnecessary overhead for a demo.
*   **Integrate with an External Platform:** Configure agents to ship logs and metrics to an external SaaS platform. This is overly complex and costly for the scope of a demo.

## Decision Outcome

Chosen option: **"OpenShift Built-in Stack"**. We will standardize on using the built-in OpenShift observability capabilities. All application components running on the cluster will be configured to:
1.  Expose metrics in a Prometheus-compatible format. A `ServiceMonitor` resource will be created to ensure these metrics are automatically scraped by the default in-cluster Prometheus.
2.  Write all logs in a structured (JSON) format to `stdout`. This allows the OpenShift Logging stack to automatically collect, parse, and index the logs for viewing in the OpenShift console.

This decision explicitly defers the implementation of more advanced observability patterns like distributed tracing, as they are not required for the demo.

### Positive Consequences

*   **Rapid Implementation:** No additional components need to be installed or configured, leveraging what the platform already provides.
*   **Zero Overhead:** No additional software to manage, secure, or pay for.
*   **Sufficient for Demo:** Provides the essential metrics and logging needed to validate the application's behavior and troubleshoot issues during the demo phase.

### Negative Consequences

*   **Not Production-Ready:** This approach may not be sufficient for a production environment, which might require longer data retention, more sophisticated alerting, and distributed tracing.
*   **Limited Customization:** We are limited to the features and configuration of the default OpenShift stack.
*   If the project moves to production, this ADR will need to be revisited.
