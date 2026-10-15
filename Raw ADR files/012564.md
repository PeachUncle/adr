## Context
nospeak’s Android background messaging mode runs inside a native foreground service and emits Android OS notifications for decrypted activity. The current implementation already uses `NotificationCompat.MessagingStyle` and can apply a `largeIcon`, but Android’s conversation UI (Android 11+) typically requires notifications to be bound to a conversation shortcut.

Separately, message content should be treated as sensitive on the lockscreen. The implementation must also respect user-customized notification channel settings by avoiding channel recreation.

## Goals / Non-Goals
- Goals:
  - Deliver Android 11+ conversation-style notifications with a prominent contact icon.
  - Show full preview text in the unlocked notification shade.
  - Redact message previews on the lockscreen while still showing the contact name.
  - Preserve user-customized channel settings by using create-if-missing semantics.
- Non-Goals:
  - Inline reply.
  - Native message send / encryption pipeline changes.

## Decisions
- Decision: Use dynamic shortcuts for conversations.
  - Publish a dynamic shortcut per `partnerPubkeyHex` (stable shortcut id).
  - Set `NotificationCompat.Builder.setShortcutId(shortcutId)` on each message notification.
  - Use the contact avatar bitmap (when available) as the shortcut icon.
  - Fallback: continue setting `largeIcon` for pre-Android 11 and for cases where shortcuts are not surfaced.

- Decision: Lockscreen sensitivity via notification-level redaction.
  - Set message notifications to `VISIBILITY_PRIVATE`.
  - Provide `publicVersion` notifications that show the contact name but replace the message body with a generic string (e.g. "New message").
  - Rationale: channel-level lockscreen visibility cannot be safely updated on existing installs without recreating channels (which would wipe user settings).

- Decision: Do not recreate notification channels.
  - Create channels only when missing.
  - Rationale: channel recreation overwrites user customization.

## Risks / Trade-offs
- Existing installs may have a messages channel whose lockscreen visibility is configured to show content. The `publicVersion` + `VISIBILITY_PRIVATE` strategy mitigates this without resetting the channel.
- Conversation shortcut visibility can vary by OEM/launcher. Binding notifications to shortcuts is the correct platform approach; `largeIcon` remains a fallback.

## Migration Plan
- No forced migration of channels; existing channels remain intact.
- First receipt of a message from a contact will create/update the dynamic shortcut for that conversation.

## Open Questions
- None.
