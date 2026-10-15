# 3. Retriever Module Implementation Approach

Date: 2025-10-15

## Status

Accepted

## Context

The current OpenAlex Explorer implementation uses a modular approach with separate retriever classes for each entity type:
- [OpenAlexPublicationRetriever](file:///Users/max/Documents/code/openalex-mcp-tool/openalex_modules/openalex_publication_retriever.py)
- [OpenAlexAuthorRetriever](file:///Users/max/Documents/code/openalex-mcp-tool/openalex_modules/openalex_author_retriever.py)
- [OpenAlexConceptRetriever](file:///Users/max/Documents/code/openalex-mcp-tool/openalex_modules/openalex_concept_retriever.py)

As we implement the additional entity types (Topics, Institutions, Sources, Publishers, Funders), we need to decide on the implementation approach for the new retriever modules.

## Decision

We will follow the existing pattern of creating separate retriever classes for each new entity type:

### Implementation Pattern
1. Create dedicated retriever modules in the [openalex_modules](file:///Users/max/Documents/code/openalex-mcp-tool/openalex_modules) directory:
   - `openalex_topic_retriever.py`
   - `openalex_institution_retriever.py`
   - `openalex_source_retriever.py`
   - `openalex_publisher_retriever.py`
   - `openalex_funder_retriever.py`

2. Each retriever will follow the established pattern:
   - Inherit from a common base pattern (though not formally enforced)
   - Implement search methods specific to the entity type
   - Include data processing and standardization logic
   - Provide metrics calculation where relevant
   - Use the shared [OpenAlexAPIClient](file:///Users/max/Documents/code/openalex-mcp-tool/slr_modules/api_clients.py#L18-L18) for API interactions

3. Consistency considerations:
   - Maintain similar method signatures across retrievers where appropriate
   - Use consistent data structure formats for returned data
   - Follow existing error handling and logging patterns
   - Apply similar naming conventions

## Consequences

### Positive
- Consistent with existing codebase architecture
- Clear separation of concerns for each entity type
- Easier to maintain and extend individual modules
- Parallel development possible for different entity types
- Familiar pattern for developers working on the project

### Negative
- Potential code duplication across similar entity types
- More files to manage as entity count increases
- May require updates to multiple modules for cross-cutting concerns

### Neutral
- Aligns with established project patterns
- No significant architectural changes required
- Maintains existing dependency structure

## Alternatives Considered

1. **Generic retriever with entity configuration**
   - Pro: Reduces code duplication, single implementation for all entities
   - Con: More complex, less explicit, harder to customize per entity type

2. **Base retriever class with inheritance**
   - Pro: Shared functionality through inheritance, reduces duplication
   - Con: More complex hierarchy, potential for tight coupling

3. **Functional approach without classes**
   - Pro: Simpler, more straightforward
   - Con: Less organized, harder to maintain as complexity grows

## Related ADRs

- [1. Enhance OpenAlex MCP Implementation](file:///Users/max/Documents/code/openalex-mcp-tool/docs/adr/001-enhance-openalex-mcp-implementation.md)

## Notes

This decision maintains architectural consistency while allowing for the implementation of the planned enhancements. The modular approach has proven effective for the existing retrievers and will scale well as we add the additional entity types.