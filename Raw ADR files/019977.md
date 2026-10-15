---
status: accepted
date: 2025-08-12
decision-makers:
  - voder-dev-team
consulted:
  - internal-tooling
  - platform-team
informed:
  - contributors
---

# ADR-0001: Use standard development tools as devDependencies

## Context and Problem Statement

This package provides development-time configuration presets and factory helpers (TypeScript JSON presets, ESLint layers, Prettier config, and testing config/factories). To author, validate, and test these presets locally and in CI we need standard developer tools (TypeScript, ESLint, Prettier, Vitest, type definitions, testing-library helpers). These tools are only required during development and must not be shipped as runtime dependencies to consumers.

Without explicitly documenting and justifying these dev-only dependencies, future reviewers may object to adding them or misunderstand their purpose.

## Decision Drivers

- Provide authoring and validation of TypeScript/ESLint/Prettier/testing presets.
- Run unit tests and coverage locally and in CI to maintain quality.
- Keep runtime footprint minimal by limiting these tools to devDependencies.
- Maintain reproducible local development and CI runs with industry-standard tooling.

## Considered Options

1. Add the required tooling as devDependencies (recommended).
2. Do not add any dev tooling and rely on consumers to test their own configs (insufficient for authoring and quality).
3. Build a custom, minimal validation toolset instead of standard tools (higher maintenance cost and lower compatibility).

## Decision Outcome

Chosen option: Add the required tooling as devDependencies.

Rationale:

- Standard tools provide well-understood, well-maintained features for authoring, linting, formatting, and testing configuration files and small helper libraries.
- Declaring them as devDependencies makes it explicit they are not runtime requirements for consumers.
- This approach minimizes maintenance friction and leverages community knowledge and integrations (editors, CI, ecosystems).

## Consequences

Positive:

- Developers can author and validate presets locally and in CI with known tools.
- Tests and formatting checks can be run consistently.
- Consumers only install the runtime package without development tool churn.

Negative:

- The repository must maintain and occasionally update these devDependencies.
- A small increase in repository setup time (npm install) for contributors.

## Confirmation / Acceptance Criteria

- The repository contains an ADR at docs/decisions/0001-use-standard-development-tools-as-devdependencies.md (this file).
- package.json will list development-only tools (e.g., typescript, vitest, eslint, prettier, @types/node) under devDependencies.
- Project scripts are added to run type checks, tests, lint, and formatting locally and in CI.
- Tests using Vitest can be run locally and in CI to exercise the exported configuration presets.

## Implementation Notes (non-normative)

- Add the tooling as devDependencies; pinning strategy (exact vs. caret) will be decided in a follow-up ADR or commit note.
- If adding any additional dev or peer dependency later, create an ADR in docs/decisions/ before committing the dependency change.

---
