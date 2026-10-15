---
title: "Standardize Docker Healthchecks for Edge Containers"
status: "Accepted"
date: 2025-10-13
authors:
  - Platform Engineering Group
tags:
  - docker
  - health
  - nginx
---

## Status

Accepted

## Context

Edge gateway and load balancer containers did not define consistent Docker `HEALTHCHECK` instructions, forcing operators to rely on ad hoc scripts and manual probing. Without standardized checks, orchestrators could not automatically recycle unhealthy replicas, and health telemetry diverged from the unified monitoring endpoints introduced by the unified health monitoring epic. The Docker healthcheck integration feature specifies reusable scripts, configurable thresholds, and Compose overlays that align container health semantics with the gateway proxy endpoints, providing a cohesive resilience story across environments.

## Decision

Adopt the standardized Docker healthcheck pattern by:

- Shipping a shared `health-check.sh` script that exercises the unified health endpoints and exits non-zero when checks fail, with support for environment-controlled timeouts and endpoint overrides.
- Embedding `HEALTHCHECK` directives in gateway and load balancer Dockerfiles that invoke the shared script and expose configurable intervals, retries, and failure thresholds.
- Updating Compose overlays and Nx automation to surface health status (`docker compose ps`, `health:docker`) and validate healthcheck execution as part of CI and integration testing.
- Logging context-rich failures from the script so operators can triage failing endpoints without attaching to running containers.

## Consequences

### Positive

- POS-001 — Enables orchestrators to restart unhealthy NGINX edge containers automatically, reducing mean time to recovery during incidents.
- POS-002 — Provides a single, reusable healthcheck implementation that stays in lockstep with gateway health endpoints, minimizing duplication across services.
- POS-003 — Surfaces health results in build pipelines and local workflows, giving engineers fast feedback before promoting images to higher environments.

### Negative

- NEG-001 — Increases image build complexity by copying scripts and maintaining additional Dockerfile directives that must remain compatible across base images.
- NEG-002 — Introduces the risk of false positives if health thresholds are tuned too aggressively, potentially causing unnecessary container restarts until configuration is calibrated.
- NEG-003 — Requires ongoing maintenance of the shared script to accommodate new endpoints, authentication requirements, or platform differences (e.g., BusyBox vs. GNU utilities).

## Alternatives

- ALT-001 — Continue relying on manual `curl` commands or ad hoc scripts per service. Rejected because it keeps orchestrators unaware of container state and perpetuates inconsistent health semantics.
- ALT-002 — Depend on orchestrator-specific probes defined outside Docker images. Rejected since the platform must support multiple deployment targets and benefits from embedding defaults directly in images for portability.
- ALT-003 — Integrate third-party monitoring agents to report container health. Rejected due to additional licensing, footprint, and divergence from the unified health monitoring design.

## Implementation Notes

- IMP-001 — Store the shared script at `tools/nginx/proxy-edge/scripts/health-check.sh`, enforce shell linting, and document supported flags and environment variables.
- IMP-002 — Update gateway and load balancer Dockerfiles to copy the script and define `HEALTHCHECK` commands with overridable `INTERVAL`, `TIMEOUT`, and `RETRIES` arguments.
- IMP-003 — Extend Compose overlays and Nx targets (e.g., `health:docker`) to verify the health status post-build, capturing logs for CI artifacts.
- IMP-004 — Provide integration tests that simulate unhealthy endpoints and assert containers transition to an `unhealthy` state within expected thresholds.

## References

- REF-001 — docs/tools/nginx/epics/unified-health-monitoring/epic.md
- REF-002 — docs/tools/nginx/epics/unified-health-monitoring/arch.md
- REF-003 — docs/tools/nginx/epics/unified-health-monitoring/features/docker-healthcheck-integration/prd.md
- REF-004 — docs/tools/nginx/epics/unified-health-monitoring/features/docker-healthcheck-integration/implementation-plan.md
- REF-005 — docs/tools/nginx/epics/unified-health-monitoring/features/gateway-proxy-health-endpoints/prd.md
