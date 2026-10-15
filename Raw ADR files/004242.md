# ADR-0002: Internationalization Architecture

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-06
- **Feature:** 001-docusaurus-book
- **Context:** The textbook must support English (default) and Urdu with proper RTL layout. Urdu-speaking readers are a key demographic for the hackathon project. The solution must handle bidirectional text, locale-specific typography, navbar/footer translations, and content translations while maintaining a single codebase.

## Decision

We will use Docusaurus native i18n with the following architecture:

- **i18n Framework**: Docusaurus built-in i18n plugin (no external libraries)
- **Default Locale**: English (`en`) with LTR direction
- **Additional Locale**: Urdu (`ur`) with RTL direction (`htmlLang: 'ur-PK'`)
- **Translation Structure**: `i18n/ur/` folder mirroring content structure
- **UI Translations**: JSON files for navbar, footer, and theme strings
- **Locale Switching**: Built-in `localeDropdown` navbar component
- **RTL Styling**: Automatic via `direction: 'rtl'` config + supplementary `rtl.css`

Configuration:
```typescript
i18n: {
  defaultLocale: 'en',
  locales: ['en', 'ur'],
  localeConfigs: {
    en: { label: 'English', direction: 'ltr', htmlLang: 'en-US' },
    ur: { label: 'اردو', direction: 'rtl', htmlLang: 'ur-PK' },
  },
}
```

## Consequences

### Positive

- Zero additional dependencies - native Docusaurus support
- Automatic RTL layout handling via CSS logical properties
- Locale-aware URL paths (`/ur/docs/...`)
- Translation workflow matches content structure (easy to maintain)
- Graceful fallback to English for untranslated pages
- SEO benefits with `hreflang` tags automatically generated
- Theme strings (navbar, footer) translate separately from content

### Negative

- Full page content must be duplicated for each locale (no inline switching)
- Translation maintenance overhead scales with content growth
- RTL edge cases may require manual CSS fixes
- No automated translation tooling (manual process)
- Build time increases with each locale added

## Alternatives Considered

**Alternative A: react-i18next + custom RTL handling**
- Pros: More control, runtime language switching, interpolation features
- Cons: Additional dependency, manual RTL setup, more boilerplate
- Rejected: Docusaurus native i18n provides sufficient features with less complexity

**Alternative B: Crowdin integration for translations**
- Pros: Collaborative translation, automated sync, translation memory
- Cons: External service dependency, cost for private projects, setup overhead
- Rejected: Overkill for initial 2-language scope; can add later if needed

**Alternative C: Single-page locale switching (no URL paths)**
- Pros: Simpler routing, smaller build output
- Cons: Poor SEO, no deep linking to specific locale, accessibility issues
- Rejected: URL-based locales are standard and SEO-friendly

## References

- Feature Spec: [specs/001-docusaurus-book/spec.md](../specs/001-docusaurus-book/spec.md)
- Implementation Plan: [specs/001-docusaurus-book/plan.md](../specs/001-docusaurus-book/plan.md)
- Related ADRs: ADR-0001 (Framework Stack)
- Context7 Research: [specs/001-docusaurus-book/research.md](../specs/001-docusaurus-book/research.md) - Section 1 (i18n Configuration)
