# ADR-001: Separation of Themed and Professional Documentation

## Status

Accepted

## Context

Agent Outfitter uses an exploration/expedition theme throughout its internal documentation to create an engaging and memorable experience. However, the fieldguides produced by this system are consumed by external projects where professional, theme-neutral documentation is expected.

Initially, the expedition metaphors were used throughout all documentation, creating potential issues:

- External projects would inherit playful language inappropriate for professional codebases
- AI agents might propagate themed language into serious technical documentation
- Developers might find the metaphors distracting or unprofessional in their projects

## Decision

We will maintain a strict separation between:

1. **Internal Documentation** (expedition-themed)

   - README.md
   - CLAUDE.md
   - Files in `docs/outfitter/`
   - Commit messages for the outfitter system itself
   - PR descriptions for outfitter features

2. **External Documentation** (professional, theme-neutral)
   - All files in `fieldguides/`
   - Any documentation that will be copied to external projects
   - Technical standards and conventions
   - Code examples and templates

## Consequences

### Positive

- Fieldguides remain professional and universally applicable
- External projects receive serious, focused documentation
- The outfitter system maintains its engaging personality where appropriate
- Clear boundaries prevent theme leakage into professional contexts

### Negative

- Contributors must context-switch between writing styles
- Additional cognitive load to remember which style to use
- Risk of accidental theme usage in fieldguides

### Mitigation

- Created `docs/outfitter/LANGUAGE.md` as style guide for internal docs
- Created `fieldguides/standards/documentation.md` for professional standards
- Updated CLAUDE.md with clear guidelines for each context
- Added explicit notes in README.md about theme boundaries

## References

- [Outfitter Language Guide](../../outfitter/LANGUAGE.md)
- [Documentation Standards](../../../fieldguides/standards/documentation.md)
