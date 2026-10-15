---
title: "Adopt Nx Automation Suite for Edge Operations"
status: "Accepted"
date: 2025-10-13
authors:
  - Platform Engineering Group
tags:
  - automation
  - nx
  - edge
---

## Status

Accepted

## Context

Operating the edge stack previously required manual Docker and script commands, increasing setup time and inconsistency across environments. The Nx automation suite feature PRD and implementation plan specify a cohesive set of Nx targets that build images, start/stop the stack, validate health, reload configuration, and tail logs, all wired into CI-friendly executors. Standardizing on this automation reduces toil and ensures reliable, repeatable workflows for platform, SRE, and release engineers.

## Decision

Implement the Nx automation suite by:

- Defining custom Nx executors and targets (`edge:build`, `edge:up`, `edge:down`, `edge:reload`, `edge:validate`, `edge:logs`) under the `tools-nginx` project, integrating Docker Compose overlays and existing scripts.
- Validating options via TypeScript schemas, returning structured output, and propagating non-zero exits on failure to support CI pipelines.
- Enabling task dependencies and caching so `edge:validate` chains from `edge:up`, and build results can reuse remote cache artifacts.
- Documenting usage patterns for local development and pipelines, including sample CI stages and troubleshooting guidance.

## Consequences

### Positive

- POS-001 — Provides consistent, discoverable commands for edge operations, lowering onboarding time for new engineers.
- POS-002 — Reduces manual errors during deployments and incident response by encapsulating best practices in Nx executors.
- POS-003 — Integrates smoothly with CI pipelines, enabling automated validation and artifact capture per run.

### Negative

- NEG-001 — Requires ongoing maintenance of custom executors and option schemas as the edge platform evolves.
- NEG-002 — Introduces a dependency on Nx tooling versions; upgrades must be coordinated to avoid breaking automation.
- NEG-003 — Demands Docker access for local and CI environments, which may complicate minimal or sandboxed setups.

## Alternatives

- ALT-001 — Continue using shell scripts and ad hoc documentation. Rejected due to lack of consistency and higher risk of human error.
- ALT-002 — Adopt a separate orchestration CLI (e.g., Makefiles). Rejected because Nx already governs the monorepo and provides caching, dependency graphing, and executor infrastructure.
- ALT-003 — Wait for a future platform migration (Kubernetes) before investing in automation. Rejected since current Docker-based workflows need immediate standardization.

## Implementation Notes

- IMP-001 — Implement executors in TypeScript using `child_process` to invoke Docker and scripts, with sanitized arguments and structured logging.
- IMP-002 — Configure target metadata in `project.json`, capturing dependencies, cache settings, and default options (e.g., `--env=development`).
- IMP-003 — Integrate automation with existing scripts (`rotate-certs.sh`, health checks) and ensure outputs are stored in `.nx/results` for traceability.
- IMP-004 — Provide documentation (`NxAutomationGuide`) with command playgrounds and CI examples, emphasizing accessibility and keyboard-friendly interactions.

## References

- REF-001 — docs/tools/nginx/epics/edge-traffic-platform/epic.md
- REF-002 — docs/tools/nginx/epics/edge-traffic-platform/arch.md
- REF-003 — docs/tools/nginx/epics/edge-traffic-platform/features/nx-automation-suite/prd.md
- REF-004 — docs/tools/nginx/epics/edge-traffic-platform/features/nx-automation-suite/implementation-plan.md
- REF-005 — docs/tools/nginx/epics/edge-traffic-platform/features/edge-operational-documentation/prd.md
