# ADR 011: Redaction Implementation - Cover vs Remove

**Date**: 2025-01-27  
**Status**: Accepted  
**Context**: Phase 11 - Redaction Tool Implementation

---

## Context and Problem Statement

Users need the ability to redact sensitive information in PDFs. However, PDF redaction can be implemented in two fundamentally different ways:

1. **Cover Approach**: Draw black boxes over content (simple but not truly secure)
2. **Remove Approach**: Parse and modify PDF content streams to delete text (complex but secure)

We need to decide which approach to implement in our client-side PDF editor, considering:
- Security implications
- Implementation complexity
- pdf-lib library capabilities
- User expectations
- Time constraints

---

## Decision Drivers

### Technical Constraints
- **pdf-lib Limitations**: pdf-lib doesn't provide built-in methods to parse and modify content streams
- **PDF Structure Complexity**: Content streams are compressed, binary, and require deep PDF knowledge to modify safely
- **Browser Environment**: Client-side implementation limits available tools and libraries

### User Needs
- **Common Use Cases**: Most users need basic visual redaction for sharing documents
- **Security Requirements**: Some users need true content removal for classified/sensitive documents
- **Ease of Use**: Tool should be simple and intuitive

### Project Constraints
- **Development Time**: Limited time budget for Phase 11
- **Scope**: Need to deliver working redaction quickly
- **Quality**: Must maintain application stability

---

## Considered Options

### Option 1: Cover-Only Redaction (Selected)
**Description**: Draw solid black rectangles over selected text. Text remains in PDF structure.

**Pros**:
- ✅ Simple to implement (~2 hours)
- ✅ Works with existing pdf-lib API
- ✅ Zero risk of PDF corruption
- ✅ Reliable and predictable
- ✅ Sufficient for 80% of use cases
- ✅ Can be enhanced later

**Cons**:
- ❌ Doesn't remove underlying text
- ❌ Not suitable for classified documents
- ❌ Can be bypassed with forensic tools
- ❌ Requires clear user warning

**Implementation Complexity**: Low  
**Security Level**: Low  
**Reliability**: High

---

### Option 2: True Content Removal
**Description**: Parse PDF content streams and remove text at the source.

**Pros**:
- ✅ Truly secure redaction
- ✅ Text completely removed
- ✅ Suitable for classified documents
- ✅ Professional-grade solution

**Cons**:
- ❌ Extremely complex implementation (20-40 hours)
- ❌ pdf-lib doesn't support this natively
- ❌ High risk of PDF corruption
- ❌ Content streams are compressed/binary
- ❌ Would need to parse PDF operators
- ❌ Edge cases difficult to handle
- ❌ Testing would be extensive

**Implementation Complexity**: Very High  
**Security Level**: High  
**Reliability**: Medium (many edge cases)

---

### Option 3: Hybrid Approach
**Description**: Cover by default, with option to attempt true removal.

**Pros**:
- ✅ Best of both worlds
- ✅ Flexible for different security needs

**Cons**:
- ❌ Still requires implementing Option 2
- ❌ Complexity not worth the benefit
- ❌ Most users won't need true removal
- ❌ Confusing UX (two modes)

**Implementation Complexity**: Very High  
**Security Level**: Medium to High  
**Reliability**: Medium

---

### Option 4: Server-Side Redaction
**Description**: Send PDF to server for professional redaction processing.

**Pros**:
- ✅ Could use professional libraries
- ✅ True content removal possible

**Cons**:
- ❌ Violates client-side architecture principle
- ❌ Privacy concerns (uploading sensitive docs)
- ❌ Requires server infrastructure
- ❌ Not aligned with project goals
- ❌ Defeats "Preview for web" concept

**Implementation Complexity**: High  
**Security Level**: High  
**Reliability**: High (but architectural mismatch)

---

## Decision

**Selected Option**: **Option 1 - Cover-Only Redaction**

We will implement visual redaction by drawing solid black boxes over selected content, with clear warnings about the limitations.

---

## Rationale

### Primary Reasons

1. **Pragmatic Solution**: Covers 80% of user needs with 20% of implementation effort
2. **Time-Effective**: Can be completed in Phase 11 timeframe (~2 hours)
3. **Reliable**: Uses well-tested pdf-lib APIs, zero corruption risk
4. **Transparent**: Clear warnings prevent misuse for high-security scenarios
5. **Extensible**: Can be enhanced later if needed

### User Scenarios Covered

