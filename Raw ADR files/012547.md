## Context
Relay Connections is currently surfaced as a desktop modal but behaves more like a separate window on mobile/Android, which breaks the unified glassmorphism app-window metaphor and feels inconsistent with the first-time sync progress experience. The app already has a glassmorphism modal pattern (e.g., SyncProgressModal) rendered from the root layout.

## Goals / Non-Goals
- Goals:
  - Unify Relay Connections presentation as a modal overlay across desktop and mobile/Android.
  - Reuse the existing glassmorphism modal visual language and motion used by the first-time sync modal.
  - Keep routing and navigation behavior simple (no new routes) by relying on the existing modal host.
- Non-Goals:
  - Redesign the contents or fields of Relay Connections.
  - Change underlying relay discovery/connection algorithms.
  - Alter first-time sync logic or scenarios beyond visual alignment.

## Decisions
- Decision: Implement Relay Connections as a modal driven by the existing global modal store/host (same layer as SyncProgressModal and ManageContactsModal) rather than a separate mobile window.
- Decision: Share or mirror the same tailwind-style glassmorphism surface classes (background, blur, border, shadow, rounded corners) used by the SyncProgress modal for the Relay Connections modal container.
- Decision: Ensure the modal is blocking (disables interaction with underlying chat UI) on both desktop and mobile, matching first-time sync behavior.

## Risks / Trade-offs
- Risk: If the modal host is heavily used, adding another root-level modal could increase perceived complexity of modal state management.
  - Mitigation: Follow the existing modal store patterns and keep Relay Connections state isolated and well-named.
- Risk: On small mobile screens, a full-screen glass modal might compete with the main app window aesthetic.
  - Mitigation: Match the existing SyncProgress modal layout and verify spacing and scroll behavior for long content.

## Migration Plan
- Implement the new modal behavior and styling behind the existing Relay Connections entry point.
- Remove or stop using any mobile-specific window/route used for Relay Connections.
- Manually verify behavior on desktop, mobile web, and Android shell builds.

## Open Questions
- Should Relay Connections be dismissible via swipe or back gesture on Android, or only via explicit close controls?
- Are there future Relay-related diagnostics that should also share this modal pattern (e.g., per-relay health details)?
