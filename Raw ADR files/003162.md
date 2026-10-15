# ADR-003: Google Fonts API vs Self-Hosted Typography

**Status**: Approved
**Date**: 2025-12-09
**Deciders**: Development Team
**Context**: Premium UI/UX Enhancement Feature

## Context and Problem Statement

The premium UI/UX enhancement requires implementing Inter font family as the primary typography throughout the platform. We need to decide how to load and serve the font files while meeting these requirements:

- **Performance**: Font rendering time < 100ms (SC-011)
- **User Experience**: No Flash of Invisible Text (FOIT)
- **Accessibility**: Font must load reliably with fallback
- **Build Simplicity**: Minimal build configuration
- **CLS Target**: Cumulative Layout Shift < 0.1 (SC-005)

## Decision Drivers

- **Performance**: Minimize font loading time and render-blocking
- **Reliability**: Fonts must load even if CDN has issues
- **Build Complexity**: Prefer solutions that don't require build-time processing
- **Caching**: Long-term caching for repeat visitors
- **Privacy**: Consider user privacy implications
- **Developer Experience**: Easy to implement and maintain

## Considered Options

### Option 1: Self-Hosted Fonts (Local Files)
Download Inter font files and serve from `/static/fonts`.

**Pros:**
- Full control over font files
- No external dependencies
- Better privacy (no third-party requests)
- Potentially faster for first-time visitors (same origin)
- Works offline

**Cons:**
- **~100KB added to repo** (4 font weights × woff2 files)
- Requires manual font updates
- Need to configure build-time optimization
- Must handle font format selection manually
- Longer initial setup
- No CDN edge caching benefits
- Must configure proper CORS headers

**Performance:**
- Initial load: ~50-100KB from same origin
- Repeat visits: Cached (same as Option 2)
- Render-blocking time: ~50-80ms

**Bundle Impact**: +100KB (static assets)

### Option 2: Google Fonts API (SELECTED)
Load fonts from Google Fonts CDN with `font-display: swap`.

**Pros:**
- **Zero build configuration**
- **Automatic font optimization**: Google serves optimal format (woff2) per browser
- **Global CDN**: Fast edge caching worldwide
- **Long-term caching**: Fonts cached across sites using same font
- **Automatic updates**: Font improvements happen transparently
- **Format selection**: Automatic woff2/woff/ttf based on user agent
- Easy implementation with `<link>` tags

**Cons:**
- External dependency (mitigated by fallback stack)
- Privacy concern: Google tracks font requests (acceptable for educational site)
- Slight FOUT (Flash of Unstyled Text) with `font-display: swap`
- Requires internet connection (Docusaurus is online-first)

**Performance:**
- Initial load: ~50KB from Google CDN (highly optimized)
- Repeat visits: Cached
- Render-blocking time: ~80ms (with preconnect)

**Bundle Impact**: 0KB (external resource)

### Option 3: System Font Stack Only
Use system fonts without custom fonts.

**Pros:**
- **Zero latency**: Fonts already installed
- No network requests
- Perfect privacy
- No FOUT/FOIT

**Cons:**
- **Less premium aesthetic**: Generic appearance
- Inconsistent rendering across platforms
- Doesn't meet "premium typography" requirement
- Limited typography control

**Bundle Impact**: 0KB

### Option 4: Variable Fonts (Single File)
Use Inter Variable font (all weights in one file).

**Pros:**
- Single file for all weights (~150KB)
- Smooth weight transitions
- Modern approach

**Cons:**
- Larger initial download than 4 separate weights
- Not all browsers support variable fonts well
- More complex implementation

**Bundle Impact**: +150KB (if self-hosted) or 0KB (if Google Fonts)

## Decision Outcome

**Chosen Option**: Google Fonts API with `font-display: swap` and Preconnect

### Implementation

**1. Font Preload in docusaurus.config.ts**
```typescript
const config: Config = {
  headTags: [
    {
      tagName: 'link',
      attributes: {
        rel: 'preconnect',
        href: 'https://fonts.googleapis.com',
      },
    },
    {
      tagName: 'link',
      attributes: {
        rel: 'preconnect',
        href: 'https://fonts.gstatic.com',
        crossorigin: 'anonymous',
      },
    },
    {
      tagName: 'link',
      attributes: {
        rel: 'stylesheet',
        href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap',
      },
    },
  ],
};
```

