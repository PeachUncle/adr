# ADR-012: Concept Network Vector Dimension Correction

## Status

Accepted

## Context

During implementation of the semantic network with Qwen embeddings, we discovered a potential mismatch between the configured vector dimension (1024) and the actual pgvector column definition. The `concept_network.embedding` column was created with a default dimension that may not match the runtime requirements.

This creates a risk of:

1. **Runtime Failures**: Dimension mismatch errors during embedding insertion
2. **Data Corruption**: Failed inserts leading to incomplete network data
3. **Inconsistent State**: Mixed dimensions within the same table
4. **Operational Issues**: Pipeline failures when embeddings cannot be stored

The migration provides a corrective action to ensure dimensional consistency.

## Decision

Implement an optional migration (`012a_concept_network_dim_fix.sql`) that can alter the vector column dimension to match runtime requirements, with safety precautions and clear warnings about data modification.

## Rationale

This decision ensures:

- **Consistency**: Vector dimensions match across the entire pipeline
- **Reliability**: Prevents runtime dimension mismatch errors
- **Safety**: Optional migration with clear warnings and backup requirements
- **Flexibility**: Supports different embedding model dimensions (768, 1024, 1536, etc.)

The approach prioritizes safety by making the migration optional and requiring explicit execution.

## Alternatives Considered

### Alternative 1: Recreate Table with Correct Dimensions

- **Pros**: Clean slate, guaranteed consistency
- **Cons**: Data loss, requires re-running entire pipeline
- **Reason Rejected**: Unacceptable data loss; defeats purpose of persistence

### Alternative 2: Runtime Dimension Detection

- **Pros**: Automatic adaptation to embedding dimensions
- **Cons**: Complex schema management, potential performance issues
- **Reason Rejected**: Over-engineering; simple ALTER is sufficient for this use case

### Alternative 3: Fixed Dimension in Schema

- **Pros**: Compile-time guarantee of dimension consistency
- **Cons**: Less flexible for different embedding models
- **Reason Rejected**: Current Qwen models use 1024 dimensions; future models may vary

## Consequences

### Positive

- Resolves dimension mismatch errors
- Enables reliable embedding storage
- Supports different embedding model dimensions
- Maintains existing data integrity

### Negative

- Requires careful execution with backups
- Potential downtime during ALTER operation
- Must be run manually when needed

### Implementation Requirements

- Create migration script with ALTER TABLE statements
- Include clear warnings and backup requirements
- Provide examples for common dimensions (768, 1024, 1536)
- Test migration on development environment first

## Related ADRs

- ADR-009: Semantic Aggregation (concept network schema)
- ADR-010: Qwen Integration (embedding generation requirements)
- ADR-007: LLM Integration (embedding model specifications)

## Notes

Migration is named `012a` to indicate it's an optional corrective action. The `a` suffix distinguishes it from required schema migrations. Should only be run if `vector_dims(embedding)` queries reveal dimensional inconsistencies.
