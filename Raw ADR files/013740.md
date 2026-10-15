# ADR-003: Annotation System Architecture

**Date**: 2025-01-XX
**Status**: Accepted
**Context**: Phase 3 Implementation

## Context

We need to implement a comprehensive annotation system that allows users to mark up PDF documents with highlights, drawings, shapes, text boxes, notes, and signatures. The system must support undo/redo, annotation persistence, and eventually export annotations back into the PDF.

## Decision

We will implement a layered annotation system with the following architecture:

### 1. Data Layer
- **AnnotationService**: Singleton service managing all annotations
  - Uses observer pattern for reactive updates
  - Maintains undo/redo history (max 20 operations)
  - Stores annotations in memory during session
  - Provides export/import functionality for persistence

### 2. State Management Layer  
- **useAnnotations hook**: React context providing annotation state
  - Wraps AnnotationService with React lifecycle
  - Manages active tool and tool settings
  - Tracks selected annotations
  - Provides convenient CRUD operations

### 3. Rendering Layer
- **AnnotationLayer**: SVG-based rendering of committed annotations
  - Positioned absolutely over PDF canvas
  - Renders all annotation types using SVG primitives
  - Handles selection highlighting
  - Efficient re-renders via React

- **AnnotationDrawing**: Interactive drawing layer
  - Separate SVG layer for in-progress annotations
  - Handles mouse events for drawing
  - Provides real-time preview
  - Commits to AnnotationService on completion

### 4. UI Layer
- **MarkupToolbar**: Tool selection and settings
  - Progressive disclosure for color/thickness pickers
  - Visual feedback for active tool
  - Undo/redo controls
  - Delete selected annotation

## Annotation Types

```typescript
type AnnotationType = 'highlight' | 'pen' | 'rectangle' | 'circle' | 
                      'arrow' | 'line' | 'text' | 'note' | 'signature'
```

Each annotation type has specific properties:
- **Highlight**: Array of bounding boxes (for multi-line), color, opacity
- **Pen**: Array of points, color, thickness
- **Shapes**: Start/end points, color, thickness
- **Text**: Position, content, font size, color, dimensions
- **Note**: Position, content (shown as icon with hover/click)
- **Signature**: Position, image data, dimensions

## Consequences

### Positive
- **Separation of concerns**: Clear boundaries between data, state, rendering, and UI
- **Performance**: SVG rendering is efficient and scalable
- **Testability**: Service layer can be tested independently
- **Flexibility**: Easy to add new annotation types
- **Undo/redo**: Built into service layer, works for all operations

### Negative
- **Memory**: All annotations stored in memory (acceptable for typical documents)
- **Complexity**: Multiple layers add architectural complexity
- **Two render layers**: Separate layers for committed vs in-progress annotations (necessary for performance)

### Trade-offs
- **No real-time collaboration**: Focused on single-user editing (future enhancement)
- **Session-based**: Annotations lost on refresh unless explicitly exported (will add auto-save with Spark KV)
- **SVG vs Canvas**: SVG chosen for easier hit detection and DOM manipulation over canvas rendering

## Implementation Notes

### Why SVG?
- Built-in hit detection (click events)
- Easy selection highlighting
- Scalable without quality loss
- CSS styling support
- Simpler than canvas-based approach

### Why separate Drawing layer?
- Avoids re-rendering all annotations during drawing
- Provides smoother real-time feedback
- Cleaner separation of concerns

### Why Observer pattern?
- Decouples service from React
- Allows multiple components to react to changes
- Makes service testable without React
- Future-proof for non-React integrations

## Alternatives Considered

### Canvas-based rendering
**Rejected**: More complex hit detection, harder to implement selection, requires manual redraw on every change.

### Single SVG layer for all
**Rejected**: Would cause performance issues during drawing as all annotations re-render on every mouse move.

### Redux/Zustand for state
**Rejected**: React Context sufficient for current scope, simpler architecture, easier to understand.

### Database persistence
**Deferred**: Will add Spark KV persistence in future iteration for auto-save between sessions.

## Future Enhancements

1. **Auto-save with Spark KV**: Persist annotations between sessions
2. **PDF export**: Embed annotations using pdf-lib
3. **Text layer integration**: Enable text selection for highlights
4. **Annotation comments**: Add threaded comments to annotations
5. **Annotation groups**: Group related annotations
6. **Annotation search**: Search annotation content
7. **Annotation analytics**: Track annotation usage patterns
