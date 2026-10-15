# ADR-0001: Data Sync Strategy

- **Date**: 2025-12-12
- **Status**: Accepted
- **Deciders**: Project Team

---

## Context

TsukiUsagi stores user data locally:
- Session history (`Documents/history.json`)
- Streak/XP data (`UserDefaults`)
- Session configuration (`UserDefaults`)
- Timer state (`@AppStorage`)

Current state:
- No iCloud sync enabled
- No `.entitlements` file
- Data is device-local only

User concerns:
- Device migration loses all history
- No cross-device sync (iPhone ↔ iPad)
- Factory reset loses progress

---

## Decision

**Phased approach to data persistence, prioritizing simplicity over full sync.**

### Phase 1: Local Hardening (v1.3) ✅ Completed
- Synchronous save for crash safety
- Error logging for debugging
- Background transition save

### Phase 2: Export/Import (v1.4) 📋 Planned
- Manual JSON export to Files app
- Manual import for device migration
- User-controlled, no sync complexity

### Phase 3: Evaluate Sync Need (v1.5+)
- Collect user feedback
- Monitor App Store reviews for "sync" requests
- Analyze usage patterns (single vs multi-device)

### Phase 4: CloudKit (v2.0) 🔮 Future
- Only if Phase 3 shows clear demand
- Start with History only
- Consider `NSUbiquitousKeyValueStore` for settings (1MB limit)

---

## Alternatives Considered

### Option A: Implement CloudKit Now
- **Pros**: Full sync, future-proof
- **Cons**: High complexity, conflict resolution, debug difficulty
- **Decision**: Rejected for v1.x

### Option B: NSUbiquitousKeyValueStore Only
- **Pros**: Simple, automatic sync for small data
- **Cons**: 1MB limit excludes History
- **Decision**: Possible for settings in future, not for History

### Option C: Export/Import First
- **Pros**: Low complexity, user control, validates need
- **Cons**: Manual process, not automatic
- **Decision**: **Accepted** as Phase 2

---

## Consequences

### Positive
- Codebase stays simple ("Silent Rabbit" philosophy)
- No sync-related bugs or support burden
- Export/Import validates user need before investing in CloudKit

### Negative
- No automatic cross-device sync in v1.x
- Users must manually export before device migration

### Mitigation
- Document limitation clearly in app and Docs
- Provide easy Export/Import flow
- Re-evaluate based on user feedback

---

## Roadmap Summary

| Version | Feature | Complexity |
|---------|---------|------------|
| v1.3 | Local save hardening | ✅ Done |
| v1.4 | Export/Import (JSON) | Low |
| v1.5+ | Feedback collection | - |
| v2.0 | CloudKit (if needed) | High |

---

## References

- [report-history-sync-save.md](../../report/report-history-sync-save.md) - Local save implementation
- [CLAUDE.md](/CLAUDE.md) - Technical debt notes
- Apple Documentation: [CloudKit](https://developer.apple.com/documentation/cloudkit)
- Apple Documentation: [NSUbiquitousKeyValueStore](https://developer.apple.com/documentation/foundation/nsubiquitouskeyvaluestore)
