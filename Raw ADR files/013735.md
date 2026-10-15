# ADR-0004: Annotation Data Structure and Storage

## Status
Accepted

## Date
2025-01-XX

## Context

The PDF viewer needs to support multiple annotation types (highlights, drawings, shapes, text, signatures) that:
- Overlay on top of rendered PDF pages
- Can be edited, moved, resized, deleted
- Persist across sessions
- Export to PDF via pdf-lib
- Support undo/redo operations
- Perform well with hundreds of annotations

**Requirements**:
- Store annotation position relative to PDF coordinates (not screen pixels)
- Handle different annotation types with shared and unique properties
- Enable efficient querying (e.g., "get all annotations for page 5")
- Support serialization for export and persistence
- Allow undo/redo history

## Decision

We will use a **typed TypeScript structure** with annotations stored in React Context and persisted via Spark KV.

### Data Structure

```typescript
interface BaseAnnotation {
  id: string // UUID
  type: AnnotationType
  pageNum: number
  timestamp: number
  bounds: {
    x: number      // PDF coordinates (not screen pixels)
    y: number
    width: number
    height: number
  }
}

type AnnotationType = 
  | 'highlight' 
  | 'underline' 
  | 'strikethrough'
  | 'pen' 
  | 'shape' 
  | 'text' 
  | 'signature'
  | 'note'

interface HighlightAnnotation extends BaseAnnotation {
  type: 'highlight' | 'underline' | 'strikethrough'
  color: string // hex color
  opacity: number // 0-1
  textContent?: string // Selected text for searchability
}

interface PenAnnotation extends BaseAnnotation {
  type: 'pen'
  points: { x: number; y: number }[] // Path points
  color: string
  thickness: number
  opacity: number
}

interface ShapeAnnotation extends BaseAnnotation {
  type: 'shape'
  shapeType: 'rectangle' | 'circle' | 'arrow' | 'line'
  strokeColor: string
  fillColor?: string
  strokeWidth: number
  opacity: number
}

interface TextAnnotation extends BaseAnnotation {
  type: 'text'
  content: string
  fontSize: number
  fontFamily: string
  color: string
  alignment: 'left' | 'center' | 'right'
}

interface SignatureAnnotation extends BaseAnnotation {
  type: 'signature'
  imageData: string // Base64 image or reference to stored signature
  signatureId?: string // Reference to saved signature
}

interface NoteAnnotation extends BaseAnnotation {
  type: 'note'
  content: string
  color: string // Sticky note color
  author?: string
}

type Annotation = 
  | HighlightAnnotation 
  | PenAnnotation 
  | ShapeAnnotation 
  | TextAnnotation 
  | SignatureAnnotation 
  | NoteAnnotation

interface AnnotationState {
  annotations: Annotation[]
  selectedId: string | null
  history: {
    past: Annotation[][]
    future: Annotation[][]
  }
}
```

### Storage Strategy

**In-Memory (React Context)**:
- Active document annotations
- Undo/redo history
- Selected annotation state

**Persistent (Spark KV)**:
- Saved signatures (reusable across documents)
- User preferences (default colors, thickness)
- Recently used colors

**Not Persisted**:
- Annotations are part of PDF document
- Export annotations into PDF when saving
- No separate annotation database

## Consequences

### Positive
- **Type Safety**: TypeScript ensures correct annotation structure
- **Efficient Querying**: Can filter by page number, type, etc.
- **Flexible**: Easy to add new annotation types
- **Serializable**: JSON-friendly for export and persistence
- **PDF Coordinate System**: Annotations survive zoom/pan/resize
- **Undo/Redo Ready**: Immutable structure supports history
- **Memory Efficient**: Only store what's needed

### Negative
- **Not Persistent Per Document**: Annotations lost on page reload (by design - export to PDF to save)
- **Memory Growth**: Large number of annotations increases memory
- **Complex Types**: Type guards needed for type-specific operations
- **Coordinate Conversion**: Must convert between PDF and screen coordinates

### Neutral
- Annotations embedded in exported PDF (not separate file)
- No collaboration features (single user)
- No annotation versioning

## Alternatives Considered

### Alternative 1: Store Annotations in Spark KV Per Document
- **Description**: Save annotations separately, keyed by document hash
- **Pros**: 
  - Annotations persist across sessions
  - Can annotate multiple documents
  - Undo after closing document
- **Cons**: 
  - Privacy concern (document data in storage)
  - Storage management complexity
  - Large storage usage
  - What about modified PDFs? (hash changes)
- **Why rejected**: Conflicts with privacy-first principle. Users should explicitly export to save. Preview doesn't save annotations unless you save the PDF.

### Alternative 2: Single Flat Array
- **Description**: Store all annotations in one array without type discrimination
```typescript
interface Annotation {
  id: string
  type: string
  pageNum: number
  [key: string]: any // Flexible properties
}
```
- **Pros**: 
  - Simple structure
  - Easy to add properties
  - No type guards needed
- **Cons**: 
  - No type safety
  - Easy to make mistakes
  - Hard to understand annotation structure
  - Difficult to refactor
- **Why rejected**: Sacrifices type safety. TypeScript's main benefit is catching errors at compile time.

### Alternative 3: Separate Arrays Per Type
```typescript
interface AnnotationState {
  highlights: HighlightAnnotation[]
  drawings: PenAnnotation[]
  shapes: ShapeAnnotation[]
  // ...
}
```
- **Pros**: 
  - Strong typing without discriminated unions
  - Easy to query by type
- **Cons**: 
  - Harder to query across types
  - Complex undo/redo (multiple arrays)
  - Duplicate logic for shared operations
  - Difficult to maintain z-index order
