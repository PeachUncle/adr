# ADR-0010: RAG System Model Choice and Hybrid Search Strategy

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-11-30
- **Feature:** 001-physical-ai-robotics-book
- **Context:** The RAG pipeline for the "Physical AI & Humanoid Robotics" textbook requires an optimal balance between retrieval quality, response latency, and cost, especially under hackathon constraints. This decision covers the choice of LLM and the retrieval strategy.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

**1. LLM Model Choice**: `gemini-2.5-flash` via Agents SDK + ChatKit will be used for the LLM.
**2. Hybrid Search Strategy**: A hybrid search strategy combining vector similarity search with keyword matching will be implemented.
   - For queries containing specific terms (e.g., function names, ROS 2 topics), an additional keyword filter will be applied to the `text` payload field in Qdrant to boost the relevance of exact matches.

## Consequences

### Positive

- **Cost-Efficiency & Speed**: `gemini-2.5-flash` is a good choice for hackathon constraints, offering a balance of speed and cost-effectiveness while still providing quality responses.
- **Improved Retrieval Accuracy**: Hybrid search leverages both semantic understanding (vector search) and precise matching (keyword search), leading to more accurate and contextually relevant results, especially for technical queries involving specific terms (e.g., code snippets, function names).
- **Reduced Hallucinations**: By grounding responses with highly relevant and specific chunks, the risk of the LLM generating inaccurate or fabricated information is significantly reduced.

### Negative

- **Implementation Complexity**: Implementing and fine-tuning a hybrid search strategy adds complexity compared to a pure vector search approach.
- **Potential for Tuning Overhead**: Optimizing the balance between vector and keyword search weights, and the `score_threshold` for Qdrant, may require empirical testing and iteration.
- **Model Limitations**: While cost-effective, `gemini-2.5-flash` might have limitations in handling extremely complex or nuanced queries compared to larger, more expensive models.

## Alternatives Considered

**1. LLM Model Alternatives**:
- **Larger, more capable models (e.g., Gemini Opus, Claude Opus)**:
   - **Why rejected**: Higher cost and potentially higher latency, which conflict with the hackathon's free/low-cost and sub-3-second response time goals.

**2. Retrieval Strategy Alternatives**:
- **Pure Vector Search**: Rely solely on vector similarity for retrieval.
   - **Why rejected**: Less effective for precise queries (e.g., specific function names, exact code snippets) where keyword matching can significantly boost relevance. Could lead to less accurate answers for highly technical content.
- **Pure Keyword Search**: Rely solely on keyword matching (e.g., BM25).
   - **Why rejected**: Lacks semantic understanding and would perform poorly on natural language queries or questions requiring conceptual understanding.

## References

- Feature Spec: /home/abdullahiqbal/Abdullah/hackathon-book-project/specs/rag-chatbot/spec.md
- Implementation Plan: /home/abdullahiqbal/Abdullah/hackathon-book-project/specs/001-physical-ai-robotics-book/plan.md
- Related ADRs: 0009-text-selection-strategy.md
- Evaluator Evidence: null
