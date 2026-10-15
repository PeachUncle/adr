---
title: 'ADR-0008: Portfolio App CI Quality Gates, Supply Chain Baselines, and Branch Protection (Rulesets)'
description: 'Establishes mandatory CI gates with stable check naming, deterministic installs, baseline CodeQL + Dependabot posture, and main-branch enforcement via GitHub Rulesets.'
sidebar_position: 8
tags:
  [
    architecture,
    adr,
    governance,
    portfolio-app,
    ci,
    github-actions,
    supply-chain,
    codeql,
    dependabot,
    branch-protection,
  ]
---

## Purpose

Establish mandatory CI quality gates, deterministic installs, and baseline supply-chain controls for the Portfolio App, and formalize enforcement via GitHub Rulesets with stable check names that can be consumed by downstream promotion checks (e.g., Vercel). This provides an enterprise-credible governance contract for merges and releases.

## Scope

Applies to the Portfolio App repository CI configuration, branch protection, and related supply-chain automation. Excludes the Documentation App except where referenced for evidence. Covers:

- Required CI checks and their stable names
- Deterministic install policy (`--frozen-lockfile`)
- Baseline CodeQL and Dependabot posture
- Enforcement via GitHub Rulesets (not classic branch protection)

## Prereqs / Inputs

- Decision owner(s): Portfolio Program (Portfolio App maintainers)
- Date: 2026-01-12
- Status: Accepted
- Related work items (optional identifiers): Portfolio Program — Portfolio App Step 3 (CI quality gates)
- Related risks (optional):
  - Regressions or broken builds merged to `main` without consistent checks
  - Non-deterministic dependency installs causing environment drift
  - Supply chain risk due to unreviewed dependency updates and missing security scanning
  - Governance drift if check names change and merge/promotion gates silently break
  - Public-safe risk if CI logs or configuration accidentally expose sensitive information

## Decision Record

### Title

ADR-0008: Portfolio App CI Quality Gates, Supply Chain Baselines, and GitHub Branch Protection (Rulesets)

### Context

- What problem are we solving?
  - The Portfolio App is a public, production-quality Next.js + TypeScript application intended to demonstrate enterprise-grade delivery discipline. Without enforceable CI gates and branch governance, the repository can drift into inconsistent formatting, type regressions, non-reproducible builds, and unreviewed dependency changes. This undermines portfolio credibility and increases operational and security risk.

- What constraints exist (time, cost, compliance, platform)?
  - Keep baseline enforcement strong but lightweight (fast CI, minimal friction).
  - Ensure deterministic outcomes across Windows 11 + WSL2 local development, GitHub Actions CI, and Vercel hosting.
  - Public-safe posture: no secrets; no private endpoints; no sensitive internal implementation details.
  - Anticipate Vercel production promotion gating via imported GitHub checks; check names must remain stable to keep governance intact.

- What assumptions are we making?
  - The repository is a single application (not a monorepo) using pnpm and lockfile-based installs.
  - The “evidence engine” for deep technical artifacts lives in the Documentation App; the Portfolio App links to it.
  - Additional checks (tests, performance budgets, accessibility gating) will be added later as the project scales, but not at the expense of baseline stability.

### Decision

We will implement and enforce mandatory CI quality gates for the Portfolio App using GitHub Actions and protect `main` using GitHub **Rulesets**. CI will consist of two required checks with stable names: **`ci / quality`** (lint, formatting check, typecheck) and **`ci / build`** (production build). CI installs will use `pnpm install --frozen-lockfile` to guarantee deterministic dependency graphs and prevent unreviewed dependency drift. As baseline supply-chain hygiene for a public repo, we will enable CodeQL scanning and Dependabot updates (weekly cadence, grouped minor/patch updates; majors excluded by default). GitHub branch protection will use Rulesets (not classic branch protection) to require PR-based merges, enforce the required checks (`ci / quality`, `ci / build`), and block force pushes and branch deletion.

Key configuration choices (high-level; no secrets):

- GitHub Actions workflow named `ci` with jobs named `quality` and `build` producing required checks:
  - `ci / quality`
  - `ci / build`
- CI triggers: `pull_request` and `push` to `main`
- Install determinism: `pnpm install --frozen-lockfile`
- Baseline security automation:
  - `.github/workflows/codeql.yml`
  - `.github/dependabot.yml`
- Branch governance: GitHub Ruleset targeting `main` requiring PR + required checks and blocking force-push/deletion

