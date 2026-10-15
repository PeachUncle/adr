# ADR-006: Display Format Strategy

**Date**: 2025-12-29
**Feature**: 003-view-tasks
**Status**: Accepted

## Context

Need to display task information in a readable, formatted way for the `list` command. Need to decide on output structure, status indicators, and summary statistics.

## Decision

Simple list with status indicators as specified in spec.md.

## Details

### Options Considered

1. **Simple list with status indicators** (chosen)
   - Pros: Clean, readable, matches spec exactly, easy to parse visually
   - Cons: Less structured than table format for programmatic use (not a requirement)

2. **Table-based format with columns**
   - Pros: Structured, aligns columns
   - Cons: Requires fixed-width fonts, harder to wrap long text, more complex

3. **JSON output option**
   - Pros: Machine-readable, useful for scripting
   - Cons: Adds complexity, not in requirements, violates simplicity principle

### Implementation

```
TODO LIST:
────────────────────────────────────
[1] ✗ Buy groceries
    Milk, eggs, bread

[2] ✓ Call dentist
    Schedule appointment

Total: 2 tasks (1 completed, 1 pending)
```

### Components

| Component | Format |
|-----------|--------|
| Header | `TODO LIST:` |
| Divider | `────────────────────────────────────` |
| Task | `[ID] SYMBOL Title\n    Description` |
| Summary | `Total: N tasks (X completed, Y pending)` |

### Status Symbols

| Status | Symbol | Unicode |
|--------|--------|---------|
| complete | ✓ | U+2713 |
| incomplete | ✗ | U+2717 |

## Rationale

- Matches the CLI interface examples in spec.md exactly
- Readable for human users (primary target)
- Easy to implement with existing Python string formatting
- Status symbols (✓/✗) provide quick visual scanning
- Summary statistics at bottom provide quick overview

## Consequences

- **Positive**: Simple, clean output that meets user needs
- **Positive**: No external dependencies
- **Neutral**: Not machine-readable (not a requirement)
