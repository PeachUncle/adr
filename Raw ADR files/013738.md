# ADR-0009: High-DPI Canvas Rendering Fix

## Status
Accepted

## Date
2025-01-27

## Context

Users reported that PDF rendering appears blurry at 100% zoom on high-DPI displays (Retina, 4K monitors, etc.). The issue affects both the main PDF viewer and thumbnail sidebar.

The root cause is that HTML canvas elements render at CSS pixel resolution by default, not physical pixel resolution. On a 2x Retina display, a canvas with `width="100"` renders 100 CSS pixels but only uses 100 physical pixels, resulting in blurry output when the browser scales it up to 200 physical pixels.

The existing PDFService implementation already accounts for `devicePixelRatio` in the rendering logic (lines 59-85 of pdf.service.ts), but the implementation may have subtle issues with how canvas dimensions are being set or cached.

## Decision

We will ensure consistent high-DPI rendering across all canvas elements by:

1. **Always multiply scale by `devicePixelRatio`** when rendering to canvas
2. **Set canvas internal dimensions** (width/height attributes) to physical pixels
3. **Set canvas CSS dimensions** (style.width/style.height) to logical CSS pixels
4. **Apply devicePixelRatio to cache keys** to prevent mismatched cached renders
5. **Verify thumbnail rendering** uses the same high-DPI aware rendering path

The formula for each canvas:
```typescript
const dpr = window.devicePixelRatio || 1
const viewport = page.getViewport({ scale: scale * dpr })

canvas.width = viewport.width  // Physical pixels
canvas.height = viewport.height  // Physical pixels
canvas.style.width = `${viewport.width / dpr}px`  // CSS pixels
canvas.style.height = `${viewport.height / dpr}px`  // CSS pixels
```

## Consequences

### Positive
- Crisp, sharp rendering on all display types (standard, Retina, 4K)
- Professional appearance matching native PDF viewers
- Better readability of text at all zoom levels
- Consistent quality between main viewer and thumbnails

### Negative
- Slightly higher memory usage (2x-3x pixels on high-DPI displays)
- Marginal performance impact on low-end devices
- Cache size increases proportionally to devicePixelRatio

### Neutral
- Behavior unchanged on standard DPI displays (dpr = 1)
- Existing cache eviction logic handles increased memory naturally

## Alternatives Considered

### Alternative 1: Ignore devicePixelRatio and render at CSS resolution
- **Description**: Keep canvas dimensions equal to CSS dimensions
- **Pros**: Lower memory usage, simpler code
- **Cons**: Blurry on modern displays, unprofessional appearance
- **Why rejected**: Quality is paramount for a PDF viewer; users expect crisp text

### Alternative 2: Make high-DPI rendering optional via settings
- **Description**: Let users toggle between quality and performance
- **Pros**: Users with performance concerns can optimize
- **Cons**: Adds UI complexity, most users won't understand the setting
- **Why rejected**: Modern devices handle high-DPI rendering well; complexity not justified

### Alternative 3: Use SVG rendering instead of canvas
- **Description**: Render PDF to SVG paths for native vector scaling
- **Pros**: Perfect scaling at any resolution
- **Cons**: PDF.js doesn't support SVG rendering; would require major rewrite
- **Why rejected**: Not feasible with current architecture

## Implementation Notes

### Main Changes Required
1. Verify pdf.service.ts renderPage() correctly applies devicePixelRatio (already implemented)
2. Ensure cache keys include devicePixelRatio (already implemented)
3. Test on various devicePixelRatio values (1.0, 1.5, 2.0, 3.0)
4. Verify no regressions in performance or memory usage

### Testing Checklist
- [ ] Test on 1x display (standard monitor)
- [ ] Test on 2x display (MacBook Retina)
- [ ] Test on 3x display (high-DPI 4K monitor)
- [ ] Verify thumbnails are sharp
- [ ] Verify main canvas is sharp at all zoom levels
- [ ] Check memory usage with large documents
- [ ] Verify cache eviction works correctly

### Browser Compatibility
- Chrome/Edge: Fully supported
- Firefox: Fully supported
- Safari: Fully supported
- All browsers expose `window.devicePixelRatio`

## References
- [MDN: devicePixelRatio](https://developer.mozilla.org/en-US/docs/Web/API/Window/devicePixelRatio)
- [High DPI Canvas](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API/Tutorial/Optimizing_canvas#scaling_for_high_resolution_displays)
- [PDF.js Examples](https://mozilla.github.io/pdf.js/examples/)
- Related: ADR-0001 (PDF.js selection)
- Related: ADR-0003 (Virtualized rendering)
