# ADR-011: PWA Implementation Strategy

**Date**: 2025-01-27  
**Status**: ✅ Accepted  
**Deciders**: Development Team  
**Related**: [ADR-008 Performance Optimization](./008-performance-optimization-polish.md)

---

## Context

After completing Phase 8 (Performance Optimization), we identified the need to transform the PDF viewer into a Progressive Web App (PWA) to provide:
- **Installability**: Users can install the app on their devices
- **Offline Support**: Basic functionality without internet connection
- **Native-like Experience**: App behaves like a native application
- **Enhanced Mobile**: Advanced touch gestures and stylus support

The goal is to make the application feel native while maintaining its client-side, privacy-first principles.

---

## Decision

### 1. PWA Framework Choice

**Decision**: Use **`vite-plugin-pwa`** with **Workbox**

**Rationale**:
- Seamless integration with Vite build system
- Automatic service worker generation
- Best practices built-in
- Active maintenance and community support
- TypeScript support

**Alternatives Considered**:
- **Manual Service Worker**: Too complex, error-prone
- **Create React App PWA template**: Not using CRA
- **Next.js PWA**: Not using Next.js framework

---

### 2. Service Worker Strategy

**Decision**: **Precache + Runtime Caching** hybrid approach

**Precache** (Immediate availability):
- Application shell (HTML, CSS, JS)
- PDF.js worker files
- Font files
- App icons

**Runtime Cache** (Cache as used):
- Google Fonts
- Dynamically loaded resources

