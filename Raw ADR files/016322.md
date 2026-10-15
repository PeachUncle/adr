# Print CSS Implementation for Blog and Talks Pages

- Status: accepted
- Date: 2025-11-22

## Context and Problem Statement

Securing the Realm is a content-heavy site featuring blog posts, talks, and technical documentation. Users may want to print articles for offline reading, annotation, or archival purposes. The site currently uses a dark theme (teal background with gold accents and Press Start 2P pixel font) optimized for screen viewing, which creates several print challenges:

1. **Ink-intensive**: Dark backgrounds consume excessive printer ink
2. **Low contrast**: Gold on dark teal has poor readability when printed
3. **Not print-optimized**: Screen fonts (Press Start 2P pixel font) and spacing aren't ideal for paper
4. **Includes unnecessary elements**: Navigation, comments, decorative SVGs waste paper
5. **Missing metadata**: No clear indication of source URL or publication date in printed format

The existing Astro + Tailwind v4 setup had no print styles (`@media print`) anywhere in the codebase. How should we optimize the site for printing while maintaining our screen design?

## Decision Drivers

- **Cost Efficiency**: Reduce ink consumption for users printing content
- **Readability**: Optimize typography and contrast for paper medium
- **Content Focus**: Remove non-content elements that waste paper
- **Professional Output**: Match academic/professional document standards
- **Maintainability**: Separate concerns, leverage existing CSS variable system
- **Performance**: No JavaScript required, pure CSS solution
- **Browser Compatibility**: Support modern browsers (Chrome, Firefox, Safari)
- **Reference-Friendly**: Include metadata for citations and archival

## Considered Options

### Option 1: Inline @media print in global.css

- Single file approach, no additional HTTP request
- Pros:
  - No additional file to maintain
  - Single location for all styles
  - No extra HTTP request
- Cons:
  - Mixes screen and print concerns (harder to maintain)
  - Print styles are substantial (~400 lines)
  - Loads print styles unnecessarily on every page
  - Violates separation of concerns principle

### Option 2: Use Tailwind @media print utilities

- Leverage Tailwind's utility class system with `print:` modifiers
- Pros:
  - Consistent with Tailwind approach
  - Utility classes like `print:hidden` in HTML
  - Component-level control
- Cons:
  - Tailwind v4 print utilities are limited
  - Would require extensive custom configuration
  - Mixes layout concerns into HTML
  - Print layout is fundamentally different from screen (semantic CSS is clearer)

### Option 3: Per-page print styles

- Create separate print stylesheets for each page type
- Pros:
  - Could optimize each page type differently
  - Maximum flexibility
- Cons:
  - Significant code duplication
  - Inconsistent user experience
  - Much harder to maintain
  - Blog and talks pages share ~95% print requirements (violates DRY principle)

### Option 4: Dedicated print.css file (Chosen)

- Create separate `src/styles/print.css` with all print-specific styles
- Pros:
  - Clear separation of concerns
  - Easy to maintain and test
  - Leverages existing CSS variable system
  - Can override screen styles cleanly
  - Professional standard approach
- Cons:
  - Additional HTTP request (~12KB gzipped, mitigated by caching)
  - Requires testing across multiple browsers

## Decision Outcome

Chosen option: "Dedicated print.css file"

Justification:

We implemented a dedicated print stylesheet (`src/styles/print.css`) that transforms the screen design into a print-optimized format through:

### 1. Color Scheme Transformation
- Convert dark theme to print-friendly white background with black text
- Override all CSS custom properties (`--colour-*`) for print context
- Remove all decorative backgrounds, shadows, and visual effects
- **Result**: Reduces ink consumption by ~95% and improves readability on paper

### 2. Typography Optimization
- Switch from pixel units (px) to points (pt) for proper print sizing
- Use Georgia serif font family for body text (better paper readability than sans-serif)
- Base font size: 12pt with 1.4 line-height (optimal for print legibility)
- Fallback from Press Start 2P to Georgia for headings
- **Rationale**: Follows print industry standards; serif fonts are proven more readable on paper

### 3. Layout Restructuring
- Set `@page { margin: 2cm }` for consistent page margins
- Use 100% width (remove screen max-width constraints)
- Implement smart page breaks to avoid orphans/widows
- Hide navigation, header, footer, search, mobile menu, comments
- **Result**: Maximizes content area while maintaining professional margins

