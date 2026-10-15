# ADR 0009: Use Jest for Unit Testing

## Status

Accepted

## Context

We need a robust, compatible, and flexible testing framework for writing and running unit tests in our Next.js React app. Key considerations:

- App uses **Next.js with App Router** (not Vite)
- Components are primarily written in **JavaScript** (TypeScript may be introduced later)
- We are focusing on **unit testing**, especially for:
  - React components
  - Utility/helper functions
  - Custom hooks

Options considered:

| Tool                     | Pros                                                     | Cons                                |
| ------------------------ | -------------------------------------------------------- | ----------------------------------- |
| **Jest**                 | Battle-tested, built-in mocking, compatible with Next.js | Slower than lighter test runners    |
| **Vitest**               | Fast, Vite-native, good DX for Vite apps                 | Not officially supported in Next.js |
| **Playwright / Cypress** | Good for e2e and UI flow testing                         | Overhead for simple unit testing    |

## Decision

We chose **[Jest](https://jestjs.io/)** as the unit testing framework for the following reasons:

- Proven compatibility with **Next.js**
- Works well with React and DOM testing via **React Testing Library**
- Built-in support for mocking, spies, and assertions
- Easy integration with CI/CD workflows
- Good ecosystem support (e.g. `jest-stare` for HTML reports)

## Consequences

- Tests will be co-located as `*.test.js` files alongside the code they test (e.g., `src/app/page.test.js`, `src/app/about/page.test.js`), rather than in a separate `__tests__/` directory
- Jest will be run via `npm test` or a custom script (`npm run test:html` for coverage output)
- The test environment will use `jsdom` for browser-like DOM testing
- React Testing Library may be added to facilitate component testing
- End-to-end tests (if needed) will be handled separately using Playwright or Cypress later
- There is an **arbitrary 85%+ test coverage goal** for Jest tests. However, since the project is still in MVP phase (with dummy data and no backend), the site structure is too fluid to justify enforcing strict coverage thresholds in CI/CD at this stage.

## Future Considerations

- Evaluate **Vitest** if project is ever ported to Vite or if test speed becomes a concern
- Consider snapshot testing or test coverage thresholds for mission-critical logic
- As complexity grows, introduce **integration tests** or mock API routes

---

_Created: 2025-06-20_
