# ADR 008: Accessibility-First Development with WCAG 2.2 AAA as Baseline

**Status:** Accepted

**Date:** 2025-10-18

**Context:**

WCAG Explorer is an application specifically designed to help people understand and implement web accessibility standards. As such, it has a unique responsibility to:

- Exemplify best practices in accessibility
- Be usable by people with disabilities
- Demonstrate that highly accessible applications are feasible
- Serve as a reference implementation for WCAG compliance
- Be usable with assistive technologies
- Support diverse user needs and preferences

The Web Content Accessibility Guidelines (WCAG) define three conformance levels:
- **Level A:** Basic accessibility (minimum)
- **Level AA:** Standard accessibility (widely adopted, often legally required)
- **Level AAA:** Enhanced accessibility (highest level, not always achievable for all content)

Most websites aim for WCAG 2.1 Level AA. We needed to decide what standard WCAG Explorer itself should meet.

**Decision:**

WCAG Explorer will be developed with **WCAG 2.2 Level AAA** as the baseline accessibility standard.

This means:
- All Level A and AA criteria MUST be met
- All achievable Level AAA criteria SHOULD be met
- Where AAA is not feasible for specific content, document the reason
- Accessibility is a requirement, not a nice-to-have
- All new features must maintain this standard

**Consequences:**

### Positive

1. **Credibility:**
   - Practices what it preaches
   - Users trust an accessibility tool that is itself accessible
   - Can be cited as reference implementation
   - Validates that AAA is achievable

2. **Inclusive User Base:**
   - Usable by people with diverse disabilities
   - Screen reader users can fully navigate
   - Keyboard-only users have full access
   - Low vision users benefit from high contrast themes
   - Cognitive disabilities accommodated with clear language

3. **Better UX for Everyone:**
   - Clear navigation benefits all users
   - Keyboard shortcuts improve efficiency
   - Good contrast is easier to read
   - Consistent patterns reduce cognitive load
   - Well-structured content is easier to understand

4. **Quality Assurance:**
   - Accessibility requirements catch bugs early
   - Forces consideration of edge cases
   - Results in more robust code
   - Better error handling

5. **Legal and Compliance:**
   - Exceeds legal requirements in all jurisdictions
   - Reduces legal risk
   - Can be used in regulated industries
   - Government and enterprise-ready

6. **Performance Benefits:**
   - Semantic HTML improves performance
   - Keyboard navigation is fast
   - Screen reader optimization benefits voice control
   - Progressive enhancement improves reliability

7. **SEO Benefits:**
   - Semantic HTML helps search engines
   - Clear headings improve content structure
   - Alt text helps image search
   - Good UX correlates with search ranking

8. **Educational Value:**
   - Code can be studied for accessibility patterns
   - Demonstrates real-world AAA implementation
   - Source code serves as learning resource
   - Shows that AAA is practical

### Negative

1. **Development Time:**
   - More time spent on accessibility features
   - Additional testing required
   - Need to consider more edge cases
   - Documentation overhead

2. **Feature Complexity:**
   - Some features require alternative implementations
   - Need to support multiple interaction modes
   - Must maintain both mouse and keyboard interfaces
   - Visual designs must work with high contrast

3. **Design Constraints:**
   - Color alone cannot convey information
   - Animations must respect prefers-reduced-motion
   - Touch targets must be minimum size
   - Contrast ratios must be high

4. **Testing Burden:**
   - Manual testing with screen readers
   - Keyboard navigation testing
   - Multiple theme testing
   - Browser compatibility across AT

5. **Performance Trade-offs:**
   - ARIA live regions add complexity
   - Focus management adds JavaScript
   - Theme system adds CSS
   - Multiple view modes increase bundle size

6. **Learning Curve:**
   - Team must deeply understand WCAG
   - Need expertise in ARIA and assistive tech
   - Must test with real users
   - Ongoing education required

### Implementation Strategies

**1. Semantic HTML First**
```tsx
// ✅ Good: Semantic elements
<nav aria-label="Filters">
  <fieldset>
    <legend>Version</legend>
    <input type="checkbox" id="v2-2" />
    <label htmlFor="v2-2">WCAG 2.2</label>
  </fieldset>
</nav>

// ❌ Bad: Divs for everything
<div className="nav">
  <div className="fieldset">
    <div className="legend">Version</div>
    <div className="checkbox" onClick={...} />
  </div>
</div>
```

**2. Keyboard Navigation**
```tsx
// All interactive elements are keyboard accessible
- Tab/Shift+Tab for navigation
- Enter/Space to activate buttons
- Arrow keys for radio groups
- Escape to close modals
- / to focus search
- F to focus filters
```

**3. Screen Reader Support**
```tsx
// ARIA live regions for dynamic content
<LiveRegion />
  <div aria-live="polite" aria-atomic="true">
    {announcements}
  </div>
</LiveRegion>

// Announce results
announce(`${total} results found, page ${page} of ${totalPages}`);

// User preference to disable
<label>
  <input type="checkbox" checked={announcementsEnabled} />
  Enable screen reader announcements
</label>
```

**4. Color and Contrast**
```tsx
// Level AAA requires 7:1 contrast for normal text, 4.5:1 for large text
// High contrast theme provides 21:1 contrast

.theme-high-contrast {
  --color-bg-primary: 0 0 0;        /* Black */
  --color-text-primary: 255 255 255; /* White */
  --color-accent: 255 255 0;         /* Bright yellow */
}

// Color is never sole indicator
<span className={`badge-${level}`}>
  <span aria-hidden="true">{levelShape}</span> {/* ●■▲ */}
  Level {level}
</span>
```

