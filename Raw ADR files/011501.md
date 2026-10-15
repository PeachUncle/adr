## ADR-0006: Mobile Jellyfin clients (Finamp, Streamyfin) require dedicated build environments

- Date: 2026-01-02T16:05:00.000Z
- Status: Accepted

### Context

During Jellyfin API compatibility testing, we evaluated mobile-focused Jellyfin clients Finamp and Streamyfin for testing against Melodee's Jellyfin API implementation.

**Finamp** (Flutter/Dart):
- Cross-platform mobile app targeting iOS and Android
- Requires Flutter SDK, Android SDK, Xcode (for iOS), and platform-specific toolchains
- Cannot be easily run on a Linux desktop without Android emulator or physical device

**Streamyfin** (React Native/Expo):
- Mobile app using Expo framework
- Requires Expo CLI, Node.js, and either iOS Simulator (macOS only) or Android emulator
- `npx expo start` launches a development server but requires mobile device/emulator to render

### Decision

Melodee will **not maintain local build/test environments** for mobile Jellyfin clients during development.

Instead, API compatibility will be validated through:
1. **API-level testing** via shell scripts (e.g., `test-jellyfin-api.sh`) that exercise all endpoints
2. **Desktop pure-API clients** like Gelly for interactive testing
3. **Community feedback** from users running mobile clients against Melodee

### Rationale

- Setting up Flutter/Android SDK or React Native/Expo with emulators is significant overhead for a .NET server project
- API-level testing provides equivalent coverage for server-side compatibility
- Desktop clients like Gelly use the same Jellyfin API endpoints as mobile clients
- Mobile-specific issues (if any) are more likely UI/UX bugs in the client than API incompatibilities

### Consequences

- Mobile client compatibility is validated indirectly through API tests
- Bugs specific to mobile clients may only surface via community reports
- Documentation should encourage community testing with mobile clients

### Compatible Mobile Clients (Target)

| Client | Platform | API Compatibility |
|--------|----------|-------------------|
| Finamp | iOS/Android | Expected compatible (same API as Gelly) |
| Streamyfin | iOS/Android | Expected compatible (uses @jellyfin/sdk) |
| Symfonium | Android | Expected compatible (pure API client) |

### Testing Strategy

1. Maintain comprehensive `test-jellyfin-api.sh` covering all endpoints used by mobile clients
2. Use Gelly (desktop) for interactive/manual testing during development
3. Document API endpoints and expected responses for community verification
4. Address mobile-specific issues as they are reported