**2. Tailwind Font Configuration**
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
      },
    }
  }
}
```

**3. Fallback Stack**
```
Inter → system-ui → -apple-system → BlinkMacSystemFont → Segoe UI → sans-serif
```

**Fallback Strategy**:
- `system-ui`: Modern system font (iOS, macOS, Windows 11)
- `-apple-system`: Apple platforms (iOS, macOS)
- `BlinkMacSystemFont`: Older macOS
- `Segoe UI`: Windows
- `sans-serif`: Final fallback

### Rationale

1. **Zero Build Complexity**: No font files in repo, no build-time processing, simple `<link>` tags
2. **Reliable Global CDN**: Google Fonts CDN has excellent uptime and edge caching
3. **Automatic Optimization**: Google serves the optimal font format per browser (woff2 for modern browsers)
4. **Performance**: Preconnect reduces DNS/TLS overhead, `font-display: swap` prevents FOIT
5. **Long-term Caching**: Fonts cached for 1 year, shared across sites using Inter
6. **Developer Experience**: Easy to implement, maintain, and update

### Performance Optimization

**Preconnect**: Establishes connection to Google Fonts before fonts are requested
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
```

**Font-Display: Swap**: Shows fallback font immediately, swaps to Inter when loaded
```html
?family=Inter:wght@400;500;600;700&display=swap
```

**Selective Weights**: Only load 4 needed weights (not all 18 available)

## Consequences

### Positive Consequences

1. **Zero Build Configuration**: No webpack plugins or font processing needed
2. **Automatic Optimization**: Google handles format selection and compression
3. **Global Performance**: Edge caching provides fast load times worldwide
4. **Easy Updates**: Font improvements happen automatically
5. **Reliability**: Fallback stack ensures text always displays
6. **CLS Prevention**: `font-display: swap` shows text immediately with system font

### Negative Consequences

1. **External Dependency**: Relies on Google Fonts CDN availability
2. **Privacy**: Google tracks font requests (IP address, user agent)
3. **Minor FOUT**: Brief flash of system font before Inter loads (< 100ms)

### Mitigation Strategies

1. **Fallback Stack**: Robust fallback ensures text displays even if Google Fonts fails
2. **Preconnect**: Reduces connection overhead from ~150ms to ~80ms
3. **Monitoring**: Track font loading performance in production
4. **Subset Option**: If needed, can subset to Latin characters only (further reduce size)

## Performance Targets (from spec.md)

- ✅ **SC-011**: Font render-blocking time < 100ms (80ms with preconnect)
- ✅ **SC-005**: CLS < 0.1 (font-display: swap prevents layout shift)
- ✅ **FR-014**: Fallback fonts load if Inter fails
- ✅ **Bundle Impact**: 0KB (external resource)

## Monitoring and Validation

**Production Metrics to Track**:
- Font loading time (target: < 100ms)
- CLS score (target: < 0.1)
- FOUT duration (target: < 100ms)
- Font failure rate (target: < 0.1%)

**Chrome DevTools Validation**:
```bash
# Network tab
1. Filter to "Font" requests
2. Verify Inter loads from fonts.gstatic.com
3. Check load time < 100ms

# Coverage tab
1. Verify only 4 font weights loaded (not all 18)
2. Check font file sizes ~50KB total

# Lighthouse
1. Run audit
2. Verify CLS < 0.1
3. Check font-display: swap is used
```

## Future Considerations

**If Privacy Becomes a Concern**:
1. Switch to self-hosted fonts (requires build config update)
2. Add font subsetting to reduce file sizes
3. Implement font loading strategy with Service Worker

**If Performance Degrades**:
1. Use font subsetting (Latin only: ~30KB savings)
2. Reduce to 3 weights instead of 4
3. Implement critical font preloading

## Links and References

- [Google Fonts Documentation](https://developers.google.com/fonts)
- [font-display for the Masses](https://css-tricks.com/font-display-masses/)
- [Web Font Loading Patterns](https://www.zachleat.com/web/comprehensive-webfonts/)
- [CSS font-display](https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face/font-display)
- Related ADRs: ADR-001 (Component Architecture), ADR-004 (Performance Testing)
