# ADR-008: Centralized Domain Associations

**Status**: Accepted (December 14, 2025)  
**Deciders**: System Architect, Todd Dunning  
**Date**: 2025-12-14

## Context

Prior to December 2025, domain relationships (materials ↔ contaminants) were managed in two problematic ways:

**Problem 1: Manual Hardcoded Scripts**
- User manually maintained linkage scripts per material
- Each script: ~50-100 lines of hardcoded contaminant lists
- Required manual updates when adding materials/contaminants
- Zero consistency checking

**Problem 2: Scattered Data**
- Associations existed in Materials.yaml, Contaminants.yaml, manual scripts
- No single source of truth
- Impossible to validate bidirectional consistency
- Cannot query "all materials affected by rust"

**Scale**:
- 153 materials × 98 contaminants = 15,000+ potential relationships
- Actual relationships: ~2,040 (13% density)
- Manual management: unsustainable

## Decision

**Create centralized association management with automated extraction and validation.**

### Architecture Components

**1. ExtractedLinkages.yaml** (Single Source of Truth)
- Location: `data/associations/ExtractedLinkages.yaml`
- Size: 499KB (2,040 associations)
- Structure:
  ```yaml
  material_to_contaminant:
    aluminum-laser-cleaning:
    - contaminant_id: rust-contamination
      frequency: common
      severity: moderate
      typical_context: general
  
  contaminant_to_material:
    rust-contamination:
    - material_id: aluminum-laser-cleaning
      frequency: common
      severity: moderate
      typical_context: general
  ```

**2. DomainAssociationsValidator** (Centralized Logic)
- Location: `shared/validators/domain_associations_validator.py`
- Size: 1,040 lines
- Responsibilities:
  - Load and cache ExtractedLinkages.yaml
  - Provide `get_related_contaminants(material_id)`
  - Provide `get_related_materials(contaminant_id)`
  - Validate bidirectional consistency
  - Ensure required metadata (frequency, severity, context)

**3. Extraction Script** (Automated Updates)
- Location: `scripts/data/extract_existing_linkages.py`
- Scans: Materials.yaml, Contaminants.yaml
- Extracts: All `applied_to`, `compatible_materials` fields
- Generates: Bidirectional associations automatically
- Validates: No orphaned references

### Integration

**All 3 Exporters Use Same Validator**:
```python
from shared.validators.domain_associations_validator import DomainAssociationsValidator

validator = DomainAssociationsValidator()
related_contaminants = validator.get_related_contaminants(material_id)
related_materials = validator.get_related_materials(contaminant_id)
```

**Frontmatter Structure** (Consistent Everywhere):
```yaml
relationships:
  related_contaminants:  # In materials/settings pages
  - id: rust-contamination
    title: Rust
    url: /contaminants/rust-contamination
    image: /images/contaminants/rust.jpg
    frequency: common
    severity: moderate
    typical_context: general
  
  related_materials:  # In contaminant pages
  - id: aluminum-laser-cleaning
    title: Aluminum
    url: /materials/aluminum
    image: /images/materials/aluminum.jpg
    frequency: common
    severity: moderate
    typical_context: general
```

## Consequences

### Positive

1. **Single Source of Truth**: 2,040 associations in one file
2. **Automated Extraction**: No manual script maintenance
3. **Bidirectional Consistency**: Materials ↔ Contaminants validated automatically
4. **100% Coverage**: All 404 pages (materials + settings + contaminants) have relationships
5. **Queryable**: Find all materials for contaminant, all contaminants for material
6. **Reusable**: Same validator used by all 3 exporters
7. **Maintainable**: Add material → run extraction → associations auto-updated

### Negative

1. **Build Step Required**: Must run extraction after data changes
2. **File Size**: ExtractedLinkages.yaml is 499KB (acceptable)
3. **Cache Management**: Validator caches data (must reload on changes)

### Neutral

1. **Extraction Time**: ~5 seconds for 251 items
2. **Memory Usage**: 499KB loaded in memory (negligible)

