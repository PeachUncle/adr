# ADR-0003: Virtualized Page Rendering Strategy

## Status
Accepted

## Date
2025-01-XX

## Context

PDF documents can be very large (100+ pages, 1000+ in extreme cases). Rendering all pages at once creates serious performance and memory problems:

**Problems with Naive Rendering**:
- Memory: 100-page PDF = 100 canvases × ~5MB each = 500MB+ RAM usage
- CPU: Rendering 100+ pages on initial load causes UI freeze (seconds of blocking)
- Scrolling: Browser struggles with hundreds of large DOM elements
- User Experience: Long loading times before user can interact

**Requirements**:
- Render PDFs with 1000+ pages without performance degradation
- First page visible within 1 second of opening
- Smooth 60fps scrolling
- Memory usage under 200MB for typical documents
- No visible lag when scrolling between pages

## Decision

We will implement **virtualized page rendering** with a buffered viewport strategy.

**Core Principles**:
1. Only render pages that are visible or near the viewport
2. Maintain a buffer of pages above and below visible area
3. Lazy-load and destroy pages as user scrolls
4. Cache rendered canvases with LRU eviction
5. Use Intersection Observer API to detect visible pages

## Consequences

### Positive
- **Scalability**: Can handle PDFs with 1000+ pages
- **Fast initial load**: First page renders in <1 second
- **Low memory**: Only ~3-5 pages rendered at a time (15-25MB)
- **Smooth scrolling**: No jank, maintains 60fps
- **Better UX**: Users can start reading immediately
- **Battery life**: Less CPU usage = better for laptops/mobile

### Negative
- **Complexity**: More complex than rendering all pages
- **Edge cases**: Must handle rapid scrolling, page size variations
- **Flashing**: Brief blank pages during very fast scrolling (acceptable trade-off)
- **Testing**: Harder to test scrolling behavior
- **State management**: Need to track which pages are rendered

### Neutral
- Requires careful tuning of buffer size (trade-off between memory and flashing)
- Need placeholder elements for unrendered pages to maintain scroll height
- Must calculate page positions for scroll synchronization

## Alternatives Considered

### Alternative 1: Render All Pages
- **Description**: Render every page on document load
- **Pros**: 
  - Simple implementation
  - No complexity with visibility detection
  - All pages immediately available
  - No flashing during scroll
- **Cons**: 
  - Unusable for large documents (minutes to load)
  - Crashes browser with memory overflow on 500+ page docs
  - Terrible user experience
- **Why rejected**: Does not meet performance requirements. Unacceptable for production use.

### Alternative 2: Page-by-Page Loading
- **Description**: Only render current page, load next page on demand
- **Pros**: 
  - Minimal memory usage
  - Very simple to implement
  - Works well for single-page navigation
- **Cons**: 
  - Breaks scrolling UX (users expect continuous scroll)
  - Requires pagination controls (not Preview-like)
  - Cannot scroll freely through document
  - Jarring page transitions
- **Why rejected**: Does not match Preview's continuous scrolling UX. Not how users expect to navigate PDFs.

### Alternative 3: Progressive Canvas Rendering
- **Description**: Render all pages but use lower resolution until viewed
- **Pros**: 
  - All pages present
  - Better than full resolution for all
  - Can provide thumbnail quality quickly
- **Cons**: 
  - Still renders all pages (memory issue)
  - Complex resolution switching logic
  - Blurry pages until loaded
  - Doesn't solve fundamental scalability problem
- **Why rejected**: Doesn't solve core memory issue. Still crashes on 1000+ page documents.

### Alternative 4: Server-Side Rendering
- **Description**: Render pages on server, send images to client
- **Pros**: 
  - Client memory stays low
  - Can optimize on server
  - Faster initial render (send pre-rendered images)
- **Cons**: 
  - Requires server infrastructure
  - Violates "client-side only" requirement
  - Privacy concerns
  - Network latency
  - Server costs
- **Why rejected**: Fundamentally conflicts with core project principle of 100% client-side processing.

## Implementation Notes

### Architecture

```typescript
interface VirtualizedRenderer {
  // Track which pages should be rendered
  visiblePageRange: { start: number; end: number }
  
  // Buffer configuration
  bufferPages: number // Pages to render above/below viewport
  
  // Rendered page cache
  renderedPages: Map<number, HTMLCanvasElement>
  
  // Page metadata
  pageHeights: number[]
  pageTops: number[]
}
```

### Algorithm

```typescript
function calculateVisiblePages(
  scrollTop: number,
  viewportHeight: number,
  pageHeights: number[],
  bufferPages: number = 2
): { start: number; end: number } {
  let currentTop = 0
  let startPage = -1
  let endPage = -1
  
  for (let i = 0; i < pageHeights.length; i++) {
    const pageBottom = currentTop + pageHeights[i]
    
    // Page is in viewport or buffer
    if (pageBottom >= scrollTop - (bufferPages * 1000) &&
        currentTop <= scrollTop + viewportHeight + (bufferPages * 1000)) {
      if (startPage === -1) startPage = i
      endPage = i
    }
    
    currentTop = pageBottom + 20 // 20px gap between pages
  }
  
  return { start: Math.max(0, startPage), end: endPage }
}
```

