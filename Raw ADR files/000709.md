## Context
Audixa MVP requires SMB access on Android with true streaming playback and seeking. SMB1 is out of scope; SMB2/SMB3 only. The app must support two profile input formats (`\\host\share` and `smb://host/share`), and must remember passwords securely (no plaintext in SQLite).

## Goals / Non-Goals
- Goals
  - Android: browse SMB shares and play remote MP4 via ExoPlayer with seek support.
  - Persist SMB profiles and remembered credentials securely across app restarts.
  - Keep the design compatible with future transcoding proxy (`PlaybackInput` stays normalized).
- Non-Goals (this change)
  - SMB1 support
  - Cloud drive/WebDAV/DLNA sources
  - Cross-device sync of SMB credentials

## Decisions
### Decision: SMBJ (Apache-2.0) for Android SMB2/SMB3
Use Java SMBJ (`com.hierynomus:smbj`) and expose it to .NET via an Android binding project.

Rationale:
- SMBJ is Apache-2.0 and actively used.
- Supports SMB2/SMB3 and random access reads required for seekable streaming.

### Decision: ExoPlayer custom DataSource for SMB streaming
Implement an ExoPlayer `DataSource` that:
- Parses `smb://host/share/path?profileId=<id>` URIs.
- Resolves the referenced profile and credentials.
- Opens a random-access handle via SMBJ.
- Reads bytes from the requested offset and supports `DataSpec.Position` seeking.

Rationale:
- Native ExoPlayer pipeline (no localhost HTTP server) reduces moving parts.
- Seek/range behavior matches ExoPlayer expectations.

### Decision: Canonical internal SMB URI
Use `smb://host/share/<path>?profileId=<id>` as the internal playback locator on Android.

Notes:
- The Library UI accepts both `\\host\share` and `smb://host/share` for profile creation.
- The system normalizes profiles and generates canonical locators for playback.

### Decision: Remembered passwords stored via platform-protected encryption
Store SMB passwords in a local secrets table as ciphertext, encrypted using a platform-protected key:
- Android: AES key generated/stored in Android Keystore.
- Windows: DPAPI (`ProtectedData`).

Rationale:
- Avoid plaintext credentials in SQLite.
- Meets "remember password" without requiring online services.

## Alternatives considered
- Use a pure-.NET SMB client from NuGet: rejected because the viable implementations are LGPL-based (commercial risk).
- Run a localhost HTTP range proxy on Android: workable but adds complexity (ports, lifecycle, additional failure modes). Kept as fallback only if ExoPlayer DataSource approach proves insufficient.

## Risks / Trade-offs
- SMB servers vary (auth methods, DFS, dialect quirks).
  - Mitigation: limit to SMB2/SMB3, add actionable error messages, add integration test hooks.
- Secure storage differences across platforms.
  - Mitigation: keep an interface boundary, implement Android + Windows for MVP platforms.

## Migration Plan
- Add new SQLite schema elements:
  - Extend `SmbProfile` to include structured fields and a `SecretId` reference.
  - Add a `Secrets` table for ciphertext blobs.
- Provide a migration path from existing profiles that stored only `RootPath`.

## Open Questions
- ExoPlayer `DataSource` API surface in Media3 bindings (exact class names/methods).
- iOS Keychain implementation (v1.0 platform).


