# ADR-014: Versioning Strategy

## Status
Accepted

## Context
CharacterCraft Lite is designed as a fully client-side, offline-capable web application distributed as:

- A **PWA** hosted on GitHub Pages
- A **standalone downloadable HTML file**

To support update checks and user-facing transparency, we include a `version.json` file in the root of the app that stores the current version.

We do **not** use traditional npm versioning, nor GitHub Releases, as our primary delivery mechanism. However, Git history and repo tags remain important.

## Decision
We adopted a simple versioning strategy using a `version.json` file in the format:

```json
{
  "version": "1.2.0",
  "lastUpdated": "2025-03-23"
}
```

- `version` is a human-readable string, updated manually or via GitHub Actions
- `lastUpdated` reflects the date of the last deployment or build
- The frontend `update-check.js` script fetches this and compares against a locally cached version to display an update banner if needed

This approach supports:
- User awareness of new releases
- Offline-first architecture (local cache comparison)
- CI/CD integration with our Parcel-based build and deploy

### Why not use GitHub Releases?
- We want versioning tied to the **deployed application**, not just the source
- Releases are not required to ship updates via Pages or PWA
- `version.json` is human-readable and easier to update via scripts

## Consequences
✅ Enables version check even when offline (once cached)  
✅ Clear separation of UI versioning from Git history  
✅ Works for both web and downloadable versions  
⚠️ Manual version bumps are error-prone without automation  
⚠️ No formal semver guarantees (though we loosely follow it)

## Future Considerations
- Automate version bumping in `version.json` via GitHub Actions or pre-deploy hooks
- Optionally publish tagged GitHub releases for major milestones
- Add a `--build-id` or commit hash for traceability in future diagnostics

---

*This strategy favors simplicity, visibility, and offline-awareness, consistent with our frontend-first and PWA principles.*

