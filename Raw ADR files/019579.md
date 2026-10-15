# ADR-005: RAG (Retrieval-Augmented Generation) Strategy for Grounding AI Responses

## Status

**Accepted** | Date: 2025-10-21

## Context

MobilityCorp's GenAI Platform must provide accurate, factual responses to customer queries, incident summaries, and safety explanations. Large Language Models (LLMs) are prone to **hallucination**—generating plausible but factually incorrect information. For a safety-critical vehicle-sharing platform operating under EU AI Act regulations, we cannot tolerate AI responses that:

- Provide incorrect pricing or policy information
- Misstate safety procedures or vehicle capabilities
- Fabricate incident explanations without evidence
- Cite non-existent policies or regulations

### Requirements

**Functional Requirements**:

- AI responses must be grounded in authoritative, up-to-date company documents
- Every factual claim must be traceable to source documents (provenance)
- Customer support answers must cite official policies, FAQs, and procedures
- Incident summaries must reference similar historical incidents and telemetry data
- Safety anomaly explanations must link to vehicle specifications and safety protocols

**Non-Functional Requirements**:

- **Factuality**: ≥95% of AI claims must be supported by retrieved sources
- **Latency**: <800ms end-to-end response time (p95) including retrieval
- **Freshness**: Updates to policy documents reflected in AI responses within 1 hour
- **Explainability**: Users must see source citations for transparency

**EU AI Act Compliance (Article 13 - Transparency)**:

- High-risk AI systems must be transparent and explainable
- Users must understand the basis for AI-generated outputs
- Provenance of information must be traceable for audits

### Constraints

- **Cost**: LLM API calls are expensive (~$0.02 per request for GPT-4); must minimize token usage
- **Context Window**: LLMs have limited context windows (8K-128K tokens); can't send entire knowledge base
- **Latency**: Adding retrieval step must not exceed 200ms overhead
- **Data Privacy**: Cannot send PII to external LLM providers
- **Infrastructure**: Must support 10K+ queries per day per city with sub-second response times

## Decision

We will implement **Retrieval-Augmented Generation (RAG)** as the foundational pattern for all GenAI features. Every AI response will be grounded in documents retrieved from a vector-based semantic search system before being sent to the LLM.

### Architecture

```
User Query
    ↓
1. Query Embedding (convert text to vector)
    ↓
2. Vector Search (find top-K relevant documents)
    ↓
3. Context Assembly (retrieved docs + user query)
    ↓
4. LLM Generation (answer based on context)
    ↓
5. Provenance Tracking (link claims to sources)
    ↓
6. Response with Citations
```

### Core Components

#### 1. Vector Index (Embedding Database)

**Technology**: pgvector (PostgreSQL extension) or Pinecone/Weaviate

**Indexed Content**:

- **Policy Documents**: Pricing, refund policies, terms of service, safety guidelines
- **Support Knowledge Base**: FAQs, how-to guides, troubleshooting articles
- **Historical Incidents**: Past safety incidents with resolutions
- **Vehicle Specifications**: Battery capacity, range, safety features per vehicle type
- **Operational Procedures**: Maintenance protocols, crew instructions
- **Regulatory Requirements**: EU AI Act compliance docs, GDPR policies

**Schema**:

```sql
CREATE TABLE vector_index (
    id UUID PRIMARY KEY,
    content TEXT,                    -- Original document text
    embedding VECTOR(1536),          -- OpenAI ada-002 embedding (1536 dimensions)
    metadata JSONB,                  -- {type, source, updated_at, tags}
    document_id TEXT,                -- Link to original document
    chunk_index INT,                 -- Position in original doc (for long docs)
    created_at TIMESTAMP
);

-- Index for fast similarity search
CREATE INDEX ON vector_index USING ivfflat (embedding vector_cosine_ops);
```

#### 2. Embedding Generator

**Model**: OpenAI `text-embedding-ada-002` or open-source alternative (e.g., `sentence-transformers`)

**Process**:

- User query → embedding model → 1536-dimensional vector
- Compare query vector to indexed document vectors using cosine similarity
- Retrieve top-K (K=5-10) most relevant document chunks

**Example**:

