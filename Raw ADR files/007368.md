# ADR-000: Use of Architecture Decision Records (ADRs)

## Status
Accepted

## Context
As the CharacterCraft Lite (formerly PersonaMate) project evolves, a number of technical, structural, and philosophical decisions have been made regarding its architecture, file organization, tooling, and overall direction. These decisions are often the result of careful reasoning, trade-offs, and long-term vision — but without proper documentation, the “why” behind them may be lost over time.

To preserve this knowledge and provide clarity for future contributors (including our future selves), we have decided to adopt **Architecture Decision Records (ADRs)**.

## Decision
We will document significant technical and design decisions as ADRs, stored in the `docs/adr/` folder.

Each ADR will:
- Be numbered sequentially starting at `000`
- Be a standalone Markdown file with a clear title and rationale
- Follow a consistent format including: `Status`, `Context`, `Decision`, and `Consequences`

The ADRs will focus on **key trade-offs and justifications**, such as:
- Folder structure and naming conventions
- Build tools and bundling strategies
- Data structure choices (e.g., dictionaries vs. conditionals)
- PWA vs. Electron decisions
- Frontend/backend separation strategies

## Consequences
- Project decisions become traceable and transparent
- Contributors can onboard faster with historical reasoning
- Refactoring discussions can reference documented intent
- Future changes can cite and update past decisions

## Format Template
```markdown
# ADR-XYZ: <Short Descriptive Title>

## Status
Proposed | Accepted | Deprecated | Superseded by ADR-###

## Context
Explain the background and reasoning behind the decision. What was the situation or challenge?

## Decision
Describe what choice was made and why it was chosen over alternatives.

## Consequences
Describe the effects of the decision — both positive and negative.
```

## Notes
- ADRs are **living documents** — they can be revised or deprecated if the project evolves
- Inspired by [Michael Nygard’s ADR pattern](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- This is meant to **support** the README, project philosophy, and CONTRIBUTING guide, not replace them

---

*“Decisions are part of the architecture. Let’s write them down.”*

*— [Michael Nygard](https://twitter.com/mtnygard)*
