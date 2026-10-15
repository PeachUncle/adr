---
title: "Expose Gateway-Scoped Proxy Health Endpoints"
status: "Accepted"
date: 2025-10-13
authors:
  - Platform Engineering Group
tags:
  - nginx
  - proxy
  - health
---

## Status

Accepted

## Context

Operators previously accessed load balancer health signals by entering individual containers or running bespoke scripts, creating delays during incidents and complicating automation. The unified health monitoring epic introduces standardized load balancer health endpoints, yet without a gateway proxy surface they remain inaccessible to external tooling. The gateway proxy health endpoints feature defines secure `/health/lb-*` routes, failure semantics, logging requirements, and Nx automation so that teams can evaluate the entire edge path through a single entry point while maintaining network isolation.

## Decision

Publish gateway-exposed health routes by:

- Adding proxied locations on the edge gateway (`/health/lb-frontend`, `/health/lb-api`, `/health/lb-email`) that forward to internal load balancer endpoints with consistent timeout, retry, and error-handling policies.
- Reusing shared security snippets (IP allowlists, rate limiting, optional auth headers) to ensure the new endpoints uphold existing access controls and do not leak internal ports.
- Formatting success and failure responses as structured JSON with correlation IDs, upstream identifiers, and latency metrics so automation can parse output deterministically.
- Extending Nx automation (`health:gateway-endpoints:test`) and documentation to validate the routes during CI and provide operators with ready-to-run diagnostics.

## Consequences

### Positive

- POS-001 — Provides a single, secure vantage point for SREs and monitoring tools to assess the health of all edge load balancers without container access.
- POS-002 — Aligns response formats and latency metrics, enabling automation and pipelines to consume results consistently across environments.
- POS-003 — Enhances observability by emitting structured logs with correlation IDs, aiding incident reconstruction and trend analysis.

### Negative

- NEG-001 — Expands the gateway surface area, necessitating careful security review to prevent misuse or inadvertent exposure of internal topology details.
- NEG-002 — Introduces additional configuration that must be maintained whenever load balancer endpoints evolve, increasing documentation and testing overhead.
- NEG-003 — Adds slight processing overhead to the gateway as it proxies health traffic and formats JSON responses, which must be monitored under high check volumes.

## Alternatives

- ALT-001 — Keep health endpoints internal to each load balancer. Rejected because it forces manual container inspection and impedes automation, prolonging incident response.
- ALT-002 — Expose load balancers directly via separate ingress rules. Rejected as it fragments access control, increases attack surface, and duplicates routing logic.
- ALT-003 — Rely on out-of-band monitoring agents installed per host. Rejected due to increased operational complexity and divergence from the unified health monitoring strategy.

## Implementation Notes

- IMP-001 — Define gateway locations using shared include files and parameterized upstream maps to simplify future service additions.
- IMP-002 — Configure `proxy_connect_timeout`, `proxy_read_timeout`, and `proxy_next_upstream` values per implementation guidance and ensure failures translate to HTTP 503 responses with descriptive bodies.
- IMP-003 — Capture request metadata (`X-Request-ID`, upstream latency) in access logs and forward to the centralized logging pipeline for correlation.
- IMP-004 — Add automated tests and documentation examples that cover success, upstream failure, and timeout scenarios, keeping the health documentation suite in sync.

## References

- REF-001 — docs/tools/nginx/epics/unified-health-monitoring/epic.md
- REF-002 — docs/tools/nginx/epics/unified-health-monitoring/arch.md
- REF-003 — docs/tools/nginx/epics/unified-health-monitoring/features/gateway-proxy-health-endpoints/prd.md
- REF-004 — docs/tools/nginx/epics/unified-health-monitoring/features/gateway-proxy-health-endpoints/implementation-plan.md
- REF-005 — docs/tools/nginx/epics/unified-health-monitoring/features/docker-healthcheck-integration/implementation-plan.md
