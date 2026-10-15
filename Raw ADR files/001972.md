# ADR-009: Semantic Aggregation & Network Analysis

## Status

Accepted

## Context

The gematria pipeline now processes nouns through extraction, validation, AI enrichment, and confidence validation. However, the enriched nouns exist as isolated data points without semantic relationships. To unlock deeper insights, we need to create a semantic network that connects related concepts based on their linguistic and theological similarity.

## Decision

Implement semantic aggregation using vector embeddings and graph analysis with the following characteristics:

1. **Vector Embeddings**: Generate 1024-dimensional embeddings for each enriched noun using lemma + insights text
2. **Similarity Computation**: Calculate cosine similarity between all concept pairs
3. **Relationship Classification**: Classify edges as "strong" (>0.90 similarity) or "weak" (>0.75 similarity)
4. **Graph Persistence**: Store embeddings and relationships in pgvector-enabled tables
5. **Report Integration**: Include network metrics in automated pipeline reports

## Implementation Details

### Architecture Components

#### Network Aggregator Node

- Located: `src/nodes/network_aggregator.py`
- Function: `network_aggregator_node(state: dict) -> dict`
- Input: Confidence-validated enriched nouns
- Output: Network summary with relationship counts and embeddings stored

#### Database Schema

```sql
CREATE TABLE concept_network (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    concept_id      UUID NOT NULL,
    embedding       VECTOR(1024) NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE concept_relations (
    source_id       UUID REFERENCES concept_network(id),
    target_id       UUID REFERENCES concept_network(id),
    similarity      DOUBLE PRECISION CHECK (similarity BETWEEN 0 AND 1),
    relation_type   TEXT CHECK (relation_type IN ('strong','weak')),
    created_at      TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (source_id, target_id)
);
```

#### LM Studio Integration

- **Embeddings**: Qwen3-Embedding-0.6B-GGUF via `/v1/embeddings`
- **Reranking**: Qwen3-Reranker-0.6B-GGUF via `/v1/chat/completions`
- **Dimensions**: 1024 (L2 normalized vectors)
- **Configuration**: `USE_QWEN_EMBEDDINGS=true` to enable real inference
- **Fallback**: Deterministic mock embeddings when disabled or in test mode
- **Batch Processing**: 16-32 texts per embedding request for efficiency

### Pipeline Integration

#### Graph Structure

```
collect_nouns → validate_batch → enrichment → confidence_validator → network_aggregator
```

#### State Management

- Network summary stored in `state["network_summary"]`
- Includes: total_nodes, strong_edges, weak_edges, embeddings_generated, similarity_computations

#### Error Handling

- NetworkAggregationError: Raised on embedding or similarity computation failures
- Pipeline continues but marks network_aggregation_failed

### Report Generation

#### Network Metrics Section

- Total nodes and edges counts
- Strong vs weak relationship breakdown
- Embedding generation statistics
- Integration with existing MD/JSON report formats

### Performance Considerations

#### Batch Processing

- O(n²) similarity computations for n concepts
- Suitable for batch sizes ≤ 50 nouns
- Scales with pgvector indexing for larger datasets

#### Storage Requirements

- 1024 floats per embedding = ~4KB per concept
- Bidirectional relationships stored once
- Indexes on similarity and relation type for query performance

## Consequences

### Positive

- **Semantic Insights**: Enables discovery of related biblical concepts
- **Query Capabilities**: Supports graph-based analysis and visualization
- **Scalable Architecture**: pgvector foundation for larger concept networks
- **Report Enhancement**: Richer pipeline analysis with network metrics

### Negative

- **Computational Cost**: O(n²) similarity calculations
- **Storage Overhead**: Vector embeddings increase database size
- **Complexity**: Additional graph analysis and maintenance

## Alternatives Considered

### Option 1: Pre-computed Similarity Matrix

- Store all pairwise similarities in advance
- Pro: Fast queries, comprehensive coverage
- Con: Storage explosion (n² entries), less flexible

### Option 2: On-demand Similarity Computation

- Calculate similarities only when queried
- Pro: Minimal storage, flexible thresholds
- Con: Slow for real-time analysis, repeated computation

### Option 3: Hierarchical Clustering

- Build concept hierarchies instead of full graph
- Pro: More interpretable structure, reduced complexity
- Con: Loss of nuanced relationships, less flexible queries

## Testing Strategy

### Unit Tests

- Embedding generation and cosine similarity math
- Relationship classification logic
- Mock embeddings for deterministic testing

### Integration Tests

- Full network aggregation pipeline
- Database roundtrip for embeddings and relations
- Report generation with network metrics

### Contract Tests

- Network aggregator behavior with various input sizes
- Error handling for embedding service failures
- Threshold boundary testing for relationship classification

## Future Considerations

### Advanced Graph Analytics

Future phases could add:

- Centrality measures (degree, betweenness, eigenvector)
- Community detection algorithms
- Path finding for concept relationships
- Graph visualization endpoints

### Dynamic Thresholds

Adaptive similarity thresholds based on:

- Domain-specific requirements (theological vs linguistic)
- Dataset characteristics and distribution
- User-defined relationship strengths

### Multi-modal Embeddings

Enhanced embeddings combining:

- Text content (current implementation)
- Structural relationships (verse/chapter context)
- Numerical patterns (gematria values)
- Metadata features (book, author, time period)

### Graph Query API

RESTful endpoints for:

- Concept similarity search
- Relationship traversal
- Subgraph extraction
- Network statistics