## Alternatives Considered

### Option A: Keep Manual Scripts

**Structure**: Individual scripts per material
```python
# scripts/linkages/aluminum_linkages.py
contaminants = [
    {"id": "rust", "frequency": "common"},
    {"id": "oil", "frequency": "common"},
    # ... 20 more hardcoded entries
]
```

**Rejected Because**:
- ❌ 153 materials × ~50 lines = 7,650 lines of duplicated code
- ❌ Zero consistency validation
- ❌ Manual updates required for every change
- ❌ Cannot query relationships programmatically
- ❌ Impossible to maintain bidirectional consistency

### Option B: Embed in Exporters

**Structure**: Each exporter hardcodes association logic
```python
# In trivial_exporter.py
def get_related_contaminants(material):
    if material.category == "metal":
        return ["rust", "oil", "grease"]
    # ... hundreds of lines of logic
```

**Rejected Because**:
- ❌ Duplication across 3 exporters
- ❌ Logic mixed with export code
- ❌ Cannot test associations independently
- ❌ No single source of truth

### Option C: Database

**Structure**: SQLite or PostgreSQL with relationships table

**Rejected Because**:
- ❌ Overkill for 2,040 static relationships
- ❌ Adds deployment complexity
- ❌ YAML files work perfectly for this scale
- ❌ Lose git diff visibility

## Validation

**Test Coverage**:
```bash
# Verify all pages have relationships
python3 tests/test_centralized_architecture.py
# Result: 404/404 pages (100%)

# Verify bidirectional consistency
python3 tests/test_domain_associations_validator.py
# Result: 2,040/2,040 associations valid (100%)
```

**Coverage Statistics**:
- Materials with linkages: 153/153 (100%)
- Settings with linkages: 153/153 (100%)
- Contaminants with linkages: 98/98 (100%)
- Total domain_linkage entries: 2,887
- Entries with severity field: 2,887/2,887 (100%)

## Migration Path

**Phase 1: Extraction** (December 14, 2025)
```bash
python3 scripts/data/extract_existing_linkages.py
# Generated: ExtractedLinkages.yaml with 2,040 associations
```

**Phase 2: Validator Creation** (December 14, 2025)
- Created DomainAssociationsValidator (1,040 lines)
- Added caching, validation, query methods
- Created comprehensive test suite (17 tests)

**Phase 3: Exporter Integration** (December 14, 2025)
- Updated TrivialFrontmatterExporter
- Updated ContaminantsExporter
- Updated CompoundsExporter
- All use same validator instance

**Phase 4: Deployment** (December 16, 2025)
```bash
python3 scripts/operations/deploy_all.py
# Exported 424 files with centralized associations
```

## Related Decisions

- **ADR-006**: ID Normalization (enables consistent association keys)
- **ADR-009**: Domain Linkages (uses centralized associations)
- **ADR-007**: Challenge Hybrid Approach (similar centralization pattern)

## References

- Associations: `data/associations/ExtractedLinkages.yaml`
- Validator: `shared/validators/domain_associations_validator.py`
- Extraction: `scripts/data/extract_existing_linkages.py`
- Tests: `tests/test_centralized_architecture.py`
- Session: `CATEGORIZATION_INFRASTRUCTURE_COMPLETE_DEC14_2025.md`

## Notes

**Key Principle**: "Centralize what varies together, separate what changes independently."

Domain associations change together (adding a material affects multiple contaminant relationships). Centralizing them in one file with one validator ensures consistency and maintainability.

**Future Enhancement**: If relationships become more complex (e.g., severity varies by context, not just material/contaminant pair), consider adding context-specific association files. Current implementation supports up to ~10,000 associations before performance concerns arise.

**Lessons Learned**:
1. Single source of truth > manual scripts (even if extraction required)
2. Centralized validation catches errors early (found 0 bidirectional inconsistencies)
3. YAML works well for this scale (499KB loads in <1ms)
4. Reusable validator = zero exporter duplication
