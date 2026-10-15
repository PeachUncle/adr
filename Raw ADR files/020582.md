# ADR-006: Universal ID Normalization to Slug Format

**Status**: Accepted (December 14, 2025)  
**Deciders**: System Architect, Todd Dunning  
**Date**: 2025-12-14

## Context

Prior to December 2025, the system had inconsistent ID formats across different data sources:

- **Materials.yaml**: Used title case display names as dictionary keys (`"Aluminum"`, `"Stainless Steel"`)
- **Contaminants.yaml**: Used kebab-case IDs (`"carbon-buildup"`, `"adhesive-residue"`)
- **Frontmatter files**: Used kebab-case with suffixes (`aluminum-laser-cleaning.yaml`, `carbon-buildup-contamination.yaml`)

This inconsistency created three problems:

1. **Data Access Confusion**: Code needed to know whether to use display name or slug ID
2. **Filename Mismatches**: Dictionary keys didn't match frontmatter filenames
3. **Duplicate Suffix Bug**: Exporter re-slugified IDs, creating double suffixes (`aluminum-laser-cleaning-laser-cleaning.yaml`)

## Decision

**Normalize all IDs across the entire system to slug format (kebab-case).**

### Implementation Details

**Materials Domain:**
- Dictionary keys: `Aluminum` → `aluminum-laser-cleaning`
- Pattern: `{material_slug}-laser-cleaning`
- Examples: `aluminum-laser-cleaning`, `stainless-steel-316-laser-cleaning`

**Contaminants Domain:**
- Dictionary keys: `carbon-buildup` → `carbon-buildup-contamination`
- Pattern: `{contaminant_slug}-contamination`
- Examples: `carbon-buildup-contamination`, `oil-contamination`

**Settings Domain:**
- Uses material base slug + `-settings`
- Pattern: `{material_slug}-settings`
- Examples: `aluminum-settings`, `stainless-steel-316-settings`

### Migration Executed

**Script**: `scripts/data/migrate_ids_to_slugs.py`
- Backed up all YAML files before migration
- Migrated 153 materials + 98 contaminants = 251 IDs total
- Atomic operation with rollback capability

**Results**:
- ✅ 100% ID consistency achieved
- ✅ Filename = Data ID = Frontmatter ID (1:1 correspondence)
- ✅ Zero duplicate suffix bugs after exporter fixes

## Consequences

### Positive

1. **Single Source of Truth**: ID exists in exactly one format everywhere
2. **Predictable Filenames**: `data[id]` directly maps to `{id}.yaml`
3. **Simplified Code**: No need for slug conversion in lookups
4. **Zero Ambiguity**: Display names are separate from IDs
5. **Scalable**: Adding new materials = add with slug ID, export automatically works

### Negative

1. **Breaking Change**: Code that used display names for lookups needed updates
2. **Migration Required**: All 251 existing entries needed one-time migration
3. **Longer IDs**: `aluminum-laser-cleaning` vs `Aluminum` (more characters)

### Neutral

1. **Display names preserved**: Stored separately in `name` field
2. **Backward compatibility broken**: Old code using display names won't work
3. **One-time cost**: Migration was 2 hours of work but permanent benefit

## Validation

**Test Coverage**:
```bash
# Verify all frontmatter filenames match data IDs
python3 tests/test_id_normalization.py
# Result: 251/251 IDs match (100%)
```

**Deployment Validation**:
```bash
# Full export with new IDs
python3 scripts/operations/deploy_all.py
# Result: 424 files exported successfully
```

## Related Decisions

- **ADR-008**: Centralized Associations (depends on consistent IDs)
- **ADR-009**: Domain Linkages (uses normalized IDs for cross-references)

## References

- Implementation: `scripts/data/migrate_ids_to_slugs.py`
- Exporter fixes: `export/core/trivial_exporter.py` (lines 718, 891, 971, 1010)
- Migration report: `ID_MIGRATION_DEC14_2025.md`
- Deployment: `scripts/operations/deploy_all.py`

## Notes

This decision established the foundation for all subsequent architectural improvements in December 2025, including centralized associations, domain linkages, and challenge taxonomy. Without ID normalization, none of these systems would work reliably.

**Key Learning**: Consistency in identifiers is more valuable than brevity. The longer slug IDs (`aluminum-laser-cleaning`) provide clarity and uniqueness that short IDs (`aluminum`) cannot guarantee across domains.
