# ADR-010: Qwen3 Integration for Real Semantic Intelligence

## Status

Accepted

## Related ADRs

- ADR-009: Semantic aggregation and network building (foundation)
- ADR-011: Concept network health verification views (validation)
- ADR-012: Concept network vector dimension correction (implementation fix)

## Related Rules

- 011-production-safety.mdc: Production safety and live model enforcement
- 013-report-generation-verification.mdc: Report generation verification

## Context

The semantic aggregation system (ADR-009) was implemented with mock embeddings for development and testing. To activate real semantic intelligence, we need to integrate Qwen3 models through LM Studio for production-quality vector embeddings and relationship validation.

## Decision

Integrate Qwen3-Embedding-0.6B-GGUF and Qwen3-Reranker-0.6B-GGUF models with the following implementation:

1. **Embedding Generation**: Real 1024-dimensional vectors using Qwen3-Embedding-0.6B-GGUF
2. **Batch Processing**: 16-32 text batching for GPU efficiency
3. **Vector Normalization**: L2 normalization for cosine similarity
4. **Reranking**: Qwen3-Reranker-0.6B-GGUF for relationship validation
5. **Configuration**: `USE_QWEN_EMBEDDINGS=true` flag for real vs mock mode
6. **Fallback**: Automatic fallback to mock embeddings when LM Studio unavailable

## Implementation Details

### Architecture Components

#### LM Studio Client Extensions

- **Location**: `src/services/lmstudio_client.py`
- **New Methods**: `get_embeddings()`, `rerank()` with logprob-based scoring
- **Environment Variables**: `USE_QWEN_EMBEDDINGS`, `QWEN_EMBEDDING_MODEL`, `QWEN_RERANKER_MODEL`
- **Rerank Features**: Logprob extraction, sigmoid scoring, batch processing (4-8 candidates)

#### Network Aggregator Updates

- **Location**: `src/nodes/network_aggregator.py`
- **Enhancement**: Rerank-driven relationship refinement with pgvector KNN + Qwen reranker
- **Two-Stage Process**: Recall (KNN) → Precision (reranking) → Edge strength calculation
- **Batch Processing**: 16-text embedding batches, 4-8 candidate rerank batches
- **Storage**: pgvector `VECTOR(1024)` with rerank evidence in `concept_relations`

### Input Formatting

Embeddings and rerank documents use structured format:

```
Document: {noun_name}
Meaning: {hebrew_text}
Primary Verse: {primary_verse_reference}
Gematria: {numeric_value}
Insight: {theological_insight}
```

### Rerank-Driven Relationship Refinement

**Algorithm Overview:**

1. Generate embeddings for all concepts using Qwen3-Embedding
2. For each source concept, find top-k nearest neighbors via pgvector KNN
3. Rerank neighbors against source concept using Qwen3-Reranker
4. Calculate edge strength: `0.5 * cosine + 0.5 * rerank_score`
5. Classify relationships: strong (≥0.90), weak (≥0.75), filtered (<0.75)

**Configuration:**

- `NN_TOPK=20`: KNN neighbors to retrieve for reranking
- `RERANK_MIN=0.50`: Minimum rerank score to keep candidates
- `EDGE_STRONG=0.90`: Strong relationship threshold
- `EDGE_WEAK=0.75`: Weak relationship threshold

**Prompt Format:**

```
System: Judge whether the Document meets the requirements based on the Query and the Instruct provided. The answer can only be yes or no.

User:
<Instruct>: Given a theological theme, identify relevant biblical nouns.
<Query>: {source_concept_document}

<Document>: {candidate_concept_document}
```

**Score Mapping:**

1. **Logprob-based** (preferred): `score = sigmoid(yes_logprob - no_logprob)`
2. **Text parsing** (fallback): "yes" → 1.0, "no" → 0.0, unclear → 0.5

### Database Schema

```sql
-- Migration 008: Concept network constraints
ALTER TABLE concept_network ADD CONSTRAINT concept_network_concept_id_unique UNIQUE (concept_id);
ALTER TABLE concept_relations ADD CONSTRAINT concept_relations_unique_pair UNIQUE (source_id, target_id);

-- Migration 009: Rerank evidence storage (PR-011)
ALTER TABLE concept_relations
ADD COLUMN cosine NUMERIC(6,5),
ADD COLUMN rerank_score NUMERIC(6,5),
ADD COLUMN edge_strength NUMERIC(6,5),
ADD COLUMN rerank_model TEXT,
ADD COLUMN rerank_at TIMESTAMPTZ DEFAULT now();
```

