# ADR 008: Settings Data Loader Architecture Migration

**Date**: December 20, 2025  
**Status**: In Progress  
**Decision Makers**: AI Assistant  
**Context**: Cleanup and consolidation initiative

---

## Context

Two settings data loaders exist in `domains/settings/`:
1. **data_loader.py** (legacy) - Function-based, 140 lines
2. **data_loader_v2.py** (new) - Class-based, 230 lines, created Dec 11, 2025

## Analysis

### Current Usage

**data_loader.py** (9 active imports):
- `domains/data_orchestrator.py` - orchestration layer
- `domains/materials/data_loader.py` - materials domain
- Self-references in docstrings

**data_loader_v2.py** (3 active imports):
- `shared/data/loader.py` - new shared loader
- `tests/test_settings_loader_v2.py` - test suite
- Self-reference in docstring

### Key Differences

| Feature | data_loader.py | data_loader_v2.py |
|---------|---------------|-------------------|
| Architecture | Function-based | Class-based (BaseDataLoader) |
| Caching | @lru_cache | CacheManager |
| File I/O | Direct yaml.safe_load | shared.utils.file_io |
| Validation | Minimal | Fail-fast BaseDataLoader |
| Created | Earlier architecture | Dec 11, 2025 refactor |

## Decision

**KEEP BOTH during migration period.**

### Rationale

1. **Active Migration**: v2 created 9 days ago as part of architecture refactor
2. **No Breaking Changes**: v2 maintains backward compatibility with v1 API
3. **Different Consumers**: Legacy code uses functions, new code uses classes
4. **Safe Migration Path**: Gradual adoption reduces risk

### Migration Strategy

**Phase 1** (Current - Q1 2026):
- Both loaders coexist
- New code uses `SettingsDataLoader` (v2)
- Legacy code continues using `load_settings_yaml()` (v1)

**Phase 2** (Q1 2026):
- Migrate high-value consumers to v2:
  - `domains/data_orchestrator.py`
  - `domains/materials/data_loader.py`
- Add deprecation warnings to v1 functions

**Phase 3** (Q2 2026):
- Remove data_loader.py after all consumers migrated
- Rename data_loader_v2.py → data_loader.py

## Consequences

### Positive
- No immediate breaking changes
- Gradual migration reduces risk
- New architecture benefits (caching, validation) available immediately
- Clear migration timeline

### Negative
- Temporary code duplication (~370 lines total)
- Two import paths for same functionality
- Requires developer awareness of preferred approach

## Compliance

✅ Follows copilot-instructions.md Rule #1: Preserve working code  
✅ Follows copilot-instructions.md Rule #4: Respect existing patterns  
✅ Documents decision (no confusion about "why two loaders?")

## Next Steps

1. Add comment in data_loader.py pointing to this ADR
2. Update documentation to recommend v2 for new code
3. Create migration tracking issue
4. Schedule Phase 2 review for Q1 2026

---

**Related**:
- `domains/settings/data_loader.py` - Legacy loader
- `domains/settings/data_loader_v2.py` - New architecture loader
- `shared/data/base_loader.py` - Base class for v2
