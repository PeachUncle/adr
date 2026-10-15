## Context
nospeak supports message and reaction notifications on web (Notifications API / service worker) and Android (Capacitor local notifications + an optional native foreground service for background messaging). Today:
- The Settings toggle for message notifications defaults to off.
- Android background messaging is separately toggled and can emit notifications while the app is backgrounded.
- Users can end up with background messaging enabled but notifications disabled, or not understand which toggle controls what.

## Goals / Non-Goals
- Goals:
  - Make Notifications and Android Background Messaging opt-out by default for new installs/devices.
  - Ensure OS permission prompts happen during explicit user actions (login), not during background restore.
  - Prevent inconsistent states (e.g., background messaging running while notifications are disabled).
  - Reduce UI confusion by renaming and conditional visibility.
- Non-Goals:
  - Change notification content, grouping, or routing logic.
  - Change NIP-17/NIP-44 messaging semantics.
  - Add a new onboarding flow or multi-step permissions UI.

## Decisions
- Decision: Interpret missing settings keys as enabled.
  - `notificationsEnabled` is treated as enabled unless explicitly stored as `false`.
  - `backgroundMessagingEnabled` is treated as enabled unless explicitly stored as `false`.
  - Rationale: preserves existing opt-out semantics while keeping storage format stable.

- Decision: Prompt for notification permission once per device on explicit login.
  - Trigger points: `login(nsec)`, `loginWithAmber()`, `loginWithExtension()`.
  - Avoid prompting during `restore()` to keep silent startup behavior and avoid surprise prompts.
  - A localStorage sentinel is used to ensure the prompt is shown at most once per device.

- Decision: Store the prompt sentinel outside the `nospeak:` / `nospeak-` namespace.
  - Current logout cleanup removes keys that start with `nospeak:` or `nospeak-`.
  - Use a key like `nospeak_notifications_permission_prompted` so it persists across logouts.
  - Rationale: prevents repeated prompting for users who sign out/in frequently.

- Decision: Background Messaging is contingent on Notifications.
  - If Notifications are disabled, Background Messaging is automatically disabled and the Android foreground service is stopped.
  - The Background Messaging toggle is hidden when Notifications are disabled to avoid implying it is actionable.
  - Rationale: background messaging is primarily valuable for delivering notifications while backgrounded; if the user opts out of notifications, we should not keep a persistent foreground service running.

- Decision: Add a native boot guard for background messaging when Notifications are disabled.
  - Even if background messaging was previously enabled, the Android boot receiver MUST NOT start the service when notifications are disabled.
  - Rationale: ensures the “Notifications off” preference is respected even when the WebView is not running.

## Risks / Trade-offs
- Defaulting notifications to enabled may increase the rate of OS permission prompts.
  - Mitigation: only prompt on explicit login (user-driven) and only once per device.
- Some users may still have OS-level permission denied.
  - Mitigation: the app remains functional; notifications simply do not appear, consistent with existing behavior.

## Migration Plan
- No migration step is required for stored settings:
  - Existing explicit `notificationsEnabled: false` and `backgroundMessagingEnabled: false` remain respected.
  - Missing keys are treated as enabled.
- Optional: during implementation, persist explicit `true` defaults when Settings is opened to make debugging easier, but this is not required for behavior.

## Open Questions
- None (user specified: default-on, hide background messaging when notifications off, prompt on login, set prompt flag before requesting permission).
