# ADR-005: Update Check Strategy

## Status
Accepted

## Context
CharacterCraft Lite is available in two forms: a hosted PWA and a downloadable single-file version. To ensure users of the downloadable version are aware when updates are available, we wanted a lightweight update-check mechanism.

This check needs to:
- Work without requiring a backend or database
- Notify users if a newer version is available
- Respect offline-first principles (fail silently)
- Avoid introducing complex tooling or dependencies

## Decision
We implemented a version check using a static `version.json` file hosted in the GitHub Pages deployment. The app fetches this file at load time and compares it to the current version hardcoded in the app.

### Mechanism
1. The current app version is injected into the `update-check.js` script at build time using a GitHub Actions workflow.
2. On app load, the script fetches `https://character-craft.github.io/lite/version.json`
3. If the version number in the JSON is higher than the current version, a message is shown in the console and/or UI
4. If the fetch fails (e.g., offline), no error is shown

This strategy avoids cross-origin issues (same domain), does not require dynamic server logic, and fits both PWA and offline-lite modes.

### Example `version.json`
```json
{
  "version": "1.2.0"
}
```

### GitHub Actions Support
A `deploy.yml` workflow includes a `sed` or script step to update `version.json` during deployment, ensuring accuracy.

## Consequences
✅ Enables users to detect updates to the tool
✅ Keeps offline users from seeing errors
✅ Requires no additional backend or infrastructure
✅ Can be extended with notification UI later
⚠️ Relies on a consistent and manual versioning process
⚠️ Requires maintenance of `version.json` in sync with deployments

## Alternatives Considered
- Auto-checking GitHub releases (more complex, more fragile)
- Prompting based on service worker cache (less transparent)
- No version checking (users miss updates)

## Future Considerations
- Add a UI indicator for update availability (e.g., “New version available” toast)
- Extend the check to include changelogs or auto-refresh links
- Refactor update-check logic into a shared utility for reuse in PWA and SaaS versions

---

*This supports our values of user transparency, lightweight tooling, and progressive enhancement.*

