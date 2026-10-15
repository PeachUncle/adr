---
title: "Publish Edge Operational Documentation Suite"
status: "Accepted"
date: 2025-10-13
authors:
  - Platform Engineering Group
tags:
  - documentation
  - operations
  - edge
---

## Status

Accepted

## Context

Operational knowledge for the edge platform was scattered across outdated READMEs and ad hoc notes, slowing incident response and complicating audits. The edge operational documentation feature PRD and implementation plan specify a cohesive set of guides—README, quick start, runbook, validation manual, and changelog—with diagrams, troubleshooting checklists, and Nx command references. Formalizing this documentation creates a reliable source of truth for running the edge stack.

## Decision

Establish the edge operational documentation suite by:

- Authoring core documents (`README.md`, `QUICKSTART.md`, `RUNBOOK.md`, `VALIDATION.md`, `CHANGELOG.md`) under `tools/nginx/docs/`, each linking to relevant Nx targets, scripts, and configuration directories.
- Incorporating architecture and operational diagrams (Mermaid) alongside decision trees for incident handling, validated during documentation builds.
- Enforcing markdown linting, broken-link checks, and review workflows so content stays accurate and accessible.
- Integrating the documentation with the Next.js portal to provide searchable, accessible guidance for platform, SRE, and application teams.

## Consequences

### Positive

- POS-001 — Reduces mean time to resolution by giving SREs runbooks and verification steps tailored to the edge stack.
- POS-002 — Improves onboarding by guiding engineers through deployment, validation, and troubleshooting workflows with tested commands.
- POS-003 — Strengthens audit readiness with documented procedures, changelog history, and references to log locations.

### Negative

- NEG-001 — Requires ongoing governance, including content reviews and changelog maintenance, to keep documentation current.
- NEG-002 — Adds build time for linting and diagram compilation in CI pipelines.
- NEG-003 — Demands coordination with tooling updates to prevent drift between documentation and automation.

## Alternatives

- ALT-001 — Continue relying on scattered notes and inline script help. Rejected due to inconsistency and poor discoverability.
- ALT-002 — Use an external wiki separate from the repository. Rejected because it disconnects documentation from versioned code changes and complicates review.
- ALT-003 — Produce minimal documentation limited to READMEs. Rejected since runbooks and validation guides are critical for operations and compliance.

## Implementation Notes

- IMP-001 — Store diagrams in `tools/nginx/diagrams/`, render via Mermaid, and validate them with documentation build scripts.
- IMP-002 — Configure Nx targets (e.g., `docs:lint-edge`) to run markdownlint, link checkers, and command validation scripts before merges.
- IMP-003 — Maintain a changelog with reviewer sign-off metadata and document review cadence to ensure content freshness.
- IMP-004 — Build accessible layouts in the Next.js docs portal (`EdgeDocsLayout`, `RunbookDecisionTree`) with keyboard-friendly navigation and high-contrast styling.

## References

- REF-001 — docs/tools/nginx/epics/edge-traffic-platform/epic.md
- REF-002 — docs/tools/nginx/epics/edge-traffic-platform/arch.md
- REF-003 — docs/tools/nginx/epics/edge-traffic-platform/features/edge-operational-documentation/prd.md
- REF-004 — docs/tools/nginx/epics/edge-traffic-platform/features/edge-operational-documentation/implementation-plan.md
- REF-005 — docs/tools/nginx/epics/automated-tls-management/features/tls-documentation-suite/prd.md
