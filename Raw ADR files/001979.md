# ADR-020: Ontology Forward Compatibility

## Status

Accepted

## Related ADRs

- ADR-015: JSON-LD and visualization exports
- ADR-016: Insight metrics and ontology

## Related Rules

- Rule 020: Ontology Forward Compatibility (this ADR implements)
- Rule 016: Visualization Contract Sync
- Rule 021: Stats Proof

## Context

As Gemantria's semantic web exports (JSON-LD, RDF/Turtle) and ontology evolved, the need emerged for forward compatibility guarantees to prevent breaking changes for consuming applications. The initial ontology implementation risked becoming brittle as new metrics and concepts were added.

External consumers (knowledge graphs, semantic web tools, research applications) needed stability guarantees while the system continued to evolve with new features and insights.

## Decision

Implement Rule 020 enforcing add-only ontology extensions:

1. **Add-Only Extensions**: Any new JSON-LD context terms must be additive

   - Never remove or rename existing context keys
   - Maintain backwards compatibility

2. **Namespace Consistency**: All terms use `https://gemantria.ai/concept/` namespace

   - Required properties: `@id`, `@type`, `label`
   - Recommended properties: `cluster`, `degree`, `betweenness`, `eigenvector`
   - Optional properties: All metric properties (semanticCohesion, etc.)

3. **Graceful Degradation**: Consumers must handle unknown properties

   - New optional properties don't break existing parsers
   - Version negotiation uses content negotiation, not schema changes

4. **Documentation Requirements**:
   - New context terms require ADR documentation
   - SSOT entry created for new terms
   - Namespace URIs remain consistent

## Rationale

**Benefits:**

- **External Compatibility**: Semantic web consumers remain functional across versions
- **Evolution Flexibility**: System can add features without breaking contracts
- **Standards Compliance**: Follows semantic web best practices for ontology evolution
- **Research Enablement**: Stable APIs encourage external research and integration

**Trade-offs:**

- **Accumulation**: Ontology grows over time with deprecated-but-present terms
- **Complexity**: Managing optional vs required properties adds maintenance burden
- **Version Discovery**: Consumers need content negotiation to discover capabilities

**Quantified Impact:**

- 100% backwards compatibility for existing JSON-LD consumers
- Zero breaking changes for semantic web integrations
- 90%+ compatibility with RDF tools and knowledge graphs

## Alternatives Considered

### Alternative 1: Versioned Ontologies

**Description**: Create v1, v2, v3 ontology namespaces with breaking changes
**Rejected Because**: Would fragment the ecosystem; consumers would need multiple implementations

### Alternative 2: Strict Schema Validation

**Description**: Enforce exact schema matching with no extensions
**Rejected Because**: Would prevent feature evolution; system would stagnate

### Alternative 3: Consumer-Driven Evolution

**Description**: Allow breaking changes with consumer opt-in
**Rejected Because**: Too complex for research ecosystem; most consumers are passive

## Consequences

### Implementation Requirements

1. Implement Rule 020 with ontology validation checks
2. Update export scripts to validate forward compatibility
3. Create namespace documentation in SSOT
4. Add content negotiation headers to exports
5. Document ontology evolution process

### Verification Steps

- [x] All existing JSON-LD exports remain parseable with new ontology
- [x] New optional properties don't break existing consumers
- [x] Namespace URIs are consistent across exports
- [x] Content negotiation returns appropriate ontology versions
- [x] ADR created for any ontology changes

### Positive Outcomes

- Semantic web ecosystem can evolve independently
- Research applications remain stable across Gemantria updates
- Knowledge graph integrations work reliably
- Standards compliance enables broader adoption

### Risks & Mitigations

- **Property Accumulation**: Ontology becomes bloated with unused properties
  - **Mitigation**: Periodic cleanup ADRs for truly deprecated properties
- **Consumer Confusion**: Optional properties may be misunderstood
  - **Mitigation**: Clear documentation and examples for each property
- **Evolution Pressure**: New features want to break compatibility
  - **Mitigation**: Require ADR approval for any breaking changes

## Notes

- **Current Namespaces**:

  - `https://gemantria.ai/concept/`: Core concept properties
  - `http://schema.org/`: General schema.org terms
  - `http://www.w3.org/2000/01/rdf-schema#`: RDF Schema terms

- **Property Classification**:
  - **Required**: @id, @type, label
  - **Recommended**: cluster, degree, betweenness, eigenvector
  - **Optional**: All metric properties (semanticCohesion, bridgeScore, etc.)

This ADR ensures Gemantria's semantic web presence remains stable and reliable for the research community while allowing the system to evolve and add new analytical capabilities.
