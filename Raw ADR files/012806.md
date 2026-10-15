# ADR-011: Progressive Disclosure with Tier 1 Metadata

**Date**: 2025-11-02
**Status**: Accepted

## Context

Loading all skill instructions on every prompt = token inefficiency. Daniel Miessler's insight: "Progressive disclosure - load metadata first, details on-demand."

## Decision

Three-tier progressive disclosure architecture:

**Tier 1: Metadata (~100 tokens)**
- Always loaded in system prompt
- YAML frontmatter in SKILL.md
- Contains: name, voice, description, triggers, use-when
- Enough for auto-activation decision

**Tier 2: Instructions (~2000 tokens)**
- Loaded on-demand when skill activated
- Core SKILL.md content
- Workflows referenced but not loaded

**Tier 3: Deep Context (~5000+ tokens)**
- Loaded explicitly when needed
- workflows/ files
- reference/ materials
- Examples and templates

**Pattern:**
```markdown
---
name: skill-name
voice: Voice Name
accent: British/Swedish/Neutral
description: One-line description
triggers:
  - keyword1
  - keyword2
use_when: When to activate this skill
capabilities:
  - capability1
  - capability2
---

# Tier 2: Core Instructions

[Main skill content ~2000 tokens]

## Workflows

See workflows/ directory for step-by-step processes.

## Reference

See reference/ directory for background materials.
```

## Consequences

**Positive:**
- ✅ Token efficiency (load only what's needed)
- ✅ Faster context loading
- ✅ Enables auto-activation (Tier 1 is enough)
- ✅ Scalable (can add many skills without bloat)

**Negative:**
- ⚠️ More complex file structure
- ⚠️ Need to maintain YAML frontmatter
- ⚠️ Workflow split across files

**Trade-offs Accepted:**
Token efficiency worth the structural complexity. Better architecture > simpler files.

## Implementation

**Skills refactored:**
- All skills have Tier 1 YAML
- Core instructions in SKILL.md body
- Workflows in workflows/ subdirectory
- Reference materials in reference/ subdirectory

**Hook support:**
- load-ufc-context.ts loads Tier 1 for all skills
- user-prompt-skill-router.ts activates based on Tier 1
- Tier 2/3 loaded when skill actually used

## Related

- ADR-003 (Skills over commands)
- ADR-012 (Proactive activation - depends on Tier 1)
- ADR-022 (Progressive disclosure skills refactoring)

---
