---
status: accepted
date: 2025-08-22
deciders: [voder-dev-team]
packages: '@voder/ui-tools'
---

# Adopt narrow ESLint exclude for ui-tools dist build outputs

## Context and Problem Statement

ESLint parser errors are being raised when the linter attempts to process compiled build outputs under the ui-tools package. These errors ("The file was not found in any of the provided project(s)") are noisy and block the standard verification pipeline. Existing tsconfig-based exact-path excludes already exist, but the volume of generated/visible build artifacts makes adding many per-file excludes impractical in the short term.

## Decision

Accept a narrowly scoped glob exclusion for the ui-tools package build outputs in the ESLint TypeScript project exclude list:

- Exclude pattern to adopt: "packages/ui-tools/dist/\*\*"

This is intentionally narrow (targets only the ui-tools package compiled outputs) to minimize exclusion surface while restoring linting operability.

## Rationale

- Minimizes developer friction by removing parser errors caused solely by generated build artifacts.
- Keeps the exclusion scope focused to a single package; does not broadly ignore dist/ directories across the repository.
- Preserves the single-path / ADR-first governance: the glob is documented here so that future reviewers can evaluate and revert/remediate when appropriate.
- Enables the linter to run successfully so verify/lint quality gates can be re-enabled and the single-path process resumed for any remaining parser errors.

## Consequences

- Positive: Restores a working lint pipeline quickly and avoids ad-hoc per-file excludes that can proliferate.
- Neutral: Temporarily hides generated artifacts in ui-tools from ESLint; this is acceptable because dist/ is a generated output and is already git-ignored.
- Mitigation: The ADR records that the exclude is temporary and should be revisited; exact-path excludes remain preferred for any additional files reported outside this glob.

## Confirmation

- Commit this ADR at docs/decisions/0003-linting-enforcement.md.
- Update tsconfig.eslint.json to include "packages/ui-tools/dist/\*\*" in the "exclude" array.
- Verify: run `npm run lint` locally and confirm the previous ESLint parser/project errors for ui-tools dist files are cleared.

---
