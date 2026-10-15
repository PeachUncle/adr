# ADR-0012: Unified Plugin Configuration System

**Status:** Accepted
**Date:** 2025-01-09
**Accepted:** 2025-01-10
**Deciders:** Jace Babin
**Tags:** configuration, plugins, architecture

## Context

We need a configuration system for super-claude plugins that allows users to:

1. **Enable/disable features** - Skills, hooks, and other plugin components
2. **Customize behavior** - Protected branches, allowed branch prefixes, etc.
3. **Override defaults** - Project-specific settings without modifying plugin code

### Current State

**Skills:**

- Use `plugins/*/skill-rules.json` for auto-activation triggers
- Works well, already shipping

**Hooks:**

- Attempted `customHooks` in `.claude/settings.json` (rejected by schema validation)
- Currently only environment variables: `CLAUDE_HOOK_*_ENABLED=false`
- Hardcoded behavior (protected branches, branch prefixes, etc.)
- No user-friendly way to customize

### The Problem

1. **Claude Code's settings.json doesn't support custom fields** - Schema validation rejects unknown properties
2. **Environment variables are clunky** - Hard to discover, not version-controllable, not user-friendly
3. **Hardcoded values are inflexible** - Users can't customize protected branches, branch naming conventions, etc.
4. **Inconsistent configuration** - Skills use JSON files, hooks use env vars

### Requirements

1. **User-friendly** - Config files visible in project, easy to edit
2. **Discoverable** - Clear where to find and how to use
3. **Version-controllable** - Team can share configuration
4. **Flexible** - Support project-specific overrides
5. **Backwards-compatible** - Don't break existing users
6. **Minimal complexity** - Don't over-engineer

## Decision

We will create a **unified configuration system** using `super-claude-config.json`:

### File Structure

**Plugin defaults** (one per plugin, shipped with marketplace):

```txt
plugins/workflow/super-claude-config.json
plugins/meta/super-claude-config.json
plugins/design-system/super-claude-config.json
```

**Project overrides** (one file total, in user's project):

```txt
.claude/super-claude-config.json
```

### Configuration Schema

**Plugin-level** (`plugins/workflow/super-claude-config.json`):

```json
{
  "plugin": "workflow",
  "skills": {
    "skill-name": {
      "triggers": {
        "keywords": ["keyword1"],
        "patterns": ["pattern1"]
      }
    }
  },
  "hooks": {
    "gitCommitGuard": {
      "enabled": true,
      "protectedBranches": ["main", "master"]
    },
    "branchNameValidator": {
      "enabled": true,
      "allowedPrefixes": [
        "feat",
        "fix",
        "chore",
        "docs",
        "test",
        "refactor",
        "perf",
        "build",
        "ci",
        "revert",
        "style"
      ],
      "allowedBranches": ["main", "master", "develop"]
    },
    "typeChecker": {
      "enabled": true,
      "timeout": 2000
    }
  }
}
```

**Project-level** (`.claude/super-claude-config.json`):

```json
{
  "workflow": {
    "hooks": {
      "gitCommitGuard": {
        "enabled": false
      },
      "branchNameValidator": {
        "allowedPrefixes": ["feat", "fix", "bugfix"],
        "allowedBranches": ["main", "production", "staging"]
      }
    },
    "skills": {
      "skill-name": {
        "enabled": false
      }
    }
  },
  "meta": {
    "skills": {
      "skill-creator": {
        "enabled": false
      }
    }
  }
}
```

### Loading Priority

1. **Plugin defaults** - `plugins/{plugin}/super-claude-config.json`
2. **Project overrides** - `.claude/super-claude-config.json` (merged by plugin name)
3. **Environment variables** - `CLAUDE_HOOK_*_ENABLED` (highest priority)

Deep merge strategy: Project overrides replace individual fields, not entire sections.

### Migration Path

1. **Rename** `skill-rules.json` → `super-claude-config.json` in each plugin
2. **Add** `skills` wrapper around existing content
3. **Add** `hooks` section with defaults
4. **Support** both filenames during transition (backwards compatible)
5. **Update** skill-activation hook to read new format
6. **Update** hook config-loader to read new format
7. **Deprecation notice** in docs for `skill-rules.json`

## Consequences

### Positive

- ✅ **User-friendly** - Config files are visible, editable, version-controllable
- ✅ **Discoverable** - One file per plugin in marketplace, one file in user project
- ✅ **Flexible** - Users can customize behavior without forking
- ✅ **Consistent** - Skills and hooks use same configuration system
- ✅ **Extensible** - Can add more sections later (commands, agents, etc.)
- ✅ **Backwards-compatible** - Environment variables still work (highest priority)

### Negative

- ❌ **Migration effort** - Need to update skill-activation hook and config-loader
- ❌ **More files** - Users have another config file to understand
- ❌ **Merge complexity** - Deep merge logic between defaults and overrides
- ❌ **Validation needed** - Schema validation to prevent invalid configs

### Neutral

- 🔄 **One config per plugin** - More files in marketplace, but clearer ownership
- 🔄 **One override file** - Centralized in `.claude/`, organized by plugin name

## Implementation Notes

1. **Create shared config loader** - `utils/super-claude-config-loader.ts`
2. **Add JSON schema** - `.claude-plugin/super-claude-config.schema.json`
3. **Update hooks** - Use config loader instead of hardcoded values
4. **Update skills** - Migrate from skill-rules.json reader
5. **Add validation** - Pre-commit hook to validate config files
6. **Document** - Clear examples in README and plugin docs

## Alternatives Considered

### Alternative 1: Environment Variables Only

- **Rejected:** Clunky, not discoverable, not version-controllable

### Alternative 2: Per-Hook Config Files (`.claude/hooks/*.json`)

- **Rejected:** Too many files, harder to manage

### Alternative 3: Extend Claude Code's settings.json

- **Rejected:** Schema validation rejects custom fields

### Alternative 4: Keep skill-rules.json, add separate hooks-config.json

- **Rejected:** Inconsistent, two files for similar purposes

### Alternative 5: Use plugin.json for config

- **Rejected:** Mixing manifest with configuration, might conflict with Claude Code schema

## Related Decisions

- [ADR-0007: Skill Auto-Activation](./ADR-0007-skill-auto-activation.md) - skill-rules.json origin
- [ADR-0010: Hook Type Selection](./ADR-0010-hook-type-selection.md) - Why we use command hooks

## References

- OpenSpec Proposal: `openspec/changes/unified-plugin-config/`
- JSON Schema: `.claude-plugin/super-claude-config.schema.json`
- Migration Guide: `docs/guides/config-migration.md` (to be created)
