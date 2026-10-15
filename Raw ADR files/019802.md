---
type: adr
id: ADR-002
status: accepted
created: 2024-12-08
modified: 2025-12-13
supersedes: null
superseded_by: null
obsoleted_by: null
related: []
---

# ADR-002: Context Priming System

## Status

Accepted

## Date

2024-12-08

## Context

Claude Code sessions lose context in two scenarios:

1. **New session**: Starting fresh with no project knowledge
2. **Compaction**: Long sessions get compacted, losing earlier context

Users must manually re-explain project structure, conventions, and current work state. This is tedious and error-prone.

## Decision

Implement a layered priming system:

### Full Priming (SessionStart hook)

Automatically runs on session start and after compaction. Outputs:
- All file contents specified in vibe-hacker.json
- Custom instructions from config
- Greenfield mode status

Uses SessionStart hook with `compact` matcher to also trigger after context compaction.

### Manual Priming (/prime command)

User-invoked command for manual re-priming when needed. Same behavior as SessionStart.

### Fallback Chain

If prime.json is missing, gracefully degrade:
```
.claude/prime.json → .claude/CLAUDE.md → README.md → docs/
```

### Configuration Format

Projects configure priming via `.claude/prime.json`:
```json
{
  "files": ["explicit/paths.md"],
  "globs": ["docs/**/*.md"],
  "instructions": "Focus on active action plans"
}
```

## Consequences

**Benefits:**
- Consistent context across sessions
- Project-specific configuration
- Graceful degradation for unconfigured projects
- User control over when full priming occurs

**Costs:**
- Requires project setup (prime.json)
- Full priming consumes context window

**Trade-offs:**
- Full priming on SessionStart consumes context but provides complete context
- Glob support adds complexity but enables dynamic file discovery

## Alternatives Considered

### Light priming on SessionStart

Only show file list on session start, require manual `/prime` for full context.

**Rejected**: Extra friction. Full priming is more useful in practice.

### Hardcoded file list

Always load README.md and docs/ARCHITECTURE.md.

**Rejected**: Not flexible enough. Projects have different structures.

## Open Questions

- Should priming track which files were loaded to avoid duplicates?

## References

- [Claude Code Hooks Guide](https://docs.anthropic.com/claude-code/hooks)
- [Claude Code Commands](https://docs.anthropic.com/claude-code/commands)

---

## Addenda
