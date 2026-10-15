# ADR-022: Progressive Disclosure Skills

**Date**: 2025-11-04
**Status**: Accepted
**Priority**: P1

## Context

Skills were growing too large:
- Some SKILL.md files >600 lines
- Workflows embedded in SKILL.md
- Reference materials mixed with instructions
- Token inefficiency (loading everything)

**Example:**
- academic-research: 674 lines (too large)
- knowledge-management: 580 lines (too large)
- All content loaded even when only metadata needed

## Decision

Three-tier skill architecture:

### Tier 1: SKILL.md Core (<180 lines)
**Contents:**
- YAML frontmatter (metadata ~15 lines)
- Core identity and purpose (~30 lines)
- Key capabilities (~40 lines)
- When to use this skill (~30 lines)
- Observable actions (~20 lines)
- Workflow index (pointers, not content) (~20 lines)
- Reference index (pointers, not content) (~15 lines)

**Total:** <180 lines, ~5,000 tokens

### Tier 2: Workflows (On-Demand)
**Location:** `skills/skill-name/workflows/`
**Contents:**
- Step-by-step processes
- Decision trees
- Quality checklists
- Examples

**Loaded:** When workflow explicitly needed

### Tier 3: Reference (Background)
**Location:** `skills/skill-name/reference/`
**Contents:**
- Background theory
- Domain knowledge
- Style guides
- Templates

**Loaded:** When deep context needed

## Results

**Refactored 5 skills:**
- academic-research: 674 → 180 lines (73% reduction)
- knowledge-management: 580 → 150 lines (74% reduction)
- swedish-academic-writing: 480 → 160 lines (67% reduction)
- technical-writing: 388 → 140 lines (64% reduction)
- föreläsning-preparation: 274 → 170 lines (38% reduction)

**Average:** 67% size reduction (2,396 → 800 lines)

## Consequences

**Positive:**
- ✅ 67% size reduction
- ✅ 73% token savings
- ✅ Better maintainability
- ✅ Scalable (can add workflows without bloating SKILL.md)
- ✅ Clear separation of concerns

**Negative:**
- ⚠️ More files to maintain
- ⚠️ Need workflow index in SKILL.md
- ⚠️ Initial refactoring effort

**Trade-offs Accepted:**
Structural complexity worth it for token efficiency and maintainability.

## Pattern

**SKILL.md structure:**
```markdown
---
[YAML frontmatter - Tier 1 metadata]
---

# Core Identity
[Who this skill is, what it does]

# Key Capabilities
[What this skill can help with]

# When to Use
[Triggers and use cases]

# Observable Actions
[What to show when activated]

# Workflows
See workflows/ directory:
- workflow1.md - [one-line description]
- workflow2.md - [one-line description]

# Reference Materials
See reference/ directory:
- reference1.md - [one-line description]
- reference2.md - [one-line description]
```

## Related

- ADR-003 (Skills over commands)
- ADR-011 (Progressive disclosure principle)
- ADR-021 (Memory refactoring - same pattern)

---
