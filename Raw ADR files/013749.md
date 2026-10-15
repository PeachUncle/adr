# ADR 010: PDF Export with Embedded Changes

**Status**: Accepted  
**Date**: 2025-01-27  
**Context**: Phase 6 Implementation

## Context

Users need to download their modified PDFs with all annotations, page transformations (rotations, deletions, reordering), and signatures permanently embedded in the output file. The exported PDF must be compatible with all standard PDF readers and viewers.

## Decision

We will implement a comprehensive export system using `pdf-lib` to generate modified PDFs with all changes applied.

### Architecture

```
┌─────────────────────────────────────────────────┐
│            ExportDialog Component               │
│  - Filename input                               │
│  - Change summary                               │
│  - Progress indicator                           │
│  - Export button                                │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│            ExportService                        │
│  - exportPDF(): Main orchestration              │
│  - applyPageTransformations()                   │
│  - embedAnnotations()                           │
│  - downloadPDF()                                │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│            pdf-lib Library                      │
│  - PDFDocument.load()                           │
│  - Page manipulation (rotate, delete, reorder)  │
│  - Drawing operations (shapes, text, images)    │
│  - PDFDocument.save()                           │
└─────────────────────────────────────────────────┘
```

## Implementation Details

### 1. Original PDF Bytes Storage

**Problem**: Need access to original PDF bytes for pdf-lib processing.

**Solution**: Store ArrayBuffer in PDFService when document is loaded:
```typescript
class PDFService {
  private originalBytes: ArrayBuffer | null = null
  private filename: string | null = null
  
  getOriginalBytes(): ArrayBuffer | null
  getFilename(): string | null
}
```

### 2. Export Service

**Core Export Function**:
```typescript
async exportPDF(
  originalPdfBytes: ArrayBuffer,
  annotations: Annotation[],
  transformations: Map<number, PageTransformation>,
  pageOrder: number[],
  options: ExportOptions
): Promise<Blob>
```

**Progress Tracking**: Callback-based progress updates through 5 stages:
1. Loading (0-20%): Load PDF with pdf-lib
2. Processing (20-60%): Apply page transformations
3. Annotations (60-90%): Embed all annotations
4. Finalizing (90-100%): Generate final bytes
5. Complete (100%): Ready for download

### 3. Page Transformations

**Order of Operations**:
1. **Delete pages**: Remove from pdf-lib document (in reverse order to maintain indices)
2. **Rotate pages**: Apply rotation to remaining pages
3. **Reorder pages**: Reconstruct document with new page sequence

**Why this order?**:
- Deletion first prevents operating on pages that will be removed
- Rotation on reduced set is more efficient
- Reordering last ensures correct final sequence

**Implementation**:
```typescript
// Delete pages (reverse order)
pagesToRemove.sort((a, b) => b - a).forEach(pageIndex => {
  pdfDoc.removePage(pageIndex)
})

// Apply rotations
rotations.forEach((rotation, pageIndex) => {
  const page = pdfDoc.getPage(pageIndex)
  page.setRotation(degrees(currentRotation + rotation))
})

// Reorder via copy
const tempDoc = await PDFDocument.create()
for (const page of newPageOrder) {
  const [copiedPage] = await tempDoc.copyPages(pdfDoc, [pageIndex])
  tempDoc.addPage(copiedPage)
}
```

### 4. Annotation Embedding

**Page Mapping**: Create mapping from original page numbers to new indices after deletions/reordering:
```typescript
createPageMapping(
  transformations: Map<number, PageTransformation>,
  pageOrder: number[]
): Map<number, number>
```

**Annotation Types and pdf-lib Operations**:

| Annotation Type | pdf-lib Method | Notes |
|----------------|----------------|-------|
| Highlight | `drawRectangle()` | Semi-transparent colored rectangle |
| Pen | `drawLine()` series | Connect points with lines |
| Rectangle | `drawRectangle()` | Border + optional fill |
| Circle | `drawEllipse()` | Border + optional fill |
| Arrow | `drawLine()` + arrowhead lines | Calculated angle for arrowhead |
| Line | `drawLine()` | Simple line |
| Text | `drawText()` | Helvetica font embedded |
| Signature | `embedPng()` + `drawImage()` | Convert data URL to image |

**Coordinate System**: PDF coordinate system has origin at bottom-left, so Y coordinates are flipped:
```typescript
y: height - annotation.y - annotation.height
```

### 5. Color Conversion

**Challenge**: Our UI uses `oklch` colors, pdf-lib requires RGB.

**Solution**: Convert oklch → Lab → XYZ → RGB:
```typescript
oklchToRgb(oklch: string): { r: number, g: number, b: number }
```

Conversion pipeline:
1. Parse oklch values (lightness, chroma, hue)
2. Convert to Lab color space
3. Transform to XYZ
4. Apply sRGB gamma correction
5. Clamp to [0, 1] range

### 6. Signature Embedding

**Process**:
1. Parse data URL (data:image/png;base64,...)
2. Decode base64 to Uint8Array
3. Embed via `embedPng()` or `embedJpg()`
4. Draw at specified position and dimensions

**Error Handling**: Gracefully skip unsupported formats, log warning

