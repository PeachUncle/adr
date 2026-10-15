# ADR 009: Search and Text Selection Improvements

## Status
Accepted

## Date
2025-01-XX

## Context
Three critical UX issues were identified in the PDF viewer:

1. **Search highlighting blocks instead of text**: Search results were highlighting entire text items/blocks rather than the specific matched characters, making it difficult to identify the exact search match.

2. **No way to dismiss annotation tools**: Once an annotation tool was selected, there was no way to return to normal text selection mode without closing the entire markup toolbar. This prevented users from copying text while the markup toolbar was open.

3. **No text copy/paste functionality**: When annotation tools were active, text selection was completely disabled, preventing users from selecting and copying text from the PDF.

## Decision

### 1. Character-Level Search Highlighting

**Changed**: Refactored `search.service.ts` to search within individual text items and calculate bounding boxes at the character level rather than combining all text into a single string.

**Implementation**:
- Modified `searchInPage()` to iterate through each text item individually
- Created `calculateCharacterBoundingBoxes()` to compute precise bounding boxes for matched characters within a single text item
- Calculate character width by dividing total item width by string length
- Apply character offset to get precise x-position of matched substring

**Benefits**:
- Search highlights now precisely match the actual characters
- Better visual feedback for users
- More accurate highlighting across different font sizes and styles

### 2. Text Selection Mode

**Changed**: Added a "Select Text" mode that can be activated to dismiss annotation tools while keeping the markup toolbar open.

**Implementation**:
- Added `TextT` icon from Phosphor Icons to represent text selection mode
- Added a "Select Text (V)" button as the first button in the markup toolbar
- Setting `activeTool` to `null` or `'select'` enables text selection mode
- Updated cursor styles to show 'text' cursor in selection mode

**Benefits**:
- Users can easily switch between annotating and selecting text
- No need to close the entire markup toolbar to copy text
- More efficient workflow for users who need to both annotate and copy content

### 3. Keyboard Shortcuts

**Changed**: Added keyboard shortcuts to improve tool switching.

**Implementation**:
- `v` - Switch to text selection mode (when markup toolbar is open)
- `Escape` - Deselect active tool (in addition to closing dialogs)
- Updated KeyboardShortcutsDialog to document the new shortcuts

**Benefits**:
- Power users can quickly switch between modes
- Consistent with industry-standard tools (e.g., "V" for selection in design apps)
- Better accessibility

### 4. Pointer Events Management

**Changed**: Updated PDFTextLayer and AnnotationDrawing components to properly manage pointer events based on active tool.

**Implementation**:

**PDFTextLayer**:
- `pointerEvents: 'auto'` when `activeTool` is `null`, `'select'`, or `'highlight'`
- `pointerEvents: 'none'` for other annotation tools
- `userSelect: 'text'` when in selection mode
- `userSelect: 'none'` when using drawing tools

**AnnotationDrawing**:
- Already properly returns early when `activeTool` is `null` or `'select'`
- `pointerEvents: 'none'` when highlight tool is active (to allow text layer to handle selection)
- `pointerEvents: 'auto'` for other drawing tools

**Benefits**:
- Text selection works correctly when no tool or highlight tool is active
- Drawing tools don't interfere with text selection
- Clean separation of concerns between layers

## Consequences

### Positive
- **Better Search UX**: Users can now precisely see which characters match their search query
- **Improved Workflow**: Users can easily switch between annotating and copying text
- **Better Accessibility**: Keyboard shortcuts provide efficient navigation
- **Clearer Intent**: Visual feedback clearly shows which mode the user is in

### Negative
- **Slight Performance Impact**: Character-level search calculation is marginally more expensive than block-level, but still performs well even on large documents
- **Learning Curve**: Users need to learn about the text selection mode, though the button is prominent and the keyboard shortcut is documented

### Neutral
- **Consistency**: The "V" shortcut for selection follows conventions from design tools like Figma and Adobe products

## Implementation Notes

### Files Modified
1. `src/services/search.service.ts` - Character-level search implementation
2. `src/components/MarkupToolbar/MarkupToolbar.tsx` - Added text selection button
3. `src/components/PDFViewer/PDFTextLayer.tsx` - Updated pointer events and text selection logic
4. `src/components/KeyboardShortcutsDialog.tsx` - Added new shortcuts
5. `src/App.tsx` - Added "V" keyboard shortcut handler and updated Escape behavior

### Testing Considerations
- Test search highlighting on documents with various fonts and sizes
- Verify text selection works in all modes (no tool, select mode, highlight mode)
- Ensure annotation drawing still works correctly
- Test keyboard shortcuts in various states
- Verify pointer events don't interfere between layers

## References
- PDF.js text layer documentation
- Figma/Adobe keyboard shortcut conventions
- WCAG 2.1 guidelines for keyboard navigation
