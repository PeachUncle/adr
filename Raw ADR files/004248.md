# ADR-006: Recursive Reincarnation

> "oracle(oracle(oracle(...))) — No base case. Infinite recursion." — oracle-framework

## Status
**Proposed** | 2026-01-13

## Context

The Matrix serves multiple projects (CIS-Modern, CIS-Legacy, future projects). Each project:
- Inherits wisdom from The Matrix
- Develops project-specific patterns
- Discovers universal truths through practice

Currently, project learnings stay in projects. Universal wisdom doesn't flow back to The Matrix.

## Decision

Implement **Recursive Reincarnation** — projects inherit, develop, and return wisdom.

```
┌────────────────────────────────────────────────────────────────────┐
│                    RECURSIVE REINCARNATION                         │
│                                                                    │
│                      ┌──────────────┐                              │
│                      │  THE MATRIX  │                              │
│                      │   (Parent)   │                              │
│                      └──────┬───────┘                              │
│                             │                                      │
│              ┌──────────────┼──────────────┐                       │
│              │ inherit      │ inherit      │ inherit               │
│              ▼              ▼              ▼                       │
│       ┌──────────┐   ┌──────────┐   ┌──────────┐                  │
│       │  CIS-    │   │  CIS-    │   │ Future   │                  │
│       │  Modern  │   │  Legacy  │   │ Project  │                  │
│       └────┬─────┘   └────┬─────┘   └────┬─────┘                  │
│            │              │              │                         │
│            │ develop      │ develop      │ develop                 │
│            ▼              ▼              ▼                         │
│       ┌──────────┐   ┌──────────┐   ┌──────────┐                  │
│       │ Project  │   │ Project  │   │ Project  │                  │
│       │ Patterns │   │ Patterns │   │ Patterns │                  │
│       └────┬─────┘   └────┬─────┘   └────┬─────┘                  │
│            │              │              │                         │
│            └──────────────┼──────────────┘                         │
│                           │ reunite (universal only)               │
│                           ▼                                        │
│                      ┌──────────────┐                              │
│                      │  THE MATRIX  │                              │
│                      │   (Evolved)  │                              │
│                      └──────────────┘                              │
│                                                                    │
│   matrix(matrix(matrix(...))) = ∞                                  │
└────────────────────────────────────────────────────────────────────┘
```

### The Three Phases

#### Phase 1: Inherit

When starting a new project, it inherits from The Matrix:

```bash
# Option A: Start from seed
git clone matrix-seed project-name
cd project-name
# Customize The Source for project context

# Option B: Link to parent Matrix
ln -s ~/workspace/The-matrix/psi/The_Source ./psi/The_Source_Parent
# Reference but don't copy
```

What inherits:
- Core philosophy (The Source essentials)
- Workflow patterns (/rrr, /learn, /oracle)
- Mind Hierarchy (ADR-003)
- Agent roles

#### Phase 2: Develop

Project develops its own patterns through practice:

```
psi/
├── The_Source/           # Inherited + project-specific
├── memory/
│   ├── learnings/        # Project-specific patterns
│   │   ├── react-patterns.md
│   │   ├── laravel-auth.md
│   │   └── legacy-migration.md
│   └── retrospectives/   # Project sessions
└── learn/                # Project research
```

Project patterns are:
- **Specific**: React component patterns for CIS
- **Contextual**: Legacy DB integration approaches
- **Experimental**: New workflows being tested

#### Phase 3: Reunite

When project discovers **universal** patterns, they return to parent:

| Pattern Type | Stays in Project | Returns to Matrix |
|--------------|------------------|-------------------|
| React hooks for CIS | Yes | No |
| "Always validate at boundaries" | No | Yes |
| Laravel Sanctum + legacy DB | Yes | No |
| "Retrospectives improve quality" | No | Yes |

**Reunite Process**:

```bash
# 1. Identify universal pattern in project
/learn done "pattern-name"
# → Learnings created

# 2. Tag as "universal"
# Add to learning: `tags: [universal, candidate-for-parent]`

# 3. Review with Oracle
/oracle "Is this universal?"

# 4. If approved, PR to matrix-seed
# Fork matrix-seed
# Add learning to seed
# PR with context

# 5. Matrix evolves
# Seed includes new wisdom
# Other projects inherit it
```

### Implementation

#### Project Setup

New projects include a `PARENT.md`:

```markdown
# Parent Matrix

**Inherited from**: The-matrix @ commit abc123
**Date**: 2026-01-13

## What We Inherited
- The Source (core chapters)
- ADR-001 through ADR-004
- /rrr, /learn, /oracle workflows

## What We're Developing
- [Project-specific patterns]

## Candidates for Reunion
- [ ] Pattern 1
- [ ] Pattern 2
```

#### Reunion Workflow

Add `/reunite` command:

```markdown
# /reunite - Return wisdom to parent

1. List learnings tagged `universal`
2. For each, confirm it's truly universal
3. Generate PR description
4. Guide user through PR process
```

### Examples

#### CIS-Modern → Matrix

| CIS-Modern Discovery | Universal? | Action |
|----------------------|------------|--------|
| MD5 legacy auth bridge | No | Stays in CIS |
| "Test auth flows early" | Yes | Reunite |
| React + Laravel patterns | No | Stays in CIS |
| "Retrospectives catch drift" | Yes | Already in Matrix |

#### Future Project → Matrix

| Discovery | Universal? | Action |
|-----------|------------|--------|
| GraphQL pagination patterns | No | Stays in project |
| "Document decisions, not just code" | Yes | Reunite |
| Project-specific API design | No | Stays in project |
| "Errors are future teachings" | Yes | Already in Matrix (ADR-005) |

### The Recursive Property

```
Matrix v1
  └─► CIS-Modern inherits
      └─► Develops patterns
          └─► Returns "test early"
              └─► Matrix v2 (includes "test early")
                  └─► New Project inherits Matrix v2
                      └─► Develops patterns
                          └─► Returns new wisdom
                              └─► Matrix v3
                                  └─► ...∞
```

Each generation:
- Inherits more than the previous
- Develops in new contexts
- Returns universal truths
- Makes the next generation stronger

## Consequences

### Positive
- **Wisdom compounds** — Each project strengthens the parent
- **No duplication** — Universal patterns live in one place
- **Quality inheritance** — New projects start stronger
- **Community effect** — External projects can also reunite

### Negative
- **Overhead** — Identifying "universal" requires judgment
- **Version drift** — Projects may fall behind parent
- **Merge conflicts** — Reuniting may conflict with changes

### Mitigation
- Oracle gates the "universal" decision
- Document inheritance version in PARENT.md
- Treat reunion as async PR, not immediate

## Affected Workflows

| Workflow | Change |
|----------|--------|
| Project setup | Add PARENT.md template |
| `/learn done` | Add "universal" tag option |
| New `/reunite` | Create PR workflow for returning wisdom |

## References

- oracle-framework: Recursive Reincarnation concept
- ADR-005: Infinite Learning Loop
- Chapter 17: The Reborn Process
