# ADR-0002: Using pdf-lib for PDF Manipulation

## Status
Accepted

## Date
2025-01-XX

## Context

The PDF Viewer & Editor needs to modify PDF documents:
- Add annotations (highlights, drawings, text, shapes)
- Embed signatures
- Reorder, delete, rotate pages
- Export modified PDFs
- Maintain PDF structural integrity

PDF.js (ADR-0001) handles rendering but is read-only. We need a complementary library for PDF modification that:
- Runs entirely in the browser
- Creates and modifies PDF documents
- Preserves original PDF quality and metadata
- Works with PDF.js output
- Has minimal dependencies
- Is actively maintained

## Decision

We will use **pdf-lib** (v1.17.1) for creating and modifying PDF documents.

pdf-lib is a pure JavaScript library for creating and modifying PDFs in Node and the browser without native dependencies.

## Consequences

### Positive
- **Zero dependencies**: Pure JavaScript, no native bindings
- **Browser-compatible**: Works in all modern browsers
- **Comprehensive API**: Can create, modify, merge, split PDFs
- **Standards compliant**: Generates valid PDF documents
- **Type-safe**: Written in TypeScript with excellent type definitions
- **Actively maintained**: Regular updates and bug fixes
- **MIT License**: Permissive open source
- **Small bundle**: ~300KB minified (~100KB gzipped)
- **Good documentation**: Clear examples and API docs

### Negative
- **Performance**: Slower than native PDF libraries for very large documents
- **Memory usage**: Loads entire PDF into memory for editing
- **Limited advanced features**: No OCR, no advanced compression algorithms
- **Form handling**: Limited support for complex interactive forms
- **Learning curve**: Different API paradigm from PDF.js

### Neutral
- Separate library means we maintain two PDF-related dependencies
- Must convert between PDF.js and pdf-lib formats when editing
- Need to manage memory carefully for large document editing

## Alternatives Considered

### Alternative 1: jsPDF
- **Description**: JavaScript library for generating PDFs
- **Pros**: 
  - Popular and well-established
  - Good for generating new PDFs
  - Large community
  - Many plugins available
- **Cons**: 
  - Primarily for creation, not modification
  - Limited ability to edit existing PDFs
  - Cannot preserve original PDF structure
  - Larger bundle size
- **Why rejected**: We need to modify existing PDFs, not just create new ones. jsPDF is better suited for PDF generation from scratch.

### Alternative 2: PDFKit
- **Description**: PDF generation library for Node.js
- **Pros**: 
  - Feature-rich for PDF creation
  - Excellent documentation
  - Streaming API
- **Cons**: 
  - Designed for Node.js (uses streams, buffers)
  - Browser support requires significant polyfills
  - Cannot easily modify existing PDFs
  - Larger bundle with polyfills (~500KB+)
- **Why rejected**: Not designed for browser use. Polyfilling Node.js dependencies would bloat the bundle significantly.

### Alternative 3: PDF.js + Manual PDF Structure Manipulation
- **Description**: Parse and modify PDF structure manually using PDF.js internals
- **Pros**: 
  - Single dependency
  - Full control over PDF structure
  - Potentially smaller bundle
- **Cons**: 
  - PDF.js internals not designed for modification
  - Very complex (PDF specification is 1000+ pages)
  - High maintenance burden
  - Easy to create invalid PDFs
  - Time-consuming to implement
- **Why rejected**: Reinventing the wheel. pdf-lib provides this functionality with better reliability and less development time.

### Alternative 4: PDFTron (WebViewer)
- **Description**: Commercial PDF SDK with web support
- **Pros**: 
  - Feature-complete
  - Excellent performance
  - Professional support
  - Advanced editing capabilities
- **Cons**: 
  - Commercial license required
  - Expensive (~$5000+/year)
  - Not open source
  - Vendor lock-in
- **Why rejected**: Cost prohibitive. Conflicts with "100% free, open source" project goals.

### Alternative 5: Server-side PDF manipulation (Python/Java libraries)
- **Description**: Use server-side libraries via API
- **Pros**: 
  - Mature libraries (PyPDF2, Apache PDFBox)
  - Better performance for large documents
  - More features
- **Cons**: 
  - Requires server infrastructure
  - Privacy concerns (documents leave client)
  - Latency for network requests
  - Violates "client-side only" requirement
- **Why rejected**: Fundamentally conflicts with core product requirement of 100% client-side processing.

## Implementation Notes

### Setup Requirements
1. Install pdf-lib: `npm install pdf-lib`
2. Import in services:
   ```typescript
   import { PDFDocument, rgb, degrees } from 'pdf-lib'
   ```

### Common Use Cases

#### Loading Existing PDF
```typescript
const existingPdfBytes = await file.arrayBuffer()
const pdfDoc = await PDFDocument.load(existingPdfBytes)
```

#### Adding Annotations
```typescript
const pages = pdfDoc.getPages()
const firstPage = pages[0]

// Draw rectangle (highlight)
firstPage.drawRectangle({
  x: 50,
  y: 200,
  width: 200,
  height: 50,
  color: rgb(1, 1, 0),
  opacity: 0.3,
})

// Add text
firstPage.drawText('Annotation text', {
  x: 50,
  y: 200,
  size: 12,
  color: rgb(0, 0, 0),
})
```

#### Embedding Images (Signatures)
```typescript
const pngImage = await pdfDoc.embedPng(signatureImageBytes)
firstPage.drawImage(pngImage, {
  x: 100,
  y: 100,
  width: 150,
  height: 50,
})
```

#### Page Manipulation
```typescript
// Remove page
pdfDoc.removePage(2)

// Rotate page
const page = pdfDoc.getPage(0)
page.setRotation(degrees(90))

// Copy pages between documents
const [copiedPage] = await targetPdf.copyPages(sourcePdf, [0])
targetPdf.addPage(copiedPage)
```

#### Exporting
```typescript
const pdfBytes = await pdfDoc.save()
const blob = new Blob([pdfBytes], { type: 'application/pdf' })
// Trigger download or display
```

### Integration with PDF.js
1. **Rendering**: Use PDF.js to render pages to canvas for display
2. **Editing**: When user adds annotation, track in application state
3. **Exporting**: 
   - Load original PDF with pdf-lib
   - Apply all annotations from state
   - Save modified PDF
   - Optionally reload with PDF.js to display changes

### Performance Considerations
- Load PDF with pdf-lib only when exporting (not during viewing)
- Cache pdf-lib document if user makes multiple edits
- Show progress indicator for large document exports
- Consider Web Worker for pdf-lib operations on large files
- Release memory after export completes

### Memory Management
```typescript
// Be conscious of memory with large PDFs
const exportPDF = async (annotations) => {
  const pdfDoc = await PDFDocument.load(originalBytes)
  // ... apply annotations ...
  const bytes = await pdfDoc.save()
  
  // Clear reference to allow garbage collection
  pdfDoc = null
  
  return bytes
}
```

## References
- [pdf-lib Official Site](https://pdf-lib.js.org/)
- [pdf-lib GitHub Repository](https://github.com/Hopding/pdf-lib)
- [pdf-lib API Documentation](https://pdf-lib.js.org/docs/api/)
- [pdf-lib Examples](https://github.com/Hopding/pdf-lib#examples)
- Related ADR: [0001-pdf-rendering-library.md](0001-pdf-rendering-library.md)
- PRD Section: "Technology Stack" (PDF Manipulation)
- ARCHITECTURE.md: "ExportService"
