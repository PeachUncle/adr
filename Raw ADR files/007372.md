# ADR-004: Dual Build Strategy — Lite (Single-File) and PWA (Modular)

## Status
Accepted

## Context
CharacterCraft Lite began as a single HTML file designed to be emailed, downloaded, or opened offline without any dependencies. As the app evolved and gained complexity, we introduced modular code with ES6 imports, a PWA version with service workers, and GitHub-hosted builds.

We now maintain **two builds**:

- A **Lite version**: a single HTML file containing all JS and CSS inline
- A **PWA version**: a modern, modular build using Parcel and GitHub Pages hosting

This dual strategy required explicit tooling and decisions to support both use cases.

## Decision
We will maintain both versions and adopt the following practices:

### PWA Version (default)
- Modular source code using ES6 modules
- Built using Parcel
- Hosted via GitHub Pages
- Provides offline caching, update checks, and clean file separation

### Lite Version (bundled)
- Produced via `parcel build`
- Output flattened into one HTML file with embedded assets
- Distributed for use in educational settings, local demos, and where network constraints exist

We keep the source modular and use Parcel to output both formats:
```bash
parcel build src/index.html --dist-dir dist --public-url ./
```

## Consequences
✅ Accommodates both offline-first usage and modern deployments
✅ Maintains backward compatibility for email/download usage
✅ Uses a single source of truth (modular ES6+ codebase)
✅ Enables clean GitHub Actions automation
⚠️ Increases complexity of the build pipeline slightly
⚠️ Requires extra attention to ensure Lite version functionality remains in sync

## Future Considerations
- We may move the Lite version to a separate branch or subfolder (`/dist-lite`) to reduce confusion
- If a SaaS version is developed, the PWA frontend may evolve into a client for the backend API
- Could introduce a CLI to build only specific targets (e.g., `npm run build:lite`)

---

*This decision supports accessibility, shareability, and progressive enhancement.*

