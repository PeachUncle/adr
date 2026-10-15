# ADR-002: Gematria and Normalization Rules

## Status

Accepted

## Context

The project requires consistent and accurate Hebrew text processing for gematria calculations. Hebrew text can have multiple representations due to Unicode normalization, diacritical marks, and textual variants. Inconsistent processing would lead to unreliable gematria calculations and difficulty matching identical concepts across different text sources.

## Decision

Establish standardized Hebrew normalization and gematria calculation rules:
1. **Normalization**: NFKD → strip combining → strip maqaf (U+05BE) / sof pasuq (U+05C3) / punctuation → NFC
2. **Gematria Method**: Mispar Hechrachi (finals = regular letters)
3. **Calculation**: Surface-form gematria with preserved calculation strings
4. **Variants**: **Ketiv primary** (written form is primary for gematria calculations); variants recorded with variant_type and span information

### Ketiv-Primary Policy (Numeric SSOT)

**Ketiv (written form) is the primary source for gematria calculations.** This is the numeric SSOT (Single Source of Truth) for all gematria values.

- **Ketiv** (כתיב): The written form in the Masoretic text is stored in the `surface` field and used for all gematria calculations
- **Qere** (קרי): The read form (when different from Ketiv) is recorded as a variant in `variant_surface` and is **not** used for gematria calculations
- **Rationale**: The written text (Ketiv) is the canonical form preserved in manuscripts; gematria calculations must be consistent and reproducible based on the written form

**Rejected Alternative: Qere-First Policy**

A Qere-first policy (where the read form would be primary for gematria) was considered but **explicitly rejected** for this implementation:
- **Rejection Date**: Phase 2 (2025-01)
- **Reason**: Ketiv represents the canonical written text; gematria calculations must be based on the preserved manuscript form, not the vocalized reading tradition
- **Status**: This alternative is archived, not active policy. Any future reconsideration would require a new ADR superseding this decision.

## Rationale

- **Consistency**: Standardized normalization ensures identical text produces identical results
- **Accuracy**: Proper Unicode handling prevents calculation errors from diacritical marks
- **Completeness**: Surface-form calculation includes all visible characters
- **Flexibility**: Variant tracking supports different textual traditions
- **Auditability**: Preserved calculation strings enable verification and debugging

## Alternatives Considered

1. **NFC Only**: Simple Unicode normalization
   - Pros: Simpler implementation
   - Cons: Leaves diacritical marks that affect gematria, inconsistent across systems

2. **NFD Normalization**: Canonical decomposition
   - Pros: Consistent decomposition
   - Cons: Separates characters that should be treated as units in gematria

3. **Mispar Gadol**: Different gematria method (finals = 500+)
   - Pros: Alternative tradition
   - Cons: Less common, would create inconsistency with traditional calculations

## Consequences

### Implementation Requirements
- Implement Unicode normalization pipeline
- Create gematria calculation functions with preserved calculation strings
- Add variant detection and recording logic
- Update all Hebrew text processing to use standardized rules

### Positive Outcomes
- Reliable and reproducible gematria calculations
- Consistent text matching across different sources
- Support for scholarly textual analysis
- Clear audit trail for calculation verification

### Risks and Mitigations
- **Performance**: Unicode processing overhead (mitigated by caching normalized forms)
- **Complexity**: Multiple normalization steps (mitigated by utility functions)
- **Maintenance**: Unicode standard evolution (mitigated by versioned normalization rules)
