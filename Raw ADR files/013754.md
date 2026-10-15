# ADR-012: PDF Editing Capabilities and Limitations

## Status
Accepted

## Context

Users have reported that the PDF viewer/editor lacks the ability to "add/remove/update any text or object in the PDF." This ADR documents the research findings on what PDF editing truly entails, what is technically feasible in a client-side web application, and the implementation strategy for high-value features.

### User Expectations vs. Technical Reality

Users often expect PDFs to be editable like Word documents. However, PDFs are fundamentally different:

**PDF Structure**:
- Collection of positioned drawing commands (like PostScript)
- Characters stored with absolute x,y coordinates
- No semantic structure (paragraphs, sentences)
- No automatic text reflow
- Fonts must be embedded or substituted

**Example**: The word "Hello" in a PDF:
```
/F1 12 Tf           % Set font
72 720 Td           % Move to position
(Hello) Tj          % Show text
```

Not `<p>Hello</p>` like HTML.

### Research Findings

After analyzing top PDF editors (Adobe Acrobat, Preview, Sejda, PDFescape, PDF Candy), we found:

1. **No web-based client-side editor can truly edit existing PDF text**
2. All use workarounds: redact original + overlay new text
3. Desktop apps with proprietary tech (Adobe) can do it, but it's extremely complex
4. Even macOS Preview (the gold standard) cannot edit existing text

**Common "Editing" Approach**:
```
1. Cover original text with white rectangle
2. Overlay new text as annotation
3. User perceives it as "editing"
4. But original text still in PDF structure
```

### Current Implementation Status

We already have excellent **Tier 1 & 2** editing capabilities:

**✅ Tier 1: Non-Destructive Additions**
- Highlights, drawings, annotations
- Text boxes (new text)
- Signatures
- Sticky notes

**✅ Tier 2: Page-Level Operations**
- Reorder pages
- Rotate pages
- Delete pages
- Export with changes

**❌ Tier 3: Content Editing** (Not implemented)
- Edit existing text
- Edit/replace images
- Fill forms
- Redact (permanent removal)
- Add blank pages
- Headers/footers/page numbers

## Decision

We will **NOT** attempt to implement full content editing (modifying existing text/images in PDF content streams). Instead, we will implement **high-value, technically feasible features** that users actually need:

### Phase 10: Form Filling ⭐⭐⭐ (HIGH PRIORITY)

**Why**: 
- Common use case (government forms, applications)
- Technically feasible with pdf-lib
- Competitive feature parity
- High user value

**Implementation**:
- Detect interactive form fields via pdf-lib
- Render HTML input overlays at field positions
- Capture user input
- Apply values to PDF on export
- Optional form flattening

**Technical Approach**:
```typescript
// Detection
const form = pdfDoc.getForm()
const fields = form.getFields()

// Extraction
const textField = form.getTextField('name')
const bounds = field.acroField.getWidgets()[0].getRectangle()

// Application
textField.setText('John Doe')
form.flatten()  // Optional: make read-only
```

### Phase 11: Document Enhancements ⭐⭐ (MEDIUM PRIORITY)

**11.1: Insert Blank Pages**
- Easy to implement (3 hours)
- pdf-lib: `pdfDoc.insertPage(index, [width, height])`
- Useful for adding separator pages

**11.2: Redaction Tool**
- Black rectangles that cover text
- **WARNING**: Text not removed from structure, only covered
- Better than nothing for basic privacy needs

**11.3: Watermarks** (Optional)
- Add text watermarks to pages
- Professional branding feature
- Simple implementation

**11.4: Page Numbers** (Optional)
- Add page numbering
- Customizable position and format
- Nice polish

### Features We Will NOT Implement

**❌ Edit Existing Text** - Reasons:
1. **Extreme Complexity**: Requires parsing content streams, understanding PDF operators
2. **Font Problems**: Must have exact font or substitution looks terrible
3. **No Reflow**: Editing one word requires manually repositioning everything
4. **Risk**: High chance of corrupting PDF
5. **Time**: Would take months to implement poorly
6. **Alternatives**: Text box overlay tool (already have!)

**❌ OCR** - Reasons:
- Requires ML models (100+ MB)
- Better as external service
- Out of scope for client-side app

**❌ PDF to Word** - Reasons:
- Extremely complex format conversion
- Better as external service
- Many free online tools already exist

**❌ Password Protection** - Reasons:
- Security implications
- Encryption complexity
- pdf-lib support is limited

## Alternative Solutions Considered

### Alternative 1: Full Content Stream Parsing

**Approach**: Parse and modify PDF content streams to edit text.

**Pros**:
- "True" text editing
- Professional feature