### Configuration

```bash
# Core Qwen integration
USE_QWEN_EMBEDDINGS=true          # Enable real embeddings
QWEN_EMBEDDING_MODEL=qwen-embed   # Embedding model name
QWEN_RERANKER_MODEL=qwen-reranker # Reranker model name
LM_STUDIO_HOST=http://127.0.0.1:1234

# Rerank-driven relationship refinement (PR-011)
NN_TOPK=20              # KNN neighbors for reranking
RERANK_MIN=0.50         # Minimum rerank score threshold
EDGE_STRONG=0.90        # Strong relationship threshold
EDGE_WEAK=0.75          # Weak relationship threshold
```

## Consequences

### Positive

- **Real Semantic Intelligence**: Production-quality embeddings + rerank validation
- **Two-Stage Refinement**: KNN recall + reranker precision for high-quality relationships
- **Edge Strength Evidence**: Stored rerank scores enable relationship confidence analysis
- **GPU Acceleration**: RTX 5070 Ti utilization for both embedding and reranking
- **Scalable Architecture**: LM Studio server handles multiple models concurrently
- **Deterministic Fallback**: Mock mode preserves testing capabilities
- **Observability**: Comprehensive metrics for Qwen usage and performance

### Negative

- **Dependency on LM Studio**: Requires running LM Studio server
- **GPU Memory Usage**: Models loaded in VRAM (~1.2GB per model)
- **Network Latency**: API calls add processing time vs local mocks
- **Model Loading Time**: Initial model load delays first inference

### Risks

- **Model Availability**: LM Studio server must be running with correct models
- **API Compatibility**: Changes in LM Studio API could break integration
- **Resource Usage**: High GPU utilization during batch processing
- **Fallback Complexity**: Mock vs real mode switching for testing

## Alternatives Considered

### Option 1: Local Model Loading

- **Pro**: No external server dependency, faster inference
- **Con**: Python dependency management, memory constraints, no GPU offloading

### Option 2: Cloud API Integration

- **Pro**: Always available, managed infrastructure
- **Con**: Cost, privacy concerns, network dependency

### Option 3: Hybrid Approach

- **Pro**: Best of both worlds (local for embeddings, cloud for complex tasks)
- **Con**: Architecture complexity, multiple API dependencies

### Option 4: Delayed Integration

- **Pro**: Keep current mock system, defer real AI to later phase
- **Con**: Miss opportunity to validate semantic network with real intelligence

## Testing Strategy

### Unit Tests

- Embedding vector normalization and dimensionality
- Reranking score mapping and error handling
- Mock vs real mode switching
- Batch processing edge cases

### Integration Tests

- Full pipeline with real embeddings enabled
- Database persistence and pgvector operations
- LM Studio API error handling and retries
- Performance benchmarking vs mock mode

### End-to-End Tests

- Genesis batch processing with real Qwen inference
- Report generation with network metrics
- Configuration validation across environments

## Performance Characteristics

### Throughput

- **Embeddings - Mock Mode**: ~1000 embeddings/second (CPU)
- **Embeddings - Real Mode**: ~50-100 embeddings/second (GPU batched, 16-32 batch)
- **Reranking - Mock Mode**: ~500 reranks/second (CPU)
- **Reranking - Real Mode**: ~10-20 reranks/second (GPU batched, 4-8 candidates)
- **Network Aggregation**: KNN (fast) + reranking (bottleneck) per concept

### Memory Usage

- **System RAM**: Minimal additional usage
- **GPU VRAM**: ~2.4GB total for both models (4-bit quantized)
- **Database**: ~4KB per embedding + rerank evidence per relationship

### Latency

- **Embeddings - Mock**: <1ms per embedding
- **Embeddings - Real**: 50-200ms per batch
- **Reranking - Mock**: <2ms per rerank
- **Reranking - Real**: 100-500ms per batch (logprob processing)
- **Network**: 10-50ms LM Studio API round-trip per request

## Future Considerations

### Advanced Reranking

- Multi-turn conversations for complex relationship validation
- Confidence score calibration based on historical accuracy
- Cross-reference validation with multiple models

### Model Optimization

- Quantization for reduced memory footprint
- Model fine-tuning on biblical corpora
- Ensemble approaches combining multiple embedding models

### Scalability

- Distributed LM Studio servers for horizontal scaling
- Embedding caching for repeated concepts
- Incremental embedding updates for evolving concepts

### Monitoring

- Embedding quality metrics and drift detection
- Model performance monitoring and alerting
- GPU utilization and temperature monitoring
