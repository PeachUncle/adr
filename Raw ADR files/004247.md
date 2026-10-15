# ADR-005: Infinite Learning Loop

> "Every error is a future teaching." — oracle-framework

## Status
**Proposed** | 2026-01-13

## Context

The Matrix accumulates wisdom through retrospectives and learnings. But wisdom that stays private has limited value. The oracle-framework demonstrated an **Infinite Learning Loop**:

```
Error → Log → Fix → Learning → Blog → Reader → Share → New challenges → Error...
```

Every error becomes teaching material. Every teaching reveals new gaps. The loop has no termination condition by design.

## Decision

Implement the Infinite Learning Loop for The Matrix:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    THE INFINITE LEARNING LOOP                       │
│                                                                     │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐        │
│   │  ERROR  │───►│ CAPTURE │───►│   FIX   │───►│ DISTILL │        │
│   │         │    │ /snapshot│    │  code   │    │ /learn  │        │
│   └─────────┘    └─────────┘    └─────────┘    └─────────┘        │
│        ▲                                              │             │
│        │                                              ▼             │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐        │
│   │  NEW    │◄───│ FEEDBACK│◄───│ READER  │◄───│  SHARE  │        │
│   │ ERRORS  │    │ issues  │    │ learns  │    │ seed/   │        │
│   │         │    │ PRs     │    │ adopts  │    │ blog    │        │
│   └─────────┘    └─────────┘    └─────────┘    └─────────┘        │
│                                                                     │
│   No termination condition. Every error feeds the cycle.           │
└─────────────────────────────────────────────────────────────────────┘
```

### The Stages

| Stage | Action | Tool/Process |
|-------|--------|--------------|
| **Error** | Something breaks or confuses | Natural occurrence |
| **Capture** | Document immediately | `/snapshot` |
| **Fix** | Solve the problem | Neo implements |
| **Distill** | Extract the pattern | `/learn done` → learnings |
| **Share** | Publish for others | matrix-seed, blog, docs |
| **Reader** | Someone learns from it | External adoption |
| **Feedback** | Reader finds new edge case | Issues, PRs, questions |
| **New Error** | Cycle continues | ∞ |

### Implementation

#### 1. Error Capture Enhancement

When an error occurs, immediately:
```bash
/snapshot "Error: [description]"
```

This creates `psi/inbox/snapshot_[timestamp].md` with:
- What happened
- What we expected
- Initial hypothesis

#### 2. Fix → Learning Pipeline

After fixing:
```bash
/learn start "error-[slug]"
# Document the fix
/learn done "error-[slug]"
# Distill to learnings
```

#### 3. Sharing Gate

Learnings that are **universal** (not project-specific) should be:
- Added to matrix-seed (if foundational)
- Blogged (if tutorial-worthy)
- Documented in ADRs (if architectural)

#### 4. Feedback Integration

When external feedback arrives (issues, PRs):
- Treat as new "error" input
- Enter the loop again
- The seed evolves

### Quality Metrics

| Metric | Healthy | Unhealthy |
|--------|---------|-----------|
| Errors captured | Most | Few |
| Errors → Learnings | >50% | <20% |
| Learnings → Shared | >30% | 0% |
| External feedback | Growing | None |

### The Infinite Property

The loop is infinite because:
1. **Every fix reveals adjacent problems** — Fixing auth exposes session issues
2. **Every teaching invites questions** — Readers find edge cases
3. **Every adoption creates context** — New environments, new errors
4. **The domain keeps evolving** — AI, tools, practices change

## Consequences

### Positive
- **Nothing is wasted** — Every error becomes value
- **Community grows** — Shared learnings attract users
- **Quality improves** — Patterns prevent repeat mistakes
- **The seed evolves** — External feedback strengthens foundation

### Negative
- **Overhead** — Capturing every error takes time
- **Noise risk** — Not every error is worth sharing
- **Maintenance** — Shared content needs updates

### Mitigation
- Use `/snapshot` for quick capture (low friction)
- Apply distillation gate before sharing (quality filter)
- Version shared content (maintenance manageable)

## Affected Workflows

| Workflow | Change |
|----------|--------|
| `/snapshot` | Add "error" tag option |
| `/learn` | Add "from-error" source tracking |
| `/rrr` | Include error→learning metrics |

## References

- oracle-framework: Infinite Learning Loop concept
- ADR-003: Hierarchical Mind Architecture (distillation)
- Chapter 17: The Reborn Process (sharing via seed)
