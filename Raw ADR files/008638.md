# 0004 - Consolidate AI Context Files

**Status:** Accepted

**Date:** 2025-11-26

**Deciders:** Marcelo Almeida (repository owner)

## Context

The repository had accumulated multiple AI assistant context files:

- `.github/copilot-instructions.md` - GitHub Copilot instructions (actively used)
- `.claude.md` - Claude-specific context
- `.clinerules` - Cline AI assistant rules
- `.cursorrules` - Cursor AI assistant rules

**Problems:**

1. **Maintenance burden** - Updates needed in multiple places
2. **Drift** - Files became outdated (`.clinerules` and `.cursorrules` still referenced Astro and GitHub Pages instead of Next.js and Vercel)
3. **Inconsistency** - Different files had different (sometimes conflicting) information
4. **Redundancy** - 80%+ content overlap across files

## Decision

Consolidate all AI context into a single source of truth: `.github/copilot-instructions.md`.

**Implementation:**

1. Merge any unique, valuable content from other files into `copilot-instructions.md`
2. Replace `.claude.md`, `.clinerules`, and `.cursorrules` with one-line pointers to the canonical file
3. Keep `copilot-instructions.md` as the single file to maintain

**Why this file?**

- `.github/copilot-instructions.md` is a standard location recognized by GitHub Copilot
- It was already the most current and comprehensive
- The `.github/` directory is a conventional location for repository configuration

## Alternatives Considered

### Option 1: Delete all other files

**Rejected** because some AI tools may specifically look for their named files (`.cursorrules`, `.clinerules`). Having them point to the canonical file ensures those tools can still find context.

### Option 2: Use symlinks

**Rejected** because symlinks don't work well across all platforms (especially Windows) and may not be followed by all AI tools.

### Option 3: Keep all files synchronized via script

**Rejected** because it adds maintenance complexity and build steps. Simpler to have one file and pointers.

## Consequences

**Positive:**

- Single source of truth for AI context
- Easier to keep documentation current
- No more drift between files
- Clear ownership and location

**Negative:**

- AI tools that don't follow the "see file X" instruction may have limited context
- Slightly more friction if a tool specifically requires its named file format

**Mitigations:**

- Keep the pointer files present so tools don't error
- If a specific tool requires different format, create minimal adapter content
