---
type: adr
id: ADR-003
status: accepted
created: 2024-12-09
modified: 2025-12-13
supersedes: null
superseded_by: null
obsoleted_by: null
related: []
---

# ADR-003: Hybrid Bash/Python for Plugin Scripts

## Status

Accepted

## Date

2024-12-09

## Context

The vibe-hacker plugin requires scripts for various automation tasks:
- Hook scripts (legacy cruft detection, protected paths enforcement)
- Planning workflows (document creation, archiving, listing)
- Context priming

We need to choose a scripting approach that balances simplicity, maintainability, and capability.

## Decision

Use a **hybrid approach**: Bash for simple operations, Python for complex text processing.

**Use Bash when:**
- Simple file operations (move, copy, check existence)
- Pipeline processing and tool composition
- JSON handling with jq
- Quick checks with grep/sed
- Scripts that primarily call other tools

**Use Python when:**
- Parsing or modifying markdown content (frontmatter, status sections)
- Template rendering with multiple variables
- Complex string manipulation
- Operations that need proper error handling and validation
- Scripts likely to grow in complexity

**Current allocation:**
| Script | Language | Rationale |
|--------|----------|-----------|
| prime.sh | Bash | File listing, jq for JSON config |
| check-legacy-cruft.sh | Bash | Grep patterns, simple detection |
| check-protected-paths.sh | Bash | Pattern matching, jq for config |
| planning/new.py | Python | Template rendering, auto-numbering |
| planning/archive.py | Python | Markdown parsing, status updates |
| planning/list.py | Python | Markdown parsing, status extraction |

## Consequences

**Benefits:**
- Right tool for the job - simpler scripts stay simple
- Python scripts are easier to test and maintain as they grow
- Bash scripts remain readable and Unix-idiomatic
- No heavy dependencies (Python 3 is ubiquitous)

**Costs:**
- Two languages in the codebase
- Contributors need familiarity with both
- Slightly inconsistent patterns between scripts

**Trade-offs:**
- Chose pragmatism over purity
- Markdown parsing in bash is possible but painful - Python is worth it there
- Could revisit if maintenance burden becomes an issue

## Alternatives Considered

### All Bash

Use bash for everything, including planning scripts.

**Rejected**: Parsing markdown to update status sections is awkward. Template rendering with multiple variables is error-prone. Maintenance cost would exceed the benefit of consistency.

### All Python

Use Python for all scripts, including simple hooks.

**Rejected**: Overkill for simple pattern matching. Adds startup overhead. Existing bash scripts work fine and are more Unix-idiomatic for their purpose.

### Node.js / Deno

Use JavaScript runtime for scripts.

**Rejected**: Adds heavier runtime dependency. No significant advantage over Python for this use case. Team more familiar with Python.

## Open Questions

None.

## References

- [FDP-002: Protected Paths System](../feature-designs/FDP-002-protected-paths.md) - Uses bash for hook scripts
- Plugin scripts in `scripts/` directory

---

## Addenda
