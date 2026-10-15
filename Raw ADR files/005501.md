# ADR-001: RAG Architecture

## Status
**Accepted**

## Context
We need to build a local-first RAG (Retrieval-Augmented Generation) system for answering policy and product questions. The system must provide accurate answers with proper citations, work offline when needed, and be suitable for production deployment.

## Decision
We will implement a modular RAG architecture with the following components:

### Core Architecture

```
┌─────────────────┐    HTTP/3001    ┌──────────────────────┐
│   User Browser  │ ──────────────> │    Next.js Frontend  │
└─────────────────┘                 │  └─ Chat Component    │
                                    │  └─ Admin Panel      │
                                    └──────────┬───────────┘
                                               │ fetch /api/*
                                               ▼ HTTP/8000
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                              │
│  ┌─────────────────┐   ┌─────────────────┐   ┌───────────────┐  │
│  │  Input Validation│   │  Error Handling │   │  CORS Config  │  │
│  │  ├─ Pydantic     │   │  ├─ Structured  │   │  ├─ Dev: local │  │
│  │  ├─ XSS Filter   │   │  │   Logging    │   │  └─ Prod: env │  │
│  │  └─ Length Limit │   │  └─ Fallbacks   │   └───────────────┘  │
│  └─────────────────┘   └─────────────────┘                      │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    RAG Engine                               │ │
│  │  ┌──────────────┐ ┌─────────────┐ ┌──────────────────────┐  │ │
│  │  │   Ingest     │ │  Retrieve   │ │      Generate        │  │ │
│  │  │ ├─ Load /data │ │ ├─ Embed Q  │ │ ├─ OpenAI/Stub LLM  │  │ │
│  │  │ ├─ Chunk docs │ │ ├─ Search   │ │ ├─ Context prompt   │  │ │
│  │  │ └─ Thread-safe│ │ └─ LRU cache │ │ └─ PII masking     │  │ │
│  │  └──────────────┘ │ └─────────────┘ │ └──────────────────────┘  │ │
│  │                   └─────────────┘ └─────────────────────┘  │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────┬───────────────────────────────────────┘
                          ▼ upsert/search
┌─────────────────────────────────────────┐
│            Qdrant Vector DB             │
│  ┌─────────────────┐ ┌─────────────────┐ │
│  │   Collections   │ │    Persistence  │ │
│  │ ├─ policy_helper│ │ ├─ Docker Vol   │ │
│  │ └─ 384-dim vecs │ │ └─ Health check │ │
│  └─────────────────┘ └─────────────────┘ │
└─────────────────────────────────────────┘
        ▲ fallback to in-memory if unavailable
```

### Key Components

#### 1. **Embedding Layer**
- **Primary**: Deterministic local embedder for offline functionality
- **Fallback**: None required (deterministic by nature)
- **Dimension**: 384 dimensions
- **Features**: Feature hashing TF embeddings

#### 2. **Vector Store**
- **Primary**: Qdrant (Dockerized)
- **Fallback**: In-memory store (thread-safe)
- **Collections**: Single collection `policy_helper`
- **Persistence**: Docker volumes

#### 3. **LLM Provider**
- **Primary**: OpenAI (gpt-4o-mini)
- **Fallback**: Stub LLM (deterministic responses)
- **Selection**: Environment-based configuration

#### 4. **Caching System**
- **Retrieval Cache**: LRU, 1000 entries
- **Generation Cache**: LRU, 500 entries
- **Purpose**: Performance optimization

## Rationale

### 1. **Local-First Approach**
- **Benefit**: Works offline without external dependencies
- **Benefit**: No data privacy concerns
- **Cost**: No API costs for development/testing
- **Decision**: Aligns with security and privacy requirements

### 2. **Deterministic Embeddings**
- **Benefit**: Reproducible results across runs
- **Benefit**: No external API dependencies
- **Benefit**: Fast, low-latency embedding generation
- **Decision**: Essential for offline capability

### 3. **Fallback Architecture**
- **Benefit**: Graceful degradation when services fail
- **Benefit**: Development reliability
- **Benefit**: Production resilience
- **Decision**: Multi-layer fallback strategy

### 4. **Thread Safety**
- **Benefit**: Prevents race conditions in concurrent scenarios
- **Benefit**: Data consistency during ingestion
- **Benefit**: Production readiness
- **Decision**: Essential for multi-user scenarios

### 5. **Caching Strategy**
- **Benefit**: Improved response times
- **Benefit**: Reduced LLM API costs
- **Benefit**: Better user experience
- **Decision**: Bounded memory usage with performance gains

### 6. **Modular Design**
- **Benefit**: Easy to swap components (LLM, vector store)
- **Benefit**: Testing flexibility
- **Benefit**: Future extensibility
- **Decision**: Supports different deployment scenarios

## Consequences

### Positive
- **High Reliability**: System works offline and online
- **Good Performance**: Caching and optimized retrieval
- **Easy Testing**: Stub models enable deterministic testing
- **Future-Proof**: Modular architecture supports extensions
- **Cost-Effective**: Local operation reduces API usage

### Negative
- **Complexity**: More components to maintain
- **Memory Usage**: Caching requires bounds management
- **Development Time**: Fallback logic increases initial effort

## Implementation Notes

### Performance Targets
- **Retrieval Latency**: <20ms (cache hit)
- **Generation Latency**: <3s (OpenAI)
- **Memory Usage**: Bounded by cache sizes
- **Concurrent Users**: Thread-safe operations

### Security Considerations
- **Input Validation**: Length limits, XSS protection
- **API Key Management**: Environment variables only
- **CORS Configuration**: Environment-specific
- **PII Protection**: Built-in masking capabilities

### Monitoring & Observability
- **Health Endpoints**: Service status and configuration
- **Metrics Collection**: Latency, usage, cache statistics
- **Structured Logging**: JSON format with context
- **Performance Tracking**: Real-time system metrics

## Alternatives Considered

### 1. **Purely Remote Architecture**
- **Rejected**: Requires constant internet connectivity
- **Reasoning**: Conflicts with local-first requirement

### 2. **Single Vector Store (No Fallback)**
- **Rejected**: Single point of failure
- **Reasoning**: Reduced reliability for production use

### 3. **External Embedding Only**
- **Rejected**: Offline capability loss
- **Reasoning**: Local-first is a core requirement

### 4. **No Caching**
- **Rejected**: Poor performance for repeated queries
- **Reasoning**: User experience impact is significant

## Related Decisions

- **ADR-002**: LLM Provider Strategy
- **ADR-003**: Vector Store Selection
- **ADR-004**: Caching Implementation
- **ADR-005**: Input Validation Strategy

---

**Status**: Accepted
**Date**: 2025-01-14
**Author**: Development Team
**Reviewers**: Architecture Review