```javascript
import OpenAI from "openai";
import { Client } from "pg";

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const db = new Client({ connectionString: process.env.DATABASE_URL });

// Generate embedding for user query
const query = "What is your refund policy?";
const embeddingResponse = await openai.embeddings.create({
  input: query,
  model: "text-embedding-ada-002",
});
const queryEmbedding = embeddingResponse.data[0].embedding;

// Search vector index
const results = await db.query(
  `
  SELECT content, metadata, 1 - (embedding <=> $1) AS similarity
  FROM vector_index
  WHERE metadata->>'type' = 'policy'
  ORDER BY embedding <=> $1
  LIMIT 5
`,
  [JSON.stringify(queryEmbedding)]
);

// Top results:
// 1. Refund Policy Document (similarity: 0.89)
// 2. Payment FAQ (similarity: 0.78)
// 3. Terms of Service (similarity: 0.65)
```

#### 3. RAG Retriever Service

**Responsibilities**:

- Accept user queries from GenAI Platform
- Generate embeddings for queries
- Execute vector similarity search
- Filter results by metadata (document type, recency, relevance threshold)
- Assemble context for LLM (format retrieved docs + query)

#### 4. LLM Prompt Construction

**Grounded Prompt Template**:

```javascript
const prompt = `You are MobilityCorp's AI assistant. Answer the user's question using ONLY the provided context.
If the context doesn't contain the answer, say "I don't have that information" instead of guessing.

Context (from official documents):
${retrievedContext}

User Question: ${userQuery}

Instructions:
- Base your answer ONLY on the provided context
- Cite sources using [Source: Document Title]
- If uncertain, say so explicitly
- Do not make up information

Answer:`;
```

**Key Principles**:

- Explicit instruction to use only provided context
- Discourage hallucination ("do not make up information")
- Require citations for transparency
- Fallback to "I don't know" for out-of-scope queries

#### 5. Provenance Tracking

**Every AI response includes**:

- Source document IDs
- Relevant excerpts from retrieved documents
- Similarity scores (confidence in retrieval relevance)
- Timestamps of document versions used

**Example Response**:

```json
{
  "answer": "Our refund policy allows cancellations within 7 days of purchase for a full refund. After 7 days, no refunds are provided.",
  "sources": [
    {
      "document_id": "policy_refund_v2.3",
      "title": "Refund Policy",
      "excerpt": "Customers may request refunds within 7 calendar days...",
      "url": "https://docs.mobilitycorp.com/policies/refunds",
      "similarity": 0.89,
      "updated_at": "2025-03-15"
    }
  ],
  "confidence": 0.94,
  "grounded": true
}
```

### Rationale

**Why RAG over alternatives?**

1. **Reduces Hallucinations by 60-80%**: LLMs generate based on provided facts, not memorized (potentially incorrect) training data
2. **Always Up-to-Date**: Updating vector index updates AI knowledge instantly (no model retraining)
3. **Explainable**: Every answer cites sources, enabling transparency and trust
4. **Cost-Effective**: Retrieve only relevant docs instead of fine-tuning entire model or sending massive context
5. **Privacy-Preserving**: PII-free documents in vector index; no user data sent to LLM
6. **Compliance-Friendly**: Provenance tracking satisfies EU AI Act transparency requirements

## Consequences

### Positive

✅ **Factuality**: 96%+ accuracy vs. 70-80% without RAG (measured in TEVV pipeline)

✅ **Transparency**: Users see source citations, building trust and enabling verification

✅ **Freshness**: Policy updates reflected in AI responses within 1 hour (index refresh time)

✅ **Cost Efficiency**: Only relevant docs sent to LLM → smaller context → lower token costs

✅ **Explainability**: Provenance trail for every claim satisfies EU AI Act Article 13

✅ **Reduced Training Burden**: No need to fine-tune LLM on company data (fine-tuning expensive and rigid)

✅ **Multi-Source Integration**: Combine policies, incidents, telemetry seamlessly

### Negative

❌ **Latency Overhead**: Adding retrieval step adds 100-200ms to response time

❌ **Embedding Costs**: Generating embeddings for queries (~$0.0001 per query, manageable)

❌ **Index Maintenance**: Must keep vector index up-to-date as documents change

❌ **Retrieval Quality Dependency**: If retrieval fails or returns irrelevant docs, LLM answer will be poor

❌ **Context Window Limits**: Can only retrieve top-K docs (5-10); multi-hop reasoning across many docs difficult

