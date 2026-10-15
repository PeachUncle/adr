---
title: "Deploy Workload-Specific Load Balancers"
status: "Accepted"
date: 2025-10-13
authors:
  - Platform Engineering Group
tags:
  - load-balancer
  - edge
  - reliability
---

## Status

Accepted

## Context

Frontend, API, and email traffic previously flowed through shared configuration, limiting workload-specific tuning and making incident isolation difficult. The dedicated load balancers feature PRD and implementation plan describe packaging separate NGINX containers for each workload with tailored caching, rate limiting, overlays, and health checks, all orchestrated via Nx. Standardizing this separation ensures predictable performance and easier scaling while keeping configurations maintainable.

## Decision

Adopt dedicated load balancers per workload by:

- Maintaining per-workload directories (`lb-frontend`, `lb-api`, `lb-email`) with Dockerfiles, base configs, and environment overlays built atop shared snippets.
- Providing Nx targets (`lb-*:build|serve|test`) that validate configuration (`nginx -t`), execute health probes, and produce structured logs labeled by workload.
- Surfacing health endpoints and metrics for each load balancer through the edge gateway, enabling consistent monitoring and alerting.
- Documenting onboarding steps so application teams can register upstreams via overlays without duplicating boilerplate.

## Consequences

### Positive

- POS-001 — Enables workload-specific tuning (caching, rate limits) without impacting other traffic classes.
- POS-002 — Simplifies incident response by isolating logs, metrics, and health checks per workload.
- POS-003 — Supports independent scaling strategies, allowing teams to add capacity or roll out changes selectively.

### Negative

- NEG-001 — Increases the number of containers to build and maintain, raising operational overhead.
- NEG-002 — Requires careful coordination to keep shared snippets compatible across all load balancers.
- NEG-003 — Adds complexity to Compose overlays and automation pipelines that must manage multiple services simultaneously.

## Alternatives

- ALT-001 — Keep a single multi-purpose load balancer. Rejected due to lack of tuning flexibility and higher blast radius during incidents.
- ALT-002 — Use a third-party load balancing service. Rejected because deployments must function in self-hosted environments without external dependencies.
- ALT-003 — Delay workload separation until a future orchestration platform migration. Rejected since current projects already require differentiated policies.

## Implementation Notes

- IMP-001 — Store configs under `tools/nginx/load-balancers/` and standardize layout (base config + overlays + shared snippets).
- IMP-002 — Ensure containers run as non-root, mount certificates read-only, and expose structured logs with `workload` labels.
- IMP-003 — Configure health endpoints (`/health`, `/metrics`) and integrate them with Nx validation scripts and monitoring dashboards.
- IMP-004 — Provide schema validation for overlays and enforce it within Nx `test` targets to prevent misconfiguration before deployment.

## References

- REF-001 — docs/tools/nginx/epics/edge-traffic-platform/epic.md
- REF-002 — docs/tools/nginx/epics/edge-traffic-platform/arch.md
- REF-003 — docs/tools/nginx/epics/edge-traffic-platform/features/dedicated-load-balancers/prd.md
- REF-004 — docs/tools/nginx/epics/edge-traffic-platform/features/dedicated-load-balancers/implementation-plan.md
- REF-005 — docs/tools/nginx/epics/edge-traffic-platform/features/shared-configuration-assets/prd.md
