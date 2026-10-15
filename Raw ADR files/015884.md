# ADR-005: Accessibility Tooling

## Status

Accepted

## Context

Rule Bound has a **non-negotiable requirement**: WCAG 2.1 AA compliance. Accessibility must be:

- Verified during development
- Tested in CI/CD
- Monitored in production (or at least pre-deployment)
- Part of the developer workflow

Key accessibility requirements:

- Screen reader compatibility
- Keyboard navigation
- Sufficient color contrast (4.5:1 for normal text, 3:1 for large text)
- Proper ARIA labels and roles
- Focus management
- Responsive text sizing
- Touch target sizes (44x44px minimum on mobile)

We need tooling that:

1. Catches accessibility issues during development
2. Runs automated tests in CI
3. Provides actionable feedback
4. Integrates well with React + TypeScript
5. Doesn't significantly slow down development

## Options Considered

### 1. ESLint Plugin (eslint-plugin-jsx-a11y)

- **Pros:**
  - Catches issues at write-time in the editor
  - Fast feedback
  - No runtime cost
  - Integrates with existing ESLint setup
  - Widely used
- **Cons:**
  - Static analysis only (can't catch runtime issues)
  - Some false positives/negatives

### 2. axe-core (Runtime Testing)

- **Pros:**
  - Industry-standard accessibility engine
  - Comprehensive rule set
  - Can test dynamic content
  - Used by many companies
- **Cons:**
  - Runtime only (not compile-time)
  - Needs to be integrated into test suite

### 3. React Testing Library + jest-axe

- **Pros:**
  - Tests accessibility in component tests
  - Integrates with existing test setup (Vitest)
  - Encourages accessible patterns
- **Cons:**
  - Only runs in tests (not during development)

### 4. Storybook + a11y addon

- **Pros:**
  - Visual component development
  - Interactive accessibility testing
  - Great for design review
- **Cons:**
  - Additional tooling overhead
  - Storybook setup required
  - May be overkill for initial setup

### 5. Manual Testing

- **Pros:**
  - Most comprehensive
  - Catches real user issues
- **Cons:**
  - Time-consuming
  - Not automated
  - Human error

## Decision

We will use a **multi-layer approach** combining multiple tools:

1. **eslint-plugin-jsx-a11y**: Development-time linting
2. **@axe-core/react**: Development-time runtime checks (dev mode only)
3. **jest-axe** (vitest-axe): Automated accessibility tests
4. **Manual testing guidelines**: For comprehensive validation

**Key reasons:**

1. **Defense in Depth**: Multiple layers catch different types of issues
2. **Fast Feedback**: ESLint catches issues immediately in editor
3. **Comprehensive**: Runtime + static analysis covers more ground
4. **CI Integration**: Automated tests ensure compliance
5. **Developer Experience**: Tools integrate seamlessly into existing workflow
6. **Industry Standard**: These are proven, widely-used tools

## Consequences

### Positive

- Accessibility issues caught early (during coding)
- Automated testing prevents regressions
- Fast feedback loop in development
- Comprehensive coverage (static + runtime + tests)
- Enforces accessibility best practices
- Low performance impact (dev-mode only checks)

### Negative

- Multiple tools to configure and maintain
- Some false positives from ESLint rules (can be tuned)
- Developers need to learn accessibility best practices

### Neutral

- Will have ESLint rules that must be followed
- CI pipeline will include accessibility tests
- Some accessibility issues still require manual testing (e.g., screen reader flow)

### Implementation Plan

#### 1. ESLint Configuration

```json
{
  "extends": ["plugin:jsx-a11y/recommended"],
  "rules": {
    "jsx-a11y/anchor-is-valid": "error",
    "jsx-a11y/alt-text": "error",
    "jsx-a11y/aria-props": "error",
    "jsx-a11y/aria-proptypes": "error",
    "jsx-a11y/aria-role": "error",
    "jsx-a11y/heading-has-content": "error",
    "jsx-a11y/label-has-associated-control": "error",
    "jsx-a11y/no-autofocus": "warn"
  }
}
```

#### 2. Runtime Development Checks

Install `@axe-core/react` and configure in main app entry (dev mode only):

```typescript
if (import.meta.env.DEV) {
  import("@axe-core/react").then((axe) => {
    axe.default(React, ReactDOM, 1000);
  });
}
```

#### 3. Automated Testing

Use `vitest-axe` in component tests:

```typescript
import { axe, toHaveNoViolations } from 'vitest-axe';

expect.extend(toHaveNoViolations);

it('should have no accessibility violations', async () => {
  const { container } = render(<Component />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

#### 4. Manual Testing Guidelines

Document in project docs:

- Keyboard navigation testing
- Screen reader testing (NVDA/JAWS/VoiceOver)
- Color contrast verification
- Touch target size verification on mobile
- Focus management testing

#### 5. CI Integration

Add to pre-push checks:

- ESLint runs (includes jsx-a11y rules)
- All tests run (includes axe tests)
- No accessibility violations allowed

### Accessibility Checklist

Every component must:

- [ ] Pass ESLint jsx-a11y rules
- [ ] Pass axe automated tests
- [ ] Have proper ARIA labels where needed
- [ ] Support keyboard navigation
- [ ] Have sufficient color contrast
- [ ] Work with screen readers (manual test)
- [ ] Have touch targets ≥44x44px on mobile

### Resources for Developers

- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)
- [eslint-plugin-jsx-a11y rules](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y)
- [axe-core rule descriptions](https://github.com/dequelabs/axe-core/blob/develop/doc/rule-descriptions.md)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
