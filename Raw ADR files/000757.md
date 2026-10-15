# ADR-009: Design for visionOS First

**Status:** Accepted
**Date:** 2025-11-24
**Decision Makers:** Development Team, Design Team
**Technical Story:** Platform Strategy

## Context

We needed to decide our platform strategy:
- Target visionOS (Apple Vision Pro) and/or iOS
- Which platform to prioritize for design and development
- How to handle platform-specific features
- Resource allocation between platforms

Apple Vision Pro represents a new computing paradigm with:
- Spatial computing capabilities
- 3D immersive environments
- Eye and hand tracking
- Revolutionary user interface patterns

## Decision

We will adopt a **visionOS-first design strategy** where:

1. **Primary Design Target**: visionOS/Apple Vision Pro
   - Design UI for spatial computing first
   - Optimize for Vision Pro capabilities
   - Use visionOS design patterns

2. **Secondary Compatibility**: iOS (iPhone/iPad)
   - Share codebase where possible
   - Adapt design for 2D screens
   - Maintain feature parity where reasonable

3. **Technology Choice**: SwiftUI
   - Single codebase for both platforms
   - Conditional compilation for platform differences
   - Platform-specific views where needed

4. **Marketing Position**: "visionOS app that also works on iPhone"
   - Not "iPhone app ported to Vision Pro"
   - Emphasize spatial computing benefits
   - Position as cutting-edge technology

## Consequences

### Positive

**Market Position**
- Early mover advantage in visionOS ecosystem
- Differentiation from competitors
- Premium positioning
- Tech-forward brand image
- Press coverage opportunities

**User Experience**
- Take full advantage of Vision Pro capabilities
- Innovative spatial interface
- Immersive wardrobe browsing
- 3D visualization possibilities
- Future AR try-on features

**Technical**
- SwiftUI works seamlessly on both platforms
- Modern codebase from day one
- Prepared for spatial computing future
- Can leverage RealityKit
- Clean architecture supports both platforms

**Business**
- Higher perceived value (premium pricing justified)
- Smaller but wealthier target audience initially
- Expansion to iOS increases TAM later
- Unique selling proposition

### Negative

**Market Size**
- Vision Pro has limited market share initially
- Smaller potential user base
- Higher barrier to entry (expensive hardware)
- Slower initial growth

**Development Challenges**
- Learning visionOS is new territory
- Limited visionOS development resources/tutorials
- Testing requires expensive hardware
- Fewer developers with visionOS experience

**Platform Limitations**
- Vision Pro simulator less accurate than iOS simulator
- Harder to test without physical device
- Some iOS users may feel like second-class citizens
- Need to maintain two design paradigms

### Risks

**Adoption Risk**
- Vision Pro may not succeed as platform
- **Mitigation**: App works on iOS as fallback

**Development Risk**
- visionOS APIs may be unstable/change
- **Mitigation**: Use stable APIs, abstract platform specifics

**Market Risk**
- Users may not value spatial features
- **Mitigation**: Ensure core value works on both platforms

## Alternatives Considered

### iOS-First, visionOS Later
- **Pros**: Larger market, proven platform, easier development
- **Cons**: Miss visionOS launch window, harder to retrofit spatial features
- **Rejected**: Less differentiation, crowded market

### Equal Priority for Both Platforms
- **Pros**: Maximize market reach, no platform bias
- **Cons**: Diluted effort, lowest common denominator design
- **Rejected**: Fails to capitalize on visionOS opportunities

### visionOS-Only
- **Pros**: Maximum focus, simplest development
- **Cons**: Very limited market, high risk
- **Rejected**: Too risky, leaves money on table

### Cross-Platform (React Native, Flutter)
- **Pros**: Could also target Android
- **Cons**: Poor visionOS support, compromised UX, no spatial features
- **Rejected**: Can't leverage visionOS capabilities

## Implementation Details

### Platform-Specific Features

**visionOS-Only Features:**
```swift
#if os(visionOS)
- Spatial window management
- 3D wardrobe visualization
- Immersive environments
- Hand gesture controls
- Eye tracking for navigation
#endif
```

**iOS-Optimized:**
```swift
#if os(iOS)
- Compact layouts for iPhone
- Tab bar navigation
- Standard gestures
- Haptic feedback
#endif
```

**Shared Features:**
- Core wardrobe management
- AI recommendations
- Color harmony
- Analytics
- All business logic