**5. Focus Management**
```tsx
// Visible focus indicators
*:focus-visible {
  outline: 2px solid rgb(var(--color-focus));
  outline-offset: 2px;
}

// Focus trap in modals
import FocusTrap from 'focus-trap-react';

<FocusTrap>
  <Modal>...</Modal>
</FocusTrap>

// Return focus on close
const triggerRef = useRef<HTMLElement>();
```

**6. Error Identification**
```tsx
// Clear error messages
<div role="alert" className="border-red-300">
  <h2 className="text-red-800">Error Loading Results</h2>
  <p className="text-red-700">{errorMessage}</p>
  <button onClick={retry}>Try Again</button>
</div>

// Form validation
<input
  aria-invalid={hasError}
  aria-describedby={hasError ? 'email-error' : undefined}
/>
{hasError && (
  <span id="email-error" role="alert">
    Please enter a valid email address
  </span>
)}
```

**7. Motion and Animation**
```css
/* Respect user preferences */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

**8. Text Alternatives**
```tsx
// All images have alt text
<img src={icon} alt={criterion.title} />

// Decorative images
<img src={decoration} alt="" role="presentation" />

// Icon buttons
<button aria-label="Add to favorites">
  <FontAwesomeIcon icon={faHeart} aria-hidden="true" />
</button>
```

**9. Skip Links**
```tsx
<div className="skip-links">
  <a href="#search" className="skip-link">
    Skip to search
  </a>
  <a href="#filters" className="skip-link">
    Skip to filters
  </a>
  <a href="#main-content" className="skip-link">
    Skip to results
  </a>
</div>
```

**10. Headings and Structure**
```tsx
// Proper heading hierarchy
<h1>WCAG Explorer</h1>
  <h2>Filters</h2>
    <h3>Version</h3>
    <h3>Level</h3>
  <h2>Results</h2>
    <h3>{criterion.title}</h3>
```

**Alternatives Considered:**

### WCAG 2.1 Level AA (Industry Standard)
- **Pros:**
  - Meets legal requirements
  - Achievable for most content
  - Industry standard
  - Widely tested patterns
- **Cons:**
  - Doesn't showcase highest level
  - Misses opportunity to demonstrate AAA
  - Less differentiation from other tools
- **Reason for rejection:** WCAG Explorer should exemplify best practices, not just meet minimums.

### WCAG 2.2 Level AA (Current Standard)
- **Pros:**
  - Most recent standard
  - Includes focus appearance (2.4.11)
  - Dragging movements alternative (2.5.7)
  - Still legally compliant
- **Cons:**
  - Still only AA level
  - Doesn't demonstrate AAA feasibility
- **Reason for rejection:** Same as above - we should exceed standards.

### WCAG 2.1 Level AAA
- **Pros:**
  - Highest level
  - Demonstrates best practices
- **Cons:**
  - Slightly older standard
  - Missing recent criteria
- **Reason for rejection:** WCAG 2.2 is current standard and includes important improvements.

### "Best Effort" Accessibility
- **Pros:**
  - Flexible
  - Pragmatic
  - Can prioritize based on user research
- **Cons:**
  - Vague, not measurable
  - Open to interpretation
  - Doesn't provide clear guidance
- **Reason for rejection:** Need concrete, testable standard. "Best effort" is too subjective.

### Selective AAA Criteria
- **Pros:**
  - Pick achievable AAA criteria
  - More realistic
  - Documents exceptions
- **Cons:**
  - Cherry-picking undermines credibility
  - Unclear which criteria to meet
  - Not a clear commitment
- **Reason for rejection:** While some AAA criteria may be impractical, we should aim for all and document exceptions, not pick and choose upfront.

**Testing Strategy:**

1. **Automated Testing:**
   - axe DevTools in development
   - Lighthouse accessibility audits in CI
   - ESLint jsx-a11y plugin

2. **Manual Testing:**
   - NVDA on Windows
   - JAWS on Windows
   - VoiceOver on macOS/iOS
   - TalkBack on Android

3. **Keyboard Testing:**
   - Navigate entire app with keyboard only
   - Test all interactive elements
   - Verify focus indicators
   - Check tab order

4. **User Testing:**
   - Test with real assistive technology users
   - Gather feedback from disability community
   - Iterate based on findings

**Exceptions (Where AAA May Not Apply):**

Some AAA criteria may not be applicable:
- **2.2.4 Interruptions (AAA):** No interruptions in our app
- **2.2.5 Re-authenticating (AAA):** No authentication yet
- **2.4.9 Link Purpose (Link Only) (AAA):** All links are clear
- **3.1.3 Unusual Words (AAA):** WCAG-specific terminology expected

Where AAA is genuinely not achievable for specific content, we document:
- Which criterion
- Why it's not achievable
- What alternatives we provide

**Notes:**

- This is not about perfection, but about commitment to excellence
- Accessibility is an ongoing process, not a one-time achievement
- Regular testing and user feedback are essential
- The team should continuously learn about accessibility
- WCAG Explorer should be a model for others to follow
- Open-sourcing the code allows others to learn from our implementation
