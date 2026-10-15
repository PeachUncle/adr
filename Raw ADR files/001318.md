# ADR-020: Accessibility Testing

## Status

Accepted

## Context

Web accessibility is a critical requirement for ensuring that the application
can be used by individuals with disabilities, complying with standards such as
WCAG (Web Content Accessibility Guidelines). Manual accessibility testing is
time-consuming and can be inconsistent across reviewers. Therefore, an automated
solution is needed to catch common accessibility issues early in the development
lifecycle.

To support this goal, we evaluated tools that can programmatically detect
accessibility violations in HTML markup and common UI patterns during
development and testing.

## Decision

We decided to use **axe** as the automated accessibility testing tool for the
project.

## Reasons

1. **Industry Standard and Compliance**:
   - axe is widely adopted and conforms to WCAG 2.1 and Section 508 guidelines,
     ensuring a high standard of accessibility compliance.

2. **Automation-Friendly**:
   - axe can be easily integrated into existing testing environments, including
     browser-based tools, unit tests, and E2E frameworks like Cypress,
     Playwright, and Selenium.

3. **Immediate Feedback for Developers**:
   - With integrations such as `axe-core` and `@axe-core/react`, developers
     receive real-time feedback on accessibility issues while developing or
     running tests.

4. **CI/CD Integration**:
   - Accessibility tests using axe can be added to automated pipelines,
     preventing regressions before deployment.

5. **Developer Tooling**:
   - The axe browser extensions (e.g., for Chrome and Firefox) provide instant
     analysis during manual testing and are helpful for debugging complex
     issues.

6. **Low False-Positive Rate**:
   - axe emphasizes accuracy, minimizing false positives and making its findings
     actionable.

## Consequences

1. **Limited Coverage of Semantic and Contextual Issues**:
   - axe focuses on detectable violations and cannot replace comprehensive
     manual testing, especially for content or UX judgments.

2. **Initial Test Setup Overhead**:
   - Integrating axe into unit or E2E tests requires additional tooling and
     configuration effort.

3. **Training Required**:
   - Developers may need a basic understanding of accessibility standards to
     interpret test results and fix issues appropriately.

## Alternatives Considered

### Pa11y:

- **Pros**: CLI-based, easy to integrate.
- **Cons**: Less comprehensive rule set and community support than axe.

### Lighthouse:

- **Pros**: Provides accessibility scoring along with performance and SEO
  metrics.
- **Cons**: Not suitable for automated testing at scale; primarily used for
  audits.

### Manual Audits Only:

- **Pros**: Context-aware and thorough.
- **Cons**: Time-intensive, subjective, and not scalable or repeatable.
