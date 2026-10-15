# ADR-003: Adoption of Modern JavaScript (ES6+ Modules)

## Status
Accepted

## Context
CharacterCraft Lite was originally built as a single HTML file with embedded `<script>` tags using older JavaScript practices (function declarations in the global scope, no imports/exports). While this was effective for rapid prototyping, it introduced several maintainability and scalability issues:

- Global scope pollution and name collisions
- Difficulty tracing dependencies
- Repetitive code and tight coupling between components
- Impossible to tree-shake or split code logically

As the project evolved into a modular tool with exportable functionality and optional backend/API support, we decided to upgrade the codebase to follow **modern JavaScript practices** using ES6+ features.

## Decision
We transitioned the codebase to **ECMAScript Modules (ES6+)** with the following changes:

- Converted all files to use `export`/`import` syntax
- Migrated from global function declarations to scoped modules
- Split logic into meaningful files (e.g., `utils.js`, `generation.js`, `documents/*.js`, etc.)
- Defined a clear `index.js` as the application entry point

This required updating all HTML references to use:
```html
<script type="module" src="js/index.js"></script>
```

And ensured our build tool (Parcel) supports bundling these modules into standalone or PWA versions.

## Consequences
✅ Improves code maintainability and separation of concerns
✅ Enables bundling, optimization, and tree-shaking
✅ Aligns with modern web standards and future-proofing
✅ Supports use of advanced tooling and frameworks (e.g. PWA, SaaS API integration)
⚠️ Requires a local server or bundler for development (modules can’t be loaded via `file://` due to CORS)
⚠️ Adds minor complexity for beginners unfamiliar with import/export

## Alternatives Considered
- Keeping everything in a single `<script>` block — simpler but limits scale
- Using CommonJS (`require`) — non-browser native and less future-proof

## Future Considerations
- Exporting certain modules (e.g. `documents/`) for reuse in a backend SaaS implementation
- Potential support for import maps or dynamic imports for advanced workflows
- Continued modular structure even if the app evolves into a microfrontend or plugin-based tool

---

*This supports our philosophy of modern, modular, and transparent code architecture.*

