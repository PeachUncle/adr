# ADR-0001: Metadata Schema Design

## Status
Proposed

## Context
TextCollector needs to store and manage bibliographic metadata for documents. We need to design a metadata schema that:

- Supports standard bibliographic information (authors, titles, dates, etc.)
- Maintains backward compatibility with existing documents
- Allows for flexible querying and filtering
- Integrates with ChromaDB's metadata capabilities
- Follows established scholarly metadata standards where possible
- Balances comprehensiveness with simplicity

The schema will be used throughout the application for document indexing, searching, and citation formatting. It needs to support different document types (articles, books, etc.) while maintaining a consistent structure.

## Decision
We will implement a layered metadata schema with three distinct sections:

1. **Bibliographic Layer** - Core scholarly information:
   ```json
   {
     "title": "Document title",
     "authors": ["Author 1", "Author 2"],
     "date": "2023-05-15",
     "publication": "Journal or Publisher",
     "doi": "10.xxxx/xxxxx",
     "citation_key": "smith2023title",
     "type": "article|book|thesis|report|webpage|other"
   }
   ```

2. **Content Layer** - Information about the document content:
   ```json
   {
     "keywords": ["keyword1", "keyword2"],
     "abstract": "Brief document summary",
     "language": "en",
     "license": "CC-BY-4.0"
   }
   ```

3. **System Layer** - Technical and processing metadata:
   ```json
   {
     "source": "filename.txt",
     "chunk_id": "filename_0",
     "created_at": "2023-05-20T14:30:00Z",
     "embedding_model": "all-MiniLM-L6-v2",
     "chunk_size": 1000,
     "chunk_overlap": 100
   }
   ```

All fields will be optional except for "source" which is required for backward compatibility. The schema will be implemented as a flat dictionary to conform to ChromaDB's metadata storage capabilities.

## Consequences

### Positive
- Clear organization of metadata by purpose
- Optional fields allow for progressive enhancement
- Compliance with scholarly citation requirements
- Support for filtering and advanced querying
- Ability to format citations in different styles

### Negative
- More complex than the current simple metadata
- Additional storage requirements
- Potential performance impact with larger metadata
- Flat structure in ChromaDB may make querying more complex

### Neutral
- Will require updates to multiple components (CLI, core, storage)
- Existing documents will have minimal metadata until enhanced

## Alternatives Considered

1. **Minimal Extension Approach**
   - Add only a few critical fields (title, author, date)
   - Simpler but less powerful for academic use cases

2. **Full Dublin Core Implementation**
   - Adopt complete Dublin Core metadata standard
   - More comprehensive but excessive for many use cases

3. **Dynamic Schema**
   - Allow completely arbitrary metadata fields
   - Maximum flexibility but harder to standardize on

4. **Separate Metadata Store**
   - Keep bibliographic metadata in a separate database
   - Could enable more complex queries but adds complexity

## References
- [Dublin Core Metadata Initiative](https://dublincore.org/)
- [CSL Citation Specification](https://citationstyles.org/)
- [Schema.org Scholarly Article](https://schema.org/ScholarlyArticle)
- [BibTeX Field Types](https://en.wikipedia.org/wiki/BibTeX)
- [ChromaDB Metadata Documentation](https://docs.trychroma.com/)