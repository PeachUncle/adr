---
title: 'ADR-0007: Host Portfolio App on Vercel with Promotion Gated by GitHub Checks'
description: 'Decision to deploy the Portfolio App to Vercel using preview deployments for PRs and production promotion gated by imported GitHub checks.'
sidebar_position: 7
tags:
  [architecture, adr, portfolio-app, hosting, vercel, cicd, release-governance]
---

## Purpose

Record the decision to host the Portfolio App on **Vercel**, using:

- preview deployments for PRs
- production deployments from `main`
- production promotion gated by imported GitHub checks (Deployment Checks)

## Scope

### In scope

- environment strategy (preview vs production)
- gating rules for production promotion
- rollback strategy and operational implications

### Out of scope

- vendor account details and secrets (never document publicly)
- non-Vercel hosting strategies beyond initial consideration

## Prereqs / Inputs

- Decision owner(s): Portfolio maintainer
- Date: 2026-01-10
- Status: Proposed (accept on successful deploy + checks gating)
- Related artifacts:
  - Portfolio App dossier deployment page: `docs/60-projects/portfolio-app/deployment.md`
  - Ops runbooks (this set): deploy/rollback/CI triage
  - ADR-0004: CI quality gates (pattern mirrored here)

## Decision Record

### Title

ADR-0007: Host Portfolio App on Vercel with Promotion Gated by GitHub Checks

### Context

The Portfolio App is a public-facing application and must demonstrate enterprise release governance:

- PR review with preview environments
- deterministic build contract
- production promotion only when checks pass
- fast rollback capability

Vercel provides Git-integrated deployments and preview environments by default, and supports gating production promotion on GitHub checks via Deployment Checks.

### Decision

Host on Vercel with the following governance:

- PR branches → preview deployments (review URLs)
- `main` → production deployment
- production **promotion** (domain assignment) requires GitHub checks to pass:
  - `ci / quality`
  - `ci / build`
- rollback is primarily Git revert + redeploy from corrected `main`

### Alternatives considered

1. **GitHub Pages**

- Pros: free static hosting
- Cons: less natural for Next.js; preview workflows less seamless; weaker full-stack narrative
- Not chosen: Vercel is more aligned with the intended stack and enterprise delivery story.

2. **Netlify**

- Pros: similar preview support
- Cons: comparable; selection depends on ecosystem preferences
- Not chosen: standardize on Vercel for the portfolio program to reduce variance.

3. **Self-hosting**

- Pros: control and “SRE story”
- Cons: operational overhead not justified for initial portfolio; increases risk of reliability issues
- Not chosen: reserved for a dedicated infrastructure demo project later.

### Consequences

#### Positive consequences

- Strong enterprise signal: gated promotion + PR previews
- Consistent workflow across portfolio properties (docs app and portfolio app)
- Simple rollback via Git revert preserves traceability
- Reduced release risk: checks must pass before production is promoted

#### Negative consequences / tradeoffs

- Vendor dependency (hosting feature set and stability)
- Requires stable check naming and CI triggers
- Must maintain parity between preview/prod build settings

#### Operational impact

- Runbooks must define:
  - deploy validation steps
  - rollback triggers and procedures
  - handling “checks pending” scenarios
- CI must run on `push` to `main`, not just PRs, so checks exist for the production commit.

#### Security impact

- Promotion gating reduces risk of shipping broken or unsafe changes
- Still requires strict “no secrets” hygiene and dependency governance

### Implementation notes (high-level)

- Configure Vercel project:
  - connect GitHub repo
  - enable preview deployments
  - enable Deployment Checks and import required GitHub checks
- Ensure GitHub Actions:
  - runs `ci` on PRs and on `push` to `main`
  - check names remain stable (do not rename lightly)
- Validate with a controlled change:
  - create PR, confirm preview, merge, confirm production promotion waits on checks

## Validation / Expected outcomes

- PR previews exist and are used for review.
- Production promotion is blocked until:
  - `ci / quality` passes
  - `ci / build` passes
- Rollback can be executed quickly and deterministically with Git revert.

## Failure modes / Troubleshooting

- Vercel waits indefinitely for checks:
  - ensure workflows run on `push` to `main`
  - ensure check names match imported checks
- Preview differs from production:
  - align Node/pnpm/toolchain and environment variables across environments
- Broken `/docs` links:
  - treat as regression; fix and record in release notes if material

## References

- Portfolio App deployment dossier: `docs/60-projects/portfolio-app/deployment.md`
- Runbooks (this set): `docs/50-operations/runbooks/rbk-portfolio-<deploy/rollback/CI triage>`
- Docs App hosting ADR: `docs/10-architecture/adr/adr-0003-hosting-vercel-with-preview-deployments.md`