**Cons**:
- Months of development
- Requires deep PDF specification knowledge
- High risk of PDF corruption
- Font subsetting issues
- No automatic reflow
- pdf-lib has limited support
- Poor UX (fonts won't match, manual positioning)

**Decision**: ❌ Rejected - Cost/benefit ratio too high

### Alternative 2: Redact + Overlay (The Industry Standard)

**Approach**: Cover original text with white box, overlay new text.

**Pros**:
- Simple to implement
- Works reliably
- Used by many commercial tools
- Low risk

**Cons**:
- Not "true" editing
- Original text still in PDF
- Font matching approximate
- Users may be confused

**Decision**: ✅ Accepted for text box tool (already implemented)

### Alternative 3: Server-Side Processing

**Approach**: Send PDF to server with editing operations, process with professional library.

**Pros**:
- Could handle complex operations
- Use mature libraries (PyPDF2, PDFBox, etc.)

**Cons**:
- Violates privacy promise (100% client-side)
- Requires server infrastructure
- Network latency
- Cost of operation

**Decision**: ❌ Rejected - Violates core product principle

## Consequences

### Positive

1. **Realistic Scope**: Focus on achievable, high-value features
2. **Form Filling**: Major gap filled, common use case
3. **Clear Messaging**: Users understand what's possible
4. **Maintain Quality**: Don't ship half-baked text editing
5. **Privacy Preserved**: All processing remains client-side
6. **Quick Wins**: Blank pages, redaction are easy additions

### Negative

1. **Cannot Edit Text**: Some users will still want this
2. **Education Needed**: Must explain PDF limitations clearly
3. **Competitive Gap**: Desktop apps (Adobe) can do more

### Mitigation

**User Education**:
```tsx
// Clear feature communication
<Alert>
  <Info className="h-4 w-4" />
  <AlertDescription>
    <strong>Why can't I edit existing text?</strong> PDFs are like 
    printed pages - text is precisely positioned, not editable like 
    Word. Use text boxes to overlay corrections, or edit the source 
    document before converting to PDF.
  </AlertDescription>
</Alert>
```

**Feature Guide**:
- ✅ You CAN: Add annotations, fill forms, manage pages
- ❌ You CANNOT: Edit existing text, OCR, convert to Word
- 💡 TIP: Use text boxes for corrections

## Implementation Plan

### Phase 10: Form Filling (2-3 days)
1. Create `FormService` for field detection and management
2. Create `useForm` hook and `FormProvider`
3. Create `FormFieldOverlay` component
4. Integrate with PDFCanvas (add form layer)
5. Update ExportService to apply form values
6. Add "Form Mode" toggle to toolbar
7. Test with various PDF forms
8. Document feature

### Phase 11: Document Enhancements (2-3 days)
1. Insert blank pages (3 hours)
2. Redaction tool (6 hours)
3. Watermarks (3 hours) - optional
4. Page numbers (6 hours) - optional

### Total: 4-6 days of work

## Side Effect Mitigation

### Layer Separation
```
Z-Index Stack:
- 30: Annotation Drawing (active)
- 25: Form Fields (NEW)
- 20: Text Layer (highlight mode)
- 15: Annotations
- 10: Text Layer (select mode)
- 5: Search Highlights
- 0: Canvas
```

### State Isolation
Each feature has dedicated context:
- `usePDF()` - View state
- `useAnnotations()` - Annotation state
- `usePageManagement()` - Page transformations
- `useForm()` - Form state (NEW)
- `useEnhancements()` - Watermarks, etc. (NEW)

### Export Order
Deterministic order prevents conflicts:
1. Page transformations
2. Blank page insertion
3. Document enhancements
4. Form field values
5. Annotations (last)

### Coordinate Consistency
Single source of truth for coordinate conversion:
```typescript
export const CoordinateUtils = {
  pdfToScreen(coords, viewport): Point
  screenToPDF(coords, viewport): Point
}
```

### Performance Monitoring
Track memory and render times to detect regressions.

### Feature Flags
Enable features progressively:
```typescript
const FEATURES = {
  FORMS: true,
  REDACTION: true,
  BLANK_PAGES: true,
  WATERMARKS: false,  // Not ready
}
```

## Testing Strategy

### Unit Tests
- Form field detection
- Coordinate conversion
- Field value application
- Blank page insertion

### Integration Tests
- Complete form filling workflow
- Export with multiple feature types
- Layer interaction

### Manual Tests
- Various PDF forms
- Different zoom levels
- Cross-browser testing
- Performance with large PDFs

## Success Metrics

**Feature Completeness**:
- [ ] Forms can be filled and exported
- [ ] Blank pages can be inserted
- [ ] Redaction tool works
- [ ] All features export correctly

**Performance**:
- No regression in load time
- Memory usage < 500MB for large PDFs
- Smooth scrolling maintained

**User Satisfaction**:
- Clear understanding of capabilities
- Reduced support requests about "editing text"
- Positive feedback on form filling

## Related Decisions

- ADR-002: pdf-lib for PDF Manipulation
- ADR-009: Text Layer Implementation
- ADR-010: PDF Export Architecture

## References

- [PDF Specification 1.7](https://www.adobe.com/content/dam/acom/en/devnet/pdf/pdfs/PDF32000_2008.pdf)
- [pdf-lib Documentation](https://pdf-lib.js.org/)
- [PDF Structure Research](../PDF_EDITING_RESEARCH.md)
- [Implementation Plan](../PDF_EDITING_IMPLEMENTATION_PLAN.md)

## Date
Current Session

## Authors
Spark Agent (AI Assistant)

## Review Status
Approved

## Notes

This decision is based on:
1. **Extensive research** into PDF structure and editing techniques
2. **Competitive analysis** of Adobe Acrobat, Preview, Sejda, etc.
3. **Technical feasibility** assessment with pdf-lib and PDF.js
4. **User needs** analysis from issue reports
5. **Time/value** trade-off considerations

The key insight: **Even macOS Preview (our UX model) cannot edit existing PDF text.** This is not a missing feature - it's a fundamental PDF limitation that no client-side web app has solved without compromising quality or privacy.

Focus on features that:
- ✅ Are technically feasible
- ✅ Provide real user value
- ✅ Maintain quality standards
- ✅ Preserve privacy (client-side)
- ✅ Can be implemented in reasonable time

This approach positions the app as a competitive, honest PDF editor that does what it can do well, rather than attempting impossible features poorly.
