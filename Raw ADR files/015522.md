# ADR-0024 — Phase 2: SDK Hardening & Artifact Integrity

Status: Proposed (Phase 2)

## Context
Phase 1 established an artifact pipeline and manifest-driven runtime registration. Before extracting repos we need a stable, minimal Host SDK surface and reproducible artifact integrity to support remote consumption & potential CDN caching.

## Goals
1. Harden `@renderx/host-sdk` public API (typed surface + d.ts package output plan)
2. Add artifact integrity (hash manifest + JSON assets) to enable cache busting & verification
3. Add optional runtime verification (compare hash file vs recalculated in dev)
4. Provide watch-friendly `build-artifacts --watch` pathway (Phase 2 scope: design + stub)
5. Prepare ESLint rules for out-of-repo plugin development (path configuration hook)

## Non-Goals (Future Phases)
- Publishing to npm
- Full repo extraction automation pipeline
- CDN upload tooling

## Decisions (Proposed)
| Topic | Decision |
|-------|----------|
| SDK Export Policy | Create `packages/host-sdk/public-api.ts` enumerating allowed exports; index.ts re-exports only from that file |
| Type Stability | Add `api-report.md` generation stub (Rush-like concept, lightweight script) for manual diff |
| Artifact Hashing | Generate `artifacts.integrity.json` with SHA256 per file + combined hash |
| Integrity Validation | Host on startup (dev only) warns if any public manifest file hash mismatches |
| ESLint Rules Externalization | Add env var `RENDERX_PLUGINS_SRC` to point rules at external plugin repo root |
| Watch Mode | Provide `scripts/build-artifacts.js --watch` placeholder (no incremental yet) |

## Risks
- Hash generation cost on large asset sets (mitigated by limiting to *.json + size < 2MB)
- Plugin authors importing internal paths (mitigated by lint + narrowed export surface)

## Migration Steps
1. Introduce `public-api.ts` & refactor `index.ts` to re-export.
2. Add hashing script + integrate into `build-artifacts.js` (optional flag).
3. Add runtime dev validator (skips in production builds or when `RENDERX_DISABLE_INTEGRITY=1`).
4. Document new environment variables & workflow.

## Success Metrics
- Test suite passes unchanged
- `npm run build` emits integrity file with stable hash set
- Manual tamper with a JSON artifact triggers dev warning

## Open Questions
- Do we embed hash references inside each manifest? (Deferred; outer integrity file sufficient.)
- Do we sign artifacts? (Deferred until distribution requirements clarified.)

---

Authored: Phase 2 Planning
