# ADR-0010: Interactive Annotation Editors (Text, Notes, Signatures)

## Status
Accepted

## Date
2025-01-27

## Context

Phase 3 of the PDF viewer requires implementing interactive annotations beyond basic drawing tools. Users need to:
- Add text boxes with editable content
- Create sticky notes with collapsible content
- Draw, upload, or select saved signatures

These annotation types require interactive editors that appear when the tool is activated, allowing users to input content before finalizing the annotation.

## Decision

We will implement three specialized editor components:

### 1. TextBoxEditor
- **Trigger**: Click anywhere when text tool is active
- **UI**: Floating textarea with save/cancel buttons
- **Features**:
  - Auto-focus on mount
  - Cmd/Ctrl+Enter to save
  - Esc to cancel
  - 200px default width, auto-height
- **Storage**: Content saved as TextAnnotation with position, content, color, fontSize

### 2. NoteEditor  
- **Trigger**: Click anywhere when note tool is active
- **UI**: Similar to TextBoxEditor but creates compact note icon
- **Features**:
  - Same keyboard shortcuts as TextBoxEditor
  - Creates 24x24 yellow sticky note icon
  - Content viewable via Popover on click
- **Storage**: Content saved as NoteAnnotation with position and content

### 3. SignatureCreator
- **Trigger**: Click anywhere when signature tool is active
- **UI**: Modal dialog with three tabs
  - **Draw**: Canvas for mouse/trackpad signature drawing
  - **Upload**: File picker for signature images
  - **Saved**: Library of up to 5 saved signatures
- **Features**:
  - Smooth signature drawing with rounded strokes
  - Clear canvas functionality
  - Save signatures to Spark KV storage
  - Delete saved signatures
  - Upload PNG/JPG signature images
- **Storage**: 
  - Signatures stored in KV as `pdf-signatures` array (max 5)
  - Placed signatures saved as SignatureAnnotation with imageData, position, width, height

## Consequences

### Positive
- Intuitive workflow: activate tool → click location → edit content
- Content preservation: signatures saved across sessions
- Flexibility: multiple signature options (draw/upload/saved)
- Note efficiency: compact icon with expandable content
- Keyboard friendly: Enter/Esc shortcuts for quick edits

### Negative
- Additional UI complexity with modals/popovers
- Signature storage uses KV space (limited to 5 to prevent bloat)
- Draw signatures less precise than physical signatures
- Note content not immediately visible (requires click)

### Neutral
- Signature creator adds ~300 LOC
- Each editor is an independent component (maintainability)
- Popover for notes requires Radix UI dependency (already in project)

## Alternatives Considered

### Alternative 1: Inline editing directly on canvas
- **Description**: Edit text/notes directly on the SVG canvas using foreignObject
- **Pros**: No separate editor UI, immediate visual feedback
- **Cons**: Difficult to implement focus management, keyboard events conflict with canvas
- **Why rejected**: Complex implementation, poor UX for positioning editors

### Alternative 2: Signature as text-based font
- **Description**: Use signature fonts (e.g., Dancing Script) instead of images
- **Pros**: Smaller storage, scalable as text
- **Cons**: Not personalized, doesn't look like real signatures
- **Why rejected**: Users expect authentic signature appearance

### Alternative 3: Unlimited saved signatures
- **Description**: Allow unlimited signatures in KV storage
- **Pros**: Never lose a signature
- **Cons**: Storage bloat, cluttered UI
- **Why rejected**: 5 signatures sufficient for most users (personal + initials + variants)

### Alternative 4: External signature service (DocuSign-style)
- **Description**: Integrate third-party signature API
- **Pros**: Legal-grade digital signatures with certificates
- **Cons**: Requires server, authentication, costs, privacy concerns
- **Why rejected**: Out of scope for client-side tool; users can export and sign externally if needed

## Implementation Notes

### Editor Positioning
- Editors positioned absolutely at click coordinates
- Must account for SVG viewport transforms when scaling
- Ensure editors don't overflow page boundaries (future enhancement)

### Signature Quality
- Canvas rendered at 450x200px for smooth drawing
- Exported as PNG with transparency for clean overlay
- Line width: 2px, black color, round caps/joins

### KV Storage Schema
```typescript
interface SavedSignature {
  id: string           // `sig-${timestamp}`
  imageData: string    // base64 PNG data URL
  timestamp: number    // creation timestamp
}

// Stored as array, newest first
const signatures: SavedSignature[] = [...]
```

### Keyboard Shortcuts
- **Cmd/Ctrl+Enter**: Save annotation
- **Esc**: Cancel annotation
- Applied consistently across all editors

## References
- [HTML Canvas API](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API)
- [Radix UI Popover](https://www.radix-ui.com/primitives/docs/components/popover)
- [Spark KV Storage](/docs/ARCHITECTURE.md#state-management)
- Related: ADR-0004 (Annotation Storage)
