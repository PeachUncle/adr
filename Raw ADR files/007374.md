# ADR-006: Naming Strategy for Variables, Functions, and Files

## Status
Accepted

## Context
As CharacterCraft Lite grew beyond a single file, consistent naming became essential for maintainability, clarity, and collaboration.

Inconsistent naming patterns can lead to confusion, bugs, or difficulty onboarding contributors. We needed a strategy that worked across:
- Variable and function names
- File and module naming
- UI element IDs and class names

## Decision
We adopted a **clear, semantically-driven naming strategy**, guided by the following principles:

### General Principles
- **Descriptive over abbreviated**: Prefer `generatePersonality()` over `genPers()`
- **LowerCamelCase** for variables and functions: `generatePrompt()`, `resetForm()`
- **Kebab-case** for filenames and CSS classes: `random-personality.js`, `.btn-copy`
- **Singular names** for utilities and documents (e.g., `generation.js`, not `generations.js`)
- **Plural** only when representing a list or collection (e.g., `coreValues`, `promptTemplates`)

### Folder Naming
- Folders are lowercase, semantic, and pluralized only when referring to sets:
  - `documents/` for markdown content generators
  - `prompts/` for zero-shot prompt logic
  - `data/` for static data like dropdown options or model vocabularies

### HTML + CSS Naming
- ID and `name` attributes use **lowerCamelCase**: `primaryAudience`, `orgName`
- CSS classes use **kebab-case**: `.chip`, `.form-section`, `.btn-generate-prompt`
- Reusable button classes start with `btn-`
- Avoid deep BEM-like naming unless warranted (e.g. no `.form__input--highlighted` unless needed)

## Consequences
✅ Easier to read and navigate codebase
✅ Consistent file and function lookup
✅ Prevents class/id clashes and improves maintainability
⚠️ Slight verbosity compared to abbreviations (intentional)

## Future Considerations
- If SCSS or a component framework is added, revisit naming for components
- Could adopt automated linting or naming conventions in CI if multiple contributors

---

*This strategy prioritizes clarity, simplicity, and predictability across the codebase.*

