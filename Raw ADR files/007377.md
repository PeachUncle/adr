# ADR-011: Hosting Strategy (GitHub Pages + Offline-First PWA)

## Status
Accepted

## Context
CharacterCraft Lite is designed to be simple to use, easy to share, and accessible even without a backend. From the outset, we wanted a way to:

- Distribute a **hosted version** users can access without setup
- Allow users to **download a standalone version** for offline or portable use
- Support **PWA features** like installability, caching, and offline fallback
- Avoid the overhead of managing infrastructure or paid hosting services

GitHub Pages offered a natural fit:
- Free and reliable static site hosting
- HTTPS by default
- Simple integration with GitHub Actions for CI/CD
- Publicly viewable with minimal setup

## Decision
We chose to **host the CharacterCraft Lite app using GitHub Pages**, backed by an **offline-first Progressive Web App (PWA)** implementation.

### Key Implementation Details
- The site is served via GitHub Pages from the `gh-pages` branch (auto-deployed)
- PWA features are enabled via `manifest.json`, `service-worker.js`, and proper caching strategies
- The same source code can be bundled into a **single HTML file** for easy distribution

This allows for two usage modes:

| Mode        | Description                                           |
|-------------|--------------------------------------------------------|
| Hosted App  | Served from `https://{user}.github.io/charactercraft-lite/` with full PWA features |
| Downloadable | Single HTML file with embedded CSS/JS and offline support |

## Consequences
✅ Simplifies hosting — no server or backend needed  
✅ Enables installation as an app (Add to Home Screen)  
✅ Zero cost to maintain or scale  
✅ Allows easy sharing via URL or file  
⚠️ No server-side logic or database (by design)
⚠️ Static file limits imposed by GitHub Pages (workaround: future API backend in Pro version)

## Future Considerations
- The **Pro Edition** may use API endpoints or dynamic generation — likely requiring a separate deployment strategy (e.g. Vercel, Render, or self-hosted backend)
- If GitHub Pages limits become restrictive, consider using Netlify or Cloudflare Pages
- Future enhancement: Allow local-first version to check for updates via GitHub release API

---

*This decision supports our philosophy of simplicity, portability, and progressive enhancement.*

