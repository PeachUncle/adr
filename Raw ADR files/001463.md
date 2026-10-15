# ADR-001: Upgrade to Next.js 15.5.3 and ESLint CLI
- **Date**: 2025-02-14
- **Status**: Accepted

## Context
The repo was pinned to Next.js 14.2.32 while `next-sanity@11.1.1` now requires Next 15.1+. CI `npm ci` runs failed with peer dependency conflicts (ERESOLVE). Linting relied on the deprecated `next lint` wrapper, and the static export build disabled minification via custom webpack overrides, inflating bundle size.

## Options
1. **Downgrade `next-sanity`** to a 10.x line compatible with Next 14.
   - Pros: No framework upgrade.
   - Cons: Loses Sanity visual editing updates; requires ongoing pin maintenance; conflicts with upstream expectations.
2. **Upgrade to Next 15** and align tooling (eslint-config-next, lint scripts).
   - Pros: Restores dependency parity; unlocks framework fixes; removes peer conflict.
   - Cons: Requires API review for App Router params, config cleanup, and build validation.

## Decision
Chose Option 2. Upgraded `next` to 15.5.3, updated `eslint-config-next` to 15.5.2, migrated linting to `eslint .`, and accepted Next’s TypeScript guidance for route typings. Added `.eslintignore` to exclude build artefacts.

## Implementation
- `package.json` / `package-lock.json`: bump Next and lint deps; add `@eslint/eslintrc`; update lint script.
- `app/projects/[slug]/page.tsx`: await promised `params` and generate metadata asynchronously per Next 15 contract.
- `app/api/metrics/route.ts`: declare `dynamic = 'force-static'` so static export succeeds with `output: 'export'`.
- `next.config.js`: remove deprecated `swcMinify` and custom webpack minimizer overrides; set `outputFileTracingRoot`.
- Added documentation: engineering charter, quality gates, observability contract, ADR template, and this ADR.

## Verification
- `npm run lint` (ESLint CLI) — pass.
- `npm run build` — pass; generated stats (First Load JS shared: 102 kB; `/` page bundle 48.7 kB). Previous config disabled minification and produced 455 kB shared JS; minification restored.
- Manual review of dynamic route confirmed `params` awaiting.

## Security & Privacy
- No new secrets introduced; Neon connection still sourced from `DATABASE_URL` (env only).
- Logging in metrics API remains structured via `NextResponse.json`; failure paths continue to log sanitized errors.
- Dependency upgrades reviewed for license compatibility (Next/Sanity MIT, ESLint MIT).

## Migration & Rollback
- Rollback by reverting commit restoring Next 14 versions and reinstalling dependencies (`npm install`).
- For downgrade, remove `.eslintignore` if lint scope needs re-expansion and reinstate prior lint script.

## Appendix
- CI failure logs: npm ERESOLVE for `next-sanity@11.1.1` vs `next@14.2.32`.
- Build benchmark outputs stored in local `npm run build` run (see `logs/build-20250214.txt` if preserved locally).
- Related docs: `docs/engineering-charter.md`, `docs/quality-gates.md`, `docs/observability.md`, `docs/adr/ADR-000-template.md`.
