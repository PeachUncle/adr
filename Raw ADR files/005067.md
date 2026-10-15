# ADR-002: Plugin Structure with Skills Subdirectory

**Status:** Accepted
**Date:** 2025-11-19
**Context:** Plugin Marketplace Migration

## Context

We need to migrate from the legacy skill-* directory structure to Claude Code's plugin marketplace format. The repository contains two skills (web-access, kalshi-markets) that need to be packaged as marketplace-installable plugins.

Claude Code expects plugins to follow a specific directory structure, but we also need to maintain backward compatibility during migration and support potential future plugin expansion.

## Decision

We will adopt the following directory structure:

```
plugins/
├── web-access/
│   ├── plugin.json              # Plugin metadata
│   └── skills/
│       └── web-access/
│           ├── SKILL.md         # Skill manifest
│           └── scripts/         # Executable scripts
│               ├── search.py
│               └── fetch.py
└── kalshi-markets/
    ├── plugin.json
    └── skills/
        └── kalshi-markets/
            ├── SKILL.md
            └── scripts/
                ├── market.py
                ├── orderbook.py
                └── ...
```

Each plugin contains:
- `plugin.json` at the plugin root (metadata, versioning, keywords)
- `skills/` subdirectory containing one or more skills
- Each skill has `SKILL.md` (skill manifest) and `scripts/` directory

## Rationale

### Why plugins/ directory?

Claude Code marketplace conventions use `plugins/` as the standard location for installable plugins. This makes the repository immediately recognizable as a plugin source.

### Why skills/ subdirectory within each plugin?

1. **Future Extensibility**: A plugin can contain multiple related skills
   - Example: web-access plugin could have separate skills for search, fetch, and scraping
   - Example: kalshi-markets could split into market-data and trading skills

2. **Clean Separation**: Plugin-level metadata (plugin.json) separated from skill-level manifests (SKILL.md)

3. **Marketplace Compatibility**: Claude Code expects this structure for plugin installation

4. **Logical Organization**: Mirrors the conceptual hierarchy (plugin → skills → scripts)

### Why duplicate plugin and skill names?

For single-skill plugins, the directory structure appears redundant:
- `plugins/web-access/skills/web-access/`

However, this provides:
1. **Consistency**: Same structure whether plugin has 1 or N skills
2. **Clarity**: Explicit distinction between plugin-level and skill-level resources
3. **Future-Proofing**: Adding a second skill doesn't require restructuring

## Alternatives Considered

### Alternative 1: Flat structure (plugins/web-access/SKILL.md)

**Rejected** because:
- Doesn't support multi-skill plugins
- Mixes plugin and skill metadata in the same directory
- Less extensible for future growth
- Doesn't align with Claude Code conventions

### Alternative 2: Keep skill-* structure

**Rejected** because:
- Not compatible with Claude Code marketplace
- Doesn't follow community conventions
- Lacks plugin-level metadata location

### Alternative 3: Monolithic repository structure

**Rejected** because:
- Harder to install individual plugins
- Couples unrelated skills together
- Poor marketplace discoverability

## Implementation

### Migration Path

1. Create new `plugins/` directory structure
2. Copy files from `skill-websearch/` → `plugins/web-access/skills/web-access/`
3. Copy files from `skill-kalshi/` → `plugins/kalshi-markets/skills/kalshi-markets/`
4. Add `plugin.json` manifests for each plugin
5. Update SKILL.md files with 2025 schema (version, allowed-tools)
6. Test all scripts work from new locations
7. Deprecate old `skill-*` directories

### Backward Compatibility

During migration:
- Old `skill-*` directories remain functional
- Scripts use relative paths, so no code changes needed
- UV execution works from any location: `uv run <path>/script.py`

After validation:
- Remove `skill-*` directories
- Update documentation to reference new paths

## Consequences

### Positive

- Marketplace-ready structure
- Clear separation of concerns (plugin vs skill)
- Supports future multi-skill plugins
- Easy to add new plugins without refactoring

### Negative

- Slightly deeper directory nesting
- Apparent redundancy for single-skill plugins (acceptable trade-off)

### Neutral

- Requires migration effort (one-time cost)
- Documentation must be updated

## References

- [Claude Code Plugin Structure](https://code.claude.com/docs/en/plugins)
- [Plugin Marketplace Migration Spec](../specs/plugin-marketplace-migration.md)
