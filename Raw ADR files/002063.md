# Architecture Decision Record: LCHO Dataset Integration and Peer Isolation

**ADR Number:** 002  
**Date:** October 2025  
**Status:** Implemented  
**Authors:** TS  

## Title
Integration of LCHO Dataset with Automatic Detection and Peer Group Isolation

## Context

The initial HAILIE Insights Engine was designed for LCRA (Low Cost Rental Accommodation) providers processing the government's TSM 2024 dataset. However, the complete government dataset includes two distinct provider types:

- **LCRA Providers:** 355 traditional social housing organizations with rental properties
- **LCHO Providers:** 56 organizations offering Low Cost Home Ownership (shared ownership/affordable purchase)

These provider types have fundamentally different business models and customer relationships:
- LCRA providers maintain rental properties and handle repairs directly
- LCHO providers sell partial ownership, with owners responsible for repairs

This difference is reflected in the TSM measures:
- LCRA providers report on all 12 TSM measures (TP01-TP12)
- LCHO providers only report on 9 measures (TP01, TP05-TP12), as repairs metrics (TP02-TP04) don't apply

## Decision

We implemented dataset separation with automatic detection:

1. **Separate Analytics Pipelines:** LCRA and LCHO data processed independently
2. **Automatic Provider Detection:** System identifies provider type from dataset
3. **Isolated Peer Comparisons:** Rankings calculated only within same provider type
4. **Unified Interface:** Single dropdown with all providers, transparent dataset handling
5. **Clear Visual Communication:** Dashboard indicates which peer group is being compared

## Rationale

### 1. Statistical Validity
- Comparing LCRA to LCHO providers would be meaningless due to different service models
- Percentile rankings only make sense within homogeneous peer groups
- Correlations between measures differ between provider types

### 2. User Experience
- Automatic detection removes complexity from user interaction
- Single interface maintains simplicity while ensuring accuracy
- Clear labeling prevents misinterpretation of peer comparisons

### 3. Data Integrity
- Missing LCHO measures (TP02-TP04) require different data structures
- Separate processing prevents null value propagation
- Dataset isolation ensures calculation accuracy

### 4. Regulatory Compliance
- Government dataset explicitly separates these provider types
- Maintaining separation aligns with regulatory reporting requirements
- Ensures comparisons match government's own analytical approach

## Alternatives Considered

### Alternative 1: Mixed Provider Comparison
**Approach:** Combine all 411 providers into single peer group  
**Pros:** Simpler implementation, larger comparison pool  
**Cons:** Statistically invalid comparisons, misleading rankings  
**Rejected:** Violates fundamental requirement for meaningful peer comparison

### Alternative 2: Manual Dataset Selection
**Approach:** User explicitly selects LCRA or LCHO before choosing provider  
**Pros:** Makes dataset separation explicit  
**Cons:** Adds friction, requires user knowledge of provider types  
**Rejected:** Unnecessary complexity when automatic detection is reliable

### Alternative 3: Separate Applications
**Approach:** Build two distinct applications for LCRA and LCHO  
**Pros:** Complete isolation, specialized interfaces  
**Cons:** Code duplication, maintenance overhead, deployment complexity  
**Rejected:** Over-engineering for a difference that only affects data layer

### Alternative 4: Interpolate Missing LCHO Measures
**Approach:** Use statistical methods to estimate TP02-TP04 for LCHO providers  
**Pros:** Creates complete dataset for all providers  
**Cons:** Introduces artificial data, violates data integrity principles  
**Rejected:** Would create misleading metrics for non-existent services

## Implementation Details

### Database Schema Enhancement
```sql
-- Added dataset_type column to distinguish providers
ALTER TABLE raw_scores ADD COLUMN dataset_type VARCHAR;  -- 'LCRA' or 'LCHO'

-- Separate percentile calculation tables
CREATE TABLE calculated_percentiles_lcra AS ...
CREATE TABLE calculated_percentiles_lcho AS ...
```

### ETL Pipeline Changes
1. **Provider Classification:** Table_Coverage sheet identifies provider type
2. **Conditional Processing:** Different column mappings for LCRA vs LCHO
3. **Separate Calculations:** Percentiles computed within dataset boundaries
4. **Validation Rules:** LCHO records with TP02-TP04 trigger warnings

### Application Layer Modifications
- `EnhancedTSMDataProcessor`: Automatic dataset detection from provider code
- `TSMAnalytics`: Dataset-aware ranking calculations
- `ExecutiveDashboard`: Visual indicators for peer group context

## Consequences

### Positive Consequences
✅ **Accurate Comparisons:** Rankings reflect true peer performance  
✅ **Data Integrity:** No mixing of incompatible provider types  
✅ **User Simplicity:** Automatic handling requires no user expertise  
✅ **Regulatory Alignment:** Matches government's analytical approach  
✅ **Extensibility:** Framework supports future provider types  

### Negative Consequences
❌ **Increased Complexity:** Dual processing paths in codebase  
❌ **Storage Overhead:** Separate tables for each dataset type  
❌ **Testing Burden:** Must validate both LCRA and LCHO paths  
❌ **Documentation Need:** Requires clear explanation of dataset differences  

### Neutral Consequences
➖ **Performance Impact:** Negligible with pre-calculated approach  
➖ **User Education:** Some users may not understand dataset separation  
➖ **Future Migrations:** Adding provider types requires ETL updates  

## Validation

The implementation was validated through:
- Processing all 411 providers (355 LCRA + 56 LCHO) successfully
- Confirming LCHO providers show no TP02-TP04 data
- Verifying rankings calculated only within dataset boundaries
- Testing automatic provider type detection accuracy

## Monitoring and Metrics

### Success Metrics
- Zero cross-dataset comparisons in production
- 100% accurate provider type detection
- No null value errors from missing LCHO measures

### Quality Indicators
- LCRA percentiles calculated from 355-provider pool
- LCHO percentiles calculated from 56-provider pool
- Clear visual indication of comparison group on dashboard

## Migration Path

For existing users of version 1.0 (LCRA-only):
1. Database rebuild with `build_analytics_db_v2.py`
2. Automatic migration of existing LCRA providers
3. Addition of 56 LCHO providers to selection
4. No breaking changes to existing functionality

## Lessons Learned

1. **Dataset Heterogeneity:** Government datasets may contain fundamentally different entity types requiring careful separation
2. **Automatic Detection:** When reliable, automatic detection provides better UX than manual selection
3. **Peer Group Integrity:** Statistical comparisons require homogeneous populations
4. **Visual Communication:** Clear labeling prevents misinterpretation when multiple datasets exist
5. **Extensibility Planning:** Design for multiple provider types even if starting with one

## Future Considerations

### Potential Enhancements
- Cross-dataset insights (where meaningful)
- Provider type conversion tracking (LCRA → LCHO transitions)
- Weighted comparisons for providers with both models
- Custom peer group definitions within dataset types

### Risk Mitigation
- Monitor for providers switching between LCRA/LCHO
- Validate dataset classifications in annual updates
- Maintain clear documentation of dataset differences

## References

- UK Government TSM Technical Guidance 2024
- Dataset source: 2024_TSM_Full_Data_v1.1_FINAL.xlsx
- Implementation PR: Enhanced Data Processor with LCRA/LCHO Support