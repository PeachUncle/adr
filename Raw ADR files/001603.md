# ADR-002: Use Flutter for Mobile Apps

**Status**: Accepted  
**Date**: 2025-10-18  
**Deciders**: Software Architect, Technical Lead, Project Manager

## Context

The Eucharist Understanding Platform aims to reach people wherever they are, including on mobile devices. Mobile apps are essential because:

- Many people prefer mobile apps for daily spiritual practices
- Push notifications can support daily prayer routines
- Offline functionality enables prayer without internet
- Native feel provides better user experience
- App store presence increases discoverability

We need a mobile development strategy that:

- Supports both iOS and Android platforms
- Delivers native-like performance and UX
- Enables rapid development with limited resources
- Maintains code quality and testability
- Allows for future scaling and feature additions
- Fits within the budget constraints of an open-source project

### Key Requirements

- Cross-platform development (iOS and Android)
- Offline-first architecture for core features
- Native performance for smooth animations
- Integration with backend API
- Push notifications support
- Local data storage
- Firebase Authentication integration
- Beautiful, accessible UI

## Decision

We will use **Flutter 3.16+** with **Dart** as the framework for mobile application development.

### Technology Stack Details

#### Core Framework

```dart
// Framework & Language
- Flutter 3.16+ (Cross-platform framework)
- Dart 3.0+ (Programming language)

// State Management
- Provider or Riverpod (Architecture decision to be made)

// Networking
- Dio (HTTP client)
- Retrofit (Type-safe API)
- connectivity_plus (Network status)

// Local Storage
- SharedPreferences (User settings)
- Hive or SQLite (Structured data cache)
- flutter_secure_storage (Sensitive data)

// Firebase Integration
- Firebase Auth (Authentication)
- Firebase Messaging (Push notifications)
- Firebase Analytics (Usage tracking)
- Firebase Crashlytics (Crash reporting)

// UI Components
- Material Design 3
- Custom design system components
- Cached network image
- flutter_svg (Vector graphics)

// Features
- url_launcher (External links)
- share_plus (Content sharing)
- package_info_plus (App info)

// Testing
- flutter_test (Unit tests)
- mockito (Mocking)
- integration_test (E2E tests)

// Build & Tools
- flutter_launcher_icons (App icons)
- flutter_native_splash (Splash screens)
- build_runner (Code generation)
```

### Architecture Pattern

```
┌─────────────────────────────────────────┐
│         Flutter Application             │
├─────────────────────────────────────────┤
│  Presentation Layer                     │
│  - Screens/Pages                        │
│  - Widgets                              │
│  - State Management (Provider/Riverpod) │
├─────────────────────────────────────────┤
│  Domain Layer                           │
│  - Business Logic                       │
│  - Use Cases                            │
│  - Models/Entities                      │
├─────────────────────────────────────────┤
│  Data Layer                             │
│  - Repositories                         │
│  - Data Sources (Remote/Local)          │
│  - DTOs (Data Transfer Objects)         │
├─────────────────────────────────────────┤
│  Infrastructure                         │
│  - API Client (Dio)                     │
│  - Local Database (Hive/SQLite)         │
│  - Firebase Services                    │
│  - Secure Storage                       │
└─────────────────────────────────────────┘
```

### Clean Architecture Implementation

Following Flutter clean architecture principles:

- **Presentation**: UI and state management
- **Domain**: Business logic, independent of implementation
- **Data**: Implementation of repositories, data sources

## Consequences

### Positive

✅ **Single Codebase**: One codebase for both iOS and Android reduces development time by approximately 40% compared to native development

✅ **Native Performance**: Flutter compiles to native code, providing 60fps animations and smooth user experience comparable to native apps

✅ **Rich UI Components**: Extensive widget library with Material Design and Cupertino (iOS-style) widgets out of the box

✅ **Hot Reload**: Instant code changes during development dramatically speed up iteration

✅ **Strong Type System**: Dart's sound type system catches errors at compile time

✅ **Large Community**: Active community with extensive packages on pub.dev

✅ **Google Support**: Backed by Google with consistent updates and long-term commitment

✅ **Fast Development**:

- Pre-built widgets
- Excellent tooling
- Clear documentation
- Good testing framework

✅ **Cost Effective**: Significantly reduces development and maintenance costs compared to maintaining two native codebases

✅ **Consistent UI**: Same look and feel across platforms (can be customized per platform if needed)

