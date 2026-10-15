# ADR-0005: React Context for State Management

## Status
Accepted

## Date
2025-01-XX

## Context

The PDF Viewer & Editor needs to manage complex state:
- Current PDF document and metadata
- Rendered pages (canvases)
- Annotations array
- UI state (zoom, current page, selected tool)
- Undo/redo history
- User preferences

**Requirements**:
- State accessible across multiple components
- Minimize prop drilling
- Support undo/redo
- Performant updates (don't re-render entire app)
- Type-safe
- Simple to understand and maintain
- No external dependencies (if possible)

**State Sharing Needs**:
- Toolbar needs to know current page, zoom, tool
- PDFViewer needs document, zoom, annotations
- Sidebar needs page thumbnails, current page
- Multiple components need to update annotations

## Decision

We will use **React Context API** with custom hooks for state management, supplemented by local component state where appropriate.

**Architecture**:
```
PDFProvider (Context)
├─ Document state (PDF document, metadata)
├─ View state (zoom, current page, scroll position)
├─ Annotation state (annotations, selected, history)
└─ Tool state (active tool, tool options)

Component State
├─ Form inputs (controlled components)
├─ UI toggles (dropdown open/closed)
├─ Temporary state (mouse position during drag)

Spark KV (Persistent)
├─ Saved signatures
├─ User preferences
└─ Recent colors
```

## Consequences

### Positive
- **Zero Dependencies**: Built into React, no additional libraries
- **Type Safe**: Full TypeScript support
- **Simple**: Easy to understand for new developers
- **Flexible**: Can split into multiple contexts if needed
- **Testing**: Easy to test with custom provider
- **Performance**: Can optimize with useMemo and selective subscriptions
- **Built-in**: No learning curve for React developers

### Negative
- **Boilerplate**: More code than Redux Toolkit
- **Performance**: Need to be careful about unnecessary re-renders
- **DevTools**: No Redux DevTools (but React DevTools works)
- **No Middleware**: Must implement side effects manually
- **Context Hell**: Can get nested if split into many contexts

### Neutral
- Need to memoize context values to prevent re-renders
- Requires understanding of React rendering behavior
- Multiple contexts can increase complexity

## Alternatives Considered

### Alternative 1: Redux Toolkit
- **Description**: Official Redux library with modern API
- **Pros**: 
  - Excellent DevTools
  - Time-travel debugging
  - Middleware ecosystem
  - Large community
  - Proven at scale
- **Cons**: 
  - Additional dependency (15KB gzipped)
  - Learning curve for Redux concepts
  - More boilerplate than Context
  - Overkill for this application size
- **Why rejected**: Unnecessary complexity for single-user, client-side app. Context API is sufficient and has zero dependencies.

### Alternative 2: Zustand
- **Description**: Lightweight state management library
- **Pros**: 
  - Very simple API
  - Small bundle (2KB)
  - No Context Provider needed
  - Good DevTools integration
  - Supports middleware
- **Cons**: 
  - External dependency
  - Less familiar to React developers
  - Smaller community than Redux
- **Why rejected**: While excellent, Context API achieves our goals without external dependencies. Keep dependencies minimal.

### Alternative 3: Jotai/Recoil
- **Description**: Atomic state management
- **Pros**: 
  - Fine-grained reactivity
  - Excellent performance
  - Modern API
  - Selector pattern
- **Cons**: 
  - Additional dependencies
  - Less mature than Redux
  - Learning curve
  - More complex mental model
- **Why rejected**: Atomic state is powerful but unnecessarily complex for our use case. Context API is simpler and sufficient.

### Alternative 4: MobX
- **Description**: Observable state management
- **Pros**: 
  - Automatic reactivity
  - Less boilerplate
  - Simple to use
  - Mutable updates
- **Cons**: 
  - External dependency
  - Magic can be confusing
  - Decorators syntax (TypeScript configuration)
  - Smaller community
- **Why rejected**: "Magic" nature can be confusing. Prefer explicit React patterns. Context API is more straightforward.

### Alternative 5: Props Only (No Global State)
- **Description**: Pass all state through props
- **Pros**: 
  - Explicit data flow
  - No global state
  - Easy to track changes
  - Simple mental model
- **Cons**: 
  - Severe prop drilling (5+ levels deep)
  - Many intermediate components
  - Hard to maintain
  - Tedious to refactor
- **Why rejected**: Prop drilling becomes unmaintainable with our component tree depth. Would significantly hurt developer experience.

## Implementation Notes

### Context Structure

```typescript
// src/hooks/usePDF.tsx

interface PDFContextValue {
  // Document state
  document: PDFDocumentProxy | null
  fileName: string | null
  numPages: number
  isLoading: boolean
  error: Error | null
  
  // View state
  zoom: number
  currentPage: number
  viewMode: 'single' | 'continuous'
  
  // Annotation state
  annotations: Annotation[]
  selectedAnnotationId: string | null
  
  // Tool state
  activeTool: Tool | null
  toolOptions: ToolOptions
  
  // Actions
  loadDocument: (file: File) => Promise<void>
  setZoom: (zoom: number) => void
  goToPage: (page: number) => void
  addAnnotation: (annotation: Annotation) => void
  updateAnnotation: (id: string, updates: Partial<Annotation>) => void
  deleteAnnotation: (id: string) => void
  selectAnnotation: (id: string | null) => void
  setActiveTool: (tool: Tool | null) => void
  undo: () => void
  redo: () => void
}

const PDFContext = createContext<PDFContextValue | null>(null)
```

### Provider Implementation

```typescript
export function PDFProvider({ children }: { children: ReactNode }) {
  // State
  const [document, setDocument] = useState<PDFDocumentProxy | null>(null)
  const [fileName, setFileName] = useState<string | null>(null)
  const [zoom, setZoom] = useState(1.0)
  const [currentPage, setCurrentPage] = useState(1)
  const [annotations, setAnnotations] = useState<Annotation[]>([])
  const [selectedAnnotationId, setSelectedAnnotationId] = useState<string | null>(null)
  const [activeTool, setActiveTool] = useState<Tool | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  
  // Derived state
  const numPages = document?.numPages ?? 0
  
  // Actions
  const loadDocument = async (file: File) => {
    setIsLoading(true)
    setError(null)
    try {
      const arrayBuffer = await file.arrayBuffer()
      const loadingTask = pdfjsLib.getDocument(arrayBuffer)
      const pdf = await loadingTask.promise
      setDocument(pdf)
      setFileName(file.name)
      setCurrentPage(1)
      setAnnotations([]) // Clear annotations for new document
    } catch (err) {
      setError(err as Error)
    } finally {
      setIsLoading(false)
    }
  }
  
  const addAnnotation = useCallback((annotation: Annotation) => {
    setAnnotations((prev) => [...prev, { ...annotation, id: crypto.randomUUID() }])
  }, [])
  
  // Memoize context value to prevent unnecessary re-renders
  const value = useMemo(
    () => ({
      document,
      fileName,
      numPages,
      isLoading,
      error,
      zoom,
      currentPage,
      annotations,
      selectedAnnotationId,
      activeTool,
      loadDocument,
      setZoom,
      goToPage: setCurrentPage,
      addAnnotation,
      updateAnnotation,
      deleteAnnotation,
      selectAnnotation: setSelectedAnnotationId,
      setActiveTool,
      undo,
      redo,
    }),
    [
      document,
      fileName,
      numPages,
      isLoading,
      error,
      zoom,
      currentPage,
      annotations,
      selectedAnnotationId,
      activeTool,
    ]
  )
  
  return <PDFContext.Provider value={value}>{children}</PDFContext.Provider>
}
```

### Custom Hook

```typescript
export function usePDF() {
  const context = useContext(PDFContext)
  if (!context) {
    throw new Error('usePDF must be used within PDFProvider')
  }
  return context
}
```

### Usage in Components

```typescript
function Toolbar() {
  const { zoom, setZoom, currentPage, numPages, goToPage } = usePDF()
  
  return (
    <div>
      <button onClick={() => setZoom(zoom + 0.1)}>Zoom In</button>
      <span>{currentPage} / {numPages}</span>
      <button onClick={() => goToPage(currentPage + 1)}>Next</button>
    </div>
  )
}

function PDFViewer() {
  const { document, zoom, annotations } = usePDF()
  
  return (
    <div>
      {/* Render pages with annotations */}
    </div>
  )
}
```

### Performance Optimization

**Split Contexts** (if needed):
```typescript
// Split into multiple contexts to reduce re-renders
const DocumentContext = createContext<DocumentState>(...)
const ViewContext = createContext<ViewState>(...)
const AnnotationContext = createContext<AnnotationState>(...)

// Consumers only re-render when their context changes
function Toolbar() {
  const { zoom, setZoom } = useView() // Only re-renders on view changes
  // ...
}
```

**Selector Pattern**:
```typescript
// Custom hook with selector to avoid re-renders
function usePDFSelector<T>(selector: (state: PDFContextValue) => T): T {
  const context = usePDF()
  return useMemo(() => selector(context), [context, selector])
}

// Usage
function PageCounter() {
  const currentPage = usePDFSelector((state) => state.currentPage)
  const numPages = usePDFSelector((state) => state.numPages)
  // Only re-renders when currentPage or numPages changes
  return <span>{currentPage} / {numPages}</span>
}
```

### Testing

```typescript
// Test helper
function renderWithPDFProvider(
  ui: ReactElement,
  { initialState }: { initialState?: Partial<PDFContextValue> } = {}
) {
  const wrapper = ({ children }: { children: ReactNode }) => (
    <PDFProvider initialState={initialState}>{children}</PDFProvider>
  )
  return render(ui, { wrapper })
}

// Test
it('updates zoom level', () => {
  const { getByText } = renderWithPDFProvider(<Toolbar />)
  fireEvent.click(getByText('Zoom In'))
  expect(getByText('110%')).toBeInTheDocument()
})
```

## When to Use Component State vs Context

**Use Context** when:
- State is needed in multiple unrelated components
- State is global to the PDF viewer
- Avoiding prop drilling (3+ levels deep)

**Use Component State** when:
- State is specific to one component
- Form inputs (controlled components)
- UI toggles (dropdown open/closed)
- Temporary state (mouse position during drag)

**Use Spark KV** when:
- State should persist across sessions
- User preferences
- Saved signatures
- Recent colors

## Future Considerations

If the application grows significantly:
- Consider Zustand for simpler API
- Consider Redux Toolkit for DevTools and middleware
- Consider splitting into multiple contexts
- Consider implementing selector pattern for performance

## References
- [React Context API](https://react.dev/reference/react/useContext)
- [React Performance Optimization](https://react.dev/learn/render-and-commit)
- Related: [0004-annotation-storage.md](0004-annotation-storage.md)
- PRD: State Management requirements
- ARCHITECTURE.md: "State Management" section
