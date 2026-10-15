# ADR 0014: Plan to Integrate CSS Linting with Stylelint

## Status

Proposed

## Context

We are currently using ESLint + Prettier + Husky + lint-staged to ensure code quality for JavaScript and React files. However, our **CSS (global and module-based)** styles are not yet linted in any automated way.

Linting CSS will help:

- Catch invalid syntax and bugs in stylesheets
- Enforce consistent patterns and naming
- Align component styles with accessibility and maintainability standards

Options considered:

| Tool          | Pros                                             | Cons                                           |
| ------------- | ------------------------------------------------ | ---------------------------------------------- |
| **Stylelint** | Mature, widely supported, great plugin ecosystem | Additional config required for CSS Modules     |
| Oxlint        | Blazing-fast Rust-based tool (early stage)       | Not yet feature complete, limited CSSM support |
| No linter     | No overhead                                      | Risk of style inconsistencies and regressions  |

## Decision

We plan to use **[Stylelint](https://stylelint.io/)** with the following goals:

- Lint both global CSS (`app/globals.css`) and `.module.css` files
- Extendable ruleset for Next.js best practices
- Integrated with Husky/lint-staged to block commits on CSS issues
- Eventually included in GitHub Actions CI checks

### Configuration Goals

- `stylelint-config-standard` as base config
- Support for `postcss`, CSS Modules, and nesting
- Extend with plugins as needed:
  - `stylelint-config-recommended`
  - `stylelint-config-css-modules`
  - `stylelint-order` (for property ordering)
- Optional: Define naming patterns for class names and selectors

### Example `stylelint.config.js` (to be added)

```js
module.exports = {
  extends: ['stylelint-config-standard', 'stylelint-config-css-modules'],
  rules: {
    'at-rule-no-unknown': [true, { ignoreAtRules: ['tailwind'] }],
    'selector-class-pattern': '^[a-z][a-zA-Z0-9]+$', // camelCase for CSS Modules
  },
};
```

## Consequences

- CSS issues will be caught before commit (once integrated with Husky/lint-staged)
- Consistent, maintainable styles across global and module CSS
- Slight increase in setup and config complexity

## Future Considerations

- Add Stylelint config and scripts to repo
- Integrate with CI/CD for PR checks
- Explore additional plugins for SCSS, accessibility, or custom rules as needed

---

_Created: 2025-06-20_