✅ **Good Firebase Integration**: Official Firebase plugins work well with Flutter

### Negative

⚠️ **Larger App Size**: Flutter apps are typically 4-5MB larger than equivalent native apps due to Flutter engine inclusion

⚠️ **Learning Curve**: Team needs to learn Dart and Flutter framework (though Dart is relatively easy for developers with Java/JavaScript experience)

⚠️ **Platform-Specific Features**: Some platform-specific features require writing native code or waiting for package updates

⚠️ **Debugging Native Issues**: Debugging platform-specific issues can be more challenging than pure native development

⚠️ **Package Quality Variance**: Third-party packages vary in quality and maintenance status

⚠️ **Widget Tree Complexity**: Deep widget trees can become hard to maintain without proper structure

### Neutral

➖ **Framework Dependency**: Tied to Flutter's release cycle and architectural decisions

➖ **Native Code Bridge**: Occasionally need to write platform-specific code for certain features

➖ **Build Times**: Initial builds can be slow, though hot reload compensates during development

## Alternatives Considered

### 1. React Native

**Pros**:

- JavaScript/TypeScript (team may already know)
- Large ecosystem
- Good community
- Hot reload
- Expo framework simplifies development

**Cons**:

- Bridge architecture can cause performance issues
- More platform-specific code needed
- Dependency on third-party native modules
- More configuration complexity
- Less consistent UI across platforms

**Why Not**: Flutter provides better out-of-the-box performance and more consistent cross-platform experience. React Native's bridge architecture introduces performance overhead that Flutter avoids with its compilation to native code.

### 2. Native Development (Swift/Kotlin)

**Pros**:

- Best possible performance
- Full access to platform APIs
- No framework overhead
- Best debugging tools
- Platform-specific best practices

**Cons**:

- Requires two completely separate codebases
- Double the development time and cost
- Need iOS and Android expertise
- Harder to maintain consistency
- Slower feature delivery

**Why Not**: With limited resources for an open-source project, developing and maintaining two codebases is not feasible. The 2x cost and time don't provide enough benefit over Flutter's near-native performance.

### 3. Xamarin

**Pros**:

- C# language
- .NET ecosystem
- Native UI components
- Microsoft backing

**Cons**:

- Smaller community than Flutter/React Native
- More complex setup
- Less popular (declining interest)
- Fewer resources and tutorials
- Limited future outlook

**Why Not**: Flutter has overtaken Xamarin in popularity and community support. The ecosystem is less vibrant, making it harder to find help and contributors.

### 4. Ionic/Capacitor

**Pros**:

- Web technologies (HTML/CSS/JavaScript)
- Can reuse web code
- Easy for web developers
- Fast development

**Cons**:

- WebView-based (performance limitations)
- Not truly native feel
- Slower animations
- Limited access to native features
- Battery drain concerns

**Why Not**: For a spiritual app where user experience is paramount, the performance and native feel of Flutter are essential. WebView limitations would compromise the quality we want to deliver.

### 5. Progressive Web App (PWA) Only

**Pros**:

- No app store approval needed
- Single codebase with web
- Easy updates
- Cross-platform by nature

**Cons**:

- Limited offline capabilities
- No push notifications on iOS
- Poor app store discoverability
- Limited access to device features
- Less engagement than native apps

**Why Not**: Many Catholics looking for daily spiritual content expect native mobile apps. PWAs have significant limitations on iOS and lack the discovery benefits of app stores.

## Implementation Plan

### Phase 1: Project Setup (Week 1)

- [x] Initialize Flutter project
- [x] Configure package structure
- [ ] Set up folder structure (clean architecture)
- [ ] Configure linting rules
- [ ] Set up version management
- [ ] Configure build flavors (dev/staging/prod)

### Phase 2: Core Infrastructure (Week 2-3)

- [ ] Implement API client with Dio
- [ ] Set up state management (Provider/Riverpod)
- [ ] Configure local storage (Hive/SQLite)
- [ ] Implement secure storage
- [ ] Create base repository pattern
- [ ] Set up error handling

### Phase 3: Firebase Integration (Week 4)

- [ ] Configure Firebase project
- [ ] Implement Firebase Auth
- [ ] Set up push notifications
- [ ] Configure analytics
- [ ] Add crash reporting
- [ ] Test authentication flows

### Phase 4: UI Foundation (Week 5-6)

