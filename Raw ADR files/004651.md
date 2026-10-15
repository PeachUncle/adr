# ADR-001: Telegram as Cloud Storage Backend

Status: Accepted
Date: 2025-12-17
Owner: User
Related Features: docs/Features/cloud-backup.md
Supersedes: N/A
Superseded by: N/A

---

## Context

We need a cloud storage solution for photo backup that provides:
- Unlimited storage capacity
- No recurring costs
- Strong privacy (user controls the data)
- Cross-platform access

Traditional cloud storage (Google Drive, iCloud, Dropbox) has limitations:
- Storage quotas requiring paid upgrades
- Privacy concerns with data mining
- Vendor lock-in

---

## Decision

Use Telegram Bot API as the cloud storage backend.

Key points:

- Photos are uploaded as documents to a private Telegram channel
- Bot token and channel ID are stored in expo-secure-store
- Files are referenced by Telegram's `file_id` for retrieval
- Message IDs are stored for deletion capability

---

## Alternatives considered

### Google Drive API

- Pros: Well-documented, reliable, cross-platform
- Cons: 15GB free limit, requires OAuth flow, data mining concerns
- Rejected because: Storage limits and privacy

### Firebase Storage

- Pros: Easy integration, real-time sync
- Cons: Pay-as-you-go pricing, Google dependency
- Rejected because: Cost at scale

### Self-hosted (S3-compatible)

- Pros: Full control
- Cons: Requires server infrastructure, costs
- Rejected because: Complexity and cost for personal use

---

## Consequences

### Positive

- Unlimited storage (Telegram doesn't limit channel storage)
- Free to use (no API costs)
- Strong E2E encryption option available
- User owns their data completely

### Negative / risks

- Telegram API rate limits (30 msg/sec to same chat)
- 50MB per file limit for bots
- Telegram policy changes could affect service
- Mitigation: Store local backups of file_ids for data portability

---

## Impact

### Code

- Affected modules: `lib/telegram/botApi.ts`, `lib/database/`
- New boundaries: All Telegram communication goes through `TelegramBotApi` class

### Data / configuration

- Data model: `photos` table stores `remoteId` (file_id) and `messageId`
- Config: Bot token in secure store, channel ID in settings
- Backwards compatibility: N/A (new project)

### Documentation

- Feature docs: docs/Features/cloud-backup.md
- Notes for AGENTS.md: Telegram rate limits documented in Rules section

---

## Verification

### Test environment

- Environment: Android emulator with Expo development build
- Data: Test bot token from @BotFather, private test channel

### Test flows

| ID | Scenario | Level | Expected result | Notes |
| --- | --- | --- | --- | --- |
| TST-001 | Upload photo | Device | Photo appears in Telegram channel | Use small test image |
| TST-002 | Download photo | Device | Photo downloaded and viewable | Use file_id from upload |
| TST-003 | Delete photo | Device | Message deleted from channel | Verify messageId works |
| TST-004 | Rate limit handling | Device | Retry with backoff | Upload 50+ images quickly |

---

## References

- Telegram Bot API: https://core.telegram.org/bots/api
- CloudGallery (reference): ../cloudgallery-ref/
