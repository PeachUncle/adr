## Context
Android currently avoids overlapping the system status bar by reserving space via hard-coded top padding (`pt-10`) that only applies when running inside the Android native shell. At the same time, the Capacitor `StatusBar` helper configures the status bar to not overlay the WebView, meaning the app cannot take full advantage of edge-to-edge layouts or system-provided safe-area insets.

## Goals / Non-Goals
- Goals:
  - Use Android edge-to-edge window insets instead of hard-coded padding.
  - Centralize safe-area handling in CSS using `env(safe-area-inset-*)` so overlays and root layout behave consistently.
  - Use Capacitor `StatusBar` APIs to manage overlay and theme-appropriate icon style.
- Non-Goals:
  - Do not introduce new navigation patterns or gesture handling.
  - Do not change existing messaging or notification semantics beyond layout and status bar presentation.

## Decisions
- Decision: Enable edge-to-edge in `MainActivity` and let the web UI own status bar spacing using safe-area CSS.
  - Rationale: This matches modern Android design guidance and avoids device-specific magic numbers in the web layout.
- Decision: Use CSS `env(safe-area-inset-top|bottom)` for Android layout and modal overlays, guarded so that non-supporting platforms effectively see zero padding.
  - Rationale: Keeps logic declarative in CSS and works both in the Android WebView and standard browsers that expose safe-area env variables.
- Decision: Integrate Capacitor `StatusBar` overlay and style control into the existing `configureAndroidStatusBar` helper, and optionally into theme application so icon contrast tracks light/dark theme.
  - Rationale: Keeps Android-specific status bar behavior confined to a single helper and avoids sprinkling plugin calls throughout the UI.

## Risks / Trade-offs
- Risk: Some Android devices or WebView versions may expose safe-area env variables differently, leading to under- or over-padding at the top or bottom.
  - Mitigation: Use conservative `env(..., 0px)` fallbacks and test on notch and non-notch devices; keep CSS utilities simple so they are easy to adjust.
- Risk: Changing to edge-to-edge could briefly regress layout if safe-area utilities are misapplied or missed in key surfaces.
  - Mitigation: Replace all known Android-only `pt-10` usages in a single pass and validate primary flows (login, chat, modals) on Android and web.

## Migration Plan
1. Update `MainActivity` to use edge-to-edge insets while keeping the WebView full-screen.
2. Update the Capacitor `StatusBar` helper to overlay the WebView and accept a theme-aware style.
3. Add global CSS safe-area utilities and apply them to the root layout and modal overlays instead of `pt-10`.
4. Validate behavior on Android devices/emulators and on desktop/mobile web.

## Open Questions
- Should the Android app also hide or minimize the navigation bar for a fully immersive experience, or is status-bar edge-to-edge sufficient?
- Should we add horizontal safe-area padding for devices with strongly curved corners, or is vertical-only padding enough for now?
