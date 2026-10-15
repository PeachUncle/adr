# Decision 002: Mobile Navigation Pattern

**Date:** 2025-11-08
**Status:** Accepted
**Deciders:** Christopher Junker, Claude Code
**Related Issues:** #13, #8
**Related PR:** #17

## Context

The portfolio site displays all 5 navigation items inline on all screen sizes. On mobile devices (< 768px), this creates a cramped, unusable experience.

**Current situation:**
```html
<nav class="site-nav">
  <ul class="site-nav__links">
    <li><a href="#about">About</a></li>
    <li><a href="#tech-radar">Tech Radar</a></li>
    <li><a href="#projects">Projects</a></li>
    <li><a href="#resume">Resume</a></li>
    <li><a href="#contact">Contact</a></li>
  </ul>
</nav>
```

**Problems on mobile (320px - 767px):**
1. 5 inline links are cramped on small screens
2. Items wrap inconsistently across devices
3. Touch targets may be too small/close together
4. No clear navigation hierarchy
5. Poor thumb-zone optimization

**Mobile-First Design Research Finding:** "No mobile-optimized navigation pattern" - scored as critical issue

## Decision

**Implement hamburger menu for mobile devices (< 768px).**

The navigation will:
- **Mobile (< 768px):**
  - Show hamburger toggle button (☰)
  - Hide navigation by default
  - Full-screen overlay menu when opened
  - Large, finger-friendly links
  - Close on link click or toggle tap

- **Desktop (≥ 768px):**
  - Show all links inline (current behavior)
  - Hide hamburger button
  - No overlay/modal behavior

## Rationale

### Why Hamburger Menu?

1. **Space Efficiency:** Frees vertical space for content
2. **Universal Recognition:** 92% of users recognize the hamburger icon (Nielsen Norman Group)
3. **Scalability:** Handles 5-10 items easily (we have 5)
4. **Single-Page Site:** Works perfectly for anchor link navigation
5. **Touch-Friendly:** Full-screen menu allows large tap targets

### Why NOT Other Patterns?

**Bottom Navigation:**
- ❌ Limited to 3-5 items (we have 5, tight fit)
- ❌ Conflicts with browser UI on some devices
- ❌ Not suitable for desktop (need to hide/show)

**Tab Bar:**
- ❌ Takes persistent vertical space
- ❌ Better for app-like interfaces
- ❌ Less space for content

**Priority+ Navigation:**
- ❌ Complex implementation
- ❌ Overkill for static 5-item menu
- ❌ Harder to maintain

