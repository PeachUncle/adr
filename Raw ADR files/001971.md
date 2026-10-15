# ADR-007: LLM Integration and Confidence Metadata

## Status

Accepted

## Context

The project requires semantic enrichment of extracted nouns beyond basic gematria calculations. While morphological analysis provides structural insights, theological and contextual understanding requires natural language processing capabilities. The system needs to add confidence-scored metadata to enable quality filtering and downstream analysis.

## Decision

Integrate LM Studio locally for theological enrichment and gematria confidence scoring, using offline inference to maintain reproducibility and avoid external API dependencies.

## Rationale

- **Offline Inference**: Keeps all processing local and reproducible
- **Structured Metadata**: Adds confidence scores (0-1) to each noun
- **Deterministic Behavior**: Fixed prompts, models, and thresholds ensure consistency
- **Provenance Tracking**: Records model versions and parameters for auditability

## Alternatives Considered

1. **Cloud API Services** (OpenAI, Anthropic, etc.)
   - Pros: No local infrastructure, managed service
   - Cons: API costs, rate limits, data privacy concerns, external dependencies

2. **No LLM Enrichment**
   - Pros: Simpler implementation, no additional dependencies
   - Cons: Limited semantic understanding, reduced analysis capabilities

3. **Rule-based Enrichment**
   - Pros: Deterministic, no ML dependencies
   - Cons: Limited coverage, maintenance overhead, less nuanced understanding

## Consequences

### Implementation Requirements
- `lmstudio_client.py`: REST API client with mock mode fallback
- `enrichment_node.py`: Inference pipeline and database logging
- Confidence scoring system (0-1 scale)
- Model version tracking and provenance

### Positive Outcomes
- Deeper semantic enrichment for theological analysis
- Quality filtering based on confidence scores
- Enhanced downstream network analysis capabilities
- Reproducible results through local inference

### Risks and Mitigations
- **Local Infrastructure**: Requires LM Studio setup (mitigated by mock mode)
- **Performance Cost**: Additional processing time per noun (acceptable for quality)
- **Model Quality**: Dependent on local model selection (validated through testing)

## Implementation

- `lmstudio_client.py`: Handles LM Studio REST API and mock mode
- `enrichment_node.py`: Performs inference and inserts results into `ai_enrichment_log`
- Confidence stored (0 – 1) with models recorded for provenance

## Related Decisions

**Note:** The current LM Studio integration approach has been updated in **ADR-066** (LM Studio + Control Plane Integration), which ratifies RFC-080. ADR-066 supersedes the LM Studio integration aspects of this ADR while preserving the confidence metadata and enrichment concepts. See ADR-066 for the current adapter pattern, health-aware routing, and control-plane logging implementation.
