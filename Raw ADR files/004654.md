# ADR-004: React Native with Expo Framework

Status: Accepted
Date: 2025-12-18
Owner: User
Related Features: All features
Supersedes: N/A
Superseded by: N/A

---

## Context

This is a rewrite of CloudGallery (originally Kotlin native Android app) to support cross-platform deployment.

Requirements:
- Cross-platform (Android, iOS)
- Native performance for photo grids and gestures
- Access to native APIs (media library, file system, secure storage)
- Fast development iteration
- User explicitly prefers **not** using Kotlin

---

## Decision

Use **React Native with Expo SDK** as the application framework.

Key points:
- Expo SDK ~54 for latest features
- Expo dev client for native module testing
- TypeScript for type safety
- File-based routing with Expo Router

Justification:
- User preference against Kotlin ruled out native Android
- Need for iOS support ruled out Android-only solutions
- Expo provides superior DX compared to bare React Native
- Managed workflow simplifies dependency management

---

## Alternatives considered

### Flutter

- Pros: Cross-platform, good performance, Material Design support
- Cons: Dart language (user prefers TypeScript/JavaScript ecosystem), larger bundle size
- Rejected because: User familiar with React/TypeScript, not Dart

### Native (Kotlin + Swift)

- Pros: Maximum performance, full platform access
- Cons: Maintain two codebases, user dislikes Kotlin, 2x development time
- Rejected because: User preference and maintenance burden

### Ionic/Capacitor

- Pros: Web technologies, easier web deployment
- Cons: WebView performance, not truly native UX
- Rejected because: Performance concerns for photo gallery with gestures

### React Native CLI (bare)

- Pros: More control, no Expo limitations
- Cons: Manual native module linking, complex setup, no Expo dev tools
- Rejected because: Expo's DX benefits outweigh limitations

---

## Consequences

### Positive

- Single codebase for Android and iOS
- TypeScript provides type safety and IDE support
- Expo modules handle complex native APIs (media library, SQLite, crypto)
- Hot reload for fast iteration
- Large React/RN community for support
- User's preferred tech stack (TypeScript)

### Negative / risks

- Expo app size larger than bare RN or native
- Some native modules require expo-dev-client (can't use Expo Go)
- Performance slightly lower than native (for photo grids)
- Mitigation: Use FlatList optimization, RecyclerListView if needed, measure performance

---

## Impact

### Code

- Language: TypeScript (strict mode)
- UI Components: React functional components with hooks
- State Management: React hooks (useState, useEffect, useCallback)
- Styling: StyleSheet API with Material Design 3 tokens
- Native modules: Expo SDK modules only (avoid react-native-* unless Expo-compatible)

### Dependencies

Key dependencies:
- expo ~54.0
- react-native ~0.81
- expo-router ~6.0 (file-based routing)
- expo-sqlite ~16.0 (database)
- expo-media-library ~18.0 (photo access)
- expo-secure-store ~15.0 (credentials)
- react-native-reanimated ~4.1 (animations)
- react-native-gesture-handler ~2.28 (touch gestures)

### Documentation

- Package versions in package.json
- Expo SDK version documented in app.json
- Native modules only via Expo SDK (documented in AGENTS.md)

---

## Verification

### Test environment

- Android: Android Studio emulator + physical device
- iOS: Xcode simulator + physical device
- Dev client: expo-dev-client for testing native modules

### Test flows

| ID | Scenario | Level | Expected result | Notes |
| --- | --- | --- | --- | --- |
| TST-001 | Build Android APK | Shell | APK installs and launches | npx expo run:android |
| TST-002 | Build iOS IPA | Shell | IPA installs and launches | npx expo run:ios |
| TST-003 | Hot reload | Device | Changes reflect instantly | Save file during dev |
| TST-004 | Native module usage | Device | media-library, sqlite, etc work | Test all Expo modules |

---

## References

- Expo docs: https://docs.expo.dev/
- React Native docs: https://reactnative.dev/
- CloudGallery reference: ../cloudgallery-ref/ (Kotlin version)
- Package versions: package.json
