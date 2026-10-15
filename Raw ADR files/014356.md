---
title: 'ADR-0003: Host Portfolio Docs App on Vercel with Preview Deployments'
description: 'Decision to host the Docusaurus documentation site on Vercel, enabling PR preview deployments and main-branch production publishing.'
sidebar_position: 3
tags: [architecture, adr, hosting, deployment, vercel, cicd]
---

## Purpose

Record the decision to host the Portfolio Docs App on **Vercel** with preview deployments for pull requests and production deploys from `main`.

## Scope

### Use when

- selecting the public hosting strategy for the documentation platform
- defining the deployment experience that supports review and quality gates

### Do not use when

- changing small build commands or minor CI tweaks unless they affect hosting posture

## Prereqs / Inputs

- Decision owner(s): Portfolio maintainer
- Date: 2026-01-06
- Status: Accepted
- Related risks:
  - misconfiguration leading to broken routing or base path confusion
  - deployment drift between preview and production
  - accidental exposure of sensitive data via build logs (must avoid)

## Decision Record

### Title

ADR-0003: Host Portfolio Docs App on Vercel with Preview Deployments

### Context

The Portfolio Docs App must be publicly accessible and demonstrate:

- professional delivery workflows
- PR-based review with preview capability
- stable production publishing from `main`
- simple rollback through Git history

We prefer free or low-cost hosting suitable for a public portfolio, while still conveying enterprise delivery discipline.

### Decision

Host the Portfolio Docs App on **Vercel**, configured to:

- deploy preview builds for PR branches (review environment)
- deploy production from `main` (published environment)
- enforce the build contract:
  - `pnpm install`
  - `pnpm build`

The primary rollback mechanism is reverting changes on `main` and redeploying.

### Alternatives considered

1. **GitHub Pages**
   - Pros:
     - free static hosting; simple
     - aligns well with static site workflows
   - Cons:
     - preview deployments are less seamless
     - can require additional base path considerations
   - Why not chosen:
     - Vercel offers a stronger “enterprise delivery feel” via PR previews.

2. **Netlify**
   - Pros:
     - strong static hosting; preview deployments supported
   - Cons:
     - comparable to Vercel; preference depends on existing workflow
   - Why not chosen:
     - Vercel selected to align with common modern full-stack portfolio hosting patterns.

3. **Self-hosting (VM/container)**
   - Pros:
     - maximum control
   - Cons:
     - operational overhead not justified for a docs site at this stage
     - distracts from the portfolio program’s primary objectives
   - Why not chosen:
     - disproportionate operational complexity for the value delivered.

### Consequences

- Positive consequences:
  - PR previews support high-quality doc review and reduce merge risk
  - Production publishes from `main`, matching enterprise “source of truth” discipline
  - Rollback is straightforward: revert PR → redeploy
  - Hosting is well-aligned with modern developer portfolio expectations

- Negative consequences / tradeoffs:
  - Hosting behavior is vendor-dependent
  - Must avoid documenting sensitive hosting configuration details publicly
  - Must ensure route base path decisions are made early and kept consistent

- Operational impact:
  - Deploy/rollback runbooks required
  - Build failures block deploy; triage process required

- Security impact:
  - No secrets in repo; minimize sensitive environment variables
  - CI/log outputs must avoid leaking identifiers
  - Dependency/supply chain and PR integrity remain key threats

### Implementation notes

#### Route base path strategy

- Decide and document `routeBasePath` early (docs at `/` vs `/docs`).
- Keep the decision consistent between local (`docusaurus.config.ts`) and Vercel deployment.

#### Build configuration

Configure Vercel with the following build contract:

```yaml
Install command: pnpm install
Build command: pnpm build
Output directory: build
Node.js version: 20.x (or higher)
```

This ensures deterministic, reproducible builds across local and hosted environments.

#### Deployment Checks: decoupling deployment creation from release promotion

**Key decision:** Enable Vercel **Deployment Checks** and configure **Required checks** to decouple production deployment creation from release promotion.

**Rationale:**
Deployment Checks are Vercel's mechanism for blocking domain assignment and production promotion until specified GitHub checks pass. This allows us to:

- Create a production deployment immediately upon merge to `main` (fast feedback loop)
- Prevent domain assignment (public availability) until required checks pass (safety gate)
- Maintain a clear audit trail: when exactly the site became publicly available

**Configuration:**

- Required checks: `ci / build` (from GitHub Actions workflow)
- When checks are green: Vercel automatically assigns the production domain
- When checks fail: deployment exists but remains unpromoted; reviewers see build failure before site goes live

This pattern ensures that even if a critical link or configuration issue reaches `main`, it is caught and the site remains stable until the issue is resolved and checks pass.

#### Build determinism: pnpm + Corepack

To ensure identical builds across local, CI, and Vercel environments, configure package manager pinning:

**Package manager pinning via `package.json`:**

- `package.json` already specifies: `"packageManager": "pnpm@10.0.0"`
- Vercel respects this field and automatically uses the pinned version ([Vercel | Package Managers](https://vercel.com/docs/package-managers))

**Corepack integration (experimental):**

- Enable `ENABLE_EXPERIMENTAL_COREPACK=1` as an environment variable in Vercel project settings
- Corepack is Node's native package manager version manager; when enabled, it enforces the exact `pnpm@10.0.0` version specified in `package.json`

**Risk/Benefit assessment:**

- **Benefit:** eliminates "works on my machine but not in CI/Vercel" errors due to package manager version drift
- **Risk:** Corepack is experimental ([Vercel | Corepack (experimental)](https://vercel.com/changelog/corepack-experimental-is-now-available)); Node team may change behavior or deprecate in favor of a stable alternative
- **Mitigation:** pinned version in `package.json` provides a fallback; if Corepack behavior changes, we can disable it and rely on Vercel's default package manager resolver, or revert to explicit install via `pnpm install --frozen-lockfile`

**Validation:**

- Check Vercel build logs: confirm they show `pnpm 10.0.0` (or the pinned version)
- Local validation: run `pnpm install --frozen-lockfile && pnpm build` to catch lockfile drift early

#### PR preview deployments

- Reviewers validate navigation, rendering, and key pages prior to merge
- Preview URLs are unique per PR and branch, enabling parallel review
- Failed builds block merge and are visible in the PR checks UI

#### Operational runbooks

Ensure the following runbooks exist and are maintained:

- **Deploy runbook** — how to interpret Vercel deployment lifecycle and validate promotion
- **Rollback runbook** — how to revert a merge and redeploy to restore production
- **Broken-links triage runbook** — how to interpret CI build failures and resolve locally

## Validation / Expected outcomes

- PR branches produce a preview deployment suitable for review
- `main` publishes production docs deterministically
- Rollback can be executed quickly via Git revert + redeploy
- Deployments do not expose secrets, internal endpoints, or sensitive logs

## Failure modes / Troubleshooting

- Base path mismatch between local and hosting:
  - mitigation: keep a stable routeBasePath decision; document it.
- Preview/prod drift:
  - mitigation: same build command and env settings; validate via `pnpm build`.
- Hosting outage:
  - mitigation: redeploy; consider fallback hosting if required for continuity.

## References

- Deployment dossier page: `docs/60-projects/portfolios-docs-app/deployment.md`
- Operations runbooks: `docs/50-operations/runbooks/`
- DevOps platform docs: `docs/30-devops-platform/`
