## Context

Nospeak runs as a Capacitor Android app that embeds the web client. Background messaging today is implemented by:
- A Java foreground service (or, more recently, a Capawesome foreground-service plugin) that only hosts a persistent notification.
- A JavaScript/WebView messaging pipeline that keeps the Nostr connection manager, subscriptions, and notifications running.

On real devices, this design often fails because the OS can suspend or slow down the WebView's JavaScript runtime even when a foreground service exists. The result is that new messages received while nospeak is backgrounded are not decrypted or notified until the user returns to the app.

Android auth has two distinct paths:
- **nsec**: the app holds the user's secret key locally.
- **Amber**: the app never sees the secret key; Amber is the signer.

The existing background messaging spec assumes a single behavior and does not distinguish clearly between these cases. For this iteration, we simplify behavior by keeping native background notifications generic (no sender/content) for both nsec and Amber sessions.

## Goals / Non-Goals

- Goals:
  - Provide a native Android foreground service that can receive new messages and fire generic notifications while the WebView is suspended.
  - Ensure behavior is consistent and privacy-preserving for both nsec and Amber sessions (no native decryption or rich previews).
  - Remove dependence on the Capawesome foreground-service plugin for background messaging behavior.
  - Keep the web client as the sole source of truth for message history and contact management; native code is notification-only.
- Non-Goals:
  - Implement full native message history storage or a parallel Nostr client UI.
  - Implement native decryption and rich sender/content previews at this stage.
  - Change the wire format for gift-wraps, seals, or rumors beyond what nostr-tools already uses.
  - Change desktop or web-only notification behaviors.

## Decisions

- Decision: Implement a dedicated native foreground service (`NativeBackgroundMessagingService`) that owns relay connections, Nostr subscriptions, and Android notifications for background messaging.
  - Rationale: Reliance on WebView for background processing is unreliable on Android. A native service can keep a lightweight Nostr client available even when the UI is not.

- Decision: Keep native behavior generic for all authorization methods: the service treats gift-wrapped events as opaque envelopes and only raises generic "new encrypted message" notifications.
  - Rationale: This respects Amber's security model and avoids expanding the native attack surface with decryption logic, while still giving users a useful indication that messages arrived.

- Decision: Keep the native service notification-only and avoid writing to the web client's IndexedDB or contact repositories.
  - Rationale: Keeps a single source of truth for message history and simplifies reconciliation. After returning to foreground, the web messaging pipeline and history sync continue to own message storage and display.

- Decision: Introduce a new Capacitor plugin `AndroidBackgroundMessaging` with `start`, `update`, and `stop` methods.
  - Rationale: Encapsulates native behavior behind a single JS API and avoids overloading generic foreground-service plugins with Nostr-specific logic.

## Risks / Trade-offs

- Risk: Generic notifications (no sender/content) are less informative than rich notifications, especially for nsec sessions.
  - Mitigation: The web client continues to provide rich sender/content information when active; this change focuses on reliability of background delivery first.

- Risk: Implementing a Nostr client (WebSocket + gift-wrap handling) in native code is still non-trivial.
  - Mitigation: Start with a minimal client that only supports the specific gift-wrap flow nospeak already uses (kind 1059 subscriptions) and relies on event IDs and EOSE to separate history from new events.

- Risk: Duplicate notifications between native and web when the app is foregrounded.
  - Mitigation: Specify that the native service is primarily for background; in foreground the web client can remain the dominant source of notifications. Use event IDs and basic deduplication if needed.

## Migration Plan

1. Spec stage (this change):
   - Update `android-app-shell` to specify that Android background messaging is provided by a native foreground service, not a WebView-based service, and that it uses generic envelope notifications for both nsec and Amber sessions.
   - Update `messaging` spec to state that Android background delivery is handled by the native foreground service using generic notifications.

2. Implementation (change application):
   - Implement `NativeBackgroundMessagingService` that:
     - Accepts `npub` (derived pubkey), optional `nsec` (for future use), and `readRelays` via Intent extras.
     - Connects to read relays and subscribes to gift-wrap events (`kind: 1059`, `#p: [pubkey]`).
     - Uses EOSE and event IDs to distinguish history from new events.
     - Shows generic "new encrypted message" notifications for new events while the UI is backgrounded.
     - Runs as a foreground service with its own notification channel and persistent notification describing connected relays.
   - Implement a new Capacitor plugin `AndroidBackgroundMessaging` that exposes `start`, `update`, and `stop` to the JS layer.
   - Update the web `BackgroundMessaging` helper and Settings to:
     - Detect auth method for explanatory copy.
     - Always use generic native background notifications regardless of auth method.
   - Remove the Capawesome foreground-service plugin and the legacy JS/WebView-based background messaging path.

3. Validation:
   - Verify on real devices that:
     - New messages generate generic notifications while the UI is backgrounded and WebView appears inactive.
     - No flood of notifications appears when enabling background messaging due to historical events.
     - Returning to the app shows messages in the correct conversations without duplicates, powered by the existing web history sync.

## Open Questions

- Do we want to introduce a future, opt-in mode for nsec sessions that enables richer native notifications, and if so, how should that be surfaced in Settings?
- Do we need a small grace period or debounce for native notifications to avoid spamming if multiple relays send the same gift-wrap event quickly?
