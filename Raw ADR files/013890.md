# ADR-009: Metadata and Logging Database

## Status
Accepted

## Date
2025-12-29

## Context
The RAG system requires a database to store metadata about document chunks, usage logs, and optional reusable intelligence data. This includes chat session information, user interactions, and analytics data. The decision involves choosing between different database solutions that can handle both structured metadata and logging requirements.

## Decision
We will use Neon Serverless Postgres to store `doc_chunks` metadata, `usage_logs`, and optional `reusable_intel` data. This provides a reliable, serverless PostgreSQL solution that scales automatically with usage.

## Alternatives Considered
- **MongoDB Atlas**: Document database for flexible schema
  - Pros: Flexible schema, good for logging data, managed service
  - Cons: Additional learning curve, potentially higher cost for this use case
- **Supabase**: PostgreSQL with additional features and auth
  - Pros: Integrated platform, good developer experience
  - Cons: Additional dependencies, potential vendor lock-in
- **Local SQLite**: Simple file-based database
  - Pros: No external dependencies, simple setup
  - Cons: No serverless scaling, concurrency issues, persistence concerns
- **Firebase Firestore**: NoSQL database with real-time features
  - Pros: Real-time capabilities, good for session data
  - Cons: Different query patterns, potential cost at scale

## Consequences
### Positive
- Serverless scaling matches usage patterns
- Familiar SQL interface and PostgreSQL ecosystem
- Good for structured data like session logs and metadata
- Supports complex queries for analytics
- Reliable transaction support

### Negative
- Serverless billing model may be unpredictable
- Cold start latency for serverless instances
- Potential connection limits that need handling
- Vendor lock-in to Neon platform

## References
- specs/002-rag-chatbot-gemini/plan.md
- specs/002-rag-chatbot-gemini/data-model.md
- specs/002-rag-chatbot-gemini/research.md