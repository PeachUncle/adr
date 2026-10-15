---
title: "Standardize Let’s Encrypt Provisioning via Nx Automation"
status: "Accepted"
date: 2025-10-13
authors:
  - Platform Engineering Group
tags:
  - tls
  - automation
  - lets-encrypt
---

## Status

Accepted

## Context

Production teams previously stood up Let’s Encrypt manually, leading to divergent installation steps, missing renewal hooks, and inconsistent logging. Those discrepancies increased the risk of renewal failures and left compliance teams without verifiable records. The Let’s Encrypt automation PRD and implementation plan define scripts and Nx tasks that detect host OS, install certbot, configure HTTP/DNS challenges, schedule renewals, and trigger NGINX reloads while emitting audit-ready logs. We must endorse this automation as the canonical path for ACME enrollment across our edge footprint.

## Decision

Mandate the `tls:setup-letsencrypt` workflow for Let’s Encrypt provisioning by:

- Providing OS-aware installation and enrollment scripts that abstract package management, challenge configuration, and secrets placement behind Nx options for domain, email, and challenge type.
- Scheduling automated renewals (cron, systemd, or launchd) with post-renewal hooks that reload NGINX, emit logs, and optionally notify operators.
- Supporting both HTTP-01 and DNS-01 challenges so the same tooling functions across diverse infrastructure constraints, including air-gapped staging environments via staging endpoints.
- Logging each enrollment and renewal to centralized files for audit review and cross-linking the automation with validation and rotation workflows to ensure end-to-end coverage.

## Consequences

### Positive

- POS-001 — Ensures every production domain is provisioned and renewed consistently, reducing outages from missed or misconfigured renewals.
- POS-002 — Delivers audit-ready logs and notifications proving certificate lifecycle management compliance.
- POS-003 — Simplifies onboarding to trusted certificates, enabling teams to deploy HTTPS quickly across supported operating systems.

### Negative

- NEG-001 — Requires privileged execution environments (sudo/root) and proper credential management, increasing operational overhead on constrained hosts.
- NEG-002 — Adds maintenance cost to track certbot, ACME API changes, and host package repositories over time.
- NEG-003 — May not cover advanced scenarios (wildcard, complex DNS providers) without additional integration work, necessitating documented manual steps for edge cases.

## Alternatives

- ALT-001 — Allow teams to manage Let’s Encrypt manually following documentation. Rejected because it perpetuates inconsistent implementations and brittle renewals.
- ALT-002 — Offload certificate issuance to cloud provider managed services. Rejected since many deployments are self-hosted or air-gapped and still require first-party automation.
- ALT-003 — Purchase commercial certificates and renew manually. Rejected due to higher cost, slower issuance, and lack of automatic renewal workflows.

## Implementation Notes

- IMP-001 — Maintain `tools/nginx/scripts/tls/setup-letsencrypt.sh` with OS detection, idempotent package installs, and challenge configuration helpers for HTTP/DNS flows.
- IMP-002 — Expose Nx executor flags (`--domain`, `--email`, `--challenge`, `--staging`, `--renew-hook`) and document usage in the TLS documentation suite.
- IMP-003 — Generate renewal schedules (cron/systemd/launchd) that invoke post-renewal hooks performing `nginx -s reload` and optional validation runs.
- IMP-004 — Store issued certificates in secure directories (`tools/nginx/secrets/tls/`) with restricted permissions and maintain logs at `/var/log/letsencrypt-automation.log` or repository equivalents for dev environments.

## References

- REF-001 — docs/tools/nginx/epics/automated-tls-management/epic.md
- REF-002 — docs/tools/nginx/epics/automated-tls-management/arch.md
- REF-003 — docs/tools/nginx/epics/automated-tls-management/features/lets-encrypt-automation/prd.md
- REF-004 — docs/tools/nginx/epics/automated-tls-management/features/lets-encrypt-automation/implementation-plan.md
- REF-005 — docs/tools/nginx/epics/automated-tls-management/features/certificate-rotation-workflow/prd.md
- REF-006 — docs/tools/nginx/epics/automated-tls-management/features/tls-documentation-suite/prd.md
