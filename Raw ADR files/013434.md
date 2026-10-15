# ADR-0001: Wayland Library Selection for On-Screen Keyboard

## Status

Proposed

## Context

We are developing an on-screen keyboard for Ubuntu Core 24+ kiosk environments using Go (version 1.24.4). The keyboard needs to support:

### Requirements

1. **Layouts**: Single-screen for now, with both anchored and free-floating positioning
2. **Language**: Go 1.24.4 on Linux/amd64
3. **Touch Gestures**: SWYPE-style input for gesture-based typing
4. **Deployment Target**: Ubuntu Core 24+ kiosks as part of a larger kiosk framework
5. **Features**:
   - Multi-lingual input support
   - Spell checking capabilities
   - Word prediction/suggestion ribbon
   - Haptic/visual feedback

### Technical Constraints

- Must work reliably on Ubuntu Core 24+ (Wayland-based)
- Performance critical for real-time touch input
- Integration with existing kiosk framework
- Long-term maintenance and support required

## Decision

**Selected: CGO + wlroots**

We will use CGO bindings to the wlroots library for our Wayland integration.

## Options Considered

### 1. rajveermalviya/go-wayland

**Pros:**
- Pure Go implementation (no CGO dependencies)
- Clean API design
- 126 stars, reasonable community interest
- Wayland client implementation in pure Go

**Cons:**
- Last commit: January 2023 (stale for ~2 years)
- Limited maintenance activity
- 7 open issues with no recent activity
- May lack advanced features needed for complex input handling
- No compositor capabilities

**Verdict:** Not suitable due to maintenance concerns and potential feature limitations.

### 2. Pure wlc (Wayland Compositor Library)

**Pros:**
- Mature compositor library
- Well-established in the Wayland ecosystem
- Good for custom compositor development

**Cons:**
- Primarily C library, would require CGO anyway
- Limited Go-specific tooling
- Overkill for client-side keyboard application
- More complex than needed for our use case

**Verdict:** Not appropriate for our client-side keyboard needs.

### 3. CGO + wlroots

**Pros:**
- **Most mature and active**: wlroots has 2,194 stars and active development
- **Comprehensive feature set**: Supports all modern Wayland protocols
- **Production proven**: Used by major compositors (Sway, Hyprland, etc.)
- **Excellent Ubuntu Core support**: Well-tested on Ubuntu-based systems
- **Layer shell support**: Essential for proper keyboard positioning
- **Input method protocol support**: Critical for multi-lingual input
- **Touch event handling**: Robust touch gesture support
- **Active maintenance**: Regular updates and bug fixes

**Cons:**
- CGO dependency adds complexity to builds
- Larger binary size
- Requires C development knowledge for debugging
- Cross-compilation complexity

**Verdict:** Best choice for production reliability and feature completeness.

### 4. Alternative Go Libraries Evaluated

**neurlang/wayland** (116 stars, last push Nov 2024):
- More recent activity than go-wayland
- Multiplatform claims but limited documentation
- Less mature than wlroots ecosystem

**dominikh/wayland-go** (26 stars, last push Mar 2022):
- Stale maintenance
- Limited feature set

**zenhack/go.wayland** (12 stars, last push Jan 2018):
- Abandoned project
- Very limited functionality

## Rationale

### Why CGO + wlroots?

1. **Production Requirements**: Our kiosk environment requires rock-solid reliability. wlroots is battle-tested in production environments.

2. **Feature Completeness**: 
   - Layer shell protocol support for proper keyboard positioning
   - Input method protocol support for multi-lingual input
   - Touch event handling for SWYPE gestures
   - Comprehensive Wayland protocol coverage

3. **Ubuntu Core 24+ Compatibility**: wlroots is well-supported on Ubuntu-based systems and integrates seamlessly with the Wayland stack.

4. **Future-Proofing**: Active development ensures protocol updates and security patches.

5. **Ecosystem Integration**: Can leverage existing wlroots-based tools and extensions.

### Trade-offs Accepted

- **Build Complexity**: CGO requires C toolchain but provides reliability
- **Binary Size**: Larger binaries acceptable for kiosk deployment
- **Development Learning Curve**: Team will need to understand wlroots concepts

## Implementation Plan

1. **Phase 1**: Create CGO bindings for essential wlroots components
   - Layer shell integration
   - Input handling
   - Basic window management

2. **Phase 2**: Implement keyboard-specific features
   - Touch gesture recognition
   - Multi-lingual input methods
   - Positioning and anchoring

3. **Phase 3**: Advanced features
   - Spell checking integration
   - Word prediction
   - Haptic feedback

## Consequences

### Positive

- Robust, production-ready Wayland integration
- Full protocol support for advanced features
- Strong ecosystem compatibility
- Long-term viability

### Negative

- CGO build complexity
- Larger binary size
- Requires C development knowledge
- Platform-specific considerations

## Monitoring

- Track wlroots release cycles and security updates
- Monitor CGO build performance and compatibility
- Evaluate alternative pure Go solutions as they mature

## References

- [wlroots GitHub](https://github.com/swaywm/wlroots)
- [Wayland Protocol Documentation](https://wayland.freedesktop.org/docs/html/)
- [Ubuntu Core Wayland Support](https://ubuntu.com/core/docs)
- [Layer Shell Protocol](https://github.com/swaywm/wlr-protocols/blob/master/unstable/wlr-layer-shell-unstable-v1.xml)

---

**Date**: 2025-07-18  
**Author**: Development Team  
**Reviewers**: TBD  
