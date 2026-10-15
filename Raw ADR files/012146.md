---
title: "Implement Observability Extensibility for Health Events"
status: "Accepted"
date: 2025-10-13
authors:
  - Platform Engineering Group
tags:
  - observability
  - health
  - adapters
---

## Status

Accepted

## Context

Unified health monitoring centralizes edge healthchecks, yet the resulting data remained trapped within local logs and command output, limiting visibility for observability teams. The observability extensibility feature defines a TypeScript event emitter, adapter interface, and configuration model so health results can stream to Prometheus, logging sinks, or future platforms without rewriting the core tooling. Establishing this extensibility aligns the edge stack with enterprise monitoring practices and enables proactive alerting.

## Decision

Adopt the health observability extensibility pattern by:

- Implementing a typed event emitter (`tools/nginx/scripts/health/events.ts`) that normalizes health results into a shared schema and dispatches them to registered adapters.
- Providing first-class adapters for Prometheus (Pushgateway/exporter) and structured logging, with retry and backoff support managed by a queue to handle transient failures.
- Externalizing configuration via `observability.config.json` (and environment variables) so operators can enable, disable, or tune adapters without code changes.
- Wiring the Nx health check task and Docker healthcheck automation to publish events through the emitter, ensuring all health workflows feed the same observability pipeline.

## Consequences

### Positive

- POS-001 — Delivers standardized health telemetry to Prometheus, logging stacks, and future adapters, enabling dashboards, alerts, and long-term trend analysis.
- POS-002 — Decouples adapter implementations from core health tooling, allowing teams to add integrations without modifying scripts or Nx targets.
- POS-003 — Improves resiliency by introducing queueing and retry policies that shield health checks from transient observability outages.

### Negative

- NEG-001 — Adds complexity to the health tooling stack; contributors must understand adapter lifecycles, configuration files, and failure handling.
- NEG-002 — Increases runtime overhead for health runs; event serialization and adapter dispatch must stay within the 5% performance budget.
- NEG-003 — Requires secure credential management for observability endpoints, raising operational diligence around secrets and access control.

## Alternatives

- ALT-001 — Leave health data local to logs and CLI output. Rejected because it offers no centralized visibility or alerting, undermining proactive operations.
- ALT-002 — Integrate directly with a single observability platform. Rejected since it locks the edge stack into one provider and complicates future integrations.
- ALT-003 — Stream data via a bespoke message bus without standardized adapters. Rejected due to additional infrastructure overhead and reduced flexibility for simple deployments.

## Implementation Notes

- IMP-001 — Define TypeScript interfaces (`HealthEvent`, `ObservabilityAdapter`) and validate configuration with `zod` to catch misconfigurations early.
- IMP-002 — Implement Prometheus and logging adapters with retry/backoff using `p-queue`, ensuring queue bounds and drop policies are configurable.
- IMP-003 — Extend the Nx health check task to emit events after each run, and optionally integrate Docker healthcheck scripts to send critical status changes.
- IMP-004 — Document adapter development guidelines, security practices for credentials, and sample observability queries within the health documentation suite.

## References

- REF-001 — docs/tools/nginx/epics/unified-health-monitoring/epic.md
- REF-002 — docs/tools/nginx/epics/unified-health-monitoring/arch.md
- REF-003 — docs/tools/nginx/epics/unified-health-monitoring/features/observability-extensibility/prd.md
- REF-004 — docs/tools/nginx/epics/unified-health-monitoring/features/observability-extensibility/implementation-plan.md
- REF-005 — docs/tools/nginx/epics/unified-health-monitoring/features/nx-health-check-task/implementation-plan.md