- **Why rejected**: Makes cross-cutting operations (undo, delete all on page, z-order) unnecessarily complex.

### Alternative 4: Use Existing Annotation Library
- **Description**: PSPDFKit, PDF.js annotations, etc.
- **Pros**: 
  - Pre-built solution
  - Mature implementation
  - Less code to write
- **Cons**: 
  - Less control
  - Bundle size
  - Licensing (commercial)
  - Harder to customize
- **Why rejected**: We need full control for custom UX. PDF.js annotations are limited. PSPDFKit is commercial.

## Implementation Notes

### Context Setup

```typescript
interface PDFContextValue {
  annotations: Annotation[]
  addAnnotation: (annotation: Omit<Annotation, 'id' | 'timestamp'>) => void
  updateAnnotation: (id: string, updates: Partial<Annotation>) => void
  deleteAnnotation: (id: string) => void
  selectAnnotation: (id: string | null) => void
  getPageAnnotations: (pageNum: number) => Annotation[]
  undo: () => void
  redo: () => void
  canUndo: boolean
  canRedo: boolean
}

const PDFContext = createContext<PDFContextValue | null>(null)
```

### Adding Annotations

```typescript
const addAnnotation = (annotation: Omit<Annotation, 'id' | 'timestamp'>) => {
  const newAnnotation: Annotation = {
    ...annotation,
    id: crypto.randomUUID(),
    timestamp: Date.now(),
  }
  
  setAnnotations((current) => {
    // Save to history for undo
    setHistory((h) => ({
      past: [...h.past, current],
      future: [], // Clear redo stack
    }))
    
    return [...current, newAnnotation]
  })
}
```

### Type Guards

```typescript
function isHighlight(ann: Annotation): ann is HighlightAnnotation {
  return ann.type === 'highlight' || ann.type === 'underline' || ann.type === 'strikethrough'
}

function isPen(ann: Annotation): ann is PenAnnotation {
  return ann.type === 'pen'
}

// Use in code
if (isPen(annotation)) {
  // TypeScript knows annotation is PenAnnotation
  renderPath(annotation.points, annotation.thickness)
}
```

### Coordinate Conversion

```typescript
// PDF coordinates to screen coordinates
function pdfToScreen(
  pdfPoint: { x: number; y: number },
  viewport: PageViewport
): { x: number; y: number } {
  const [x, y] = viewport.convertToViewportPoint(pdfPoint.x, pdfPoint.y)
  return { x, y }
}

// Screen coordinates to PDF coordinates
function screenToPDF(
  screenPoint: { x: number; y: number },
  viewport: PageViewport
): { x: number; y: number } {
  const [x, y] = viewport.convertToPdfPoint(screenPoint.x, screenPoint.y)
  return { x, y }
}
```

### Querying Annotations

```typescript
// Get all annotations for a page
const pageAnnotations = annotations.filter((ann) => ann.pageNum === pageNum)

// Get selected annotation
const selected = annotations.find((ann) => ann.id === selectedId)

// Get annotations by type
const highlights = annotations.filter(isHighlight)
```

### Undo/Redo

```typescript
const undo = () => {
  setHistory((h) => {
    if (h.past.length === 0) return h
    
    const previous = h.past[h.past.length - 1]
    const newPast = h.past.slice(0, -1)
    
    setAnnotations(previous)
    
    return {
      past: newPast,
      future: [annotations, ...h.future],
    }
  })
}

const redo = () => {
  // Similar logic for redo
}
```

### Exporting to PDF

```typescript
async function exportWithAnnotations(
  originalPDF: ArrayBuffer,
  annotations: Annotation[]
): Promise<Uint8Array> {
  const pdfDoc = await PDFDocument.load(originalPDF)
  
  // Group by page
  const byPage = groupBy(annotations, (a) => a.pageNum)
  
  for (const [pageNum, anns] of Object.entries(byPage)) {
    const page = pdfDoc.getPage(Number(pageNum) - 1)
    
    for (const ann of anns) {
      switch (ann.type) {
        case 'highlight':
          drawHighlight(page, ann)
          break
        case 'pen':
          drawPath(page, ann)
          break
        // ... other types
      }
    }
  }
  
  return await pdfDoc.save()
}
```

## Performance Considerations

- **Indexing**: Consider Map<pageNum, Annotation[]> for O(1) page lookups
- **Rendering**: Only render annotations for visible pages
- **History Size**: Limit undo history to last 50 actions
- **Memory**: Clear annotations when document closes

## Testing Strategy

```typescript
describe('Annotation System', () => {
  it('adds annotation with generated id', () => {
    const { addAnnotation } = useAnnotations()
    addAnnotation({ type: 'highlight', pageNum: 1, bounds, color })
    expect(annotations).toHaveLength(1)
    expect(annotations[0].id).toBeDefined()
  })
  
  it('filters by page number', () => {
    const page2Anns = getPageAnnotations(2)
    expect(page2Anns.every(a => a.pageNum === 2)).toBe(true)
  })
  
  it('supports undo/redo', () => {
    addAnnotation(ann1)
    addAnnotation(ann2)
    undo()
    expect(annotations).toHaveLength(1)
    redo()
    expect(annotations).toHaveLength(2)
  })
})
```

## References
- Related: [0001-pdf-rendering-library.md](0001-pdf-rendering-library.md)
- Related: [0002-pdf-manipulation-library.md](0002-pdf-manipulation-library.md)
- PRD: "Annotation Toolbar" feature
- ARCHITECTURE.md: "AnnotationService"
- TECHNICAL_SPEC.md: "Annotation System"
