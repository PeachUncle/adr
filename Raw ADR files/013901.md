---
title: Migration from OpenAI API to Google Gemini API
date: 2024-12-19
status: accepted
---

## Context

The Physical AI & Humanoid Robotics textbook project was initially built using OpenAI's GPT-4o API for the RAG chatbot functionality. The project requires an LLM API for:
- Chat completions (answering student questions)
- Text embeddings (document retrieval)
- Content personalization (adapting explanations to user backgrounds)
- Translation (Urdu language support)

However, the OpenAI API key is not available for this implementation, while a Gemini API key is available.

## Decision

We will migrate from OpenAI API to Google's Gemini API for all LLM functionality:

| Functionality | OpenAI | Gemini |
|--------------|--------|--------|
| Chat Model | gpt-4o | gemini-1.5-flash |
| Embedding Model | text-embedding-3-small | text-embedding-004 |
| SDK | openai>=1.12.0 | google-generativeai>=0.8.0 |
| API Key | OPENAI_API_KEY | GEMINI_API_KEY |

## Rationale

### Options Considered

1. **Continue with OpenAI API**
   - Pros: No code changes needed
   - Cons: API key not available, project non-functional

2. **Use Local LLM (Ollama)**
   - Pros: No API key needed, privacy
   - Cons: Significant infrastructure setup, performance concerns

3. **Migrate to Gemini API** ✅ Selected
   - Pros: Available API key, similar functionality, good performance
   - Cons: Code changes required, embedding dimension differences

4. **Use Claude API**
   - Pros: High quality responses
   - Cons: Different API key setup, no native embeddings

### Trade-offs

**Gemini API Advantages:**
- Available API key (GEMINI_API_KEY)
- Similar chat completion interface
- Built-in function calling support
- Good streaming capabilities
- Competitive performance for educational content
- Native embedding model

**Gemini API Disadvantages:**
- Different API interface requires code changes
- Potentially different response quality/style
- Different embedding model dimensions (768 vs 1536)
- Requires document re-ingestion

### Technical Impact

| Component | Change Required |
|-----------|----------------|
| requirements.txt | Replace openai with google-generativeai |
| config.py | OPENAI_API_KEY → GEMINI_API_KEY |
| embedding_service.py | Use Gemini text-embedding-004 |
| chat.py | Import new Gemini agent |
| content.py | Use Gemini for personalization/translation |
| .env | Update environment variable |

### Compatibility Preserved

- Frontend API interface unchanged
- Same streaming response format (SSE)
- Same request/response models
- Same authentication mechanism
- Same logging to Neon Postgres

## Consequences

### Positive

- Project becomes functional with available API key
- Maintains all hackathon requirements (100 points RAG + 50 bonus personalization + 50 bonus translation)
- Similar performance characteristics
- Reduced dependency on OpenAI ecosystem
- Single provider for both chat and embeddings

### Negative

- Response style may differ slightly from GPT-4o
- Embedding dimensions change (768 vs 1536) - requires Qdrant reindexing
- Additional testing required for quality assurance
- Team needs to learn Gemini API patterns

### Mitigation

- Thorough testing of all chat functionality
- Re-ingestion of documents with new embeddings
- Quality comparison between OpenAI and Gemini responses
- Adjust system prompts if response quality differs

## Implementation

### Files Modified

```
rag_chatbot/
├── requirements.txt              # openai → google-generativeai
├── .env                          # OPENAI_API_KEY → GEMINI_API_KEY
├── src/
│   ├── core/
│   │   └── config.py            # Update API key config
│   ├── services/
│   │   ├── embedding_service.py # Gemini embeddings
│   │   └── gemini_agent_service.py # New Gemini agent (created)
│   └── api/
│       ├── chat.py              # Use Gemini agent
│       └── content.py           # Gemini for personalization/translation
```

### Validation Criteria

- [x] Backend starts successfully with Gemini API
- [x] Chat endpoint returns streaming responses
- [x] Personalization endpoint works with user backgrounds
- [x] Translation endpoint produces Urdu translations
- [x] Document ingestion works with new embeddings
- [x] Frontend integration remains functional

## Related

- Spec: `specs/003-gemini-api-migration/spec.md`
- Plan: `specs/003-gemini-api-migration/plan.md`
- Tasks: `specs/003-gemini-api-migration/tasks.md`
- Research: `specs/003-gemini-api-migration/research.md`
- Hackathon Requirements: RAG Chatbot Development (100 points)
- Content Personalization (50 bonus points)
- Urdu Translation (50 bonus points)
