# ADR-001: Flat but Contextual Folder Structure

## Status
Accepted

## Context
As CharacterCraft Lite grew from a single-file prototype to a modular ES6+ project, it became clear that organizing source files would significantly impact maintainability and contributor experience.

The initial structure followed a simple `js/` folder with multiple files. However, as functionality grew (generation, prompts, documents, UI, data), we needed a strategy to group files logically — without introducing excessive depth or fragmentation.

We considered:
- Keeping everything flat in `js/`
- Grouping by layer (e.g. `components/`, `services/`, etc.)
- Grouping by type (e.g. `js/`, `css/`, `data/`)
- Grouping by domain or function (e.g. `documents/`, `prompts/`)

## Decision
We adopted a **flat-but-contextual folder layout**, grouping files by *what they do* rather than *what they are*:

```
src/
├── js/
│   ├── index.js                ← Main entry
│   ├── generation.js           ← Core summary + description logic
│   ├── export.js, utils.js     ← Helper logic
│   ├── random-personality.js   ← Surprise Me! generator
│   ├── data/                   ← Static data (dropdown options, core values)
│   ├── prompts/                ← Zero-shot prompt builders
│   ├── documents/             ← Markdown document generators (RAG docs)
│   ├── ui/                     ← DOM manipulation, nav, modals
```

Key principles:
- Start flat, group only when a **domain emerges**
- Favor **functionality** over file type (e.g., `documents/` instead of `services/`)
- Only create folders when they group **2 or more files**
- Use meaningful, human-readable names (e.g., `prompts/`, not `llm-utils/`)
- Avoid deep nesting unless scaling demands it

## Consequences
✅ Improves navigability — contributors can find files by purpose, not by implementation detail
✅ Reduces friction for simple edits and context switching
✅ Keeps future refactors easier (e.g., migrating `documents/` to an API later)
⚠️ May occasionally cause ambiguity about where new logic should go — this can be resolved via ADRs

## Future Considerations
If CharacterCraft grows significantly, we may later adopt a hybrid or layered architecture (e.g., MVC-style). Until then, this approach balances clarity and simplicity.

We may also revisit:
- Breaking `data/` into separate logical groupings if it grows
- Splitting out shared UI components if needed

---

*This decision supports our philosophy of modern, modular, human-centered architecture.*

*— [Michael Nygard](https://twitter.com/mtnygard)*