#### ✅ Suitable Use Cases (Majority)
- Removing names/addresses from documents shared informally
- Hiding salary information in job offers
- Obscuring personal details in examples
- Concealing proprietary information for screenshots
- Basic privacy protection for everyday documents

#### ❌ Unsuitable Use Cases (Minority)
- Government classified documents
- Legal discovery materials
- HIPAA-protected medical records requiring audit trails
- Financial documents with regulatory requirements
- Documents where forensic analysis is a concern

For unsuitable cases, we guide users to professional tools.

---

## Implementation Strategy

### Technical Approach
```typescript
// 1. Add redaction annotation type
type: 'redaction'
boxes: BoundingBox[]
removeText: boolean  // Future flag for true removal

// 2. Render as solid black SVG rectangles
fill: rgb(0, 0, 0)
opacity: 1

// 3. Export as black PDF rectangles
page.drawRectangle({
  color: rgb(0, 0, 0),
  opacity: 1
})
```

### User Communication
1. **Warning Dialog**: Shows on first use explaining:
   - What redaction does (covers content)
   - What it doesn't do (remove from structure)
   - When to use professional tools
   - Best practice for maximum security

2. **Export Confirmation**: Redactions highlighted with warning icon

3. **Documentation**: Clear explanation in help/docs

---

## Consequences

### Positive
- ✅ Fast implementation timeline
- ✅ Stable, reliable feature
- ✅ Meets most user needs
- ✅ Clear user communication
- ✅ Can enhance later if needed
- ✅ Maintains client-side architecture

### Negative
- ❌ Not suitable for high-security use cases
- ❌ Some users may expect true removal
- ❌ Requires prominent warnings
- ❌ Potential misuse if warnings ignored

### Mitigation Strategies

**For Negative Consequences**:
1. **Prominent Warning**: Show dialog on first use
2. **Clear Documentation**: Explain limitations throughout UI
3. **Alternative Guidance**: Direct high-security users to professional tools
4. **Future Enhancement**: Keep `removeText` flag for potential future implementation

---

## Alternative Recommendations

For users who need true content removal, we recommend:

### Professional Tools
- **Adobe Acrobat Pro**: Industry-standard redaction with content removal
- **Foxit PhantomPDF**: Professional redaction capabilities
- **Nitro Pro**: Business-grade PDF redaction

### Alternative Approaches
1. **Print to PDF**: Print redacted document to new PDF (flattens content)
2. **Image Conversion**: Convert to images, then back to PDF (removes all text)
3. **Specialized Tools**: Use dedicated redaction software for sensitive documents

---

## Future Considerations

### Potential Enhancement Path
If demand for true content removal is high:

1. **Phase 1**: Research PDF content stream parsing
2. **Phase 2**: Implement content stream parser
3. **Phase 3**: Add text removal capability
4. **Phase 4**: Extensive testing with diverse PDFs
5. **Phase 5**: Add as opt-in feature with warnings

**Estimated Effort**: 4-6 weeks full-time

**Prerequisites**:
- User research showing high demand
- Resources for extensive testing
- Risk acceptance for potential PDF corruption cases

---

## Related Decisions

- **ADR 001**: Client-side processing principle (redaction must be client-side)
- **ADR 006**: pdf-lib as PDF manipulation library (constrains redaction approach)

---

## References

### Research
- [PDF Reference 1.7](https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf) - PDF specification
- [pdf-lib Documentation](https://pdf-lib.js.org/) - Library capabilities
- [NIST Guidelines on PDF Redaction](https://www.nist.gov/) - Security requirements

### Similar Tools
- **Sejda**: Uses cover approach for basic redaction
- **PDFTron WebViewer**: Offers both modes (cover + remove)
- **Preview.app**: Uses cover approach in basic mode

---

## Decision Outcome

**Status**: Accepted  
**Date**: 2025-01-27  
**Participants**: Spark Agent  
**Next Review**: After user feedback from Phase 11 testing

---

## Lessons Learned

### What Went Well
- Clear decision framework helped choose pragmatic solution
- User communication strategy addresses limitations honestly
- Implementation stayed within time budget

### What to Improve
- Could conduct user research on security needs before implementation
- Could explore hybrid approaches in more detail

### Key Insight
**"Perfect is the enemy of good."** A simple, honest solution with clear warnings is better than a complex solution with hidden limitations or a delayed/missing feature.

---

**Author**: Spark Agent  
**Reviewers**: Pending  
**Last Updated**: 2025-01-27
