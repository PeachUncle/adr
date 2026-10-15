---
status: accepted
date: 2025-08-14
deciders:
  - voder-dev-team
consulted:
  - platform-team
  - tooling-experts
informed:
  - contributors
packages: '@voder/dev-config'
---

# ADR-0005: Require exact version alignment for vitest packages

## Context and Problem Statement

The dev-config package runs Vitest with the V8 coverage provider in CI-style test runs (script: `npm run test:ci`). Some environments require the provider plugin `@vitest/coverage-v8` to be present to collect coverage with the V8 provider. Without the provider installed, `npm run test:ci` may fail with a "Cannot find module '@vitest/coverage-v8'" error.

An inspection run identified a compatible published provider version: `@vitest/coverage-v8@3.2.4`. That provider has a peer requirement on `vitest@3.2.4`. Adding the provider therefore requires version alignment: both packages must use the same version to ensure compatibility.

## Decision Drivers

- Make `npm run test:ci` runnable locally and in CI with V8 coverage provider.
- Keep runtime package minimal: development-only tools must reside in `devDependencies`.
- Follow repository governance: every new direct dependency (and significant tool upgrades) requires an ADR.
- Ensure deterministic, reproducible test runs for contributors and CI.
- Verify version alignment through automated tests rather than manual inspection.

## Considered Options

1. Add `@vitest/coverage-v8` and upgrade `vitest` to the most recent stable versions that are compatible with each other (recommended).
2. Add a different coverage provider version compatible with the repository's vitest version (if available).
3. Change `test:ci` to avoid the v8 provider (e.g., use a different provider or omit coverage in `test:ci`).

## Decision Outcome

Chosen option: Add `@vitest/coverage-v8` and upgrade `vitest` to compatible versions in devDependencies (version aligned).

Rationale:

- The coverage provider and vitest must have matching versions due to peer dependency requirements.
- The package's test configuration uses the V8 provider; installing the provider with version alignment reduces runtime incompatibility risk.
- Both packages should be updated to the most recent stable versions that are compatible with each other.
- Bundling the ADR with package.json/package-lock changes (per governance) ensures reviewers see motivation and accept the dependency change together.

## Consequences

Positive:

- `npm run test:ci` will run coverage with the V8 provider deterministically across developer machines and CI.

Negative / Risks:

- Upgrading Vitest is a toolchain change and may surface minor compatibility differences requiring test/config fixes.
- Additional devDependencies must be maintained.
- Version alignment constraint requires coordinated updates of both packages.

Mitigations:

- Run verification (type-check, test:ci, lint, format:check) after install.
- Address any test or config issues in small focused commits documented in the PR.
- Add automated tests to verify version alignment constraints are maintained.

## Implementation

When this ADR is accepted, the local non-interactive steps will be:

1. Install the dependencies at compatible versions:
   npm install --no-audit --no-fund --save-dev @vitest/coverage-v8 vitest

2. Verify locally:
   npm run type-check
   npm run test:ci
   npm run lint
   npm run format:check

3. Add automated vitest tests to verify version alignment between vitest and @vitest/coverage-v8.

4. Bundle the ADR and the package.json/package-lock changes together in the same PR so reviewers can accept the ADR and the dependency update as a single logical change.

## Confirmation / Acceptance Criteria

- ADR file exists at docs/decisions/0006-add-@vitest-coverage-v8.md and is marked Accepted.
- package.json devDependencies include compatible versions of:
  - "@vitest/coverage-v8"
  - "vitest"
- `npm run type-check` completes without errors.
- `npm run test:ci` runs and produces coverage using the v8 provider without "Cannot find module '@vitest/coverage-v8'" errors.
- Automated tests verify version alignment between vitest and @vitest/coverage-v8.
- Lint/format checks pass (or failures are addressed and documented).

## Notes

- The version alignment requirement is due to peer dependency constraints: the coverage provider must match the vitest version.
- When updating these packages in the future, both should be updated together to maintain compatibility.
- If the project prefers to remain on an earlier Vitest major line, an alternative is to select a coverage provider version compatible with that Vitest version. That option was considered but the preferred path is to standardize on the most recent compatible versions.
- Do not commit package.json/package-lock.json until this ADR is included in the same change set.
