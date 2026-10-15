# ADR-0035 — Externalize JSON Components to NPM and Discovery via `renderx.components`

- Status: Accepted
- Date: 2025-09-24
- Related Issue: https://github.com/BPMSoftwareSolutions/renderx-plugins-demo/issues/237

## Context

This repository is a thin host and should not own plugin/component data. Historically, JSON component catalogs (e.g., button.json, input.json) lived under `catalog/json-components/` and were copied to `public/json-components/` for the dev server and build steps. As part of decoupling and reuse, component JSON catalogs are being externalized to a separate NPM package so multiple hosts can consume them without copying source.

The new package, `@renderx-plugins/components` (>= 0.1.0), publishes one or more directories that contain JSON component definitions. Packages declare these directories using a `renderx.components` field in their `package.json`.

Example:

```
{
  "name": "@renderx-plugins/components",
  "version": "0.1.0",
  "renderx": {
    "components": ["json-components"]
  }
}
```

## Decision

- The host will discover component catalogs from installed packages by scanning `node_modules` for packages whose `package.json` contains a `renderx.components` string array. Each listed directory is copied to `public/json-components/`.
- During the transition, any repo-local `catalog/json-components/` files will also be copied only if a file with the same name was not already provided by a package (i.e., prefer package over local to avoid duplication and drift).
- Build artifacts continue to include `json-components/` by reusing existing `scripts/build-artifacts.js` copy logic (no change required).

## Changes

- `scripts/sync-json-components.js` enhanced to:
  - Discover and copy from `node_modules/*` and `node_modules/@scope/*` when `renderx.components` is declared
  - Copy local `catalog/json-components/` files only for items not already provided by packages
  - Default `--srcRoot` remains `catalog/`; `--outPublic` remains `public/`
- Documentation updated in `README.md` to describe the discovery mechanism and precedence.
- Added this ADR documenting the boundary and approach.

## Alternatives Considered

- Keeping host-owned `json-components` only — rejected due to coupling and duplication across hosts.
- Hardcoding specific package names — rejected; discovery via manifest field is more extensible and avoids hardcoded lists.

## Consequences

- The host dev server and builds no longer require local `catalog/json-components/` to function, provided `@renderx-plugins/components` (or compatible packages) are installed.
- Teams can publish additional component sets without modifying the host; the host will discover them via the `renderx.components` field.
- If both local and package catalogs exist, the package versions take precedence to avoid duplication. Local files can be removed once migration is complete.

## Migration Notes

- Install the components package in the host: `npm install @renderx-plugins/components@0.1.0`.
- Ensure `npm run pre:manifests` (or `npm run dev` / `npm run build`) executes `scripts/sync-json-components.js` so `public/json-components/` is populated from packages.

## Acceptance Criteria (from Issue #237)

- Host dev server populates `public/json-components/` from the package (no local required)
- Library panel and drag/drop continue to work as before
- ESLint rules over `public/json-components` remain green
- CI passes with all tests and lint

## References

- Issue #237
- `scripts/sync-json-components.js`
- `scripts/build-artifacts.js`
- `src/domain/components/inventory/inventory.service.ts` (unchanged)