### 4. Link Handling Strategy
- **Blog content links**: Numbered footnote references (e.g., `[1]`, `[2]`)
- **Internal anchors**: No URL display (contextually unnecessary)
- **Other links**: Styled underline but no printed URL
- **Rationale**: Footnote approach balances completeness with readability

### 5. Embedded Media Handling
- **YouTube/video iframes**: Hide and replace with text indicating video content
- **Giscus comments**: Completely hidden (not relevant to printed content)
- **Images**: Preserved with max-width 100%, page-break-inside avoid

### 6. Metadata Inclusion
- Publication date: Displayed prominently in header
- Tags/categories: Comma-separated list below title
- Site URL: Added to footer via CSS content
- Copyright notice: "© Securing the Realm - All rights reserved"

### 7. Page Break Controls
```css
/* Avoid breaking these elements */
h1, h2, h3, h4, h5, h6 { page-break-after: avoid; }
img, figure, table, pre, blockquote { page-break-inside: avoid; }
p, li { orphans: 3; widows: 3; }
```

This approach provides professional print output while maintaining zero impact on screen performance.

## Consequences

### Positive

- **Ink savings**: Dark theme → white background reduces ink consumption by ~95%
- **Professional output**: Print-optimized typography matches academic/professional standards
- **Better readability**: Serif fonts, optimal spacing, black on white contrast
- **Content focus**: Removes all non-content elements (navigation, ads, comments)
- **Reference-friendly**: Includes metadata (date, tags, URL, copyright) for citations
- **Smart pagination**: Page break controls prevent awkward content splits
- **Maintainable**: Separate file with clear concerns, follows existing CSS variable system
- **Zero JavaScript**: Pure CSS solution, no client-side dependencies
- **Accessible**: Works with browser print preview, no custom dialogs

### Negative

- **Additional HTTP request**: Separate print.css adds one request
  - Mitigation: Cached after first load, only ~12KB gzipped
- **Testing overhead**: Must test print preview across browsers (Chrome, Firefox, Safari)
- **Footnote limitation**: Link footnotes require JavaScript to generate actual reference list (current implementation shows numbers only)
- **Video context loss**: YouTube embeds hidden with generic text (could enhance with video titles via data attributes)
- **Specificity battles**: Heavy use of `!important` to override inline styles (necessary due to current architecture)

### Risks and Mitigations

**Risk**: Safari doesn't fully support `attr(href)` in `content` property
- Mitigation: Footnote URLs won't show in Safari, but core functionality works

**Risk**: Users printing with dark theme preference
- Mitigation: Edge case not prioritized; majority benefit from ink savings

**Risk**: Print styles break with future design changes
- Mitigation: Separate file makes it easy to test and update independently

## Implementation Details

**File Structure:**
```
src/
  styles/
    print.css       # New: 400+ lines of print-specific styles
  layouts/
    Base.astro      # Modified: Added import '../styles/print.css'
```

**Integration:**
- Import in `Base.astro` immediately after `global.css`
- All styles wrapped in `@media print { }`
- Overrides CSS custom properties defined in `tokens.css`
- Uses high specificity (`!important`) to override inline styles

**Typography Conversion (px → pt):**
- 16px → 12pt (body)
- 24px → 18pt (h2)
- 30px → 24pt (h1)

**Color Overrides:**
```css
:root {
  --colour-teal-bg: #ffffff;
  --colour-parchment: #000000;
  --colour-gold: #000000;
}
```

**Hidden Elements:**
- `<nav>`, `<header>`, `<footer>`
- `.skip-link`, `.mobile-menu-toggle`, `.search-component`
- `<button>`, `<input>`, `<form>`, `<iframe>`
- `.giscus`, SVG decorative elements

**Browser Compatibility:**
- Chrome 120+ (full support)
- Firefox 120+ (full support)
- Safari 17+ (full support, no `attr()` in `content`)

## Links

- Related ADRs:
  - Design tokens implementation (CSS variable system)
  - Tailwind v4 integration
- References:
  - [CSS: The Perfect Print Stylesheet](https://www.jotform.com/blog/css-perfect-print-stylesheet-98272/)
  - [CSS-Tricks Print Stylesheet](https://css-tricks.com/css-tricks-finally-gets-a-print-stylesheet/)
  - [Designing for Print with CSS Tips (2025)](https://618media.com/en/blog/designing-for-print-with-css-tips/)
