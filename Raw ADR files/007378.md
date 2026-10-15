# ADR-012: Build & Deployment Workflow (Parcel + GitHub Actions)

## Status
Accepted

## Context
As CharacterCraft Lite transitioned from a single-file prototype to a modular ES6+ codebase, we needed a consistent and repeatable process for:

- Bundling JS modules into a single deployable file (for standalone/offline use)
- Generating the public assets (HTML, manifest, icons) for GitHub Pages
- Injecting version metadata into `version.json`
- Publishing updates automatically on merge to `main`

We considered several build tools and deployment strategies. Simplicity and flexibility were the key drivers.

## Decision
We adopted the following build and deployment workflow:

### Tooling
- **Parcel** for bundling ES modules and generating a single-page app
  - Requires minimal config
  - Supports PWA features
  - Friendly for small/modular front-end projects
- **GitHub Actions** for CI/CD
  - Triggers on push to `main`
  - Runs `npm run build` to compile site
  - Automatically deploys to the `gh-pages` branch via `peaceiris/actions-gh-pages`
  - Optionally updates the version number in `version.json`

### Commands
```bash
npm run build      # Builds production-ready app with Parcel
npm run preview    # Launches local server to test built output
npm run deploy     # Custom script to trigger GitHub Actions (if local push not preferred)
```

### Structure
```
root/
├── .github/workflows/deploy.yml
├── src/
│   ├── index.html
│   ├── js/...
│   ├── style.css
├── dist/           # Parcel output
├── version.json    # Updated automatically
```

## Consequences
✅ Enables modular code during development, without sacrificing portability  
✅ Builds both a modern PWA and a downloadable standalone HTML bundle  
✅ Provides repeatable, low-maintenance deployment via GitHub Actions  
⚠️ Ties build process to Parcel (future switch requires migration)
⚠️ Version bump logic must remain aligned with Git history (currently manual or scripted)

## Future Considerations
- Consider switching to version tagging or semver via GitHub Releases
- Extend the GitHub Action to run tests or linting before deploy
- Consider adding a `build:standalone` target to explicitly generate the downloadable single-file version

---

*This decision aligns with our priorities of modern workflows, low-friction contribution, and automated delivery.*

