---
category: architectural-decisions
date: 2025-12-19
component: global
severity: critical
tags: [memory, hindsight, architecture, agents, multi-agent]
related_memories: []
---
# Adopt Hindsight as Unified Memory Architecture

TTA.dev adopts Hindsight as the standard memory system for all agents, enabling persistent learning across sessions and knowledge sharing between worktree agents.

## Context

**When:** December 2025
**Where:** TTA.dev agent architecture
**Who:** Core development team
**What:** Establishing a unified memory system for all AI agents

## Decision

Adopt Hindsight as the standard memory architecture for:
- Worktree agents (Copilot, Cline, Augment)
- Sub-agents spawned during workflows
- External integrations with user repositories
- Future TTA.dev distributions

## Rationale

### Problem Statement

Multiple agents working on TTA.dev needed persistent memory but were using incompatible approaches:
- Copilot: `.github/copilot-instructions.md` (static)
- Cline: `.clinerules` (session-scoped)
- Augment: `.augment/memory/` (file-based, isolated)

This led to:
- Repeated mistakes across sessions
- Knowledge not shared between agents
- No semantic search capability
- Inconsistent memory formats

### Alternatives Considered

1. **Agent-specific memory files**
   - Pros: Simple, agent-native
   - Cons: Fragmented, no sharing, no semantic search
   - **Rejected:** Doesn't solve cross-agent sharing

2. **Central database (PostgreSQL/Redis)**
   - Pros: Powerful queries, scalable
   - Cons: Complex setup, overkill for file-based projects
   - **Rejected:** Violates TTA.dev's "zero setup" philosophy

3. **Logseq only**
   - Pros: Rich linking, human-readable, existing system
   - Cons: Hard for programmatic access, not optimized for agents
   - **Rejected:** Complements but doesn't replace agent memory

4. **Hindsight (chosen)**
   - Pros: File-based (git-friendly), semantic search, memory banks, cross-agent sharing
   - Cons: New system to learn, needs integration work

### Why Hindsight

1. **File-based storage** - Git-friendly, works offline, no database setup
2. **Semantic indexing** - Intelligent retrieval beyond keyword search
3. **Memory banks** - Organized by domain (tta-dev, user-repo, session)
4. **Cross-agent sharing** - Unified format all agents can use
5. **Configurable** - YAML config for customization

## Implementation

### Directory Structure

```text
.hindsight/
├── config.yaml           # Configuration
├── banks/                # Memory storage
│   ├── tta-dev/         # TTA.dev patterns
│   ├── user-repo/        # Target repo knowledge
│   └── session/          # Current session
└── templates/            # Memory templates
```

### Integration Points

1. **Worktree agents**: Load tta-dev bank on startup
2. **Sub-agents**: Inherit parent memory scope
3. **User repos**: Index codebase → user-repo bank
4. **Logseq**: Optional sync for human review

### Migration Path

Existing memories in `.augment/memory/` will be migrated to `.hindsight/banks/tta-dev/` with category mapping:
- `implementation-failures/` → `implementation-failures/`
- `successful-patterns/` → `successful-patterns/`
- `architectural-decisions/` → `architectural-decisions/`

## Lesson Learned

Unified memory architecture enables agents to truly learn and collaborate. The key insight is that memory format matters less than having a single source of truth that all agents can access.

### Do

- ✅ Write memories after significant learnings
- ✅ Use the template for consistency
- ✅ Tag generously for retrieval
- ✅ Update existing memories when patterns evolve

### Don't

- ❌ Create agent-specific memory files
- ❌ Skip memory writing for "minor" issues
- ❌ Duplicate existing memories
- ❌ Store session-specific info in persistent banks

## Applicability

**When to Apply:**
- All TTA.dev agent development
- User repository integrations
- Sub-agent orchestration
- Cross-session learning requirements

**When NOT to Apply:**
- Ephemeral one-off tasks
- Non-TTA.dev projects (unless they adopt Hindsight)

## References

- [Hindsight Memory Architecture](../../../docs/agents/HINDSIGHT_MEMORY_ARCHITECTURE.md)
- [AGENTS.md](../../../AGENTS.md)
- [Platform Agent Context](../../../platform/agent-context/)

---

**Created:** 2025-12-19
**Last Updated:** 2025-12-19
**Verified:** [x] Yes
