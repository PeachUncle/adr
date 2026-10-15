# ADR-010: Document Ingest and Chunking Strategy

## Status
Accepted

## Date
2025-12-29

## Context
The RAG system needs to process documentation content from the Docusaurus site and break it into manageable chunks for embedding and retrieval. The chunking strategy impacts retrieval quality, embedding performance, and user experience. The system must handle various document types and structures while maintaining semantic coherence.

## Decision
We will implement a paragraph-aware chunker with <=1500 character chunks and 200-character overlap. The ingest process will be idempotent with upsert logic based on content hash, and the payload will include full text content for accurate retrieval and display.

## Alternatives Considered
- **Fixed Character Chunks**: Simple 1000/2000 character splits
  - Pros: Simple implementation, predictable chunk sizes
  - Cons: May break semantic boundaries, poor context for retrieval
- **Sentence-Aware Chunking**: Split at sentence boundaries
  - Pros: Maintains sentence coherence, better semantic boundaries
  - Cons: May create very variable chunk sizes
- **Semantic Chunking**: Use embeddings to determine semantic boundaries
  - Pros: Best semantic coherence, optimal for retrieval
  - Cons: More complex implementation, higher processing overhead
- **Document-Section Chunking**: Split by document sections/headers
  - Pros: Maintains logical document structure
  - Cons: May create very large chunks, less granular retrieval

## Consequences
### Positive
- Balances context retention with embedding efficiency
- Overlap maintains semantic continuity across chunks
- Idempotent processing ensures safe re-runs
- Content-based hashing prevents duplicates
- Full text in payload enables accurate citation and display

### Negative
- May create chunks that break mid-sentence
- Overlap increases storage requirements
- Fixed size may not be optimal for all document types
- Complexity of overlap handling in retrieval

## References
- specs/002-rag-chatbot-gemini/plan.md
- specs/002-rag-chatbot-gemini/research.md
- specs/002-rag-chatbot-gemini/data-model.md