**Rationale**:
- Fast initial load (precached shell)
- Reduced cache size (don't cache everything)
- Works offline for core functionality
- Automatic updates with service worker lifecycle

---

### 3. Offline Storage Strategy

**Decision**: **IndexedDB via `idb` wrapper**

**What to Store**:
- Recently opened PDFs (last 5-10 documents)
- Annotations for offline PDFs
- User signatures
- App preferences

**Storage Limits**:
- Maximum cache size: 100MB
- Oldest-first eviction when limit reached
- User notification before eviction

**Rationale**:
- IndexedDB supports large binary files (PDFs)
- `idb` provides Promise-based API (cleaner than raw IndexedDB)
- Works across all modern browsers
- Better than localStorage for large data

**Alternatives Considered**:
- **localStorage**: 5-10MB limit, too small for PDFs
- **Cache API**: Not designed for structured data
- **File System Access API**: Limited browser support

---

### 4. Touch Gesture Implementation

**Decision**: **Custom gesture detection** (no library)

**Gestures Implemented**:
- **Pinch-to-zoom**: Two-finger scale
- **Swipe navigation**: Left/right for page navigation
- **Long-press**: Future enhancement (context menu)

**Rationale**:
- Simple gestures don't need heavy library
- Full control over gesture behavior
- No library dependency bloat
- Can optimize for PDF viewer use case

**Alternatives Considered**:
- **Hammer.js**: Abandoned, no longer maintained
- **use-gesture**: React-specific, but adds 20KB
- **GestureRecognizer API**: Limited browser support

---

### 5. Stylus/Apple Pencil Support

**Decision**: **PointerEvent API with pressure detection**

**Features**:
- Detect stylus vs touch vs mouse
- Pressure-sensitive drawing (where supported)
- Palm rejection (heuristic-based)
- Low-latency path rendering

**Implementation**:
```typescript
element.addEventListener('pointermove', (e: PointerEvent) => {
  if (e.pointerType === 'pen') {
    const pressure = e.pressure || 0.5
    const thickness = baseThickness * pressure * 2
    // Draw with variable thickness
  }
})
```

**Rationale**:
- PointerEvent unifies mouse/touch/stylus
- Pressure data available where supported (iPad Pro, Surface)
- Better than separate touch/mouse handlers
- Future-proof (standard API)

---

### 6. Install Prompt Strategy

**Decision**: **Smart timing + dismissible banner**

**Timing**:
- Show after 5 seconds of app usage
- Only show if not already installed
- Respect user dismissal for 7 days
- Store dismissal in localStorage

**UI**:
- Non-blocking bottom banner
- Clear benefits explanation
- One-click install action
- Dismissible with "Not Now" option

**Rationale**:
- Doesn't interrupt initial workflow
- Users understand what they're getting
- Not annoying (respects dismissal)
- Follows UX best practices

---

### 7. Update Notification Strategy

**Decision**: **Non-blocking toast notification**

**Behavior**:
- Detect new service worker available
- Show toast: "New version available"
- User can refresh immediately or continue working
- No forced reload (user control)

**Rationale**:
- Users shouldn't lose work
- Updates aren't urgent
- User decides when to update
- Follows Progressive Enhancement

---

## Consequences

### Positive ✅

1. **Better User Experience**
   - App feels native on mobile devices
   - Works offline (basic functionality)
   - Touch gestures improve mobile usability
   - Stylus support enables precision annotation

2. **Increased Engagement**
   - Installed apps have higher retention
   - Offline support reduces friction
   - Native-like feel increases perceived quality
   - Gesture support makes mobile viable

3. **Privacy Maintained**
   - All data stored locally (IndexedDB)
   - No server communication for core features
   - User controls when/what to cache
   - Aligns with privacy-first principles

4. **Performance Improvements**
   - Precached resources load instantly
   - Reduced network requests
   - Smoother mobile interactions
   - Gesture performance optimized

### Negative ⚠️

1. **Increased Complexity**
   - Service worker lifecycle management
   - IndexedDB quota management
   - Gesture conflict resolution
   - Cross-browser testing burden

2. **Larger Bundle Size**
   - vite-plugin-pwa: ~50KB
   - idb: ~2KB
   - Workbox runtime: ~20KB
   - Total: ~72KB increase (acceptable)

3. **Browser Compatibility**
   - Service Workers not in IE11 (acceptable)
   - PointerEvent pressure varies by device
   - Install prompt only in Chrome/Edge (iOS limited)
   - Offline features gracefully degrade

4. **Storage Management**
   - Need to handle quota exceeded errors
   - Cache eviction logic required
   - User education about offline storage
   - Potential for stale data issues

---

## Implementation Plan

### Phase 9A: Core PWA (Week 1, Days 1-2)
- [x] Install vite-plugin-pwa and dependencies
- [x] Configure PWA manifest
- [x] Create app icons
- [x] Set up service worker with Workbox
- [x] Implement install prompt component
- [x] Add offline indicator

### Phase 9B: Touch Gestures (Week 1, Days 3-4)
- [x] Implement useGestures hook
- [x] Add pinch-to-zoom to PDFViewer
- [x] Add swipe navigation
- [ ] Visual feedback for gestures
- [ ] Test on iOS and Android

### Phase 9C: Offline Storage (Week 2, Days 5-6)
- [ ] Set up IndexedDB schema
- [ ] Cache recently opened PDFs
- [ ] Store annotations offline
- [ ] Implement sync logic
- [ ] Add cache management UI

### Phase 9D: Stylus Support (Week 2, Day 7)
- [ ] Detect stylus input (PointerEvent)
- [ ] Implement pressure sensitivity
- [ ] Add palm rejection heuristics
- [ ] Test with Apple Pencil
- [ ] Test with Surface Pen

---

## Testing Strategy

### PWA Compliance
- [ ] Lighthouse PWA audit (score >90)
- [ ] Test install on iOS (Safari)
- [ ] Test install on Android (Chrome)
- [ ] Test install on desktop (Chrome, Edge)
- [ ] Verify offline functionality

### Touch Gestures
- [ ] Pinch zoom on iPad
- [ ] Pinch zoom on Android tablet
- [ ] Swipe navigation on mobile
- [ ] Gesture conflicts with browser
- [ ] Multi-touch support

### Stylus Input
- [ ] Apple Pencil on iPad Pro
- [ ] Surface Pen on Surface device
- [ ] Generic capacitive stylus
- [ ] Pressure sensitivity accuracy
- [ ] Palm rejection effectiveness

### Cross-Browser
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Chrome Mobile
- [ ] Safari Mobile

---

## Monitoring & Metrics

### Installation Metrics
- Install rate (conversions from prompt)
- Installed vs web usage ratio
- Uninstall rate (if trackable)
- Platform distribution (iOS/Android/Desktop)

### Offline Usage
- % of sessions offline
- Offline feature usage
- Cache hit rate
- Sync success rate

### Gesture Adoption
- % of users using pinch zoom
- % of users using swipe navigation
- Gesture error rate (conflicts)
- Average gestures per session

### Stylus Usage
- % of sessions with stylus
- Stylus vs touch annotation ratio
- Average stroke count per session
- Pressure sensitivity usage

---

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Service Worker breaks app | High | Low | Extensive testing, fallback, version control |
| Quota exceeded crashes | Medium | Medium | Graceful handling, user notifications |
| Gesture conflicts | Medium | Low | Extensive device testing, config options |
| Poor install conversion | Low | Medium | A/B test prompt timing, improve messaging |
| Offline sync conflicts | Medium | Low | Last-write-wins strategy, user notification |

---

## Future Enhancements

### Phase 10 Considerations
- Background sync for annotations
- Push notifications for updates
- Share target API integration
- File handling API (open PDFs directly)
- Shortcuts API (quick actions)
- Badging API (unsaved changes indicator)

---

## References

- [MDN: Progressive Web Apps](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
- [Workbox Documentation](https://developers.google.com/web/tools/workbox)
- [PointerEvent API](https://developer.mozilla.org/en-US/docs/Web/API/PointerEvent)
- [IndexedDB Best Practices](https://developers.google.com/web/fundamentals/instant-and-offline/web-storage/indexeddb-best-practices)
- [PWA Install Criteria](https://web.dev/install-criteria/)

---

**Decision Maker**: Spark Agent  
**Date**: 2025-01-27  
**Review Date**: 2025-02-27 (1 month)
