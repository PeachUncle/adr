---
title: 'ADR-0005: Portfolio App Stack — Next.js + TypeScript'
description: 'Decision to implement the Portfolio App as a Next.js App Router application using TypeScript, pnpm, and modern UI/tooling aligned to enterprise delivery expectations.'
sidebar_position: 5
tags:
  [architecture, adr, portfolio-app, nextjs, typescript, tooling, governance]
---

## Purpose

Record the decision to implement the Portfolio App using **Next.js (App Router) + TypeScript** as the foundational stack, including tradeoffs, operational consequences, and validation criteria.

## Scope

### In scope

- core application framework choice
- language/tooling baseline (TypeScript, pnpm)
- implications for performance, maintainability, and deploy model

### Out of scope

- detailed component libraries and design system selection (may be a follow-on ADR)
- any authentication strategy (explicitly deferred)

## Prereqs / Inputs

- Decision owner(s): Portfolio maintainer
- Date: 2026-01-10
- Status: Proposed (accept on merge of stack scaffold)
- Related artifacts:
  - Portfolio App dossier: `docs/60-projects/portfolio-app/`
  - CI gates policy ADR: ADR-0004 (expanded checks for portfolio docs app; mirrored posture for portfolio app)

## Decision Record

### Title

ADR-0005: Portfolio App Stack — Next.js (App Router) + TypeScript

### Context

The Portfolio App must be a high-grade, public-facing web application that demonstrates:

- modern full-stack competence and current industry practices
- enterprise SDLC discipline: CI gates, reproducible builds, PR governance
- performance and accessibility fundamentals
- a clean path to incremental enhancement (projects, demos, case studies)

The Portfolio App will be paired with the Documentation App (Docusaurus) as an evidence engine. The Portfolio App must integrate evidence links cleanly and reliably without becoming a second documentation platform.

### Decision

Implement the Portfolio App using:

- **Next.js (App Router)** for routing, rendering, and production-grade patterns
- **TypeScript** as the application language
- **pnpm** for dependency management and determinism
- **CSS/system**: Tailwind-based styling (implementation detail; confirm via follow-up ADR if needed)
- **Hosting**: Vercel (see ADR-0007)

Primary design constraints:

- Static-first and content-driven early (no auth; minimal backend surface)
- Strong CI quality gates (lint/format/typecheck/build)
- Evidence links to Documentation App as first-class UX elements

### Alternatives considered

1. **React + Vite SPA**

- Pros: simple build and deploy, straightforward client-side routing
- Cons: weaker SSR/SEO defaults; more work to deliver enterprise-grade routing and metadata; less “platform” narrative
- Not chosen: Next.js provides stronger built-in patterns for a portfolio that must read like production engineering.

2. **Static site generator only (Astro, Gatsby)**

- Pros: excellent performance; static-first by default
- Cons: less aligned with a “full-stack” Next.js enterprise narrative; varying ecosystem maturity and constraints
- Not chosen: Next.js is a stronger default for demonstrating modern full-stack patterns.

3. **Custom Node/Express + templating**

- Pros: explicit backend control and classic architecture story
- Cons: slower to deliver; increased security surface; less aligned with modern TS/React ecosystem expectations
- Not chosen: unnecessary complexity for portfolio value; better deferred to a dedicated demo project.

### Consequences

#### Positive consequences

- Strong alignment with current enterprise web engineering norms
- Good foundations for SSR/SEO, metadata, and performance tuning
- Clean integration with Vercel preview + production workflows
- Type safety and maintainability across growing project content

#### Negative consequences / tradeoffs

- Dependency ecosystem complexity (supply chain risk must be managed)
- Must enforce discipline to avoid “framework sprawl” and overengineering
- Some features (forms, auth, CMS) are deferred to preserve simplicity and safety

#### Operational impact

- CI must support TS type checks and deterministic builds
- Runbooks required for deploy/rollback/CI triage
- Release governance via checks is recommended (see ADR-0007)

#### Security impact

- Must enforce “no secrets” hygiene and safe-publication rules
- Supply chain posture becomes first-class (Dependabot, review, scanning)

### Implementation notes (high-level)

- Scaffold repo with Next.js + TS using pnpm.
- Add CI jobs:
  - `quality`: lint + format check + typecheck
  - `build`: Next build
- Create initial routes:
  - `/`, `/cv`, `/projects`, `/projects/[slug]`
- Implement data-driven project metadata and stable slugs.
- Ensure evidence links to `/docs` or docs subdomain are parameterized and consistent.

## Validation / Expected outcomes

- Local dev and build are deterministic:
  - `pnpm install`, `pnpm dev`, `pnpm build`
- CI gates pass on PRs and on `main`.
- Preview deployments are reviewable and consistent with production behavior.
- App routes render correctly and meet baseline performance/accessibility expectations.

## Failure modes / Troubleshooting

- Toolchain drift (Node/pnpm mismatches) → pin and document toolchain; treat drift as a defect.
- Link drift to documentation evidence pages → treat as breaking; fix and note in release notes.
- Overgrowth of dynamic features → require ADR before adding backend surfaces.

## References

- Portfolio App dossier hub: `docs/60-projects/portfolio-app/index.md`
- Deployment governance: `docs/60-projects/portfolio-app/deployment.md`
- Testing and gates: `docs/60-projects/portfolio-app/testing.md`
- Hosting ADR (this set): ADR-0007
