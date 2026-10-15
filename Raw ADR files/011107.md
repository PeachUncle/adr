# ADR-001: PDF Generation Approach

**Status**: Proposed
**Date**: 2025-10-29
**Decision Makers**: Development Team
**Consulted**: PRD Analysis, Technology Research

---

## Context

The Math Worksheet Generator needs to generate PDF worksheets dynamically. Each PDF must include:
- Header with title, grade level, date
- Math problems with proper spacing
- Visual aid placeholders or embedded SVG images
- Answer key (separate PDF)
- Page numbers and footer
- Professional formatting

**Requirements**:
- Generation time: <5 seconds per worksheet
- File size: <2MB per worksheet
- Browser compatibility (PDF must open in all major browsers)
- Server-side generation (no client-side rendering)
- Must work in Vercel serverless environment

---

## Decision Drivers

1. **Speed**: Fast generation time (<5 seconds)
2. **Simplicity**: Easy to implement and maintain
3. **Ecosystem Fit**: Works well with Next.js/Vercel
4. **Layout Control**: Sufficient control for worksheet formatting
5. **Cost**: No additional API costs
6. **Deployment**: Compatible with Vercel serverless

---

## Options Considered

### Option A: Python FastAPI + ReportLab

**Description**: Deploy a separate Python microservice using FastAPI and ReportLab for PDF generation.

**Architecture**:
```
Next.js API → Python FastAPI Service → ReportLab → PDF → Return to Next.js
```

**Pros**:
- ✅ ReportLab is mature and powerful (industry standard)
- ✅ Excellent layout control and typography
- ✅ Can handle complex PDF requirements
- ✅ Python has strong PDF ecosystem
- ✅ Can deploy as Vercel Python serverless function

**Cons**:
- ❌ Separate service to maintain (different language)
- ❌ Higher cold start latency (~2-3 seconds)
- ❌ More complex deployment
- ❌ Python dependencies in Node.js project
- ❌ Requires Python runtime in production
- ❌ Harder to debug (context switching between JS and Python)

**Estimated Generation Time**: 2-3 seconds (after cold start)
**Cold Start**: 2-3 seconds
**Complexity**: High

---

### Option B: Node.js + PDFKit ✅ RECOMMENDED

**Description**: Use PDFKit library directly in Next.js API routes for PDF generation.

**Architecture**:
```
Next.js API → PDFKit → PDF → Return
```

**Pros**:
- ✅ Pure JavaScript (same ecosystem as Next.js)
- ✅ Simpler deployment (no separate service)
- ✅ Faster cold starts (~500ms)
- ✅ Easier to maintain (one language)
- ✅ Good layout control for our needs
- ✅ Works perfectly in Vercel serverless
- ✅ Smaller bundle size
- ✅ Direct access to Node.js streams
- ✅ Easy to debug

**Cons**:
- ⚠️ PDFKit less powerful than ReportLab
- ⚠️ More manual layout calculations
- ⚠️ Limited advanced features (tables, complex layouts)

**Estimated Generation Time**: 1-2 seconds
**Cold Start**: 500ms
**Complexity**: Medium

---

### Option C: Puppeteer/Playwright (HTML to PDF)

**Description**: Generate worksheets as HTML and convert to PDF using headless browser.

**Architecture**:
```
Next.js API → HTML Template → Puppeteer → PDF → Return
```

**Pros**:
- ✅ Familiar HTML/CSS for layout
- ✅ Easy to style and preview
- ✅ Can use existing React components

**Cons**:
- ❌ Very slow (~10-20 seconds per PDF)
- ❌ High memory usage
- ❌ Large deployment size (Chromium binary)
- ❌ Expensive in serverless (time = cost)
- ❌ Cold start >5 seconds
- ❌ Not suitable for Vercel hobby/pro plans

**Estimated Generation Time**: 10-20 seconds
**Cold Start**: 5-10 seconds
**Complexity**: Medium
**Status**: ❌ Rejected (too slow, too expensive)

---

### Option D: Third-Party API (DocRaptor, PDFShift, etc.)

**Description**: Use external PDF generation API service.

**Pros**:
- ✅ No maintenance
- ✅ Professional quality

**Cons**:
- ❌ Additional API costs ($0.01-0.10 per PDF)
- ❌ External dependency (reliability risk)
- ❌ Data sent to third party (privacy concern)
- ❌ Rate limits
- ❌ Network latency

