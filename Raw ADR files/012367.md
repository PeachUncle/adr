# ADR 0012: Use ESLint for JavaScript and React Linting

## Status

Accepted

## Context

To maintain code quality, enforce consistent patterns, and catch errors early, we decided to use a static code analysis tool. The project uses JavaScript and React (Next.js App Router), which benefits significantly from real-time linting and formatting.

Options considered:

| Tool       | Pros                                                       | Cons                                  |
| ---------- | ---------------------------------------------------------- | ------------------------------------- |
| **ESLint** | Widely adopted, great plugin ecosystem, fully customizable | Can be verbose without good config    |
| Oxlint     | Fast, emerging Rust-based linter                           | Not mature, lacks React ecosystem yet |
| No linter  | No setup overhead                                          | Code quality and readability degrade  |

## Decision

We chose **[ESLint](https://eslint.org/)** for linting JavaScript and React code, along with:

- **Prettier**: For consistent formatting
- **Husky**: For Git hooks
- **lint-staged**: To run ESLint only on staged files

This ensures:

- Consistent code quality and formatting
- Errors are caught **before commits**
- Fast developer feedback loops

The ESLint configuration includes:

- Base rules from `eslint:recommended`
- React and React Hooks rules
- Integration with Prettier via `eslint-config-prettier` to avoid rule conflicts

Husky is set up with a pre-commit hook:

```json
"husky": {
  "hooks": {
    "pre-commit": "lint-staged"
  }
}
```

## Consequences

- All staged JavaScript and React files are automatically linted before commit
- Code that fails linting cannot be committed (enforced by Husky)
- Consistent formatting is enforced by Prettier
- Developers must install and maintain Husky/lint-staged setup locally
- Linting errors are surfaced quickly, improving code quality

## Future Considerations

- Expand ESLint config as codebase grows (TypeScript, accessibility, etc.)
- Integrate with CI/CD for PR checks
- Add Stylelint for CSS/SCSS linting

---

_Created: 2025-06-20_