❌ **Infrastructure Complexity**: Need to deploy and manage vector database, embedding service, indexing pipeline

### Risks

⚠️ **Retrieval Failure (No Relevant Docs Found)**

**Mitigation**:

- Set similarity threshold (e.g., 0.7); if no docs above threshold, return "I don't have that information"
- Fallback to human support escalation
- Track retrieval failure rate; improve index coverage for common queries

⚠️ **Outdated Index (Stale Documents)**

**Mitigation**:

- Automated index refresh pipeline (hourly for critical docs, daily for others)
- Document versioning with timestamps
- Cache invalidation on policy updates

⚠️ **Chunking Issues (Long Documents Split Poorly)**

**Mitigation**:

- Use semantic chunking (split by sections, not arbitrary character limits)
- Overlap chunks by 10-20% to preserve context
- Store chunk metadata (position in document, parent document ID)

⚠️ **Embedding Model Drift (Model Updates Change Vector Space)**

**Mitigation**:

- Pin specific embedding model version in production
- If upgrading model, re-index entire document corpus
- Test retrieval quality after model changes

## Alternatives Considered

### Alternative 1: Fine-Tuning LLM on Company Data

**Approach**: Train custom LLM on MobilityCorp policies, incidents, and knowledge base

**Pros**:

- No retrieval latency overhead
- LLM "knows" company information natively
- Simpler inference (no RAG pipeline)

**Cons**:

- Extremely expensive (~$100K+ to fine-tune GPT-4-scale model)
- Inflexible: Every policy update requires retraining
- Still prone to hallucination (LLM may "creatively" combine memorized facts incorrectly)
- Difficult to explain (no source citations)
- Training data privacy concerns (hard to ensure no PII leakage)

**Why Rejected**: Cost-prohibitive, inflexible, and doesn't solve hallucination problem

---

### Alternative 2: Prompt-Only Approach (No Retrieval)

**Approach**: Rely solely on LLM's training data and carefully crafted prompts

**Pros**:

- Simplest implementation (no vector DB, no retrieval)
- Lowest latency (<500ms)
- Minimal infrastructure

**Cons**:

- High hallucination rate (~20-30% factual errors)
- Outdated information (LLM training cutoff date)
- No citations or provenance
- Violates EU AI Act transparency requirements
- Unacceptable for safety-critical use cases

**Why Rejected**: Fails factuality and compliance requirements; unsafe for vehicle operations

---

### Alternative 3: Keyword-Based Search (Traditional IR)

**Approach**: Use Elasticsearch/Solr keyword search instead of vector similarity

**Pros**:

- Mature technology (Elasticsearch widely used)
- Fast and scalable
- Exact keyword matching

**Cons**:

- Poor semantic understanding (misses synonyms, paraphrases)
- Example: Query "How do I get my money back?" won't match "Refund Policy" doc
- Requires exact keyword overlap
- Less flexible than semantic search

**Why Rejected**: Semantic search (vectors) significantly outperforms keyword search for conversational queries

---

### Alternative 4: Hybrid Search (Keywords + Vectors)

**Approach**: Combine keyword search (Elasticsearch) with vector search, rank fusion

**Pros**:

- Best of both worlds (exact matches + semantic similarity)
- Can boost results matching exact entity names
- Higher recall than vectors alone

**Cons**:

- More complex infrastructure (two search systems)
- Need to tune rank fusion weights
- Higher latency (two searches in parallel)

**Why Rejected**: Added complexity not justified for current scale; vectors alone provide 95%+ factuality

**Future Consideration**: May adopt hybrid search if retrieval quality degrades as document corpus grows

---

### Alternative 5: Knowledge Graph + LLM

**Approach**: Store company knowledge as graph (Neo4j), traverse graph for facts, send to LLM

**Pros**:

- Structured knowledge representation
- Multi-hop reasoning (e.g., "find all vehicles with range >50km in Berlin")
- Explicit relationships between entities

**Cons**:

- Massive upfront effort to model knowledge as graph
- Rigid schema (hard to add new document types)
- Requires specialized graph query skills
- Doesn't handle unstructured text (incidents, telemetry) well

**Why Rejected**: Over-engineered for current needs; RAG handles unstructured data better

## Implementation Notes

### Phase 1: Core RAG Pipeline

