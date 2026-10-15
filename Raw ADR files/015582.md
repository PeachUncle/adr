# Decision 001: Mobile-First CSS Refactor

**Date:** 2025-11-08
**Status:** Accepted
**Deciders:** Christopher Junker, Claude Code
**Related Issues:** #12, #8
**Related PR:** #17

## Context

The portfolio site currently uses a **desktop-first** CSS architecture with `max-width` media queries. This means:
- Base styles are written for desktop (1024px+)
- Media queries scale down for smaller screens
- Mobile users download unnecessary desktop styles
- Violates modern mobile-first best practices

**Current approach:**
```css
.hero-section__title {
  font-size: 3rem; /* Desktop default */
}

@media (max-width: 768px) {
  .hero-section__title {
    font-size: 2rem; /* Scale down for tablet */
  }
}

@media (max-width: 480px) {
  .hero-section__title {
    font-size: 1.75rem; /* Scale down for mobile */
  }
}
```

**Problems:**
1. Mobile users (58.67% of web traffic) load desktop styles they never use
2. Goes against progressive enhancement principles
3. Makes mobile optimizations harder to reason about
4. Google uses mobile-first indexing for SEO

**Mobile-First Design Research Score:** 7.4/10 (critical issue identified)

## Decision

**Refactor all CSS to mobile-first architecture using `min-width` media queries.**

This means:
- Write base styles for mobile (320px - smallest modern device)
- Use `min-width` media queries to progressively enhance for larger screens
- Follow breakpoints: 320px (base), 481px, 600px, 769px, 1024px, 1440px

**New approach:**
```css
.hero-section__title {
  font-size: 1.75rem; /* Mobile default (28px) */
}

@media (min-width: 481px) {
  .hero-section__title {
    font-size: 2rem; /* Small tablet (32px) */
  }
}

@media (min-width: 769px) {
  .hero-section__title {
    font-size: 3rem; /* Desktop (48px) */
  }
}
```

## Rationale

1. **Performance:** Mobile users only download styles relevant to their device
2. **Progressive Enhancement:** Start with minimum viable experience, enhance upward
3. **Maintainability:** Easier to add features for larger screens than remove them
4. **SEO:** Aligns with Google's mobile-first indexing
5. **Industry Standard:** WCAG, Material Design, Apple HIG all recommend mobile-first
6. **User Base:** 58.67% of traffic is mobile (Statcounter 2024)

## Alternatives Considered

### Option 1: Keep Desktop-First (Rejected)
**Pros:**
- No refactor needed
- Maintains current logic flow

**Cons:**
- Poor performance for majority of users
- Harder to optimize for mobile
- Against industry best practices
- Fails mobile-first design audit

**Decision:** Rejected - doesn't solve the core problem

### Option 2: Responsive (Device-Agnostic) with Mixed Queries (Rejected)
**Pros:**
- Flexible approach
- Can mix `min-width` and `max-width`

**Cons:**
- Harder to maintain consistency
- Confusing mental model
- Still requires refactor effort

**Decision:** Rejected - mobile-first is clearer

### Option 3: Adaptive (Fixed Breakpoints) (Rejected)
**Pros:**
- Discrete layouts for specific devices
- Can optimize per device

**Cons:**
- More brittle (new devices break layout)
- More CSS to maintain
- Less fluid

**Decision:** Rejected - responsive is more future-proof

## Consequences

### Positive
- ✅ Better mobile performance (reduced CSS payload)
- ✅ Easier to add desktop features
- ✅ Aligns with industry standards
- ✅ Better SEO (mobile-first indexing)
- ✅ Forces mobile-first thinking (better UX)

### Negative
- ⚠️ Requires refactoring all responsive CSS (~2-3 hours)
- ⚠️ Need to test all breakpoints after refactor
- ⚠️ May reveal existing mobile UX issues (good, but more work)

### Neutral
- 📝 Developers need to think mobile-first going forward
- 📝 May need to adjust future features to start mobile

## Implementation Plan

### Phase 1: Audit Current Media Queries
- [x] Identify all `max-width` media queries in `styles.css`
- [x] Document current breakpoints (768px, 480px)
- [x] Note which styles are desktop-specific

### Phase 2: Refactor by Section
1. [ ] CSS Variables (`:root`) - already mobile-friendly
2. [ ] Global Styles (body, html) - make mobile base
3. [ ] Skip Link - already mobile-friendly
4. [ ] Site Header & Navigation - refactor
5. [ ] Hero Section - refactor
6. [ ] About Section - minimal changes
7. [ ] Tech Radar Section - refactor grid
8. [ ] Projects Section - refactor grid
9. [ ] Resume Section - refactor buttons
10. [ ] Contact Section - refactor buttons
11. [ ] Focus Indicators - already mobile-friendly
12. [ ] Button Styles - verify mobile sizing
13. [ ] Site Footer - minimal changes
14. [ ] Responsive Design section - COMPLETE REWRITE

### Phase 3: Testing
- [ ] Chrome DevTools mobile emulation (320px, 375px, 414px, 768px, 1024px)
- [ ] Lighthouse mobile audit (target: 95+)
- [ ] Real device testing (iPhone, Android)
- [ ] Verify no horizontal scroll at any breakpoint
- [ ] Verify all interactive elements accessible

### Phase 4: Documentation
- [ ] Update decision record with lessons learned
- [ ] Document new breakpoint strategy in README

## Success Criteria

- [ ] All `max-width` media queries converted to `min-width`
- [ ] Mobile styles (320px) are the base (no media query)
- [ ] Lighthouse mobile performance score ≥ 90
- [ ] No horizontal scrolling on any device (320px - 2560px)
- [ ] All tests passing (linters, accessibility, unit tests)

## Estimated Effort

**2-3 hours**

Breakdown:
- Audit current CSS: 30 min
- Refactor responsive sections: 1.5 hours
- Testing and fixes: 30-60 min

## References

- [mobile-first-design-research.md](../mobile-first-design-research.md) - Section 9.1.1
- [Issue #12](https://github.com/cjunks94/resume-improvements/issues/12)
- [Issue #8](https://github.com/cjunks94/resume-improvements/issues/8) - Mobile-first design research
- Google Mobile-First Indexing: https://developers.google.com/search/mobile-sites/mobile-first-indexing
- W3C Mobile Best Practices: https://www.w3.org/TR/mobile-bp/
- "Mobile First" by Luke Wroblewski: https://abookapart.com/products/mobile-first

## Timeline

- **Proposed:** 2025-11-08
- **Accepted:** 2025-11-08
- **Implementation Start:** 2025-11-08
- **Target Completion:** 2025-11-08 (same day)

## Notes

This decision is part of a larger mobile-first initiative including:
- Decision 002: Mobile Navigation Pattern (hamburger menu)
- Decision 003: Touch Target Enforcement (coming)

All three decisions (#12, #13, #14) are Priority 1 critical issues that must be addressed together for WCAG 2.1 Level AA compliance.

---

**Status Update:**
- 2025-11-08: Decision accepted, implementation in progress