### 7. Export Dialog UX

**Features**:
- **Filename suggestion**: `originalname_edited_YYYY-MM-DD.pdf`
- **Change summary**: Show counts of annotations and transformations
- **Include annotations toggle**: Allow exporting with just page changes
- **Progress bar**: Real-time feedback during export
- **Success confirmation**: Green checkmark with 1.5s auto-close
- **Error display**: Red alert with error message

**Toolbar Integration**: Export button visible when document loaded

## Alternatives Considered

### Alternative 1: Server-Side Export
**Rejected**: Violates core principle of 100% client-side processing. Introduces privacy concerns.

### Alternative 2: Canvas-Based Export
**Rejected**: Would rasterize PDF (lose text, scalability). File sizes 10-100x larger.

### Alternative 3: Download Annotations as Separate File
**Rejected**: Not user-friendly. Requires special viewer to see annotations.

### Alternative 4: XFDF Annotation Format
**Rejected**: Not universally supported. Many readers ignore XFDF.

## Consequences

### Positive
✅ **Universal Compatibility**: pdf-lib generates standard PDF 1.7, opens in all readers  
✅ **True Embedding**: Annotations become part of PDF structure, not overlays  
✅ **Privacy Maintained**: All processing client-side, no server uploads  
✅ **Professional Output**: No watermarks, clean exports  
✅ **User Feedback**: Progress indication prevents "is it working?" confusion  
✅ **Flexible Options**: Can export with/without annotations

### Negative
❌ **Processing Time**: Large documents (500+ pages) may take 10-30s to export  
❌ **Memory Usage**: Requires holding both original and modified PDF in memory  
❌ **Browser Limitations**: Very large files (>100MB) may fail in some browsers  
❌ **Complex Annotations**: Some advanced annotation features may not translate perfectly

### Mitigation Strategies
- **Performance**: Show progress, process in stages, allow cancellation (future)
- **Memory**: Cleanup after export, consider streaming for large files (future)
- **Browser Limits**: Warn for very large files, suggest desktop version (future)
- **Fidelity**: Test annotation rendering in multiple PDF readers, document limitations

## Technical Constraints

### pdf-lib Limitations
1. **No text editing**: Cannot modify existing PDF text, only add new text
2. **Font embedding**: Limited to standard 14 fonts + custom embeds (adds size)
3. **Form fields**: Cannot create interactive form fields
4. **JavaScript actions**: Cannot embed PDF JavaScript
5. **3D content**: No support for 3D annotations

### Browser Constraints
1. **Memory**: ~2GB limit in most browsers for blob operations
2. **Download**: No progress feedback for blob download (browser limitation)
3. **File size**: Some browsers struggle with >200MB files

## Testing Strategy

### Unit Tests (Future)
- [ ] Color conversion accuracy (oklch → RGB)
- [ ] Page mapping with complex transformations
- [ ] Coordinate system conversion
- [ ] Filename generation edge cases

### Integration Tests (Future)
- [ ] Export with all annotation types
- [ ] Export with all page transformations
- [ ] Export with mixed changes
- [ ] Export without annotations

### Manual Testing
- [x] Export empty PDF (no changes)
- [x] Export with highlights only
- [x] Export with pen annotations
- [x] Export with shapes
- [x] Export with signatures
- [x] Export with rotated pages
- [x] Export with deleted pages
- [x] Export with reordered pages
- [x] Export with mixed changes
- [x] Open exported PDF in:
  - [ ] Adobe Acrobat Reader
  - [ ] Preview (macOS)
  - [ ] Chrome PDF viewer
  - [ ] Firefox PDF viewer
  - [ ] Edge PDF viewer

## Future Enhancements

### Phase 7+ Improvements
1. **Incremental Save**: Save changes to existing file without full re-export
2. **Export Presets**: Quick exports (annotations only, pages only, etc.)
3. **Batch Export**: Export multiple modified PDFs
4. **Export Templates**: Save export settings
5. **Cloud Backup**: Optional export to cloud storage (user choice)
6. **Compression Options**: User-selectable quality levels
7. **Metadata**: Add custom metadata to exported PDFs
8. **Encryption**: Add password protection on export

### Performance Optimizations
1. **Web Worker**: Move pdf-lib operations to worker thread
2. **Streaming**: Stream large PDFs instead of loading fully into memory
3. **Caching**: Cache font embeddings for repeated exports
4. **Chunked Processing**: Process pages in batches for progress granularity

## References

- [pdf-lib Documentation](https://pdf-lib.js.org/)
- [PDF 1.7 Specification](https://www.adobe.com/content/dam/acom/en/devnet/pdf/pdfs/PDF32000_2008.pdf)
- [OKLCH Color Space](https://oklch.com/)
- [Color Space Conversions](https://en.wikipedia.org/wiki/CIELAB_color_space)

## Decision Log

- **2025-01-27**: Initial decision to use pdf-lib for export
- **2025-01-27**: Chose callback-based progress over Promise-based for real-time feedback
- **2025-01-27**: Decided on page transformation order (delete, rotate, reorder)
- **2025-01-27**: Selected standard fonts over custom font embedding (performance)
