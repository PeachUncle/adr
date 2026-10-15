## Context
nospeak supports Android background messaging via a native foreground service that maintains relay WebSocket connections while the WebView is suspended. Today, this service treats incoming NIP-17 gift-wrap events (kind 1059) as opaque and emits only generic "new encrypted message" notifications.

nospeak also supports Android local notifications via the JS runtime (`NotificationService` + `@capacitor/local-notifications`). This can cause duplicate notifications and does not provide background delivery when the WebView is not executing.

The user wants:
- plaintext previews on Android notifications
- reaction notifications
- tap routing to the correct conversation
- service-only notifications on Android when background messaging is enabled
- Amber-only decryption (no Kotlin crypto port)

## Goals / Non-Goals
- Goals:
  - Decrypt gift-wrap → seal → rumor using Amber (NIP-55) in the native background service.
  - Show plaintext message previews (truncated) and reaction previews.
  - Combine message + reaction activity into a single grouped notification per conversation.
  - Ensure notification taps open the correct `/chat/<npub>` route.
  - Prevent duplicate Android notifications by suppressing JS-driven Android notifications when background messaging is enabled.
  - Improve reliability of "live" detection and dedupe across service restarts.

- Non-Goals:
  - Do not implement on-device NIP-44/NIP-04 decryption in Kotlin/Java.
  - Do not introduce push notifications or server-side delivery.
  - Do not attempt full sender-name/avatar resolution in the native service.
  - Do not redesign Settings UI.

## Decisions
- Decision: Use Amber’s NIP-55 content provider for decryption.
  - Rationale: avoids local key handling and keeps crypto implementation out of the app.

- Decision: Determine "notify vs suppress" by decrypting to the inner rumor and checking `rumor.pubkey != currentUserPubkeyHex`.
  - Rationale: the outer gift-wrap pubkey is not a reliable sender identity.

- Decision: Combine message and reaction notifications into a single per-conversation Android notification.
  - Rationale: reduces notification spam and aligns with the requested UX.

- Decision: Implement tap routing via a lightweight Capacitor plugin that reads intent extras and notifies the web layer.
  - Rationale: mirrors the existing inbound share routing pattern and keeps navigation logic in the Svelte app.

- Decision: When background messaging is enabled, Android notification emission is owned by the native service and JS-driven Android notification scheduling is suppressed.
  - Rationale: avoids duplicates and ensures background delivery when the WebView is suspended.

## Alternatives considered
- Port all decryption to Kotlin/Java.
  - Rejected: higher security surface area and long-term maintenance burden; Amber already provides decrypt for the chosen auth mode.

- Keep notifications in JS and attempt to keep WebView alive.
  - Rejected: unreliable under Android background execution constraints.

## Risks / Trade-offs
- Decryption in background depends on Amber availability and permissions; if Amber rejects or is unavailable, notifications fall back to generic.
- Notifications may not include sender names/avatars until a future enhancement adds native profile caching.
- Android OEM background restrictions may still affect service scheduling; this change improves behavior within the constraints of foreground services.

## Migration Plan
- Ship behind existing toggles:
  - Background messaging enabled controls service lifecycle.
  - Notifications enabled controls whether the service emits message/reaction notifications.
- Preserve generic fallback notifications when decrypt fails.
- Roll out in an Android build and validate on at least one physical device.

## Open Questions
- None for this change; UX choices have been specified (truncate previews, attachment phrase, combined grouping).
