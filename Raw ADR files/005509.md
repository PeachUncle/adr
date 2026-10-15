# ADR-001: Backend PDF Generation with QuestPDF

## Status
Accepted

## Context
The frontend section of the repository previously used `react-pdf` (via the `DocumentViewer` component) to create and download resumes. While this approach worked, there were several limitations:

1. **Performance**: Client-side PDF generation can be resource-intensive and slow, especially on lower-end devices
2. **Font Consistency**: Ensuring Times New Roman font was consistently rendered across different browsers and devices was challenging
3. **Maintainability**: Having PDF generation logic in the frontend made it harder to maintain and extend
4. **Scalability**: Client-side generation doesn't scale well for batch operations or server-side processing needs

## Decision
We decided to migrate PDF generation to the backend using .NET with the QuestPDF library.

### Implementation Details

1. **QuestPDF Library**: We chose QuestPDF for its:
   - Fluent API that makes PDF creation intuitive
   - Strong .NET integration
   - Community license for open source projects
   - Excellent typography support including Times New Roman

2. **Architecture**:
   - Created a `PdfGeneration` feature folder under `Features/`
   - Implemented `IComponent` pattern for each resume section (matching frontend structure)
   - Created a service interface `IPdfGenerationService` for dependency injection
   - Added API endpoint at `/api/v1/resume/{resumeId}/pdf`

3. **Template Structure** (matching frontend layout):
   - Personal Info section (name, role, contact details)
   - Summary section
   - Work Experience section (with bullet points)
   - Education section (with bullet points)
   - Projects section (with clickable links and bullet points)
   - Skills section (category-based)

4. **Typography**:
   - Times New Roman font family for all text
   - A4 page dimensions (210mm × 297mm)
   - Margins: 48pt top, 16pt bottom, 64pt horizontal
   - Font sizes matching frontend: 18pt for name, 10pt for body text

## API Integration

The frontend can request PDFs from the backend using:

```typescript
// Example frontend integration
const downloadPdf = async (resumeId: string) => {
  const response = await fetch(`/api/v1/resume/${resumeId}/pdf`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (response.ok) {
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'resume.pdf';
    link.click();
    URL.revokeObjectURL(url);
  }
};
```

## Consequences

### Positive
- **Consistent Output**: PDF rendering is now server-side, ensuring consistent output regardless of client browser/device
- **Better Font Support**: Times New Roman font is reliably rendered using QuestPDF's typography engine
- **Improved Performance**: Client devices are no longer burdened with PDF generation
- **Extensibility**: The component-based architecture makes it easy to add new sections or modify layouts
- **Scalability**: Backend generation enables future features like batch PDF generation
- **Security**: Resume data processing stays on the server

### Negative
- **Network Dependency**: PDF download now requires a network request to the backend
- **Server Resources**: PDF generation consumes server resources instead of client resources
- **Migration Effort**: Frontend integration needs to be updated to use the new API endpoint

### Mitigations
- PDFs are generated on-demand and not cached, keeping server memory usage low
- The endpoint is authenticated to prevent unauthorized access
- The component structure mirrors the frontend, making future changes easier to synchronize

## References
- [QuestPDF Documentation](https://www.questpdf.com/)
- Original frontend template: `frontend/src/app/(private)/resume/components/document-viewer.tsx`
- PDF sections: `frontend/src/components/pdf-sections/`
