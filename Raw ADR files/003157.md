# ADR-003: Vector Database and Embedding Strategy for RAG Pipeline

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2025-12-18
- **Feature:** 002-rag-data-ingestion
- **Context:** Selection of the vector database and the embedding model for transforming textual content into numerical representations suitable for similarity search in the RAG pipeline. These choices are fundamental to the performance, accuracy, and scalability of the retrieval system.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

The RAG pipeline will utilize the following vector database and embedding strategy:
-   **Vector Database:** Qdrant Cloud (Free Tier) will be used for storing vector embeddings and their associated metadata.
-   **Embedding Model:** The Cohere API, specifically the `embed-english-v3.0` model, will be used to generate embeddings from text chunks.
-   **Interaction Pattern:** Text chunks will be processed in batches when calling the Cohere API to optimize performance and API usage. Data will be stored and updated in Qdrant using the `upsert` operation.

## Consequences

### Positive

-   **Qdrant Cloud:** Provides a fully managed, scalable, and performant vector database solution, significantly reducing the operational overhead associated with self-hosting and managing a vector database. The free tier allows for cost-effective development and initial deployment.
-   **Cohere API (`embed-english-v3.0`):** Grants access to a high-quality, state-of-the-art text embedding model from a leading AI provider. This ensures that the generated embeddings are semantically rich and contribute to highly relevant search results, directly enhancing the RAG system's performance.
-   **Batching for Embeddings:** Optimizing Cohere API calls by batching text chunks improves throughput, reduces overall processing time, and helps in managing API rate limits effectively.
-   **`Upsert` Operation:** Using Qdrant's `upsert` functionality simplifies the pipeline's update logic, allowing for idempotent operations. This means the pipeline can be re-run safely to update existing content or add new content without needing complex logic to differentiate between new and old data.

### Negative

-   **Vendor Lock-in:** Reliance on specific commercial providers (Cohere and Qdrant) introduces potential vendor lock-in. Switching to alternative services or self-hosted solutions in the future might require significant code changes and data migration efforts.
-   **Cost and Scalability Limits:** While a free tier is available, scaling the solution beyond the free tier's limits (e.g., for very large datasets or high query volumes) will incur costs. There could be performance or storage bottlenecks if the free tier's capabilities are exceeded.
-   **External Service Reliability:** The pipeline's operation is dependent on the availability, performance, and API stability of both Cohere and Qdrant. Outages or degraded performance from these external services will directly impact the data ingestion process.
-   **Embedding Model Specificity:** The `embed-english-v3.0` model is optimized for English text. If the Docusaurus content expands to include other languages, this embedding model might not be suitable, necessitating a change or addition of multilingual models.

## Alternatives Considered

-   **Alternative Vector Database (Self-hosted Solutions: Qdrant, Weaviate, Milvus):**
    -   **Description:** Deploying and managing an open-source vector database instance on custom infrastructure (e.g., Docker, Kubernetes).
    -   **Why rejected:** While offering complete control and potentially lower long-term costs for very large-scale deployments, self-hosting introduces significant operational complexity including setup, maintenance, scaling, backups, and security management. This additional overhead is undesirable for an initial project with limited resources.
-   **Alternative Vector Database (Other Managed Services: Pinecone, Chroma, etc.):**
    -   **Description:** Utilizing other managed vector database providers.
    -   **Why rejected:** Qdrant Cloud was specifically requested, provides a robust feature set, and offers a viable free tier that meets the project's current needs. There was no compelling technical advantage identified to choose an alternative managed service at this stage.
-   **Alternative Embedding Model (Open-source Models: Sentence-BERT, fine-tuned BERT/RoBERTa):**
    -   **Description:** Using open-source embedding models that can be hosted locally or on custom infrastructure.
    -   **Why rejected:** While potentially reducing API costs and external dependencies, open-source models often require managing model inference infrastructure. Furthermore, to achieve performance comparable to state-of-the-art commercial APIs like Cohere, they typically require significant fine-tuning, which adds complexity and development time. Cohere API was explicitly requested for its ease of use and high-quality embeddings out-of-the-box.

## References

- Feature Spec: `specs/002-rag-data-ingestion/spec.md`
- Implementation Plan: `specs/002-rag-data-ingestion/plan.md`
- Related ADRs: N/A
- Evaluator Evidence: `specs/002-rag-data-ingestion/research.md`
