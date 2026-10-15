# ADR-009: Build, Updates & Code Signing

Status: Accepted
Date: 2025-08-22
Owners: Archon Core

## Context

We ship Archon as a desktop app for Windows, macOS, and Linux. Users expect secure, signed builds and a simple update story.

## Decision

- **Build targets**: Windows (MSI), macOS (DMG), Linux (AppImage). CI builds all three.
- **Code signing**:
  - Windows: Sign with Authenticode via Microsoft **SignTool**; timestamp builds.  [oai_citation:9‡Microsoft Learn](https://learn.microsoft.com/en-us/windows/win32/seccrypto/signtool?utm_source=chatgpt.com)
  - macOS: Sign with Developer ID cert and **notarize** with Apple Notary Service; staple tickets.  [oai_citation:10‡Apple Developer](https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution?utm_source=chatgpt.com)
  - Linux: Sign **AppImages** using `appimagetool` (+GPG). Provide public key & verification instructions.  [oai_citation:11‡docs.appimage.org](https://docs.appimage.org/packaging-guide/optional/signatures.html?utm_source=chatgpt.com)
- **Updates (MVP)**: Manual "Check for updates" linking to GitHub Releases. (Auto-update can be added later per ecosystem best practices.)  [oai_citation:12‡electronjs.org](https://electronjs.org/docs/latest/tutorial/updates?utm_source=chatgpt.com)
- **Release channeling**: Stable tags only; release notes included with hashes and signature info.

## Rationale

Platform-native signing maximizes user trust and avoids SmartScreen/Gatekeeper friction. Notarization is Apple’s recommended path for Developer ID–signed software. AppImage supports embedded GPG signatures, which is the de facto Linux approach. A manual update keeps MVP complexity low while remaining secure.  [oai_citation:13‡Apple Developer](https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution?utm_source=chatgpt.com) [oai_citation:14‡Microsoft Learn](https://learn.microsoft.com/en-us/windows/win32/seccrypto/signtool?utm_source=chatgpt.com) [oai_citation:15‡docs.appimage.org](https://docs.appimage.org/packaging-guide/optional/signatures.html?utm_source=chatgpt.com)

## Alternatives Considered

- **Auto-update in v1**: Faster iteration but adds infra, signing automation, and edge-case handling; defer.
- **Unsigned Linux builds**: Easier, but users cannot verify provenance.

## Consequences

- Positive: Predictable, verifiable installs; minimal friction on all OSes.
- Negative: Requires cert procurement and CI secrets management.
- Follow-ups: Consider auto-update once signing and CI are battle-tested.

## Implementation Notes

- Windows: `signtool sign /fd SHA256 /tr <tsa> /td SHA256 ...` in CI.  [oai_citation:16‡Microsoft Learn](https://learn.microsoft.com/en-us/windows/win32/seccrypto/signtool?utm_source=chatgpt.com)
- macOS: `codesign` + `xcrun notarytool submit --wait` + `stapler staple`.  [oai_citation:17‡Apple Developer](https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution?utm_source=chatgpt.com)
- Linux: `appimagetool -s` with GPG key; publish public key and verification steps.  [oai_citation:18‡docs.appimage.org](https://docs.appimage.org/packaging-guide/optional/signatures.html?utm_source=chatgpt.com)

## Review / Revisit

- Revisit when enabling auto-update flows and additional package formats (e.g., deb/rpm, Homebrew).
