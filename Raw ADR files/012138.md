---
title: "Enforce TLS Compose Overlay and Hardened NGINX Snippets"
status: "Accepted"
date: 2025-10-13
authors:
  - Platform Engineering Group
tags:
  - tls
  - nginx
  - security
---

## Status

Accepted

## Context

Edge services historically copied TLS configuration piecemeal, resulting in inconsistent cipher suites, missing security headers, and unsecured certificate mounts. Those variations lowered SSL Labs scores and complicated audits. The TLS Compose overlay feature PRD and implementation plan define reusable NGINX snippets and Docker Compose overlays that mount certificates read-only, enable HTTPS by default, and codify hardened headers alongside validation tasks. We need a binding decision to standardize all edge deployments on this overlay pattern.

## Decision

Harden edge deployments by adopting the shared TLS Compose overlay and snippet library:

- Provide curated snippets (`tls.conf`, `headers.conf`, `logging.conf`) that enforce modern TLS protocols, OCSP stapling, HSTS, and structured logging, included consistently across proxy and load balancer containers.
- Ship Docker Compose overlays that bind HTTPS ports, configure secure volume mounts, redirect HTTP to HTTPS, and expose health checks invoked via Nx validation tasks.
- Expose Nx commands (`nginx-edge:enable-tls`, `nginx-edge:test-https`) that apply overlays, run `nginx -t`, and execute SSL scanning to confirm hardened posture.
- Document override mechanisms so teams can extend headers or ciphers while inheriting secure defaults, and ensure overlays integrate with certificate generation and rotation outputs.

## Consequences

### Positive

- POS-001 — Delivers consistent, high-grade TLS posture across environments, improving audit outcomes and external scan ratings.
- POS-002 — Simplifies HTTPS activation for application teams with a single overlay command, reducing configuration drift.
- POS-003 — Encourages automated validation through Nx tasks, catching misconfigurations before deployment.

### Negative

- NEG-001 — Requires teams to align on standardized snippets, potentially constraining bespoke edge cases that need divergent TLS policies.
- NEG-002 — Adds Compose complexity and may lengthen container startup when running additional validation steps like `testssl.sh`.
- NEG-003 — Demands ongoing maintenance to keep snippets aligned with evolving best practices and newly discovered vulnerabilities.

## Alternatives

- ALT-001 — Allow each team to craft bespoke NGINX configuration. Rejected because it reintroduces configuration drift and weak security defaults.
- ALT-002 — Depend solely on infrastructure-as-code templates outside the monorepo. Rejected since many services rely on Docker Compose locally and need consistent defaults in-repo.
- ALT-003 — Integrate TLS settings directly into application-specific Compose files. Rejected to avoid duplication and ensure updates propagate centrally.

## Implementation Notes

- IMP-001 — Store snippets under `tools/nginx/common/snippets/` and reference them via `include` directives within overlay configs; lint with `nginx -t` during CI.
- IMP-002 — Maintain `docker-compose.tls.yaml` overlays that mount certificate directories read-only, configure environment variables, and expose HTTPS ports for each edge service.
- IMP-003 — Provide Nx executors for enabling the overlay and running validation (`nginx-edge:enable-tls`, `nginx-edge:test-https`) including optional SSL scan integrations.
- IMP-004 — Document activation steps, environment variables, and troubleshooting guides within the TLS documentation suite, ensuring teams understand override patterns.

## References

- REF-001 — docs/tools/nginx/epics/automated-tls-management/epic.md
- REF-002 — docs/tools/nginx/epics/automated-tls-management/arch.md
- REF-003 — docs/tools/nginx/epics/automated-tls-management/features/tls-compose-overlay/prd.md
- REF-004 — docs/tools/nginx/epics/automated-tls-management/features/tls-compose-overlay/implementation-plan.md
- REF-005 — docs/tools/nginx/epics/automated-tls-management/features/automated-development-certificates/prd.md
- REF-006 — docs/tools/nginx/epics/automated-tls-management/features/certificate-rotation-workflow/prd.md
- REF-007 — docs/tools/nginx/epics/automated-tls-management/features/tls-documentation-suite/prd.md
