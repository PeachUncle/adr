# ADR-002: Accessibility and Semantic HTML Guidelines

## Status

Accepted

## Context

Accessibility (a11y) and semantic HTML are critical for creating inclusive web experiences. Without strict guidelines and enforcement, accessibility issues can be introduced that exclude users with disabilities. Additionally, semantic HTML improves SEO, maintainability, and overall code quality.

The project needs:
- Consistent accessibility standards across all code
- Automated enforcement of a11y rules
- Clear guidelines for AI agents and developers
- Semantic HTML structure for better SEO and maintainability

## Decision

We will enforce strict accessibility and semantic HTML guidelines throughout the codebase:

### 1. Automated Linting with BiomeJS

- Enable all a11y rules at error level in BiomeJS
- Rules include: `useKeyWithClickEvents`, `useKeyWithMouseEvents`, `useValidAnchor`, `useValidAriaProps`, `useValidAriaValues`, `useValidLang`, `useFocusableInteractiveElements`, `useSemanticElements`
- All a11y violations will block commits via pre-commit hooks

### 2. Semantic HTML Requirements

- Use semantic HTML elements: `<header>`, `<nav>`, `<main>`, `<article>`, `<section>`, `<aside>`, `<footer>`
- Maintain proper heading hierarchy (h1 → h2 → h3, no skipping levels)
- Use appropriate semantic elements for content structure
- Avoid generic `<div>` and `<span>` when semantic alternatives exist

### 3. Accessibility Requirements

- **Images**: All images must have descriptive `alt` attributes
- **Forms**: All form inputs must have associated `<label>` elements
- **Interactive Elements**: All interactive elements must be keyboard accessible
- **ARIA**: Use ARIA attributes when semantic HTML is insufficient
- **Keyboard Navigation**: Ensure all functionality is accessible via keyboard
- **Focus Management**: Proper focus indicators and logical tab order
- **Color Contrast**: Ensure sufficient color contrast (enforced via design system)

### 4. Documentation

- Comprehensive guidelines in `AGENTS.md` for AI agents
- ADR documentation for architectural decisions
- Examples and best practices included in documentation

## Consequences

### Positive

- **Inclusive Design**: All users, including those with disabilities, can access the site
- **Better SEO**: Semantic HTML improves search engine understanding
- **Maintainability**: Semantic HTML makes code more readable and maintainable
- **Legal Compliance**: Reduces risk of accessibility-related legal issues
- **Automated Enforcement**: Pre-commit hooks prevent accessibility regressions
- **Consistent Standards**: All code follows the same accessibility guidelines

### Negative

- **Development Time**: May require additional time to implement accessibility features
- **Learning Curve**: Team members need to understand a11y best practices
- **Stricter Linting**: More linting errors that must be resolved before committing
- **Potential Overhead**: Some features may require more complex implementations to be accessible

### Mitigation

- Provide clear documentation and examples in `AGENTS.md`
- Use component library (DaisyUI) that follows accessibility standards
- Regular code reviews focused on accessibility
- Automated tools catch issues early in development

## Guidelines for Implementation

### Semantic HTML Elements

```html
<!-- Good: Semantic structure -->
<header>
  <nav>
    <ul>
      <li><a href="/">Home</a></li>
    </ul>
  </nav>
</header>
<main>
  <article>
    <h1>Article Title</h1>
    <section>
      <h2>Section Title</h2>
      <p>Content</p>
    </section>
  </article>
</main>
<footer>Footer content</footer>

<!-- Bad: Generic divs -->
<div class="header">
  <div class="nav">
    <div class="link">Home</div>
  </div>
</div>
```

### Accessibility Examples

```html
<!-- Good: Accessible image -->
<img src="photo.jpg" alt="A person reading a book in a library" />

<!-- Bad: Missing alt text -->
<img src="photo.jpg" />

<!-- Good: Accessible form -->
<label for="email">Email Address</label>
<input type="email" id="email" name="email" required />

<!-- Bad: Missing label -->
<input type="email" name="email" />

<!-- Good: Keyboard accessible button -->
<button type="button" onclick="handleClick()">Click me</button>

<!-- Bad: Non-interactive element with click -->
<div onclick="handleClick()">Click me</div>
```

### Heading Hierarchy

```html
<!-- Good: Proper hierarchy -->
<h1>Main Title</h1>
<h2>Section Title</h2>
<h3>Subsection Title</h3>

<!-- Bad: Skipping levels -->
<h1>Main Title</h1>
<h3>Subsection Title</h3> <!-- Missing h2 -->
```

## References

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [MDN Semantic HTML](https://developer.mozilla.org/en-US/docs/Glossary/Semantics#semantic_elements)
- [BiomeJS A11y Rules](https://biomejs.dev/linter/rules/#a11y)

