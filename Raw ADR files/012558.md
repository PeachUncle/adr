## Context
Nospeak already supports NIP-17 encrypted DMs and NIP-25 kind 7 reactions within that flow. Reactions are decrypted, stored, and rendered as aggregated emoji chips under each message, but they are not currently wired into the unread contact indicator (green dot) or notification plumbing. The unread indicator is driven solely by message timestamps and `lastReadAt`, and the notification pipeline only fires for new messages, not for reactions. Android background messaging uses a native foreground service that subscribes to gift-wrapped events and raises generic "new encrypted message" notifications without decrypting content.

## Goals / Non-Goals
- Goals:
  - Treat incoming reactions from other participants as conversation activity that can drive unread indicators and foreground notifications.
  - Keep reactions as lightweight activity attached to messages rather than new chat bubbles.
  - Align reaction-driven notifications with existing web and Android notification rules (settings, permissions, and suppression when viewing the active conversation).
  - Preserve the Android background messaging model where the native foreground service continues to raise generic encrypted-message notifications for any relevant gift-wrapped event without learning message contents or distinguishing reactions from messages.
- Non-Goals:
  - Changing how reactions are displayed in the UI under messages.
  - Promoting reactions to standalone message records or bubbles.
  - Altering the core NIP-17/NIP-25 event formats or encryption pipeline.

## Decisions
- Represent reactions as conversation activity: use per-contact activity tracking (for example, a `lastActivityAt` concept) that is updated by both messages and reactions, while leaving the message record format unchanged.
- Keep unread semantics contact-centric: compute the green-dot unread indicator from the difference between a contact's last activity and the last time the user viewed that conversation, so that new reactions alone can make a contact appear unread.
- Add dedicated foreground reaction notifications: introduce reaction-specific notification behavior in the existing notification service, mirroring suppression rules used for messages and navigating back to the relevant conversation when tapped.
- Preserve background service opacity: keep the Android background messaging foreground service behavior generic for all gift-wrapped events (including reactions) and ensure the spec explicitly clarifies that reactions are covered as opaque encrypted messages.

## Alternatives Considered
- **Message-like treatment for reactions**: promote each reaction to a separate message record that could appear in history or drive unread and notifications identically to messages. This was rejected because the current UX deliberately renders reactions as aggregated chips under messages, not as standalone bubbles, and adding message records for each reaction would complicate history semantics and UI.
- **Reusing message notification API directly for reactions**: call the existing "new message" notification path with adapted text for reactions. This was considered but rejected in favor of a small reaction-specific wrapper to keep message and reaction behavior clearly separated while still sharing underlying notification channels and suppression logic.

## Risks / Trade-offs
- Users may perceive reactions as less important than messages; treating them as unread/notification events could increase notification volume. Mitigation: mirror existing suppression rules, and scope reaction notifications only to incoming reactions from other participants.
- Android background messaging is intentionally generic and best-effort; there may still be edge cases where reaction gift-wraps arrive while the app is backgrounded but notifications are suppressed by OS-level policies. This is consistent with existing background messaging constraints.

## Migration Plan
- Implement per-contact activity tracking and reaction-driven updates in a backward-compatible way so existing contacts remain valid.
- Roll out reaction foreground notifications in a way that reuses existing notification channels and settings to avoid additional user configuration.
- Rely on the existing Android background messaging foreground service to continue raising generic notifications for all gift-wrapped events, including reactions, without requiring schema or protocol changes.

## Open Questions
- Should reaction-driven notifications include any short preview text or strictly focus on the fact that a reaction occurred (for example, "Alice reacted ❤️ to your message")?
- Should the unread indicator for reactions clear only when the user opens the conversation that contains the reacted-to message, or is contact-level read semantics (open any part of the conversation) sufficient?
