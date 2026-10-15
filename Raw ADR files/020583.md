# ADR-007: Material Challenges as Embedded Attributes (Hybrid Approach)

**Status**: Accepted (December 16, 2025)  
**Deciders**: System Architect, Todd Dunning  
**Date**: 2025-12-16

## Context

Material challenges (e.g., "High reflectivity", "Thermal shock and microcracking") exist in 153 settings pages with significant reuse patterns:

**Data Analysis**:
- 804 total challenge instances
- 51 unique challenge types
- Top challenges appear in 42 materials (27% reuse rate)
- Challenge details vary by material (e.g., reflectivity ranges: 60-95% for aluminum vs 40-70% for ceramics)

**Question**: Should `challenges` be:
- **Option A**: Separate domain with independent entities (like contaminants)?
- **Option B**: Embedded attributes with no standardization?
- **Option C**: Hybrid approach with embedded data + standardized IDs?

## Decision

**Use Hybrid Approach (Option C): Embedded attributes with standardized `challenge_id` fields.**

### Rationale

**Why NOT a separate domain**:

1. **Challenges are attributes, not entities**
   - Contaminants: "Oil" exists independently and can contaminate many materials ✓
   - Challenges: "High reflectivity" doesn't exist independently—it's a property OF specific materials ✗

2. **Material-specific data cannot be separated**
   - Aluminum: reflectivity 60-95% at 1064nm, melting point 660°C
   - Titanium: reflectivity 40-60% at 1064nm, melting point 1668°C
   - Same challenge name, different values → Must stay embedded

3. **Solutions are contextual**
   - "High reflectivity" solution for metals: Use UV wavelength (355nm)
   - "High reflectivity" solution for ceramics: Increase power density
   - Solutions depend on material category → Cannot be domain-independent

**Why NOT fully embedded without IDs**:

1. **Query requirement**: Need to find all materials with specific challenge
2. **Analytics requirement**: Need to analyze challenge distribution
3. **Standardization**: 42 materials use same challenge names—need consistency

### Implementation

**Data Structure**:
```yaml
challenges:
  thermal_management:
  - challenge: High reflectivity              # Human-readable name
    challenge_id: high_reflectivity           # ← Standardized query ID
    severity: high                            # Material-specific
    reflectivity_range: 60-95% at 1064nm     # Material-specific
    impact: "Most laser energy reflected..."  # Material-specific
    solutions:                                # Material-specific
    - Use shorter wavelengths (355nm UV)
```

**Components Created**:

1. **ChallengeTaxonomy.yaml**: Canonical list of 51 challenge types
   - Location: `data/materials/ChallengeTaxonomy.yaml`
   - Provides: Standardized IDs, descriptions, categories

2. **Exporter Enhancement**: `_enrich_challenges_with_ids()`
   - Location: `export/core/trivial_exporter.py` (line 1645)
   - Converts challenge text → snake_case ID automatically

3. **Query Tool**: Cross-material challenge analysis
   - Location: `scripts/tools/query_challenges.py`
   - Commands: `--stats`, `--list-challenges`, `<challenge_id>`

## Consequences

### Positive

1. **Queryable**: Find all materials with `high_reflectivity` challenge
2. **Material-Specific**: Preserve reflectivity ranges, thresholds, solutions per material
3. **No New Domain**: Avoid complexity of managing separate challenge entities
4. **Standardized**: Consistent IDs enable programmatic access
5. **Scalable**: Adding new challenges = automatic taxonomy update
6. **Analytics-Friendly**: Can analyze challenge distribution, frequency, severity

### Negative

1. **Duplication**: Common challenge text repeated across materials (mitigated by IDs)
2. **Not Fully Normalized**: Some redundancy in challenge descriptions
3. **Update Pattern**: Changing challenge text requires updating all instances (rare operation)

### Neutral

1. **Query performance**: In-memory loading acceptable for 153 materials
2. **Storage overhead**: Minimal (~20KB extra for challenge_id fields)

## Alternatives Considered

### Option A: Separate Challenge Domain

**Structure**:
```yaml
# challenges/Challenges.yaml
challenges:
  high_reflectivity:
    name: "High reflectivity"
    category: surface_characteristics
    materials:
    - aluminum-laser-cleaning:
        severity: high
        reflectivity_range: 60-95%
```

**Rejected Because**:
- ❌ Inverts relationship (challenges own materials, not vice versa)
- ❌ Material-specific data separated from material context
- ❌ Complex to maintain bidirectional links
- ❌ Challenges aren't independent entities

### Option B: Fully Embedded (No Standardization)

**Structure**:
```yaml
challenges:
  thermal_management:
  - challenge: High reflectivity  # No challenge_id
    severity: high
    ...
```

**Rejected Because**:
- ❌ Cannot query "all materials with high reflectivity"
- ❌ No standardization across materials
- ❌ Analytics impossible without text parsing
- ❌ 42 materials using same challenge = need standard ID

## Validation

**Test Coverage**:
```bash
# Verify all challenges have IDs
python3 tests/test_challenge_taxonomy.py
# Result: 804/804 challenges have challenge_id (100%)

# Query all materials with high_reflectivity
python3 scripts/tools/query_challenges.py high_reflectivity
# Result: 42 materials found
```

**Statistics**:
- Materials with challenges: 153/153 (100%)
- Total challenge instances: 804
- Unique challenge types: 51
- Challenges with IDs: 804/804 (100%)

## Related Decisions

- **ADR-006**: ID Normalization (enables consistent challenge_id generation)
- **ADR-008**: Centralized Associations (similar hybrid approach)

## References

- Taxonomy: `data/materials/ChallengeTaxonomy.yaml`
- Exporter: `export/core/trivial_exporter.py` (method: `_enrich_challenges_with_ids`)
- Query tool: `scripts/tools/query_challenges.py`
- Analysis: Session transcript December 16, 2025

## Notes

**Key Insight**: Not everything should be a domain. The decision to keep challenges as material attributes (with queryable IDs) follows the principle: **"Make it a domain only if it has independent existence."**

Challenges don't exist independently—they're properties of materials that vary by material. The hybrid approach provides the best of both worlds: embedded context + query capabilities.

**Future Enhancement**: If challenge management becomes more complex (e.g., recommended solutions become challenge-specific rather than material-specific), reconsider Option A. Current implementation can migrate to full domain if needed.