### Alternatives considered

List each alternative and why it was not chosen:

1. No required CI gates (developer-run checks only)
   - Pros:
     - Lowest friction; fastest merges.
     - No CI maintenance overhead.
   - Cons:
     - Higher regression risk; “broken main” is more likely.
     - Inconsistent formatting/types can accumulate.
     - Weak enterprise credibility signal for a public portfolio.
   - Why not chosen:
     - Conflicts with the portfolio’s verification-first, enterprise-evidence posture.

2. Single build-only gate
   - Pros:
     - Simple and fast; ensures deploy artifact compiles.
     - Fewer moving parts.
   - Cons:
     - Allows formatting drift and lint/type regressions to enter `main`.
     - Builds fail later and are harder to triage without earlier-stage signals.
   - Why not chosen:
     - Insufficient for a TypeScript codebase that is intended to scale and be reviewed like production.

3. Non-frozen installs in CI (`pnpm install` without `--frozen-lockfile`)
   - Pros:
     - Fewer failures from lockfile drift.
     - “It just installs” even when lockfile is stale.
   - Cons:
     - Allows transitive dependency drift without review.
     - Breaks reproducibility and complicates troubleshooting.
     - Increases supply chain exposure window and unpredictability.
   - Why not chosen:
     - Determinism is a core enterprise delivery requirement and a key credibility signal.

4. No baseline supply-chain automation (skip CodeQL and Dependabot)
   - Pros:
     - Less alert noise and fewer maintenance PRs.
     - Lower CI/runtime overhead.
   - Cons:
     - Weak supply-chain posture for a public repo.
     - Misses standard enterprise controls and documented security hygiene.
   - Why not chosen:
     - The portfolio explicitly aims to demonstrate modern, enterprise-grade SDLC and security discipline.

5. Classic branch protection rules instead of GitHub Rulesets
   - Pros:
     - Familiar and simpler configuration.
     - Commonly used historically.
   - Cons:
     - Less flexible policy evolution and layering.
     - Weaker narrative for modern governance management as checks and branches expand.
   - Why not chosen:
     - Rulesets better support layered governance, clearer enforcement, and future-proof policy management.

### Consequences

- Positive consequences:
  - Prevents unreviewed changes from landing in `main`.
  - Enforces consistent formatting, type safety, and build integrity.
  - Improves triage by separating “quality” failures from “build” failures.
  - Ensures deterministic dependency graphs and reduces drift-related incidents.
  - Strengthens supply-chain posture and auditability for a public repo.
  - Provides high-signal evidence of enterprise delivery discipline.

- Negative consequences / tradeoffs:
  - Increased friction: CI can block merges for formatting, lint, or type issues.
  - Lockfile discipline required: dependency updates must be deliberate and reviewed.
  - Security automation may produce maintenance work (Dependabot PRs, CodeQL findings).
  - Check naming stability becomes an operational “API” that must be preserved.

- Operational impact:
  - Stable check names become a governance contract used by:
    - GitHub Rulesets required checks
    - Vercel promotion checks (when enabled)
    - runbooks and operational triage documentation
  - CI topology is fixed:
    - `ci / quality` gates `ci / build`
  - Runbooks must define triage paths for each check type.

- Security impact:
  - CodeQL increases early detection of risky patterns and common vulnerabilities.
  - Dependabot reduces vulnerability exposure windows by keeping dependencies current.
  - Frozen lockfile reduces the chance of unreviewed transitive dependency changes.

- Cost/complexity impact:
  - Adds CI workflows and security automation to maintain.
  - Slightly longer PR feedback loops and ongoing dependency maintenance cadence.
  - Reduced long-term costs due to fewer regressions and clearer triage.

### Implementation notes (high-level)

- What changes are required?
  - Ensure scripts exist and remain functional:
    - `lint` (ESLint CLI)
    - `format:check` and `format:write` (Prettier)
    - `typecheck` (`tsc --noEmit`)
    - `build` (`next build`)
  - Implement GitHub Actions workflows:
    - `.github/workflows/ci.yml`
      - workflow name: `ci`
      - jobs: `quality`, `build`
      - stable checks: `ci / quality`, `ci / build`
      - installs: `pnpm install --frozen-lockfile`
    - `.github/workflows/codeql.yml`
    - `.github/dependabot.yml`
  - Add PR discipline scaffolding:
    - `.github/pull_request_template.md`
  - Configure GitHub Ruleset targeting `main`:
    - require PRs
    - require `ci / quality` and `ci / build`
    - block force pushes
    - prevent deletion
    - require conversation resolution (recommended)

