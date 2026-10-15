# ADR-0001: Package Management with pnpm

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-06
- **Feature:** Project Initialization
- **Context:** The project requires a package manager for Node.js dependencies. With multiple options available (npm, yarn, pnpm), we need to select one that aligns with our performance, disk space, and dependency management requirements.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Use pnpm as the package manager for all Node.js dependencies in the project. This includes:
- Installing and managing dependencies via pnpm
- Using pnpm for all build, development, and deployment scripts
- Ensuring all team members use pnpm consistently
- Configuring CI/CD pipelines to use pnpm

## Consequences

### Positive

- Significant disk space savings through hard linking of identical packages
- Faster installation times due to efficient dependency resolution and parallel downloads
- Strict dependency management preventing phantom dependencies
- Improved performance in monorepo scenarios
- Reduced node_modules size compared to npm and yarn
- Better support for workspace protocols and cross-linking packages

### Negative

- Potential learning curve for team members unfamiliar with pnpm
- Some packages may have compatibility issues with pnpm's strict dependency model
- Requires understanding of pnpm-specific features like workspace protocols
- Smaller community compared to npm, potentially fewer resources for troubleshooting

## Alternatives Considered

Alternative A: npm (default package manager)
- Pros: Most widely used, largest community, familiar to most developers
- Cons: Larger disk usage, slower installation times, potential for phantom dependencies
- Rejected because: Doesn't meet our performance and disk space requirements

Alternative B: Yarn (Classic or Berry)
- Pros: Good performance, lockfile support, workspaces feature
- Cons: Larger disk usage than pnpm, some compatibility issues with certain packages
- Rejected because: pnpm provides better performance and disk efficiency

## References

- Feature Spec: /specs/001-docusaurus-init/spec.md
- Implementation Plan: /specs/001-docusaurus-init/plan.md
- Related ADRs: None
- Evaluator Evidence: Performance benchmarks and disk usage comparisons
