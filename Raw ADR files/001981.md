# ADR-022: Cross-Text Pattern Analysis

## Status

Accepted

## Context

As the Gemantria project advances through Phase 5 (correlation analytics), we need to extend beyond individual concept correlations to analyze patterns that span multiple biblical books. Biblical texts often contain recurring motifs, shared themes, and structural patterns across different books. Understanding these cross-text relationships provides deeper insight into biblical structure and thematic consistency.

The current correlation engine (Phase 5) focuses on pairwise concept relationships within the semantic network. Phase 6 requires expanding this to identify statistical patterns and associations between different biblical books themselves.

## Decision

Implement cross-text pattern analysis that:

1. **Analyzes concept overlap between books** using association rule mining metrics
2. **Computes pattern strength** through weighted combination of Jaccard similarity, confidence, and support
3. **Generates structured exports** validated against `docs/SSOT/graph-patterns.schema.json`
4. **Integrates with reporting** via "Cross-Book Pattern Analytics" section
5. **Enforces validation** through Rule 032 (Pattern Integrity Validation)

## Rationale

### Benefits and Advantages

- **Thematic Discovery**: Identifies recurring biblical motifs across different texts
- **Structural Analysis**: Reveals how concepts cluster and relate across book boundaries
- **Quality Assurance**: Validates semantic consistency across biblical canon
- **Research Enablement**: Provides data foundation for biblical studies and theology
- **Extensibility**: Framework can accommodate additional pattern types (temporal, thematic, etc.)

### Trade-offs Considered

- **Computational Complexity**: Cross-book analysis increases from O(n²) concept pairs to O(b²) book pairs where b = number of books
- **Data Requirements**: Requires concepts to have book associations in database
- **Statistical Rigor**: Association metrics (lift, confidence) may be less meaningful with small datasets
- **Schema Evolution**: New JSON schema adds maintenance overhead

### Alignment with Project Goals

- **Correctness**: Extends gematria validation to cross-textual relationships
- **Determinism**: Pattern strength calculations use fixed, reproducible formulas
- **Safety**: Fail-closed validation prevents invalid pattern exports
- **Documentation**: Comprehensive ADR and schema documentation

## Alternatives Considered

### Alternative 1: Database-Only Implementation

- **Pros**: Leverages existing correlation views, potentially faster queries
- **Cons**: Limited to pairwise concept correlations, misses book-level patterns
- **Reason Rejected**: Doesn't provide the cross-text pattern analysis specifically requested

### Alternative 2: NetworkX Graph Analysis Only

- **Pros**: Rich graph algorithms for community detection and centrality
- **Cons**: No association rule mining metrics (lift, confidence, support)
- **Reason Rejected**: Missing statistical foundation required for pattern validation

### Alternative 3: Manual Pattern Definition

- **Pros**: Expert-driven pattern identification, higher accuracy
- **Cons**: Not scalable, subjective, doesn't leverage existing data
- **Reason Rejected**: Contradicts automated, data-driven approach

## Consequences

### Positive

- **Enhanced Analytics**: Cross-text pattern discovery adds new dimension to analysis
- **Schema Standardization**: New JSON schema provides consistent pattern representation
- **Reporting Integration**: Automated inclusion in pipeline reports
- **Research Value**: Enables new types of biblical pattern analysis

### Negative

- **Increased Complexity**: Additional export function and schema maintenance
- **Performance Impact**: Cross-book computation adds to export time
- **Data Dependencies**: Requires book associations in concept data

### Implementation Requirements

1. **Schema Creation**: `docs/SSOT/graph-patterns.schema.json` with required fields
2. **Export Function**: `export_patterns()` in `scripts/export_stats.py`
3. **Report Integration**: "Cross-Book Pattern Analytics" section in `scripts/generate_report.py`
4. **Rule Enforcement**: Rule 032 validation in CI/CD pipeline
5. **Testing**: Unit tests for pattern computation algorithms

## Related ADRs

- **ADR-016**: Insight Metrics & Ontology (foundation for pattern metrics)
- **ADR-018**: Pattern Correlation Engine (Phase 5 correlation framework)

## Notes

### Pattern Strength Calculation

Pattern strength combines multiple metrics with weights:

- Jaccard similarity: 40% (set overlap)
- Confidence: 40% (conditional probability)
- Support: 20% (joint occurrence frequency)

### Future Extensions

- **Temporal Patterns**: Sequence analysis across books
- **Thematic Clustering**: Hierarchical pattern organization
- **Interactive Visualization**: Web UI for pattern exploration
- **Statistical Validation**: Bootstrap confidence intervals

### Statistical Considerations

Association metrics may have limited statistical power with small datasets. Future work should consider:

- Minimum sample size requirements
- Statistical significance testing
- Confidence interval estimation