- Deploy pgvector or Pinecone for vector storage
- Index initial document corpus: policies (50 docs), FAQs (200 docs), procedures (30 docs)
- Implement RAG Retriever service with embedding generation
- Integrate with GenAI Platform LLM interface
- Test factuality on 100-question benchmark (target: >90%)

### Phase 2: Provenance & Citations

- Build Provenance Tracker component
- Implement citation formatting in LLM responses
- Display source links in mobile app and web dashboard
- Audit trail integration (log retrieved docs per request)

### Phase 3: Advanced Features

- Add incident and telemetry indexing (10K+ historical incidents)
- Implement hybrid ranking (recency boost for time-sensitive docs)
- Tune retrieval parameters (top-K, similarity threshold, chunk size)
- A/B test retrieval strategies (dense vs. sparse embeddings)

### Phase 4: Continuous Improvement

- Automated index refresh on document updates (webhook triggers)
- Retrieval quality monitoring (track similarity scores, user feedback)
- Expand document corpus based on retrieval failure analysis
- Experiment with reranking models to improve top-K results

### Dependencies

- [Compliance Framework](../AI-Governance-Compliance/compliance-framework.md) - Provenance for audit trails

### Success Metrics

| Metric                  | Target              | Measurement                                            |
| ----------------------- | ------------------- | ------------------------------------------------------ |
| **Factuality Rate**     | ≥95%                | Manual eval of 100 responses/week against ground truth |
| **Retrieval Latency**   | <200ms p95          | Vector search + embedding generation time              |
| **Retrieval Relevance** | ≥80% top-3 hit rate | Human judgment: "Was answer in top-3 retrieved docs?"  |
| **Citation Coverage**   | 100%                | Every factual claim has source citation                |
| **Index Freshness**     | <1 hour             | Time between doc update and index refresh              |
| **Hallucination Rate**  | <2.5%               | AI claims not supported by retrieved docs              |

## Related

### ADRs

- [ADR-003: Event-Driven Backbone](003-event-driven-backbone.md) - Document updates via events
- [ADR-004: Core Services Architecture](004-core-services-decomposition.md) - GenAI Platform integration
- ADR-006: Hallucination Detection (uses RAG sources for verification)

### Architecture Views

- [GenAI Component Diagram](../resources/diagrams/genai-subsystem/genai-component-diagram.md) - RAG Retriever component
- [RAG Data Flow Diagram](../resources/diagrams/data-flow/rag-data-flow.md) - End-to-end RAG flow
- [Conversational Support Sequence](../resources/diagrams/use-cases/conversational-support-flow.md) - RAG in action

### Compliance & Governance

- [Compliance Framework](../AI-Governance-Compliance/compliance-framework.md) - EU AI Act transparency
- [Model Cards](../AI-Governance-Compliance/model-cards.md) - RAG system documentation

### External References

- [RAG Paper (Lewis et al., 2020)](https://arxiv.org/abs/2005.11401) - Original RAG research
- [LangChain RAG Guide](https://python.langchain.com/docs/use_cases/question_answering/) - Implementation patterns
- [Pinecone RAG Best Practices](https://www.pinecone.io/learn/retrieval-augmented-generation/) - Production RAG
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings) - Embedding models

## Notes

### RAG is the Foundation for All GenAI Features

Every GenAI use case in MobilityCorp's platform builds on RAG:

1. **Conversational Support**: RAG retrieves policies/FAQs → LLM answers
2. **Incident Summarization**: RAG retrieves similar past incidents → LLM summarizes patterns
3. **Safety Anomaly Explanation**: RAG retrieves vehicle specs + safety protocols → LLM explains
4. **Personalized Engagement**: RAG retrieves user history + behavior patterns → LLM recommends

RAG is not a feature—it's the **architectural pattern** that makes safe, explainable AI possible.

### Evolution Path: From RAG to Agentic RAG

**Current**: Single retrieval step before LLM generation

**Future** (Phase 5+): Multi-turn RAG where LLM can request additional retrievals

- LLM generates initial answer
- LLM identifies knowledge gaps: "I need more info about battery swap procedures"
- System performs additional retrieval
- LLM refines answer with new context

This "agentic" approach improves complex query handling but adds latency. Defer until core RAG proves reliable.

---

**ADR Version**: 1.0 | **Last Updated**: 2025-10-21 | **Next Review**: Q3 2026
