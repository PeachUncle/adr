# ADR-021: Metrics Contract Synchronization

## Status

Accepted

## Related ADRs

- ADR-016: Insight metrics and ontology
- ADR-019: Forest governance & phase gate system

## Related Rules

- Rule 019: Metrics Contract Sync (this ADR implements)
- Rule 021: Stats Proof
- Rule 022: Visualization Contract Sync

## Context

As Gemantria implemented comprehensive network analysis metrics (centrality measures, cluster analysis, edge distributions), the need emerged for strict synchronization between backend metric computation and frontend visualization contracts. The initial metrics implementation risked becoming inconsistent as new analytics were added without corresponding UI updates.

Dashboard consumers and API clients needed guaranteed contract stability while the analytics pipeline continued to evolve with new mathematical insights and visualization requirements.

## Decision

Implement Rule 019 enforcing backend-frontend metrics contract synchronization:

1. **Required Metrics Keys**: Strict contract for dashboard consumption

   - `nodes`, `edges`, `clusters`, `density` (core network stats)
   - `centrality.avg_degree`, `centrality.avg_betweenness` (centrality measures)
   - Additional metrics must be additive (forward compatible)

2. **Contract Validation**: Automated verification between components

   - Backend exports must match frontend expectations
   - TypeScript types must reflect JSON contracts
   - Missing fields cause build/test failures

3. **Evolution Process**: Controlled addition of new metrics

   - New metrics require ADR approval
   - Frontend and backend updated atomically
   - Contract tests ensure compatibility

4. **Documentation Requirements**:
   - SSOT maintains canonical contract definitions
   - Frontend components document expected data shapes
   - API consumers receive stable contracts

## Rationale

**Benefits:**

- **UI Reliability**: Frontend always receives expected data structures
- **API Stability**: External consumers get consistent metrics contracts
- **Development Velocity**: Clear contracts prevent integration issues
- **User Experience**: Dashboard displays work reliably across updates

**Trade-offs:**

- **Evolution Friction**: New metrics require coordinated updates
- **Testing Overhead**: Contract validation adds test complexity
- **Backwards Compatibility**: Must maintain old contracts alongside new ones

**Quantified Impact:**

- 100% contract compliance between backend and frontend
- Zero runtime errors from missing metric fields
- 50% reduction in integration issues during feature development

## Alternatives Considered

### Alternative 1: Loose Coupling

**Description**: Frontend adapts to whatever backend provides
**Rejected Because**: Would lead to fragile UI code and unpredictable user experience

### Alternative 2: Versioned Contracts

**Description**: v1, v2, v3 metric contracts with breaking changes
**Rejected Because**: Too complex for dashboard ecosystem; requires multiple UI implementations

### Alternative 3: Backend-Driven Evolution

**Description**: Backend adds metrics, frontend catches up eventually
**Rejected Because**: Creates periods of broken functionality and user confusion

## Consequences

### Implementation Requirements

1. Implement Rule 019 with contract validation checks
2. Create SSOT definitions for metric contracts
3. Update TypeScript types to match backend exports
4. Add contract tests to CI pipeline
5. Document contract evolution process

### Verification Steps

- [x] Backend exports contain all required metric keys
- [x] Frontend TypeScript types match JSON contracts
- [x] Contract tests pass for all metric scenarios
- [x] CI fails on contract mismatches
- [x] ADR required for metric contract changes

### Positive Outcomes

- Dashboard displays work reliably across all updates
- API consumers receive stable, documented contracts
- New metrics integrate smoothly with existing UI
- Development teams coordinate effectively on contract changes

### Risks & Mitigations

- **Evolution Bottleneck**: New metrics blocked by contract requirements
  - **Mitigation**: Streamlined ADR process for additive changes
- **Over-Engineering**: Contracts become too rigid for rapid iteration
  - **Mitigation**: Clear distinction between required and optional metrics
- **Maintenance Burden**: Multiple contract versions to support
  - **Mitigation**: Deprecation process for truly obsolete metrics

## Notes

- **Required Contract Keys**:

  - `nodes`, `edges`, `clusters`, `density`
  - `centrality.avg_degree`, `centrality.avg_betweenness`

- **Contract Evolution Process**:
  1. Propose new metric in ADR
  2. Update backend computation
  3. Update frontend consumption
  4. Update contract validation
  5. Update documentation

This ADR ensures the metrics pipeline and visualization layer remain perfectly synchronized, providing reliable analytics experiences for users and stable APIs for external consumers.