**Cost**: $10-100/month (1000 worksheets)
**Status**: ❌ Rejected (adds significant cost)

---

## Decision: Option B (Node.js + PDFKit)

**Rationale**:

1. **Best for MVP Speed**
   - Simplest to implement
   - Fastest iteration cycle
   - Adequate for worksheet layouts

2. **Cost Effective**
   - No additional API costs
   - Lower serverless compute time
   - Smaller bundle size

3. **Ecosystem Fit**
   - Pure JavaScript/TypeScript
   - Works natively with Next.js
   - Easy for team to maintain

4. **Performance**
   - Fast generation (1-2 seconds)
   - Low cold start latency
   - Efficient memory usage

5. **Future Flexibility**
   - Can switch to ReportLab later if needed
   - Good enough for 80% of use cases
   - Easy to extend

---

## Implementation Plan

### Phase 1: Proof of Concept (Phase 0)

```javascript
// lib/pdf/generator.ts
import PDFDocument from 'pdfkit';

export async function generateWorksheetPDF(data) {
  const doc = new PDFDocument({
    size: 'LETTER',
    margins: { top: 50, bottom: 50, left: 50, right: 50 }
  });

  // Add header
  doc.fontSize(20).text('Math Worksheet', { align: 'center' });
  doc.fontSize(12).text(`Grade ${data.gradeLevel} - ${data.topic}`);

  // Add problems
  data.problems.forEach((problem, index) => {
    doc.fontSize(14).text(`${index + 1}. ${problem.question}`);
    doc.moveDown(0.5);
  });

  // Finalize PDF
  doc.end();

  return doc; // Stream
}
```

### Phase 2: Full Implementation (Days 3-4)

Tasks:
1. Install PDFKit: `npm install pdfkit @types/pdfkit`
2. Create `lib/pdf/generator.ts`
3. Implement worksheet layout:
   - Header with title, grade, date
   - Problem list with proper spacing
   - Visual aid placeholders
   - Page numbers
4. Implement answer key layout
5. Add theme styling (colors, fonts)
6. Test with all problem types
7. Optimize for file size

### Testing Checklist
- [ ] PDF opens in Chrome
- [ ] PDF opens in Firefox
- [ ] PDF opens in Safari
- [ ] PDF opens in Edge
- [ ] PDF prints correctly
- [ ] File size <2MB
- [ ] Generation time <5 seconds
- [ ] All text renders correctly
- [ ] SVG assets embed properly (if applicable)

---

## Consequences

### Positive

1. **Faster Development**
   - Can prototype quickly
   - Single codebase (TypeScript)
   - Easier onboarding for new developers

2. **Lower Costs**
   - No external API fees
   - Shorter serverless execution time
   - Smaller deployment size

3. **Better Control**
   - Direct control over PDF generation
   - No external dependencies
   - Can optimize for our specific use case

### Negative

1. **Limited Features**
   - May struggle with complex layouts
   - Manual positioning calculations
   - Less sophisticated typography

2. **Learning Curve**
   - Team needs to learn PDFKit API
   - PDF coordinate system can be tricky
   - Debugging layout issues

### Mitigation Strategies

1. **For Complex Layouts**
   - Keep worksheets simple (MVP approach)
   - Use templates for consistent layout
   - Test early and often

2. **For Future Scalability**
   - Design modular PDF generation
   - Abstract layout logic
   - Easy to swap implementations later

---

## Alternatives Revisited

**When to reconsider ReportLab (Option A)**:
- User requests complex layouts (tables, multi-column)
- Need advanced typography features
- Performance becomes critical (>10k worksheets/day)
- Team becomes comfortable with Python microservices

**Migration Path** (if needed):
1. Keep same API contract
2. Implement Python service
3. Deploy alongside Node.js version
4. A/B test performance
5. Gradually migrate

---

## References

- [PDFKit Documentation](http://pdfkit.org/)
- [ReportLab Documentation](https://www.reportlab.com/docs/)
- [Vercel Serverless Functions](https://vercel.com/docs/functions)
- PRD: Section 6.5 (Technology Stack)

---

## Revision History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-10-29 | 1.0 | Initial decision | Development Team |

---

**Next Steps**:
1. ✅ Decision made: PDFKit
2. ⏳ Create proof-of-concept (Phase 0)
3. ⏳ Test in Vercel environment
4. ⏳ Implement full generator (Days 3-4)
