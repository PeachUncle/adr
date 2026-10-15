# ADR-002: Multi-Agent RAG Architecture

## Status

**Accepted** - January 2026

## Context

Sentinel RFP's primary value is generating high-quality RFP responses using AI. We need to decide the architecture for AI-powered response generation:

1. **Monolithic Prompt**: Single LLM call with all context
2. **Simple RAG**: Retrieve → Generate pattern
3. **Multi-Agent RAG**: Specialized agents with orchestration

### Requirements

- Complex queries require multi-step reasoning
- Responses need citations and traceability
- Trust scores must be explainable
- Different tasks need different capabilities
- Cost optimization is critical (LLM costs)
- Must handle 200+ page RFP documents

## Decision

**Implement Multi-Agent RAG architecture with specialized agents orchestrated by a conductor.**

### Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MULTI-AGENT RAG ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│                              USER QUERY                              │
│                                  │                                   │
│                                  ▼                                   │
│                         ┌───────────────┐                           │
│                         │ ORCHESTRATOR  │                           │
│                         │   (Conductor) │                           │
│                         └───────┬───────┘                           │
│                                 │                                    │
│            ┌────────────────────┼────────────────────┐              │
│            │                    │                    │              │
│            ▼                    ▼                    ▼              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │ KNOWLEDGE AGENT │  │  PLANNER AGENT  │  │ REASONING AGENT │     │
│  │                 │  │                 │  │                 │     │
│  │ • Vector search │  │ • Query decomp  │  │ • Response gen  │     │
│  │ • Full-text     │  │ • Search plan   │  │ • Synthesis     │     │
│  │ • Reranking     │  │ • Parallelization│ │ • Tone adapt   │     │
│  └─────────────────┘  └─────────────────┘  └────────┬────────┘     │
│                                                      │              │
│                                                      ▼              │
│                                            ┌─────────────────┐      │
│                                            │ REVIEWER AGENT  │      │
│                                            │                 │      │
│                                            │ • Fact check    │      │
│                                            │ • Trust score   │      │
│                                            │ • Citation      │      │
│                                            └─────────────────┘      │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Agent Specifications

#### 1. Orchestrator (Conductor)

- **Role**: Route queries, manage agent lifecycle, merge results
- **Model**: Claude 3.5 Sonnet (fast, good reasoning)
- **Responsibilities**:
  - Classify query complexity
  - Determine agent sequence
  - Handle failures and retries
  - Aggregate final response

#### 2. Knowledge Agent

- **Role**: Information retrieval from knowledge base
- **Model**: None (algorithmic)
- **Components**:
  - pgvector for semantic search
  - Meilisearch for full-text
  - Cross-encoder reranker
- **Output**: Ranked document chunks with relevance scores

#### 3. Planner Agent

- **Role**: Decompose complex queries into sub-queries
- **Model**: Claude 3.5 Sonnet
- **Example**:

```
Input: "Describe your security approach and GDPR compliance"

Output Plan:
1. Search: "security policy architecture"
2. Search: "SOC2 ISO27001 certifications"
3. Search: "GDPR data protection policy"
4. Search: "data processing agreements"
5. Synthesize: Combine into cohesive response
```

#### 4. Reasoning Agent

- **Role**: Generate final response from retrieved context
- **Model**: Claude 3.5 Sonnet (200K context)
- **Responsibilities**:
  - Process large context windows
  - Maintain consistent terminology
  - Apply win themes
  - Generate structured response

#### 5. Reviewer Agent

- **Role**: Quality assurance and scoring
- **Model**: Claude 3.5 Sonnet
- **Output**:
  - Trust Score (0-100)
  - Factual verification results
  - Citation mappings
  - Improvement suggestions

### Implementation Approach

```typescript
// No LangChain dependency - custom implementation
class AgentOrchestrator {
  async processQuery(query: QueryInput): Promise<AgentResponse> {
    // 1. Classify query complexity
    const complexity = await this.classifyQuery(query);

    // 2. Simple queries: direct to Knowledge + Reasoning
    if (complexity === 'simple') {
      const context = await this.knowledgeAgent.search(query);
      return this.reasoningAgent.generate(query, context);
    }

    // 3. Complex queries: full pipeline
    const plan = await this.plannerAgent.decompose(query);
    const contexts = await Promise.all(plan.searches.map((s) => this.knowledgeAgent.search(s)));

    const response = await this.reasoningAgent.generate(query, this.mergeContexts(contexts));

    // 4. Always run reviewer
    return this.reviewerAgent.review(response);
  }
}
```

## Consequences

### Positive

- **Specialization**: Each agent optimized for its task
- **Explainability**: Clear trace of decision path
- **Flexibility**: Easy to swap/upgrade individual agents
- **Quality**: Multi-pass review improves accuracy
- **Cost control**: Can use smaller models for simple tasks

### Negative

- **Latency**: Multiple LLM calls increase response time
- **Complexity**: More moving parts to maintain
- **Cost**: More LLM calls (mitigated by caching)
- **Debugging**: Harder to trace issues across agents

### Mitigations

- Implement response streaming for perceived performance
- Cache intermediate results aggressively
- Build comprehensive logging/tracing
- Start simple, add agents incrementally

## Cost Optimization

| Strategy             | Impact                            |
| -------------------- | --------------------------------- |
| Semantic caching     | -40% LLM calls                    |
| Query classification | -30% (skip planner for simple)    |
| Batch embeddings     | -60% embedding costs              |
| Model tiering        | -25% (GPT-3.5 for classification) |

## Related ADRs

- ADR-006: LLM Provider Abstraction
- ADR-001: Event-Driven Architecture

## References

- [Anthropic Claude Best Practices](https://docs.anthropic.com/claude/docs/prompt-engineering)
- [Multi-Agent Systems in LLM Applications](https://www.anthropic.com/research)
