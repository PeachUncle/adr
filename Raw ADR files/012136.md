---
title: "Institute Certificate Validation Pipeline Guardrails"
status: "Accepted"
date: 2025-10-13
authors:
  - Platform Engineering Group
tags:
  - tls
  - validation
  - compliance
---

## Status

Accepted

## Context

Before TLS automation, engineers distributed certificates without consistent checks for key alignment, SAN coverage, file permissions, or impending expiry. This gap created production outages when mismatched pairs were deployed and left auditors without evidence that controls were enforced. The certificate validation feature PRD and implementation plan describe an Nx-exposed pipeline that validates cryptographic integrity, permission hygiene, and policy thresholds while emitting JSON reports suitable for CI and compliance review. We need an authoritative decision to make this pipeline a mandatory guardrail across environments.

## Decision

Adopt the certificate validation pipeline as a standard control by:

- Shipping `tls:validate-certs` Nx automation that orchestrates an OpenSSL-backed script to check modulus alignment, SAN coverage, signature algorithms, and file permissions for every certificate bundle before release.
- Emitting structured JSON and human-readable reports stored under repository artifacts so CI pipelines and auditors can consume the same evidence.
- Enforcing configurable warning thresholds (default 30 days) and failing builds when certificates are expired, mismatched, or non-compliant with permission standards.
- Integrating the validation run into pre-deployment workflows and documenting remediation guidance so teams resolve findings before promotion.

## Consequences

### Positive

- POS-001 — Prevents production outages caused by mismatched or expired certificates by failing builds ahead of deployment.
- POS-002 — Supplies machine-readable audit artifacts that demonstrate adherence to TLS governance without manual paperwork.
- POS-003 — Raises developer confidence by providing actionable remediation guidance and consistent formatting across local and CI contexts.

### Negative

- NEG-001 — Adds execution time to build pipelines, especially when scanning large certificate directories.
- NEG-002 — Requires ongoing maintenance of validation rules and JSON schemas as cryptographic standards evolve.
- NEG-003 — Demands OpenSSL (and optionally `jq`) availability in every execution environment, increasing setup complexity for lightweight containers.

## Alternatives

- ALT-001 — Rely on manual review checklists for certificate integrity. Rejected because human inspection is error-prone and does not scale across environments.
- ALT-002 — Defer validation to downstream load balancers or cloud-managed services. Rejected because self-hosted and air-gapped deployments still need first-party assurance before distribution.
- ALT-003 — Build a centralized certificate inventory service that performs validation. Rejected due to higher operational overhead and latency compared with portable scripts embedded in the monorepo.

## Implementation Notes

- IMP-001 — Maintain `tools/nginx/scripts/tls/validate-certs.sh` with idempotent checks, leveraging modulus comparisons and permission audits.
- IMP-002 — Version the JSON report schema and persist artifacts to `tools/nginx/scripts/tls/reports/` for CI downloads; include run IDs and timestamps.
- IMP-003 — Provide Nx executor flags (`--path`, `--warn-days`, `--output`) and document usage patterns in the TLS documentation suite.
- IMP-004 — Add Bats-based unit tests and snapshot coverage to guard against regressions in script behavior.

## References

- REF-001 — docs/tools/nginx/epics/automated-tls-management/epic.md
- REF-002 — docs/tools/nginx/epics/automated-tls-management/arch.md
- REF-003 — docs/tools/nginx/epics/automated-tls-management/features/certificate-validation-pipeline/prd.md
- REF-004 — docs/tools/nginx/epics/automated-tls-management/features/certificate-validation-pipeline/implementation-plan.md
- REF-005 — docs/tools/nginx/epics/automated-tls-management/features/tls-documentation-suite/prd.md