### Using Intersection Observer

```typescript
const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      const pageNum = parseInt(entry.target.dataset.pageNum!)
      
      if (entry.isIntersecting) {
        // Page entering viewport - render it
        renderPage(pageNum)
      } else {
        // Page left viewport - consider cleanup
        schedulePageCleanup(pageNum)
      }
    })
  },
  {
    root: null, // viewport
    rootMargin: '1000px', // Buffer zone
    threshold: 0,
  }
)

// Observe placeholder elements
pageElements.forEach((el) => observer.observe(el))
```

### Page Placeholder Pattern

```tsx
function PagePlaceholder({ pageNum, height }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          renderPageToCanvas(pageNum, canvasRef.current!)
        }
      },
      { rootMargin: '1000px' }
    )
    
    if (canvasRef.current) {
      observer.observe(canvasRef.current)
    }
    
    return () => observer.disconnect()
  }, [pageNum])
  
  return (
    <div style={{ height: `${height}px` }} data-page={pageNum}>
      <canvas ref={canvasRef} />
    </div>
  )
}
```

### Memory Management

```typescript
class PageCache {
  private cache = new Map<number, HTMLCanvasElement>()
  private maxSize = 10 // Keep max 10 rendered pages
  private accessOrder: number[] = []
  
  set(pageNum: number, canvas: HTMLCanvasElement) {
    if (this.cache.size >= this.maxSize) {
      // Evict least recently used
      const lruPage = this.accessOrder.shift()!
      this.cache.delete(lruPage)
    }
    
    this.cache.set(pageNum, canvas)
    this.accessOrder.push(pageNum)
  }
  
  get(pageNum: number): HTMLCanvasElement | undefined {
    const canvas = this.cache.get(pageNum)
    if (canvas) {
      // Move to end (most recently used)
      this.accessOrder = this.accessOrder.filter((p) => p !== pageNum)
      this.accessOrder.push(pageNum)
    }
    return canvas
  }
}
```

### Performance Tuning

**Buffer Size**: Trade-off between memory and responsiveness
- Small buffer (1-2 pages): Lower memory, more flashing during fast scroll
- Large buffer (4-5 pages): Higher memory, smoother experience
- **Recommended**: 2 pages above + 2 pages below = 5 total rendered

**Debouncing**: Prevent excessive re-renders during scroll
```typescript
const debouncedUpdatePages = debounce(() => {
  updateVisiblePages()
}, 100) // Wait 100ms after scroll stops

scrollContainer.addEventListener('scroll', debouncedUpdatePages)
```

**Progressive Rendering**: For initial load
```typescript
async function loadDocument(file: File) {
  const pdf = await pdfjsLib.getDocument(arrayBuffer).promise
  
  // Render first page immediately
  await renderPage(1)
  
  // Load remaining pages in background
  requestIdleCallback(() => {
    for (let i = 2; i <= pdf.numPages; i++) {
      // Pre-calculate page heights for scroll positioning
      calculatePageHeight(i)
    }
  })
}
```

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time to first page | <1 second | Load document → first canvas visible |
| Scroll FPS | 60fps | Monitor frame drops during scroll |
| Memory usage (100 pages) | <200MB | Chrome DevTools memory profiler |
| Memory usage (1000 pages) | <250MB | Chrome DevTools memory profiler |
| Page render time | <200ms | Time from request to canvas ready |

## Testing Strategy

```typescript
describe('Virtualized Rendering', () => {
  it('only renders visible pages', async () => {
    const { container } = render(<PDFViewer file={largePDF} />)
    const renderedPages = container.querySelectorAll('canvas')
    expect(renderedPages.length).toBeLessThan(10) // Not all 100+ pages
  })
  
  it('renders new pages when scrolling', async () => {
    const { container } = render(<PDFViewer file={largePDF} />)
    
    // Scroll to page 50
    fireEvent.scroll(container, { target: { scrollTop: 50000 } })
    
    await waitFor(() => {
      const page50 = container.querySelector('[data-page="50"]')
      expect(page50).toBeInTheDocument()
    })
  })
  
  it('cleans up off-screen pages', async () => {
    // Test LRU cache eviction
  })
})
```

## References
- [Intersection Observer API](https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API)
- [react-window](https://github.com/bvaughn/react-window) - Virtual scrolling library for inspiration
- [Virtualized Lists in React](https://web.dev/virtualize-long-lists-react-window/)
- PRD: Performance Requirements
- ARCHITECTURE.md: PDFService - Rendering Strategy
- Related: [0001-pdf-rendering-library.md](0001-pdf-rendering-library.md)
