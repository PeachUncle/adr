# ADR-021: Memory System Refactoring

**Date**: 2025-11-04
**Status**: Accepted
**Priority**: P1

## Context

**Problem:**
- learnings.md: 127KB, 3,314 lines, 36,655 tokens (exceeds 25,000 Read limit)
- decisions.md: 58KB, 1,787 lines (~20,000 tokens, approaching limit)
- Cannot read learnings.md in single operation
- Violates progressive disclosure principle
- Growing daily - problem worsens over time

**UFC Philosophy Violation:**
> "The file system IS the context system. Keep it organized, keep it clean, keep it powerful."

## Decision

Refactor memory system using **chronological archiving** + **categorical organization** + **progressive disclosure**.

### Three-Tier Architecture

**Tier 1: Current & Active (Always Loadable)**
```
context/memory/
├── learnings.md                    # CURRENT MONTH ONLY (~500 lines, <10KB)
├── decisions/INDEX.md              # All ADRs metadata (~2KB)
└── analysis/INDEX.md               # All analyses metadata (~2KB)
```
Total: <15KB, <5,000 tokens

**Tier 2: Archived & Historical (On-Demand)**
```
context/memory/
├── learnings-archive/
│   ├── INDEX.md
│   ├── 2025-11.md
│   └── 2025-10.md
├── decisions/
│   ├── active/
│   ├── superseded/
│   └── deprecated/
└── analysis/
    ├── incidents/
    └── [topic-specific analyses]
```

**Tier 3: Deep Context (Explicit Load)**
Full ADR content, full month learnings, full analyses - only when needed.

## Implementation

**Phase 1: Learnings Archive**
1. Create learnings-archive/ directory
2. Extract entries by month
3. Create INDEX.md with summaries
4. Keep only current month in learnings.md

**Phase 2: Decisions Refactoring**
1. Create decisions/ with active/superseded/deprecated/
2. Extract each ADR to individual file
3. Create INDEX.md with Tier 1 metadata
4. Delete monolithic decisions.md

**Phase 3: Analysis Consolidation**
1. Create analysis/ directory
2. Consolidate analysis files
3. Create INDEX.md
4. Move incidents to incidents/ subdirectory

## Consequences

**Positive:**
- ✅ Context efficiency (can read learnings.md now)
- ✅ Progressive disclosure (Tier 1 → 2 → 3)
- ✅ Maintainability (small files)
- ✅ Scalability (monthly archives)
- ✅ Searchability (INDEX.md files)
- ✅ 84% reduction in primary learnings file

**Negative:**
- ⚠️ Migration effort (~20 hours)
- ⚠️ Monthly maintenance required
- ⚠️ More directories to understand

**Trade-offs Accepted:**
Migration and maintenance worth it for context window efficiency and scalability.

## Success Metrics

**File Sizes:**
- learnings.md: 127KB → <20KB (84% reduction)
- decisions/INDEX.md: <5KB
- analysis/INDEX.md: <3KB
- No single file >20KB in memory/

**Context Loading:**
- Target: Load all Tier 1 in <2s
- Current: Cannot load learnings.md at all ❌
- Goal: <2s for all Tier 1 ✅

## Maintenance

**Monthly (1st of each month):**
- Archive last month from learnings.md
- Update learnings-archive/INDEX.md
- Keep only current month in learnings.md

**Quarterly:**
- Review active ADRs
- Move superseded to superseded/
- Update INDEX.md files

## Related

- ADR-001 (UFC System)
- ADR-011 (Progressive Disclosure)
- This template is result of ADR-021

---
