---
title: "Publish Integrated TLS Documentation Suite"
status: "Accepted"
date: 2025-10-13
authors:
  - Platform Engineering Group
tags:
  - tls
  - documentation
  - enablement
---

## Status

Accepted

## Context

The TLS automation work introduces multiple scripts and Nx tasks, yet knowledge transfer was fragmented across ad hoc notes and outdated READMEs. Teams struggled to locate authoritative instructions for certificate generation, validation, rotation, and Let’s Encrypt workflows, slowing onboarding and creating operational risk. The TLS documentation suite PRD and implementation plan outline a structured library of quickstarts, runbooks, troubleshooting guides, compliance checklists, and diagrams that link directly to automation commands. We need an explicit decision to treat this suite as the single source of truth for TLS operations.

## Decision

Adopt the curated TLS documentation suite by:

- Organizing Markdown content under `tools/nginx/docs/tls/` with standardized frontmatter, changelog entries, and peer review checkpoints for every update.
- Providing dedicated guides for each workflow (generate, validate, rotate, enroll, overlay) that cross-link to scripts, Nx targets, and log locations so engineers can execute tasks directly from the docs.
- Embedding Mermaid diagrams and decision trees that describe certificate flows, rotation lifecycle, and troubleshooting paths, validated via documentation build pipelines.
- Integrating the documentation into the Next.js portal and ensuring search/indexing surfaces TLS content prominently for self-service discovery.

## Consequences

### Positive

- POS-001 — Speeds onboarding and reduces escalations by giving engineers a single, well-structured reference for every TLS workflow.
- POS-002 — Improves audit readiness with compliance checklists, log references, and documented review history.
- POS-003 — Keeps automation and documentation aligned through linting, changelog requirements, and cross-link validation.

### Negative

- NEG-001 — Requires ongoing content governance, including peer reviews and changelog maintenance for every update.
- NEG-002 — Increases build time slightly due to documentation linting and diagram compilation.
- NEG-003 — Demands coordination with development teams to keep examples accurate as scripts evolve, creating additional workload for maintainers.

## Alternatives

- ALT-001 — Leave documentation distributed across READMEs and wiki pages. Rejected because it perpetuates inconsistencies and knowledge silos.
- ALT-002 — Rely on inline script help (`--help`). Rejected since it lacks broader operational context, diagrams, and compliance guidance.
- ALT-003 — Outsource documentation to an external knowledge base. Rejected due to slower iteration speed and difficulty aligning updates with code changes.

## Implementation Notes

- IMP-001 — Establish directory structure and frontmatter schema, enforcing presence via markdownlint and custom lint rules in CI.
- IMP-002 — Maintain a `CHANGELOG.md` capturing publication history and reviewer sign-off, referenced in release notes for TLS tooling updates.
- IMP-003 — Wire documentation pages into the Next.js site (`my-programs-app`) with components like `TlsDocsIndexPage`, ensuring accessible navigation and keyboard-friendly layouts.
- IMP-004 — Automate diagram validation (`npm run docs:validate`) and broken-link checks to prevent regressions before merges.

## References

- REF-001 — docs/tools/nginx/epics/automated-tls-management/epic.md
- REF-002 — docs/tools/nginx/epics/automated-tls-management/arch.md
- REF-003 — docs/tools/nginx/epics/automated-tls-management/features/tls-documentation-suite/prd.md
- REF-004 — docs/tools/nginx/epics/automated-tls-management/features/tls-documentation-suite/implementation-plan.md
- REF-005 — docs/tools/nginx/epics/automated-tls-management/features/automated-development-certificates/prd.md
- REF-006 — docs/tools/nginx/epics/automated-tls-management/features/certificate-validation-pipeline/prd.md
- REF-007 — docs/tools/nginx/epics/automated-tls-management/features/certificate-rotation-workflow/prd.md
- REF-008 — docs/tools/nginx/epics/automated-tls-management/features/lets-encrypt-automation/prd.md
