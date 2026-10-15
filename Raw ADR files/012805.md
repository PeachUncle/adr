# ADR-008: Project-Local .claude/ Must Be Minimal

**Date**: 2025-11-02
**Status**: Accepted

## Context

Initial project setup copied entire PAI structure (agents/, hooks/, skills/, settings.json) into project directory at `/path/to/project/.claude/`. This created conflicts:
- Hooks loading from wrong location
- Settings duplicated
- Confusion about "source of truth"
- Maintenance nightmare (changes needed in 2 places)

## Decision

Project-local `.claude/` directory must be MINIMAL:

**ONLY allowed in project `.claude/`:**
```
project/.claude/
├── claude.md → ../CLAUDE.md (symlink to root CLAUDE.md)
└── settings.local.json (optional - project-specific permissions)
```

**NEVER copy to project `.claude/`:**
- ❌ agents/ (use global from ~/.claude/)
- ❌ hooks/ (use global)
- ❌ skills/ (use global)
- ❌ settings.json (use global)
- ❌ PAI infrastructure

**UFC Layer 4 Pattern:**
```
project/
├── CLAUDE.md (project instructions, root level)
└── .claude/
    └── claude.md → ../CLAUDE.md (symlink for safety)
```

## Rationale

**Single Source of Truth:**
- Global PAI lives in `~/.claude/`
- Projects reference global via Claude Code's loading mechanism
- No duplication = no conflicts

**Project CLAUDE.md at root:**
- More discoverable (visible in file tree)
- Standard pattern (like README.md)
- Easier to edit

**Symlink safety net:**
- If Claude Code looks in `.claude/` directory
- Symlink ensures it finds instructions
- Layer 4 enforcement

## Consequences

**Positive:**
- ✅ Single source of truth (no hook conflicts)
- ✅ Easier maintenance (one place to update)
- ✅ No confusion about which settings apply
- ✅ Cleaner project structure

**Negative:**
- ⚠️ Need to create symlink for each project
- ⚠️ settings.local.json less discoverable

**Trade-offs Accepted:**
Small symlink effort worth it to avoid duplication/conflicts.

## Migration

**If project has full PAI copy:**
1. Backup project `.claude/` directory
2. Delete all except settings.local.json (if needed)
3. Create symlink: `cd project/.claude && ln -s ../CLAUDE.md claude.md`
4. Verify hooks load from global location
5. Test project still works

## Related

- ADR-001 (UFC System - this is Layer 4)
- UFC.md documentation

---
