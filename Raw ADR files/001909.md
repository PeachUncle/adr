# ADR-0002: RAG System with Gemini 2.5 Flash and Qdrant

**Date**: 2025-12-12
**Status**: Accepted
**Context**: 001-ai-native-textbook-platform
**Decision Makers**: Factual Verifier Agent, Content Implementor

## Context

The platform requires an intelligent RAG (Retrieval-Augmented Generation) chatbot that:
- Answers questions based ONLY on textbook content
- Provides accurate citations to specific chapters/sections
- Maintains conversation context
- Responds within 2 seconds (90% of queries)

## Decision

We will implement RAG using:
1. **Gemini 2.5 Flash** (via OpenAI-compatible SDK) for LLM generation
2. **Qdrant Cloud** (Free Tier) for vector storage
3. **OpenAI `text-embedding-3-small`** for embeddings
4. **Neon PostgreSQL** for conversation history storage

## Rationale

### LLM Selection: Why Gemini 2.5 Flash?

**Options Considered**:
- **Option 1: OpenAI GPT-4**
  - ✅ Excellent quality
  - ❌ Expensive ($0.03/1K tokens)
  - ❌ Rate limits restrictive for free tier
- **Option 2: OpenAI GPT-3.5-Turbo**
  - ✅ Fast
  - ✅ Affordable ($0.002/1K tokens)
  - ❌ Lower quality for complex technical content
- **Option 3: Gemini 2.5 Flash (Selected)**
  - ✅ **Free tier with high limits** (1500 requests/day)
  - ✅ **Fast response time** (optimized for low latency)
  - ✅ **OpenAI SDK compatible** (drop-in replacement)
  - ✅ Good quality for technical Q&A
  - ✅ Generous rate limits for hackathon/MVP

**Winner**: Gemini 2.5 Flash provides best cost/performance ratio for MVP.

### Vector Database: Why Qdrant?

**Options Considered**:
- **Option 1: Qdrant Cloud (Selected)**
  - ✅ Free tier: 1GB storage (sufficient for textbook)
  - ✅ Excellent Python SDK
  - ✅ Fast similarity search
  - ✅ Easy metadata filtering
  - ❌ Requires cloud dependency
- **Option 2: FAISS (Local)**
  - ✅ No external dependency
  - ✅ Fast
  - ❌ No managed hosting on Vercel
  - ❌ Harder to persist state
- **Option 3: Pinecone**
  - ✅ Good developer experience
  - ❌ Free tier very limited
  - ❌ More expensive at scale

**Winner**: Qdrant Cloud offers best free tier and Python integration.

### Embedding Model: Why text-embedding-3-small?

- **Dimensions**: 1536 (fits Qdrant free tier limits)
- **Cost**: $0.00002/1K tokens (very affordable)
- **Quality**: High for technical content
- **Speed**: Fast inference
- **Alternative Considered**: Gemini embeddings (not as mature)

## Implementation Architecture

```
┌─────────────────┐
│  User Question  │
└────────┬────────┘
         │
         v
┌─────────────────────────────────────┐
│  1. Embed Query                     │
│     (text-embedding-3-small)        │
└────────┬────────────────────────────┘
         │
         v
┌─────────────────────────────────────┐
│  2. Retrieve Relevant Chunks        │
│     (Qdrant similarity search)      │
│     top_k=5, threshold=0.7          │
└────────┬────────────────────────────┘
         │
         v
┌─────────────────────────────────────┐
│  3. Augment with Context            │
│     - Retrieved chunks              │
│     - Conversation history (last 5) │
│     - System prompt                 │
└────────┬────────────────────────────┘
         │
         v
┌─────────────────────────────────────┐
│  4. Generate Response               │
│     (Gemini 2.5 Flash)              │
│     - Answer question               │
│     - Extract citations             │
└────────┬────────────────────────────┘
         │
         v
┌─────────────────────────────────────┐
│  5. Store in Neon PostgreSQL        │
│     (chat_sessions, chat_messages)  │
└─────────────────────────────────────┘
```

## Consequences

### Positive

- **Cost-Effective**: Free tier sufficient for 1000+ users
- **Fast Responses**: Gemini Flash optimized for low latency
- **Easy Integration**: OpenAI SDK compatibility simplifies code
- **Scalable**: Can upgrade Qdrant/Gemini plans if needed
- **Good Developer Experience**: Well-documented SDKs

### Negative

- **Vendor Lock-In**: Dependent on Qdrant Cloud and Gemini availability
- **Free Tier Limits**:
  - Qdrant: 1GB storage (~100K vectors)
  - Gemini: 1500 requests/day
- **Network Dependency**: Requires internet for vector search and LLM calls

### Neutral

- Need to monitor usage against free tier limits
- Can switch to self-hosted Qdrant if needed
- Gemini quality acceptable but not state-of-art (GPT-4 level)

## Performance Targets

- **Query Response Time**: < 2 seconds (90th percentile)
- **Embedding Generation**: ~100ms per query
- **Vector Search**: ~50ms per query
- **LLM Generation**: ~1-1.5 seconds
- **Total Budget**: ~2 seconds ✅

## Content Chunking Strategy

- **Chunk Size**: 512-1024 tokens
- **Overlap**: 50 tokens
- **Semantic Boundaries**: Preserve paragraph structure
- **Metadata**: chapter_id, chapter_title, file_path, chunk_index
- **Estimated Chunks**: 3000-5000 for 13-week curriculum

## System Prompt

```
You are a teaching assistant for the Physical AI & Humanoid Robotics course.

Answer questions using ONLY the provided textbook content below.

Always cite specific chapter sections in your response (e.g., "Chapter 8, Section 2").

If the question is not covered in the provided content, say:
"I can only answer questions about Physical AI and Humanoid Robotics content from this textbook."

Provided Content:
[Retrieved chunks inserted here]

Question: [User question]
```

## Compliance

- ✅ **FR-007**: Chatbot uses only textbook content (RAG-based retrieval)
- ✅ **FR-008**: Citations to specific chapter sections
- ✅ **FR-010**: Off-topic question rejection
- ✅ **FR-011**: Conversation context maintained
- ✅ **SC-002**: 90% accurate responses within 2 seconds

## Migration Path

If free tiers are exceeded:
1. **Qdrant**: Upgrade to paid plan ($25/month for 10GB)
2. **Gemini**: Use API key with billing enabled
3. **Alternative**: Switch to self-hosted Qdrant + OpenAI GPT-3.5-Turbo

## Related Decisions

- ADR-0001: Monorepo Architecture
- ADR-0003: Citation Extraction Strategy

---

**Status**: ✅ **ACTIVE** - Currently implemented with Gemini + Qdrant
