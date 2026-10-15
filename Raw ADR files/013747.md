# ADR 009: Page Management Architecture

**Date**: 2025-01-27  
**Status**: Accepted  
**Context**: Phase 5 - Page Management

## Context

Users need to manipulate PDF pages beyond just viewing them. Common operations include rotating pages to fix orientation issues, deleting unwanted pages, and reordering pages to reorganize documents. These operations must be performant, reversible (undo/redo), and preserve all existing annotations.

## Decision

We've implemented a comprehensive page management system with the following architecture:

### 1. Service Layer: PageManagementService

**Responsibilities**:
- Track page transformations (rotation, deletion state)
- Maintain page ordering
- Implement undo/redo history
- Notify observers of state changes

**Key Design Decisions**:
- **Transformations Map**: Each page has a `PageTransformation` object tracking its rotation (0°, 90°, 180°, 270°) and deletion state
- **Page Order Array**: Separate from transformations, allows reordering without modifying transformation data
- **Observer Pattern**: Components subscribe to state changes for reactive updates
- **History Stack**: Stores up to 20 operations with bidirectional traversal
- **Non-Destructive**: Deletions mark pages as deleted rather than removing them, enabling undo

### 2. React Context: usePageManagement

**Provides**:
- Page transformation state
- Page selection state (multi-select with Shift/Cmd)
- Operation functions (rotate, delete, reorder)
- Undo/redo capabilities
- Helper functions (getRotation, isDeleted, getVisiblePages)

**Integration**:
- Wraps application content within PDFProvider scope
- Initializes with document page count
- Synchronizes with PDF document lifecycle

### 3. UI Components

#### ThumbnailSidebar (Enhanced)
- **Multi-Selection**: Shift+click for range, Cmd/Ctrl+click for individual
- **Visual Feedback**: Selected pages have distinct border, current page highlighted
- **Drag-and-Drop Reordering**: Native HTML5 drag API
- **Rotation Display**: Thumbnails rotate with CSS transform
- **Bulk Actions**: Delete button appears when pages selected
- **Page Counter**: Shows visible page count (e.g., "Pages (47)" after deletions)

#### PageContextMenu (New)
- **Right-Click Context Menu**: Attached to each thumbnail
- **Operations**: Rotate Left, Rotate Right, Delete Page(s)
- **Smart Labels**: Shows "Delete Pages" when multiple selected
- **Shadcn ContextMenu**: Uses pre-built component for consistency

### 4. PDF Rendering Integration

**PDFCanvas Updates**:
- Accepts rotation from usePageManagement
- Passes rotation to pdf.js viewport
- Re-renders on rotation changes

**PDFService Updates**:
- `renderPage()` accepts optional rotation parameter (default 0)
- Cache keys include rotation to prevent incorrect cached renders
- pdf.js handles rotation transform internally

**PDFViewer Updates**:
- Filters deleted pages from rendering
- Respects page order from pageManagementService
- Maintains virtualization with transformed pages

## Alternatives Considered

### Alternative 1: Modify PDF.js Document Directly
**Pros**: Single source of truth  
**Cons**: pdf.js doesn't support document modification, would require recreation  
**Rejected**: Performance and complexity concerns

### Alternative 2: Store Transformations in Annotations
**Pros**: Could export with PDF  
**Cons**: Transformations are document-level, not annotations  
**Rejected**: Conceptual mismatch

### Alternative 3: Create New PDF for Each Operation
**Pros**: Simple, always exportable  
**Cons**: Very slow, high memory usage, no undo  
**Rejected**: Poor user experience

## Consequences

### Positive
- ✅ **Non-Destructive**: All operations reversible via undo
- ✅ **Performant**: Transformations are metadata only until export
- ✅ **Flexible**: Easy to add new transformation types
- ✅ **Consistent**: Same patterns as annotation system
- ✅ **Accessible**: Keyboard shortcuts, clear visual feedback

### Negative
- ⚠️ **Export Complexity**: Transformations must be applied during PDF generation (Phase 6)
- ⚠️ **State Synchronization**: Multiple state sources (PDF, annotations, transformations)
- ⚠️ **Memory**: History stack adds memory overhead

### Neutral
- ℹ️ **Learning Curve**: Users must understand "deleted" vs "hidden" pages
- ℹ️ **Testing Surface**: Complex state transitions require thorough testing

## Implementation Notes

### Page Numbering
- Original page numbers preserved in UI (page 5 stays "5" even after reordering)
- Visual order changes, not semantic numbering
- Alternative: Renumber pages after reorder (rejected for clarity)

### Annotation Preservation
- Annotations stored by original page number
- Follow page through reorder operations
- Remain visible on deleted pages (for undo)
- Must be transformed during export (Phase 6)

### Keyboard Shortcuts (Future)
- `Cmd/Ctrl+[` : Rotate left
- `Cmd/Ctrl+]` : Rotate right
- `Cmd/Ctrl+Backspace` : Delete selected pages
- `Cmd/Ctrl+Z` : Undo
- `Cmd/Ctrl+Shift+Z` : Redo

## Future Enhancements

1. **Batch Operations**: Apply rotation to multiple pages at once
2. **Page Duplication**: Copy existing pages
3. **Page Insertion**: Insert blank pages or pages from other PDFs
4. **Crop Tool**: Trim page margins
5. **Page Thumbnails**: Update thumbnails after rotation
6. **Persistent State**: Save transformations to localStorage for recovery
7. **Export Preview**: Show final document structure before export

## Related ADRs

- ADR 001: PDF Rendering Library (pdf.js)
- ADR 002: PDF Manipulation Library (pdf-lib)
- ADR 004: Annotation Storage (similar state management pattern)
- ADR 005: State Management (React Context pattern)

## References

- [pdf.js Viewport API](https://mozilla.github.io/pdf.js/api/draft/module-pdfjsLib-PageViewport.html)
- [HTML5 Drag and Drop API](https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API)
- [Command Pattern for Undo/Redo](https://refactoring.guru/design-patterns/command)
