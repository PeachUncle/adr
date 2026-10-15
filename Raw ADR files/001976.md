# ADR-014: Relations & Pattern Discovery

## Status

Accepted

## Related ADRs

- ADR-010: Qwen integration with embedding models (foundation for relations)
- ADR-011: Concept network health verification views (validation framework)
- ADR-012: Concept network vector dimension correction (implementation fix)

## Related Rules

- 011-production-safety.mdc: Production safety and live model enforcement
- 013-report-generation-verification.mdc: Report generation verification

## Context

We have verified 1024-dim embeddings in `concept_network`. Next: derive edges,
communities, and centrality to enable UI graph and analytics.

## Decision

- Enable KNN cosine neighbors with optional rerank filter.
- Persist edges with strength and rerank evidence.
- Compute Louvain communities and degree/betweenness/eigenvector centrality.
- Add soft/hard confidence gates (warn vs fail) to balance quality and progress.
- Export viz-ready JSON.

## Rationale

- **Relations**: KNN provides efficient similarity search; rerank adds semantic validation
- **Pattern Discovery**: Communities reveal topical clusters; centrality identifies key concepts
- **Confidence Gates**: Soft warnings allow progress while hard fails prevent low-quality data
- **Exports**: JSON format enables immediate UI consumption

## Alternatives Considered

- **Full graph algorithms**: Considered NetworkX vs custom implementations; NetworkX chosen for robustness
- **Edge persistence**: Considered computed-on-demand vs stored; stored chosen for performance
- **Confidence thresholds**: Single threshold vs soft/hard; soft/hard chosen for flexibility

## Consequences

- **Positive**: Richer analytics and graph exports with clear quality signaling
- **Implementation**: New migration required; pipeline extended with pattern discovery
- **Performance**: KNN computation scales with batch size; optimize for large graphs later
- **Dependencies**: NetworkX added for graph algorithms

## Implementation Notes

- Relations computed per batch after embeddings
- Pattern discovery runs post-pipeline via separate script
- Confidence gates integrate with existing enrichment flow
- All new tables have appropriate indexes for query performance
