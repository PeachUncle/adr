# Design: Theme-aware logo and favicon branding

## Overview
This design describes how to align nospeak's branding assets (favicons, app icons, and in-app logo) with the updated white-on-transparent logo and the existing Catppuccin-based theme system. The goal is to:
- Use a Latte Text-tinted logo for all static icons (favicons, PWA icons, notification icons).
- Drive in-app logo color via the existing theme mode and Catppuccin palette rather than hard-coded filters.

## Current State
- The root `nospeak.png` has been updated by the user to a white-on-transparent logo.
- Favicons and PWA icons under `static/favicons/` are older, non-Lavender variants.
- The chat header logo in `ChatView.svelte` uses `/nospeak.png` with an inline CSS filter to approximate a violet color, not directly tied to theme variables.
- The Settings → About view shows `/nospeak.png` without theme-aware colorization.
- `src/lib/stores/theme.ts` defines Catppuccin Latte, Frappe, Macchiato, and Mocha palettes and provides `applyTheme` / `applyThemeMode`, which:
  - Export CSS variables like `--color-lavender` and `--color-text` on the `:root` element.
  - Toggle the `dark` class on `<html>` when the effective theme is Frappe, Macchiato, or Mocha.
- Theme mode selection (System / Light / Dark) is already specified under the `settings` spec and implemented in the Settings General section.

## Design Decisions

### D1: Use Latte Lavender for all static icon assets
All browser favicons, PWA icons, and notification/badge icons will be rendered using the Latte Lavender color (`#7287fd`). This ensures consistent branding in browser chrome, OS app switchers, and notifications regardless of the active runtime theme mode.

- Source: a single high-resolution Latte Lavender-tinted PNG derived from the updated white-on-transparent logo.
- Outputs: `favicon-16x16.png`, `favicon-32x32.png`, `favicon-192x192.png`, `favicon-512x512.png`, `apple-touch-icon.png`, and `favicon.ico`, all stored under `static/favicons/`.
- Notification icon: either `favicon.svg` or a dedicated PNG (e.g., `notification-icon.png`) using the same Latte Lavender logo.

### D2: Centralize in-app logo styling via CSS
Instead of repeating inline filters on each `<img src="/nospeak.png">`, a shared CSS class (e.g., `.app-logo`) will control color behavior:

- The base logo asset is the white-on-transparent `nospeak.png` served from `static/`.
- `.app-logo` will:
  - Ensure consistent rendering (block display, antialiasing, and any shared layout tweaks).
  - Apply a colorizing filter in bright/light mode so the logo appears in Latte Lavender.
  - Disable or alter the filter under `.dark` so the logo appears visually white against dark backgrounds, matching Catppuccin Frappe `text` color.

Because the logo is a bitmap, exact mapping from white to `--color-lavender` / `--color-text` will be approximate when using CSS filters. If future precision is required, the bitmap can be replaced with an SVG version of the logo that uses `fill: var(--color-lavender)` and `fill: var(--color-text)` directly.

### D3: Drive logo appearance from theme mode
The existing theme system already:
- Maps `ThemeMode = 'light'` to Catppuccin Latte.
- Maps `ThemeMode = 'dark'` to Catppuccin Frappe.
- Uses `ThemeMode = 'system'` to pick Latte or Frappe based on `prefers-color-scheme`.
- Applies a `dark` class to `<html>` when the effective theme is Frappe, Macchiato, or Mocha.

The logo styling will rely on these mechanisms rather than duplicating state:
- Bright mode behavior (Latte effective theme) is defined through non-`.dark` selectors (e.g., `:root:not(.dark) .app-logo`).
- Dark mode behavior (Frappe effective theme) is defined through `.dark .app-logo` selectors.

### D4: Scope of UI changes

- **Messaging capability**:
  - Chat header logo (`ChatView.svelte`) uses the shared `.app-logo` class so its color follows the theme.
  - Notification icons (via `NotificationService`) use the new Latte Lavender icon asset.
- **Settings capability**:
  - Settings → About logo uses the shared `.app-logo` class and thus reflects the active theme mode.

No changes will be made to theme selection UI, messaging protocols, or data storage.

## Alternatives Considered

- **Inline filters per usage**: Keeping logo colorization expressed as inline `style` filters in each component was rejected because it is harder to maintain, cannot easily adapt to new theme modes, and duplicates logic.
- **Theme-dependent static assets**: Serving separate static logo files per theme (e.g., `/nospeak-light.png`, `/nospeak-dark.png`) was rejected for now because it complicates asset handling and caching. Using a single white asset plus CSS keeps the implementation minimal while still matching the requested colors closely.

## Risks and Mitigations

- **Approximate color mapping with CSS filters**: Because the logo is a bitmap, filters may not perfectly match `#7287fd` and Frappe `text` color.
  - *Mitigation*: Use the existing, proven violet filter as a baseline and tune if necessary; document the possibility of switching to SVG for exact color control later.
- **PWA icon cache**: Browsers may cache old favicons and PWA icons.
  - *Mitigation*: Update icon contents without changing paths, and document that users may need to hard-refresh or reinstall the PWA to see new icons immediately.
