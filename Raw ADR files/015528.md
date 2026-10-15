# ADR-0029 — Canvas Externalization Phases 2–4 — Prerelease, Host Switch to NPM, Repo Split

Status: Proposed
Date: 2025-09-14
Related issue: #138 — Canvas externalization (Phases 2–4): prereleases, host switch to npm, split repos, docs
Related ADRs: ADR-0028 (Canvas externalization — Phase 1)

## Context
Phase 1 established Canvas UI/runtime as externalized packages inside this repo and added host-level guardrails/tests. Next, we will:
- Publish prerelease packages to npm for Canvas UI and Canvas-Component runtime
- Switch the host to consume those npm packages (instead of workspace copies)
- Split packages into their own repositories and complete documentation

We want a smooth path with minimal disruption to CI and the host app.

## Decision (Plan)
- Prepare packages for publication (metadata, files) without publishing yet.
- Publish prerelease tags (e.g., 0.1.0-rc.x) under the “next” dist-tag to avoid default uptake.
- Update the host to depend on the published versions, verifying both dev and CI preview flows.
- After a soak period, move packages into dedicated repos and remove workspace copies from this repo.

## Implementation Outline

### Phase 2 — Prerelease Packages (npm)
1) Package metadata
- Ensure publishability (publishConfig.access=public; files includes dist and json-sequences where applicable)
- Ensure exports map is correct for UI and deep symphony paths

2) Build and validate locally
- npm run build (root and packages)
- npm pack (each package) and optionally test via verdaccio/yarn link

3) Publish prerelease (requires npm permissions; run from each package dir)
- npm version prerelease --preid=rc
- npm publish --access public --tag next

Notes
- Do not change runtime behavior; only metadata and artifact inclusion.
- Keep semver discipline; bump rc tag when pushing changes.

### Phase 3 — Host Switch to npm packages
1) Replace workspace deps with semver ranges in host package.json
- "@renderx-plugins/canvas": "^0.1.0-rc.x"
- "@renderx-plugins/canvas-component": "^0.1.0-rc.x"

2) Install and verify
- npm install
- npm run build && npm test && npm run e2e

3) Preview/CI adjustments
- Ensure Vite pre-bundle picks up the npm packages (optimizeDeps/include if needed)
- Keep manifest-based mounting; no repo-relative handlers

### Phase 4 — Split Repositories and Cleanup
1) Create dedicated repositories for both packages
2) Migrate code, tests, and package-local ESLint guardrails
3) Set up their CI (build, test, publish) and semantic-release or equivalent
4) Update docs (USING_CANVAS.md per package, link from host)
5) After soak, remove workspace packages from this repo; keep only host integration/tests

## Consequences
- Host becomes independent of workspace builds for Canvas pieces.
- Faster iteration on packages with dedicated CI and release pipelines.
- Clearer separation of concerns and boundaries, enforced by npm and repo isolation.

## Rollback Plan
- If issues arise, pin host back to workspace packages (or previous rc) and file follow-up issues.

## Open Questions
- Repository naming and ownership for the two packages
- License and README content to publish with packages
- Whether to add sideEffects: false for tree-shaking (needs quick verification)

## Status Notes
- RX_E2E_DIAG env flag documented in ADR-0028 to keep CI logs quiet by default; no change to this plan.

