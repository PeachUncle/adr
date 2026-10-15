# ADR-004: Implement Local-First Data Strategy

**Status:** Accepted
**Date:** 2025-11-24
**Decision Makers:** Development Team, Privacy Officer
**Technical Story:** Privacy and Security Requirements

## Context

We needed to decide where to store user data for the Wardrobe Consultant app. Key considerations:
- User privacy is a core value
- Wardrobe data is highly personal
- Users may have sensitive information (measurements, photos)
- Network connectivity may be unreliable
- App should work offline
- Must comply with GDPR, CCPA, and other privacy regulations

## Decision

We will implement a **local-first data strategy** where:

1. **All data stored on-device by default**
   - Core Data for structured data
   - File system for photos
   - Keychain for sensitive information

2. **No cloud storage in v1.0**
   - No server-side database
   - No user accounts required
   - No data transmission to our servers

3. **Optional cloud sync in future versions**
   - Will use iCloud (Apple's infrastructure)
   - User opt-in required
   - E2E encryption where possible

4. **Processing happens on-device**
   - AI recommendations computed locally
   - No server-side processing
   - All algorithms run in-app

## Consequences

### Positive

**Privacy**
- Maximum user privacy - data never leaves device
- No server breaches possible
- Compliance with privacy laws by default
- User maintains complete control
- No user accounts or authentication needed

**Performance**
- Instant data access (no network latency)
- Works fully offline
- No server costs or scaling issues
- Consistent performance regardless of location

**User Experience**
- No internet required for core features
- No login/signup friction
- Immediate app usage after install
- No "sync" delays or conflicts

**Business**
- No server infrastructure costs
- No database hosting fees
- Simpler compliance requirements
- Lower operational complexity

### Negative

**Features**
- No multi-device sync (initially)
- No collaborative features
- No cloud backup
- No server-side analytics

**User Concerns**
- Data lost if device lost (without iCloud backup)
- Can't easily transfer to new device
- No access from multiple devices
- Users may expect cloud features

**Development**
- Future cloud sync will be complex
- Migration to cloud model requires careful planning
- May need to refactor for cloud features later

### Risks

**Data Loss**
- Users could lose data if device fails
- **Mitigation**: Implement iCloud backup, export functionality

**Feature Expectations**
- Users may expect multi-device sync
- **Mitigation**: Clear communication in onboarding and marketing

**Competitive Pressure**
- Competitors may offer cloud features
- **Mitigation**: Emphasize privacy as competitive advantage

## Alternatives Considered

### Cloud-First with Server Storage
- **Pros**: Multi-device sync, backup, collaborative features
- **Cons**: Privacy concerns, server costs, compliance complexity, requires authentication
- **Rejected**: Conflicts with privacy-first value proposition

### Hybrid Approach (Local + Cloud)
- **Pros**: Best of both worlds
- **Cons**: Complex to implement, sync conflicts, privacy still a concern
- **Rejected**: Too complex for v1.0, can be added later

### iCloud-Only
- **Pros**: Apple's infrastructure, no our servers needed, better sync
- **Cons**: Requires Apple account, some privacy concerns, vendor lock-in
- **Rejected**: Want to work without any account initially

### Peer-to-Peer Sync
- **Pros**: No central server, privacy preserved
- **Cons**: Complex implementation, unreliable, limited use cases
- **Rejected**: Technical complexity too high

## Implementation Details

### Data Storage

**Core Data**
```swift
// In-memory for tests, on-disk for production
let container = NSPersistentContainer(name: "WardrobeConsultant")
container.persistentStoreDescriptions.first?.setOption(
    FileProtectionType.complete as NSObject,
    forKey: NSPersistentStoreFileProtectionKey
)
```

**Photo Storage**
```swift
// File system with encryption
let photoURL = FileManager.default.urls(
    for: .applicationSupportDirectory,
    in: .userDomainMask
).first!
// Files protected with NSFileProtectionComplete
```

**Sensitive Data (Measurements)**
```swift
// Keychain Services
let keychain = KeychainWrapper.standard
keychain.set(measurements, forKey: "userMeasurements")
```

### Future Cloud Sync Design

When implementing cloud sync (v2.0+):

1. **Use CloudKit**
   - Leverages Apple's infrastructure
   - Built-in sync engine
   - User's iCloud account

2. **Opt-In Model**
   - Default remains local-only
   - User explicitly enables sync
   - Clear explanation of data sharing

3. **Conflict Resolution**
   - Last-write-wins for most data
   - Manual resolution for important conflicts
   - Sync only when user initiates

## Privacy Benefits

This decision enables us to honestly state:

✅ "Your data stays on your device"
✅ "We don't store your photos"
✅ "No account required"
✅ "Works completely offline"
✅ "No data sharing or selling"
✅ "Bank-level encryption"

These statements are powerful marketing differentiators and build user trust.

## Performance Benefits

Local-first architecture provides:

- **Instant Response**: No network latency (< 50ms for most operations)
- **Offline First**: 100% functionality without internet
- **Reliable**: No server downtime affects users
- **Scalable**: No server capacity planning needed
- **Cost**: Zero cloud infrastructure costs

## Migration Path

If we need cloud features later:

1. **Phase 1** (v1.0): Local-only ✅ Current
2. **Phase 2** (v1.5): iCloud backup (optional)
3. **Phase 3** (v2.0): CloudKit sync (opt-in)
4. **Phase 4** (v3.0): Collaborative features (if needed)

Each phase maintains backward compatibility with local-only mode.

## Success Metrics

This decision is successful if:

- ✅ Zero data breaches (impossible with no server)
- ✅ 5-star privacy ratings
- ✅ "Privacy-first" mentioned in reviews
- ✅ Works perfectly offline
- ✅ Data access < 50ms average
- ✅ No server costs

## References

- [Local-First Software](https://www.inkandswitch.com/local-first/)
- [Apple File System Security](https://developer.apple.com/documentation/uikit/protecting_the_user_s_privacy/encrypting_your_app_s_files)
- [GDPR Data Minimization](https://gdpr-info.eu/art-5-gdpr/)
- [Apple Keychain Services](https://developer.apple.com/documentation/security/keychain_services)

## Review History

- 2025-11-24: Initial proposal
- 2025-11-24: Privacy review completed
- 2025-11-24: Accepted unanimously

---

**Related ADRs:**
- [ADR-003: Use Core Data for Persistence](ADR-003-core-data.md)
- [ADR-008: Store Sensitive Data in Keychain](ADR-008-keychain-storage.md)
- [ADR-010: No Third-Party Analytics](ADR-010-no-third-party-analytics.md)
