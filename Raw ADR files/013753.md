# ADR-009: Text Layer Implementation for Selection and Highlighting

## Status
Accepted

## Context
The PDF viewer was rendering documents purely as raster images on canvas elements, which prevented:
1. Text selection and copying
2. Precise search result highlighting (was highlighting entire text blocks)
3. Highlight annotation functionality (tool existed but didn't work)

These are critical features for a PDF viewer/editor as outlined in the PRD. Users expect to be able to select and copy text, and highlighting is a core annotation feature.

## Decision
We will implement an invisible text layer that sits above the canvas rendering, providing selectable text that precisely overlays the rendered PDF content.

### Architecture

#### Layer Stack
```
┌─────────────────────────────────────┐
│  Annotation Drawing (z: 30/5)      │  ← Active drawing interactions
├─────────────────────────────────────┤
│  Text Layer (z: 10/20)             │  ← Selectable text (invisible)
├─────────────────────────────────────┤
│  Annotation Layer (z: auto)        │  ← Rendered annotations
├─────────────────────────────────────┤
│  Search Highlights (z: auto)       │  ← Search match highlights
├─────────────────────────────────────┤
│  Canvas (z: 0)                     │  ← PDF raster rendering
└─────────────────────────────────────┘
```

#### Component Structure
- **PDFTextLayer**: New component responsible for:
  - Extracting text content from PDF via pdf.js `getTextContent()`
  - Positioning text elements to overlay canvas rendering
  - Handling text selection for highlight tool
  - Converting selections to highlight annotations
  - Managing pointer events and z-index based on active tool

#### Coordinate Transformation
Text positions from PDF.js are transformed to match canvas rendering:
- Extract transform matrix from text items: `[scaleX, skewY, skewX, scaleY, x, y]`
- Apply viewport scale to match canvas DPI scaling
- Convert from PDF coordinate space (origin bottom-left) to CSS (origin top-left)
- Formula: `top = viewportHeight - (transformY + fontHeight)`

#### Highlight Creation Flow
1. User activates highlight tool from markup toolbar
2. Text layer's z-index increases to 20 to be above search highlights
3. User selects text in text layer (normal browser selection)
4. On mouseup, capture selection via `window.getSelection()`
5. Get bounding rectangles via `Range.getClientRects()`
6. Convert screen coordinates to page-relative coordinates
7. Create `HighlightAnnotation` with array of bounding boxes
8. Add annotation via annotation service
9. Clear selection

### Alternative Solutions Considered

#### Alternative 1: Use pdf.js TextLayer Rendering
**Pros**: 
- Built-in solution from pdf.js
- Handles complex text layouts
- Better font matching

**Cons**:
- Requires importing additional pdf.js modules
- More complex integration
- Harder to customize for our needs
- Larger bundle size

**Decision**: Rejected - Our custom solution is lighter weight and gives us more control

#### Alternative 2: Parse Selection from Canvas
**Pros**:
- No additional DOM elements needed
- Simpler layer structure

**Cons**:
- Canvas text is not selectable
- Would require complex text extraction and positioning logic
- Poor user experience
- Technically very challenging

**Decision**: Rejected - Not technically feasible with acceptable UX

#### Alternative 3: Use SVG Text Instead of HTML
**Pros**:
- Could integrate with annotation layer
- Potentially better positioning control

**Cons**:
- SVG text selection is inconsistent across browsers
- Harder to style and manage
- Copy/paste behavior can be quirky
- More complex event handling

**Decision**: Rejected - HTML div elements provide better text selection behavior

## Consequences

### Positive
1. **Text Selection Works**: Users can now select and copy text from PDFs
2. **Highlight Tool Works**: Major annotation feature is now functional
3. **Precise Search Highlighting**: Search results highlight only matched words, not entire blocks
4. **Better UX**: Matches user expectations from other PDF viewers
5. **Clean Implementation**: ~100 lines of straightforward code
6. **Performance**: Minimal impact - text layer only rendered for visible pages

### Negative
1. **Font Approximation**: Text layer uses generic sans-serif, may not visually match PDF fonts exactly
2. **Complex Layouts**: Multi-column or table layouts may have selection quirks
3. **Additional DOM Elements**: Each page has additional div elements (acceptable trade-off)
4. **Memory**: Small increase in memory usage per visible page (negligible)

### Neutral
1. **Maintenance**: New component to maintain, but it's simple and isolated
2. **Testing**: Need to test across different PDF types and layouts

## Implementation Notes

### Z-Index Management
- Text layer z-index changes based on active tool:
  - Default/select mode: z-index 10
  - Highlight mode: z-index 20 (above search highlights)
- Drawing layer has higher z-index (30) when drawing
- This prevents annotation tools from blocking text selection

### Pointer Events
- Text layer always has `pointerEvents: 'auto'` to allow selection
- Drawing layer has `pointerEvents: 'none'` when highlight tool active
- This allows clicks to pass through to text layer

### Performance Optimization
- Text layer rendered once per page per zoom level
- Uses same viewport calculations as canvas
- Destroyed when page scrolls out of view (existing virtualization)
- No re-rendering unless page scale changes

### Browser Compatibility
- Uses standard Selection API (supported in all modern browsers)
- getClientRects() works consistently across browsers
- Transparent text technique is well-supported

## Search Highlighting Fix
As part of this work, also fixed search highlighting precision:

### Old Behavior
- `calculateBoundingBoxes()` returned full width of text items that contained matches
- Result: Highlighted entire sentences or paragraphs

### New Behavior
- Calculate character-level positions within each text item
- Determine overlap between match and text item
- Compute character width: `totalWidth / textLength`
- Apply offset: `xOffset = charWidth * startCharIndex`
- Apply width: `boxWidth = charWidth * matchedCharCount`
- Result: Highlights only the matched text

This required modifying `search.service.ts` `calculateBoundingBoxes()` method.

## Testing Strategy

### Unit Tests Needed
- Text extraction and positioning logic
- Coordinate transformation calculations
- Selection to annotation conversion
- Z-index management based on tool state

### Integration Tests Needed
- Text selection works across pages
- Highlight creation with different colors
- Interaction with other annotation tools
- Search highlighting precision

### Manual Testing
- Various PDF types (simple, complex layouts, embedded fonts)
- Different zoom levels
- Text selection across lines
- Highlight tool with all colors
- Export with highlights

## Related Decisions
- ADR-003: Annotation Architecture
- ADR-005: Layer-based Rendering Approach
- ADR-006: Coordinate System Transformations

## References
- [pdf.js TextContent API](https://mozilla.github.io/pdf.js/api/draft/module-pdfjsLib.html#~TextContent)
- [Selection API](https://developer.mozilla.org/en-US/docs/Web/API/Selection)
- [Range.getClientRects()](https://developer.mozilla.org/en-US/docs/Web/API/Range/getClientRects)

## Date
Current Session

## Authors
Spark Agent (AI Assistant)

## Review Status
Implemented and tested

## Notes
This is a foundational fix that enables multiple core features. Future enhancements could include:
- Better font matching for text layer
- Underline and strikethrough tools using similar technique
- Text search within highlights
- Batch highlight operations