- [ ] Create design system
- [ ] Build reusable widgets
- [ ] Implement theme system
- [ ] Create navigation structure
- [ ] Build common layouts
- [ ] Implement responsive design

### Phase 5: Testing & CI/CD (Week 7-8)

- [ ] Write unit tests
- [ ] Create widget tests
- [ ] Set up integration tests
- [ ] Configure CI/CD pipeline
- [ ] Set up code coverage
- [ ] Configure automated testing

### Phase 6: App Store Preparation (Months 4-5)

- [ ] Create app icons
- [ ] Design splash screens
- [ ] Write app store descriptions
- [ ] Create screenshots
- [ ] Submit for review
- [ ] Plan release strategy

## Technical Specifications

### Folder Structure

```
mobile/
├── lib/
│   ├── core/              # Core functionality
│   │   ├── constants/     # App constants
│   │   ├── errors/        # Error handling
│   │   ├── network/       # API client
│   │   └── utils/         # Utilities
│   ├── features/          # Feature modules
│   │   ├── auth/
│   │   │   ├── data/      # Repositories, data sources
│   │   │   ├── domain/    # Entities, use cases
│   │   │   └── presentation/ # UI, widgets, state
│   │   ├── gospel/
│   │   ├── community/
│   │   └── profile/
│   ├── shared/            # Shared components
│   │   ├── widgets/       # Reusable widgets
│   │   └── theme/         # Theme configuration
│   └── main.dart          # App entry point
├── test/                  # Tests
├── android/               # Android-specific
├── ios/                   # iOS-specific
├── assets/                # Images, fonts, etc.
└── pubspec.yaml          # Dependencies
```

### Performance Targets

- **App Size**: <30MB on iOS, <25MB on Android
- **Startup Time**: <2 seconds on modern devices
- **Frame Rate**: 60fps for animations
- **Memory Usage**: <150MB baseline
- **Battery Impact**: Minimal background drain

### Device Support

- **iOS**: iOS 12.0 and above
- **Android**: Android 5.0 (API level 21) and above
- **Screen Sizes**: All phone and tablet sizes
- **Orientations**: Portrait primary, landscape supported

## Security Considerations

### Data Storage

- Sensitive data encrypted with flutter_secure_storage
- API tokens stored securely
- Local database encrypted at rest
- User credentials never stored locally

### API Communication

- HTTPS only
- Certificate pinning for production
- Token-based authentication
- Automatic token refresh
- Request signing for sensitive operations

### Code Security

- Obfuscation enabled for release builds
- API keys stored in environment variables
- No hardcoded secrets
- Proper permission handling

## Success Criteria

- [x] Flutter project initialized and building
- [ ] Clean architecture implemented
- [ ] Authentication working (Firebase)
- [ ] API integration complete
- [ ] Offline mode functional
- [ ] Push notifications working
- [ ] 80%+ test coverage
- [ ] Apps published to both stores
- [ ] Performance targets met
- [ ] User feedback positive (>4.0 rating)

## Platform-Specific Considerations

### iOS

- App Store review guidelines compliance
- iOS-specific design patterns
- Privacy policy requirements
- Sign in with Apple (if using social login)
- Push notification certificates

### Android

- Google Play policies compliance
- Material Design guidelines
- ProGuard configuration
- Play Store listing requirements
- Firebase Cloud Messaging setup

## Monitoring & Metrics

### Key Metrics to Track

- Crash-free rate (>99.5%)
- App launch time
- Screen load times
- API response times
- Offline functionality usage
- User retention rates
- Feature adoption

### Tools

- Firebase Crashlytics
- Firebase Analytics
- Firebase Performance Monitoring
- Custom event tracking

## References

- [Flutter Documentation](https://flutter.dev/docs)
- [Dart Language Tour](https://dart.dev/guides/language/language-tour)
- [Flutter Architecture Samples](https://fluttersamples.com/)
- [Material Design 3](https://m3.material.io/)
- [Firebase for Flutter](https://firebase.google.com/docs/flutter/setup)
- [Clean Architecture in Flutter](https://resocoder.com/flutter-clean-architecture-tdd/)

## Revision History

- **2025-10-18**: Initial version - Accepted
- **Status**: Active

---

**Next Review**: 2026-04-18 (6 months)  
**Owner**: Software Architect  
**Stakeholders**: Mobile Team, Technical Lead
