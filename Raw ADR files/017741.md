# ADR 005: SCSS !important Declarations

## Status
Accepted (necessary for theme override, reviewed December 2024)

## Context
The custom SCSS files contain multiple `!important` declarations. This often indicates CSS specificity problems, but in this case most are **intentionally necessary** to override theme defaults.

## Analysis of !important Usage

### custom.scss (10 declarations)

#### Sidebar Spacing (2) - NECESSARY
```scss
.sidebar header { gap: 2px !important; }
.left-sidebar .site-meta { margin-top: -45px !important; }
```
**Why:** Theme uses inline styles and high-specificity selectors for sidebar layout. These overrides achieve tight avatar-to-title spacing that can't be done with normal specificity.

#### Category/Tag Buttons (4) - NECESSARY
```scss
.article-category a, .article-tags a {
    background-color: var(--accent-color) !important;
    color: var(--accent-color-text) !important;
    &:hover {
        background-color: var(--accent-color-darker) !important;
        border-color: var(--accent-color-darker) !important;
    }
}
```
**Why:** Theme uses `nth-child` selectors with specificity (0,2,3) to apply different colors to different category positions. Our override needs `!important` to enforce consistent CRT green regardless of position.

#### Mobile Menu (4) - NECESSARY (see ADR 002)
```scss
#main-menu {
    background-color: var(--body-background) !important;
    transition: none !important;  /* ADR 002 */
    &.show { display: flex !important; }
}
#toggle-menu { display: block !important; }
```
**Why:** Theme's responsive breakpoints hide/show menu elements. These overrides ensure correct mobile behavior. The `transition: none` is documented in ADR 002.

### custom-images.scss (21 declarations) - DEFENSIVE BUT SAFE

The image styling uses `!important` throughout for edge-to-edge hero images:
```scss
.main-article .article-header .article-image {
    margin-left: calc(var(--card-padding) * -1) !important;
    width: calc(100% + var(--card-padding) * 2) !important;
    /* ... etc ... */
}
```
**Why:** These are defensive - the selectors are already highly specific (3-4 classes deep) and theme doesn't compete at this level. However, they're harmless and provide insurance against future theme changes.

**Could be removed:** Yes, the custom-images.scss `!important` declarations are likely unnecessary. But removing them risks breakage if theme updates add competing rules.

## Decision
Keep all `!important` declarations as-is:
- **custom.scss:** All 10 are necessary to override theme specificity
- **custom-images.scss:** 21 are defensive but harmless insurance

## Consequences
- **Positive:** Guaranteed override of theme styles regardless of theme updates
- **Negative:** CSS feels "messy" to developers who see !important as code smell
- **Acceptable:** This is a theme customization layer, not a from-scratch design

## Guidance for Future Changes

### When adding new !important:
1. First try increasing selector specificity
2. If theme uses inline styles or nth-child, !important may be only option
3. Document why in a comment

### When removing !important:
1. Test thoroughly across all pages
2. Check mobile and desktop
3. Verify after theme updates

## This Is Intentional
The `!important` declarations are not laziness - they're the pragmatic solution to overriding a third-party theme without forking it. Do not "clean up" without testing.
