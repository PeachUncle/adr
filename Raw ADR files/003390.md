# ADR-001: Embedding Pipeline Architecture Decision

**Status**: Accepted
**Date**: 2025-12-16

## Context

For the embedding pipeline feature, we need to make key architectural decisions about how to extract content from Docusaurus URLs, generate embeddings, and store them for RAG-based retrieval. The system needs to handle the specific requirements of processing documentation sites like https://sadiaism.github.io/Q4-Hackathon-book-write/ and make the content searchable through vector similarity.

## Decision

We will implement a single-file Python solution (main.py) with the following architecture:

**Technology Stack:**
- **Language**: Python 3.11
- **Embedding Service**: Cohere's embed-multilingual-v3.0 model
- **Vector Database**: Qdrant
- **Web Scraping**: requests + BeautifulSoup4
- **Package Management**: UV

**System Design:**
- `get_all_urls`: Function to crawl and discover all URLs from a base Docusaurus site
- `extract_text_from_url`: Function to extract clean text content from a single URL
- `chunk_text`: Function to split text into overlapping chunks to preserve context
- `embed`: Function to generate vector embeddings using Cohere API
- `create_collection`: Function to set up Qdrant collection named `rag_embedding`
- `save_chunks_to_qdrant`: Function to store embeddings with metadata in Qdrant
- `main`: Orchestrates the entire pipeline execution

## Consequences

**Positive:**
- Cohere provides high-quality embeddings with good multilingual support
- Qdrant offers efficient vector similarity search with good performance
- Single-file implementation simplifies deployment and maintenance
- Modular function design allows for easy testing and debugging
- Open-source tools (Qdrant) provide flexibility for self-hosting

**Negative:**
- Depends on external API (Cohere) which may have rate limits and costs
- Single-file approach may become unwieldy as functionality grows
- Requires proper error handling for network-dependent operations
- Potential data privacy concerns with sending content to external embedding service

## Alternatives

**Alternative 1: OpenAI embeddings + Pinecone**
- Use OpenAI's text-embedding-ada-002 model with Pinecone vector database
- Pros: Mature ecosystem, good documentation
- Cons: Higher cost, vendor lock-in with both embedding and vector DB

**Alternative 2: Local embeddings + FAISS**
- Use sentence-transformers models locally with FAISS vector database
- Pros: No external dependencies, better privacy control
- Cons: Requires more infrastructure management, potentially lower quality embeddings

**Alternative 3: Multi-file modular approach**
- Split functionality across multiple Python modules
- Pros: Better separation of concerns, easier maintenance
- Cons: Contradicts requirement for single-file implementation

## References

- specs/003-embedding-pipeline/spec.md
- specs/003-embedding-pipeline/plan.md
- specs/003-embedding-pipeline/research.md