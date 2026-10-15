---
type: adr
id: ADR-001
status: accepted
created: 2024-12-08
modified: '2025-12-15'
supersedes: null
superseded_by: null
obsoleted_by: null
related: []
---

# ADR-001: Greenfield Mode for Prototype Projects

## Status

Accepted

## Date

2024-12-08

## Context

When working on new/prototype projects with Claude Code, a common problem occurs: Claude tends to add backwards-compatibility code even when there are no users to be backwards-compatible with. This manifests as:

- Deprecation comments (`// deprecated: use newMethod()`)
- Re-exporting removed types for compatibility
- Renaming unused variables with `_` prefix instead of deleting
- Documenting "the old way" in migration guides
- Keeping old implementations "for reference"

This cruft creates confusion in greenfield projects where there is no "old way" and no users to migrate.

## Decision

Implement a multi-layered "Greenfield Mode" in the plugin:

1. **CLAUDE.md directive**: Project-level instructions stating the project is greenfield
2. **PostToolUse hook**: Quick regex check on edited files for legacy patterns
3. **Stop hook (Haiku)**: LLM review of session for greenfield violations

The Stop hook uses a prompt-based approach with Haiku to review Claude's work and warn about violations, rather than blocking. This provides feedback without interrupting flow.

We explicitly chose NOT to use UserPromptSubmit for constant reminders, as this was deemed too noisy during brainstorming sessions.

## Consequences

**Benefits:**
- Claude receives clear guidance that backwards compatibility is unwanted
- Violations are caught and flagged before they accumulate
- Warn-only mode allows iteration without blocking
- Haiku review catches semantic violations that regex misses

**Costs:**
- Small latency from Stop hook Haiku call (~500ms)
- May produce false positives on legitimate comments containing "deprecated"

**Trade-offs:**
- Chose warn-only over blocking for initial implementation
- Chose Stop hook over UserPromptSubmit for less noise
- Chose Haiku review over regex-only for better semantic understanding

## Alternatives Considered

### Constant UserPromptSubmit reminders

Inject greenfield reminder on every prompt.

**Rejected**: Too noisy during brainstorming. Claude tunes out constant reminders.

### Blocking on detection

Block Claude from finishing if violations detected.

**Rejected for now**: Too aggressive for initial implementation. Can be enabled later.

### Regex-only detection

Use only pattern matching without LLM review.

**Rejected as sole approach**: Regex catches obvious patterns but misses semantic violations. Kept regex for PostToolUse (fast), added Haiku for Stop (thorough).

## Open Questions

- Should violations accumulate and block after N warnings?
- Should there be a per-file allowlist for legitimate deprecation comments?

## References

- [Claude Code Hooks Guide](https://docs.anthropic.com/claude-code/hooks)

---

## Addenda
### 2025-12-13: v0.2.0 Migration Test

This addendum was added to test the append functionality on locked documents.
### 2025-12-15: v2 Validation Test

This addendum confirms the append workflow works correctly for locked documents.
