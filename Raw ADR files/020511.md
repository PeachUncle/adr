# 2. CPT and Network Structure Design

Date: 2024-12-24

## Status

Proposed

## Context

During our exploration of Bayesian Networks, we discovered several key insights about the nature of Conditional Probability Tables (CPTs) and network structure:

1. Network Structure Fundamentals:
   - Nodes represent points in a vector space
   - Edges represent causal relationships between nodes
   - The network structure itself should be simple and focused
   - Additional capabilities should be layered on top

2. CPT Representations:
   - CPTs can be implemented in multiple ways:
     - Discrete state mappings
     - Mathematical functions
     - Sampled data with approximation functions
   - The choice of representation depends on the nature of the relationship being modeled
   - Some relationships (like phase transitions) have complex boundaries and temporal aspects

3. System Purpose:
   - The system serves dual purposes:
     - Identifying constant structures/constraints in reality
     - Exploring the implications of those constraints
   - Networks can be generated through:
     - Theoretical reasoning (conscious thought)
     - Empirical evidence (real-world data)
   - Both types are structurally identical but differ in origin

4. Key Insights:
   - A node needs at least 2 states to carry information
   - Constants emerge from patterns in relationships
   - Real-world relationships often have fuzzy boundaries
   - Sampling and approximation can handle complex cases

## Decision

1. Keep the core Network structure minimal:
```typescript
interface Node {
    id: string;
    name: string;
    states: string[];    // Minimum 2 states
    cpt: Map<string, number>;
}

interface Edge {
    id: string;
    from: string;
    to: string;
}

interface Network {
    id: string;
    name: string;
    nodes: Map<string, Node>;
    edges: Map<string, Edge>;
}
```

2. Allow for different CPT implementations:
   - Start with basic discrete state mappings
   - Design for future extension to functions and sampling
   - Keep implementation details separate from core structure

3. Separate Concerns:
   - Core network structure (nodes, edges, basic operations)
   - CPT implementations (discrete, functional, sampled)
   - Evolution/learning systems
   - Analysis tools

## Consequences

### Positive
- Clean, focused core structure
- Flexibility in CPT implementation
- Clear separation of concerns
- Foundation for both theoretical and empirical use

### Negative
- May need to refactor as we add more complex CPT types
- Some efficiency lost by keeping core simple
- Additional complexity in layered systems

### Risks
- Need to ensure CPT implementations remain compatible
- Complex relationships might strain simple structure
- Balance between flexibility and complexity

## Notes

The system's ability to compare theoretical models with empirical results will be crucial for its effectiveness as a learning tool. The simple core structure provides a foundation for this comparison while allowing for sophisticated implementations of specific relationships.