### Design Approach

**visionOS Design Principles:**
1. **Spatial Depth**: Use z-axis for organization
2. **Glassmorphism**: Frosted glass materials (.ultraThinMaterial)
3. **Floating Windows**: Multiple concurrent views
4. **Natural Gestures**: Tap, pinch, rotate in 3D space
5. **Eye Comfort**: Appropriate sizing and spacing

**iOS Adaptation:**
1. Convert 3D layouts to scrollable 2D
2. Use standard iOS navigation patterns
3. Maintain visual style (glassmorphism works on iOS too)
4. Keep gesture vocabulary simple

### Code Organization

```swift
// Shared business logic
Domain/
Infrastructure/

// Platform-specific presentation
Presentation/
├── Shared/         // Works on both platforms
├── visionOS/       // Vision Pro specific
└── iOS/            // iPhone/iPad specific
```

### Testing Strategy

**visionOS Testing:**
- Simulator for basic functionality
- Physical device for spatial features
- Eye tracking requires device
- Gesture testing needs device

**iOS Testing:**
- Comprehensive simulator testing
- Device testing for final QA
- Broader device coverage needed

## User Experience Vision

### visionOS Experience

Imagine opening the app on Vision Pro:

1. **Launch**: Wardrobe appears as floating window in space
2. **Browse**: Items arranged in 3D space, organized by color/category
3. **Detail**: Tap item, it enlarges in immersive view, rotate with gestures
4. **Outfit**: Multiple items float together, see combination in 3D
5. **Analytics**: Charts and stats in spatial arrangement

**Unique Value**: "See your wardrobe in a whole new dimension"

### iOS Experience

Same app on iPhone:

1. **Launch**: Standard app icon, familiar interface
2. **Browse**: Grid view of items, scroll vertically
3. **Detail**: Full-screen item view, swipe for more
4. **Outfit**: List of items in combination
5. **Analytics**: Standard charts

**Value**: "Professional wardrobe management on the go"

## Marketing Implications

**Positioning:**
- "The first AI wardrobe consultant for Vision Pro"
- "Experience fashion in spatial computing"
- "Built for the future of computing"

**Target Audience:**
- Early adopters and tech enthusiasts
- Fashion-forward professionals
- Vision Pro owners (small but affluent)
- Eventually: broader iOS market

**Pricing Strategy:**
- Premium pricing justified by platform
- Vision Pro users expect quality apps
- iOS users get same value at same price

## Success Metrics

This strategy succeeds if:

- ✅ Featured in visionOS App Store
- ✅ Press coverage for innovative spatial UI
- ✅ Positive reviews mention Vision Pro experience
- ✅ iOS users still satisfied with experience
- ✅ Conversion rate to Pro subscription > 10%

## Migration Path

**Phase 1** (v1.0): visionOS-optimized, iOS-compatible ✅
**Phase 2** (v1.5): Enhanced iOS experience based on feedback
**Phase 3** (v2.0): Advanced spatial features (AR try-on)
**Phase 4** (v3.0): Fully immersive visionOS environment

## Technical Challenges & Solutions

### Challenge: Different Interaction Models
**Solution**: Abstract user intents, implement platform-specific handlers

### Challenge: Different Layout Paradigms
**Solution**: SwiftUI's adaptive layouts, platform-specific views

### Challenge: Testing Without Hardware
**Solution**: Comprehensive unit/integration tests, manual QA on device

### Challenge: Performance Differences
**Solution**: Profile on both platforms, optimize for lowest common denominator

## References

- [visionOS Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/designing-for-visionos)
- [Building Apps for visionOS](https://developer.apple.com/visionos/)
- [SwiftUI Cross-Platform Development](https://developer.apple.com/documentation/swiftui)
- [Spatial Computing Design Patterns](https://developer.apple.com/videos/play/wwdc2023/10076/)

## Review History

- 2025-11-24: Initial proposal
- 2025-11-24: Design review
- 2025-11-24: Accepted with enthusiastic support

---

**Related ADRs:**
- [ADR-002: Use SwiftUI with MVVM Pattern](ADR-002-swiftui-mvvm.md)
- [ADR-001: Adopt Clean Architecture](ADR-001-clean-architecture.md)

**Future Considerations:**
- Revisit if Vision Pro adoption much lower than expected
- Consider Android if iOS growth plateaus
- May add Apple Watch app (v2.0+)