**Horizontal Scroll:**
- ❌ Poor discoverability (users don't know to scroll)
- ❌ Harder to access items off-screen
- ❌ Inconsistent scrolling behavior across devices

## Alternatives Considered

### Option 1: Keep Inline Navigation (Rejected)
**Current behavior:** All 5 items always visible, wrapping on small screens

**Pros:**
- No implementation work
- All items always visible

**Cons:**
- Cramped on mobile
- Inconsistent wrapping
- Touch targets too small
- Poor mobile UX

**Decision:** Rejected - doesn't solve mobile usability

### Option 2: Bottom Navigation (Considered)
**iOS/Android app-style bottom bar**

**Pros:**
- Thumb-friendly (easy to reach)
- Always visible
- Modern mobile pattern

**Cons:**
- Limited to 3-5 items (we have 5 = tight)
- Persistent vertical space consumption
- Conflicts with browser UI (Safari, Chrome)
- Not suitable for desktop (need to hide)
- Less content space on mobile

**Decision:** Rejected - better for apps than websites

### Option 3: Horizontal Scroll Menu (Considered)
**Scrollable horizontal list of nav items**

**Pros:**
- Keeps items visible
- Simple implementation
- No toggle needed

**Cons:**
- Poor discoverability (no visual cue to scroll)
- Items off-screen are hidden
- Inconsistent scrolling across devices
- Awkward on desktop

**Decision:** Rejected - poor discoverability

### Option 4: Accordion Navigation (Rejected)
**Expandable sections in place**

**Pros:**
- No overlay/modal
- Items stay in flow

**Cons:**
- Takes vertical space when expanded
- Pushes content down (CLS)
- More complex interaction model
- Overkill for flat 5-item menu

**Decision:** Rejected - too complex for simple menu

## Consequences

### Positive
- ✅ Better mobile UX (dedicated space for navigation)
- ✅ Larger touch targets (48x48px minimum)
- ✅ More content space on mobile
- ✅ Universal pattern (users understand hamburgers)
- ✅ Scales to 10+ items if needed later

### Negative
- ⚠️ Navigation hidden by default (reduces discoverability)
- ⚠️ Requires JavaScript (degrades gracefully if JS disabled)
- ⚠️ Extra tap to access menu (vs always visible)
- ⚠️ Implementation effort (3-4 hours)

### Neutral
- 📝 Need to add hamburger icon (SVG)
- 📝 Need to manage menu open/close state
- 📝 Need to trap focus in open menu (accessibility)

## Implementation Plan

### Phase 1: HTML Structure (30 min)
1. [ ] Add hamburger toggle button before `<nav>`
2. [ ] Add SVG icons (menu ☰ and close ✕)
3. [ ] Add `aria-expanded`, `aria-controls`, `aria-label` attributes
4. [ ] Add `.sr-only` class for screen reader text

**Code:**
```html
<button class="menu-toggle"
        aria-expanded="false"
        aria-controls="site-nav"
        aria-label="Toggle navigation menu">
  <svg class="icon-menu" aria-hidden="true">...</svg>
  <svg class="icon-close" aria-hidden="true" hidden>...</svg>
</button>

<nav id="site-nav" class="site-nav" aria-label="Main navigation">
  <!-- existing nav items -->
</nav>
```

### Phase 2: Mobile CSS (1-1.5 hours)
1. [ ] Style hamburger button (≥48x48px touch target)
2. [ ] Hide button on desktop (≥768px)
3. [ ] Style full-screen overlay menu for mobile
4. [ ] Add slide-in animation (transform: translateX)
5. [ ] Style nav links (large, centered, spaced)
6. [ ] Add backdrop (semi-transparent overlay)

**Key styles:**
```css
@media (max-width: 767px) {
  .menu-toggle { /* ≥48x48px button */ }
  .site-nav__links { /* full-screen, slide from left */ }
  .site-nav__link { /* 48px tall, centered */ }
}

@media (min-width: 768px) {
  .menu-toggle { display: none; }
}
```

### Phase 3: JavaScript Behavior (1 hour)
1. [ ] Toggle `aria-expanded` on button click
2. [ ] Toggle menu visibility (add/remove class or attribute)
3. [ ] Swap icons (menu ☰ ↔ close ✕)
4. [ ] Close menu when nav link clicked
5. [ ] Close menu on Escape key
6. [ ] Trap focus in open menu (accessibility)
7. [ ] Return focus to toggle button when closed

**Key logic:**
```javascript
toggle.addEventListener('click', () => {
  const expanded = toggle.getAttribute('aria-expanded') === 'true';
  toggle.setAttribute('aria-expanded', !expanded);
  nav.setAttribute('aria-expanded', !expanded);
  // Swap icons, manage focus
});

// Close on nav link click
navLinks.forEach(link => {
  link.addEventListener('click', closeMenu);
});

// Close on Escape
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && isOpen) closeMenu();
});
```

### Phase 4: Accessibility (30 min)
1. [ ] Screen reader testing (VoiceOver, NVDA)
2. [ ] Keyboard navigation (Tab, Enter, Escape)
3. [ ] Focus trap (Tab cycles within open menu)
4. [ ] ARIA state management
5. [ ] Skip link still works

### Phase 5: Testing (30 min)
1. [ ] Mobile devices (iPhone, Android)
2. [ ] Touch interaction smooth
3. [ ] Animation performance (60fps)
4. [ ] Desktop navigation unaffected
5. [ ] Works with JavaScript disabled (graceful degradation)

## Accessibility Considerations

**WCAG 2.1 Requirements:**
- **2.1.1 Keyboard:** All functionality keyboard accessible
- **2.1.2 No Keyboard Trap:** Users can exit menu with keyboard
- **2.4.3 Focus Order:** Logical tab order
- **4.1.2 Name, Role, Value:** Proper ARIA attributes

**Implementation:**
```html
<!-- Proper ARIA -->
<button aria-expanded="false" aria-controls="site-nav" aria-label="Toggle menu">

<!-- Focus trap in open menu -->
<script>
  // First and last focusable elements
  const focusableElements = nav.querySelectorAll('a, button');
  const firstFocusable = focusableElements[0];
  const lastFocusable = focusableElements[focusableElements.length - 1];

  // Trap Tab key
  lastFocusable.addEventListener('keydown', (e) => {
    if (e.key === 'Tab' && !e.shiftKey) {
      e.preventDefault();
      firstFocusable.focus();
    }
  });
</script>
```

## Performance Considerations

**Animation Performance:**
- Use `transform` (GPU-accelerated) not `left/right`
- Use `will-change: transform` sparingly (memory cost)
- Prefer CSS transitions over JavaScript animation

**Code:**
```css
.site-nav__links {
  transform: translateX(-100%);
  transition: transform 0.3s ease;
  will-change: transform; /* Only when menu is opening */
}

.site-nav__links[aria-expanded="true"] {
  transform: translateX(0);
}
```

**Reduced Motion:**
```css
@media (prefers-reduced-motion: reduce) {
  .site-nav__links {
    transition: none; /* Instant toggle for users who prefer reduced motion */
  }
}
```

## Success Criteria

- [ ] Hamburger button visible on mobile (< 768px)
- [ ] Button hidden on desktop (≥ 768px)
- [ ] Touch target ≥ 48x48px
- [ ] Menu slides in smoothly (< 300ms)
- [ ] All nav links accessible and properly sized
- [ ] Keyboard accessible (Tab, Enter, Escape)
- [ ] Screen reader announces state changes
- [ ] Focus trapped in open menu
- [ ] Closes on link click
- [ ] Graceful degradation without JavaScript

## Estimated Effort

**3-4 hours**

Breakdown:
- HTML structure: 30 min
- CSS styling: 1-1.5 hours
- JavaScript behavior: 1 hour
- Accessibility: 30 min
- Testing: 30 min

## Files to Create/Modify

**New file:**
- `scripts.js` (menu toggle logic)

**Modified files:**
- `index.html` (add button, update nav)
- `styles.css` (mobile menu styles)

**Add to HTML `<head>`:**
```html
<script src="scripts.js" defer></script>
```

## References

- [mobile-first-design-research.md](../mobile-first-design-research.md) - Section 3 (Mobile Navigation Patterns)
- [Issue #13](https://github.com/cjunks94/resume-improvements/issues/13)
- Nielsen Norman Group - Hamburger Menus: https://www.nngroup.com/articles/hamburger-menus/
- WCAG 2.1 - ARIA Menus: https://www.w3.org/WAI/ARIA/apg/patterns/menu-button/
- Material Design - Navigation Drawer: https://m3.material.io/components/navigation-drawer

## Timeline

- **Proposed:** 2025-11-08
- **Accepted:** 2025-11-08
- **Implementation Start:** 2025-11-08
- **Target Completion:** 2025-11-08 (after Decision 001 complete)

## Dependencies

- Decision 001 (Mobile-First CSS) should be complete first
- Touch target enforcement (Decision 003) will verify button sizing

## Notes

**Graceful Degradation:**
If JavaScript is disabled, the menu should remain visible (no-JS fallback):

```html
<noscript>
  <style>
    .menu-toggle { display: none !important; }
    .site-nav__links { transform: none !important; }
  </style>
</noscript>
```

**Future Enhancements:**
- Backdrop click to close
- Swipe gestures to open/close
- Smooth scroll to section after click
- Active section indicator in menu

---

**Status Update:**
- 2025-11-08: Decision accepted, pending implementation after Decision 001
