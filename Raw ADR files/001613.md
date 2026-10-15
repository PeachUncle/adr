# ADR-20251015-rich-text-editor-pending

## Status
Proposed

## Context
ExvoRed requires rich text formatting for long-form text fields: exvoto transcriptions (which need superscript support for footnote markers), exvoto "Información adicional" (additional information), and catalog descriptions. Currently, these fields use plain `<textarea>` elements that only support plain text, forcing users to manually type formatting indicators like "[superscript: 1]" or lose formatting information.

Historical transcription conventions require superscript for footnote references, abbreviation markers, and editorial annotations. Bold and italic are needed to indicate emphasis in original texts or editorial additions. Paragraph breaks must be preserved to maintain readability of long transcriptions (500+ words). The rich text editor must integrate seamlessly with React 19, work within modal forms and detail pages, support keyboard navigation (Tab, Enter), and not interfere with Excel-mode navigation.

The editor must store formatted text in a machine-readable format (HTML or Markdown) that can be safely stored in SQLite text fields. XSS prevention is critical; user-generated HTML must be sanitized to prevent script injection. Bundle size is a concern; adding a rich text editor should not increase the main bundle by more than 100KB (gzipped). The editor must be accessible (WCAG 2.1 AA compliance) and work with screen readers.

## Decision
**DECISION PENDING** - Three options are under consideration:

### Option A: TipTap
- Modern, extensible rich text editor built on ProseMirror
- TypeScript-first with excellent React integration
- Modular: can include only needed features (bold, italic, superscript, paragraphs)
- Bundle size: ~50KB gzipped with basic extensions
- Outputs structured HTML with predictable schema
- Strong community support and active development
- Supports custom keyboard shortcuts
- License: MIT (free for all uses)

### Option B: Quill
- Mature, stable editor with 10+ years of development
- Simple API with good documentation
- Built-in XSS protection via sanitization
- Bundle size: ~150KB gzipped (includes all features)
- Outputs HTML or Delta JSON format
- Large community and extensive plugin ecosystem
- Good accessibility support out of the box
- License: BSD (free for all uses)

### Option C: Slate.js
- Highly customizable, React-native editor framework
- Full control over rendering and behavior
- TypeScript support with type-safe API
- Bundle size: ~100KB gzipped
- Outputs custom JSON structure (requires serialization)
- Steep learning curve; requires significant custom code
- Smaller community, fewer pre-built plugins
- License: MIT (free for all uses)

## Consequences

### Positive (All Options)
- Formatting preservation: Transcriptions retain superscript, bold, italic, and paragraph structure
- User experience: WYSIWYG editing familiar to users from word processors
- Data quality: Formatted text improves readability in view mode and exports
- Academic conventions: Superscript support enables proper scholarly transcription notation

### Negative (All Options)
- Bundle size increase: 50-150KB added to page chunks that include rich text fields
- Storage format complexity: Must store HTML or JSON in database; increases field size by 20-50% due to markup tags
- XSS risk: User-generated HTML requires sanitization library (DOMPurify, ~20KB) to prevent script injection
- Migration needed: Existing plain text fields must be wrapped in `<p>` tags or converted to HTML
- Accessibility testing: Rich text editors require additional WCAG testing for keyboard and screen reader support
- Learning curve: Users accustomed to plain text must learn formatting toolbar

### Pending Evaluation Criteria
1. **Bundle size impact**: Measure actual gzipped size with tree-shaking
2. **Superscript support**: Verify all options support `<sup>` tags reliably
3. **XSS prevention**: Test sanitization libraries for security
4. **Keyboard integration**: Ensure Tab key exits editor and doesn't conflict with Excel mode
5. **Accessibility**: Test with NVDA/JAWS screen readers
6. **Performance**: Benchmark rendering 1000-word transcriptions with formatting

## Alternatives Considered

### Alternative 1: Markdown with Preview
**Rejected because:** Markdown does not have native superscript syntax (requires `<sup>` HTML tags embedded in Markdown, which defeats the purpose). Users must learn Markdown syntax (**, *, #), which is unfamiliar to humanities researchers. Preview-edit mode split requires extra clicks to switch between modes. Rendering Markdown to HTML requires a parsing library (marked.js, ~20KB), adding bundle size without providing WYSIWYG benefits.

### Alternative 2: ContentEditable with Manual Formatting
**Rejected because:** Building a custom rich text editor on `contentEditable` is extremely complex. Browser inconsistencies in `contentEditable` behavior (especially copy/paste) create endless edge cases. Manually implementing bold, italic, superscript commands requires hundreds of lines of code and extensive cross-browser testing. No built-in sanitization or structured output. Reinventing the wheel when mature libraries exist is poor engineering practice.

### Alternative 3: Plain Text with Formatting Indicators
**Rejected because:** Plain text with indicators like "[SUP]1[/SUP]" or "**bold**" defeats the purpose of rich text editing. View mode would need to parse and convert these indicators to HTML, adding complexity. Users must memorize formatting syntax. Copy-pasting from external sources (PDFs, other catalogs) loses formatting. This approach provides no improvement over current plain `<textarea>` implementation.

## Next Steps
1. Create prototype implementations of TipTap, Quill, and Slate.js in isolated test components
2. Measure bundle size impact with production builds
3. Test superscript functionality and XSS sanitization for each option
4. Conduct user testing with target researchers to evaluate WYSIWYG editor UX
5. Make final decision and create superseding ADR

## References
- TipTap: https://tiptap.dev/
- Quill: https://quilljs.com/
- Slate.js: https://www.slatejs.org/
- DOMPurify (XSS sanitization): https://github.com/cure53/DOMPurify
- Related plan item: `/home/marcos/Documentos/Programming/JavaScript/ExvoRed/.claude/docs/plan.md` (rich-text-editor-for-long-fields)