- What gets removed or deprecated?
  - Any reliance on `next lint` (Next.js 16 no longer supports it); linting is via ESLint CLI.
  - Direct pushes/merges to `main` that bypass PR review and required checks.

- What migration considerations exist?
  - If check names or workflow/job naming changes are required, coordinate updates across:
    - GitHub Ruleset required checks
    - Vercel promotion checks (if enabled)
    - Documentation App dossier pages and runbooks referencing check names
  - If the repo evolves into a workspace/monorepo, revisit:
    - dependency placement and install commands
    - CI working directory strategy
    - potential split of check sets per package

## Validation / Expected outcomes

- How will we confirm the decision is successful?
  - PRs cannot merge to `main` unless both required checks pass:
    - `ci / quality`
    - `ci / build`
  - CI fails if lockfile is stale or missing (`--frozen-lockfile` enforcement).
  - CodeQL runs on PRs and `main` successfully at least once, and scheduled runs execute.
  - Dependabot opens weekly PRs (grouped minor/patch) and GitHub Actions updates.

- What metrics/signals should improve?
  - Lower frequency of broken builds landing in `main`.
  - Faster feedback loops and clearer categorization of failures (quality vs build).
  - Reduced code review noise from formatting drift.
  - More predictable dependency update cadence and reduced vulnerability exposure time.

- What regression risks must be checked?
  - Renaming the workflow or jobs causing required checks to disappear or change names.
  - Misconfigured Ruleset resulting in unintended merges or blocked merges.
  - Lockfile drift from dependency updates that do not update the lockfile.
  - Toolchain drift (Node/pnpm versions) causing CI/local mismatch.
  - Security automation producing excessive false positives or unmanageable PR volume.

## Failure modes / Troubleshooting

- What can go wrong because of this decision?
  - `main` merge blocked because required checks are missing (workflow not running) or renamed.
  - `--frozen-lockfile` fails due to lockfile drift after dependency changes.
  - Formatting fails due to Prettier plugin/module format mismatch (e.g., CJS config requiring ESM plugin).
  - CodeQL fails due to permissions or configuration issues.
  - Dependabot PR volume or conflicts becomes noisy.

- What are the rollback or mitigation options?
  - If governance blocks all merges due to misconfiguration:
    - temporarily adjust Ruleset required checks only as an emergency measure
    - immediately restore correct checks after CI is fixed
    - document exception in release notes or incident/postmortem if impactful
  - If lockfile drift blocks CI:
    - update lockfile in a dedicated PR with explicit rationale and evidence
  - If Prettier plugin issues block formatting:
    - use `prettier.config.mjs` and reference plugins by name
    - if still blocked, temporarily remove plugin with a follow-up task to re-enable
  - If CodeQL is unstable:
    - tune schedule/queries; avoid disabling without updating this ADR and dossier security posture
  - If Dependabot noise is high:
    - adjust groups, cadence, or PR limit; document changes in security posture docs

- How do we detect failures early?
  - CI runs on all PRs and on `main`.
  - GitHub Ruleset prevents bypass of required checks.
  - CI triage runbook provides consistent diagnosis paths.
  - Dependabot and CodeQL provide continuous supply-chain and static-analysis signals.

## References

- Related architecture pages:
  - `docs/60-projects/portfolio-app/02-architecture.md`
  - `docs/60-projects/portfolio-app/05-testing.md`
  - `docs/60-projects/portfolio-app/03-deployment.md`
  - `docs/60-projects/portfolio-app/04-security.md`
  - `docs/60-projects/portfolio-app/06-operations.md`

- Related threat model(s):
  - `docs/40-security/threat-models/portfolio-app-threat-model.md`

- Related runbook(s):
  - `docs/50-operations/runbooks/rbk-portfolio-deploy.md`
  - `docs/50-operations/runbooks/rbk-portfolio-rollback.md`
  - `docs/50-operations/runbooks/rbk-portfolio-ci-triage.md`

- Related CI/CD documentation:
  - Portfolio App repo:
    - `.github/workflows/ci.yml`
    - `.github/workflows/codeql.yml`
    - `.github/dependabot.yml`
  - Internal-only env contract:
    - `docs/_meta/env/portfolio-app-env-contract.md`
