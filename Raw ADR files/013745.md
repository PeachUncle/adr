# ADR 008: Document-Wide Search with Result Highlighting

**Date**: 2025-01-27
**Status**: Accepted
**Deciders**: Development Team

## Context

Users need to quickly locate specific content within PDF documents that may contain hundreds of pages. Search is a critical feature mentioned in the PRD as part of Phase 2, with specific requirements:
- Search across entire document within 500ms for documents up to 500 pages
- Real-time result highlighting
- Case-sensitive and whole-word search options
- Navigation between matches with keyboard shortcuts
- Match counter showing current position

The challenge is implementing performant search that works with our canvas-based rendering approach while providing clear visual feedback.

## Decision

We implemented a comprehensive search system with the following architecture:

### 1. Search Service (`SearchService`)
- **Text Extraction**: Uses PDF.js `getTextContent()` to extract text with positional data from each page
- **Caching Strategy**: Caches extracted text per page to avoid redundant extraction on subsequent searches
- **Search Algorithm**: String-based search with support for:
  - Case-sensitive matching
  - Whole-word matching (using regex word boundary checks)
  - Multiple matches per page
- **Bounding Box Calculation**: Computes screen coordinates for each match using PDF transform matrices

### 2. State Management (`useSearch` hook)
- **React Context**: Provides search state globally to all components
- **Match Navigation**: Tracks current match index and provides next/previous functions
- **Progress Tracking**: Reports search progress percentage for user feedback during long searches
- **Page Integration**: Automatically navigates viewport to pages containing the current match

### 3. UI Components

#### SearchBar
- **Floating Design**: Appears at top of viewport with smooth transitions
- **Real-time Search**: Debounced input (300ms) for responsive searching without excessive re-calculations
- **Keyboard Shortcuts**:
  - `Cmd/Ctrl+F`: Open search
  - `Enter`: Next match
  - `Shift+Enter`: Previous match
  - `Esc`: Close search
- **Options**: Checkboxes for case-sensitive (Aa) and whole-word (Word) search
- **Match Counter**: Shows "N of M matches" for user orientation

#### SearchHighlight
- **Overlay Approach**: Renders as absolute-positioned divs over canvas content
- **Visual Distinction**: 
  - Current match: `accent/40` with 2px ring for prominence
  - Other matches: `accent/20` for context without distraction
- **Per-Page Rendering**: Only highlights for visible pages to maintain performance

## Alternatives Considered

### 1. Text Layer Approach
**Description**: Render PDF.js text layer and use browser's native find functionality

**Pros**: 
- Native text selection support
- Browser's built-in search
- Better accessibility for screen readers

**Cons**:
- Text layer positioning is complex and often misaligned with canvas
- Less control over highlight appearance
- Conflicts with custom canvas rendering approach
- Harder to implement custom match navigation
- Additional DOM nodes impact performance

**Why Rejected**: We prioritized visual accuracy and custom highlight control. The canvas-based approach ensures perfect visual alignment and gives us full control over highlight styling. We can add text selection as a separate feature later.

### 2. Full-Text Index (Inverted Index)
**Description**: Build an inverted index of all words in the document upfront

**Pros**:
- Extremely fast search (O(1) word lookup)
- Supports advanced queries (fuzzy search, regex, phrase queries)
- Better for repeated searches

**Cons**:
- Initial indexing cost (slow for large documents, blocks UI)
- Memory overhead (index can be larger than document)
- Overkill for typical use cases
- Complexity doesn't match our needs

**Why Rejected**: String-based search is fast enough for documents up to 500 pages (our target). The added complexity and memory overhead aren't justified. We can revisit if users report performance issues.

### 3. Worker-Based Search
**Description**: Run search in a Web Worker to avoid blocking UI thread

**Pros**:
- Non-blocking search operation
- Better UX for large documents
- Maintains 60fps during search

**Cons**:
- Increased complexity (message passing, serialization)
- PDF.js already uses workers for rendering (additional worker overhead)
- Cannot directly access DOM or React state
- Overkill for search operations that complete in < 500ms

**Why Deferred**: Current implementation is fast enough and non-blocking due to async/await. We can add this optimization if users report UI freezing with very large documents (>1000 pages).

## Implementation Details

### Text Extraction
```typescript
const textContent = await page.getTextContent()
const items = textContent.items
  .filter((item): item is TextItem => 'str' in item)
  .map(item => ({
    str: item.str,
    transform: item.transform,  // [scaleX, skewY, skewX, scaleY, x, y]
    width: item.width,
    height: item.height
  }))
```

### Bounding Box Calculation
We use PDF transform matrices to convert PDF coordinates to screen coordinates:
```typescript
const [scaleX, , , scaleY, x, y] = item.transform
const box = {
  x,
  y,
  width: item.width * Math.abs(scaleX),
  height: item.height * Math.abs(scaleY)
}
```

**Note**: PDF.js y-coordinates are bottom-up (origin at bottom-left), so we flip them in the render layer.

### Performance Considerations
- **Caching**: Text extraction results are cached per page (survives zoom changes)
- **Debouncing**: Search input is debounced by 300ms to reduce re-calculations
- **Lazy Highlighting**: Only visible pages render highlight overlays (virtualized)
- **Progress Reporting**: Long searches report progress to show spinner and percentage

## Consequences

### Positive
- ✅ Fast search performance (< 500ms for 500-page documents, meets PRD requirement)
- ✅ Clear visual feedback with distinct current match highlighting
- ✅ Intuitive keyboard navigation matches macOS Preview
- ✅ Clean separation of concerns (service layer, state management, UI)
- ✅ Extensible for future features (search history, regex, find & replace)
- ✅ Memory-efficient with page-level caching
- ✅ Works seamlessly with existing virtualized rendering

### Negative
- ❌ No native text selection from search results (requires separate text layer)
- ❌ Bounding boxes may be slightly inaccurate for complex typography (rotated text, ligatures, right-to-left languages)
- ❌ Search is not instant for very large documents (>1000 pages)
- ❌ No fuzzy search (typo tolerance)

### Neutral
- 📝 Text extraction cache grows with document size (acceptable trade-off for performance)
- 📝 Search is single-threaded (could be improved with Web Workers if needed)
- 📝 Highlights are visual overlays, not selectable (consistent with canvas approach)

## Related Decisions
- ADR 001: PDF.js for rendering (enables text extraction via `getTextContent()`)
- ADR 006: Virtualized rendering (search highlights respect virtualization)
- ADR 007: Keyboard navigation (search adds Cmd/Ctrl+F, Enter, Shift+Enter)

## Future Improvements
1. **Search History**: Dropdown with recent searches for quick re-search
2. **Regular Expressions**: Support regex patterns for power users
3. **Find & Replace**: For editable text annotations (Phase 3+)
4. **Fuzzy Search**: Typo tolerance using Levenshtein distance
5. **Search Scope**: Options for current page, selection, or all pages
6. **Export Results**: Generate list of matches with page numbers and context
7. **Search Panel**: Dedicated sidebar showing all matches with context preview
8. **Multi-term Search**: AND/OR operators for complex queries

## References
- [PDF.js Text Layer Documentation](https://mozilla.github.io/pdf.js/examples/)
- [PRD Section 3: Text Selection & Search](../../PRD.md)
- Implementation Status: Phase 2 Complete
