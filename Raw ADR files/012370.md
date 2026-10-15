# ADR 0017: Plan to Adopt TypeScript

## Status

Proposed

## Context

The Meatbag project is currently written in JavaScript (ESM modules) using Next.js App Router, React, and vanilla CSS Modules. The project is rapidly iterating on MVP features and UI/UX flows, and architectural decisions are still evolving.

However, long-term maintainability, readability, and tooling support for JavaScript can suffer as the codebase grows and more contributors get involved. TypeScript offers stronger developer ergonomics and more automated documentation opportunities — especially in combination with Docusaurus.

## Decision

We **plan to adopt TypeScript incrementally** in the future.

Reasons for deferring now:

- Time constraints: learning and refactoring would slow MVP delivery
- Focus is currently on UI, UX, auth, and core business logic
- Type safety is helpful but not mission-critical for MVP testing

Reasons for adopting later:

- ✅ Strong static typing improves reliability and developer confidence
- ✅ Enables **Typedoc** integration for auto-generating API documentation in Docusaurus
- ✅ Better IDE support, autocomplete, and refactor tools
- ✅ Makes future contributions safer and less error-prone

## Migration Plan (Later Phase)

- Adopt TypeScript one folder/module at a time (e.g. `/utils`, `/hooks`)
- Rename files: `.js` → `.ts` or `.jsx` → `.tsx`
- Use `@ts-check` with JSDoc as an optional transition bridge
- Leverage `tsconfig.json` with incremental type checking
- Integrate Typedoc CLI to generate `docs/api/` markdown files for Docusaurus

## Consequences

- Current setup remains in JavaScript to maximize velocity
- Future onboarding will need updated tooling (e.g. ESLint for `.ts`, `tsconfig`)
- May require some type modeling for 3rd-party libraries (e.g. NextAuth)

## Future Considerations

- Consider creating a dedicated `typedoc.config.js` and outputting to `/docs/api/`
- Use `dtslint` or strict mode to enforce consistency over time
- Document code migration steps in a `CONTRIBUTING.md` guide
- Align ESLint rules with TypeScript support (`@typescript-eslint`)

---

_Created: 2025-06-20_
