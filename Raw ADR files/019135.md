See the [technical decision index for all ADRs](../technical-decisions.md)

# ADR-005: Search Architecture and Performance

**Date**: September 3, 2025  
**Status**: Accepted  
**Context**: Need fast, accurate search across user items with mobile-optimized performance.

## Decision

**Phase 1**: PostgreSQL full-text search with tsvector  
**Phase 2**: Enhanced with trigram similarity and ranking  
**Future**: Elasticsearch if search requirements become complex

## Implementation

### Search Vector Generation

See the [Search Implementation Spec](../implementation-specs/search.md) for SQL triggers and pg_trgm setup.

### Search API Implementation

For REST endpoint contracts and payload schemas related to search (including filters and suggestions), see the [API specification](../implementation-specs/api-specification.md).

The Go service skeleton is available in the [Search Implementation Spec](../implementation-specs/search.md).

## Search Features

### Phase 1 Capabilities

- **Full-text Search**: Natural language queries across name and description
- **Category Filtering**: Filter by item categories
- **Location Filtering**: Filter by storage locations
- **Status Filtering**: Filter by item status (active, sold, etc.)
- **Ranking**: Relevance-based result ordering

### Phase 2 Enhancements

- **Fuzzy Matching**: Trigram similarity for typo tolerance
- **Auto-suggestions**: Query completion and suggestions
- **Advanced Filters**: Price range, date range, condition
- **Saved Searches**: User-defined search presets

## Performance Optimization

### Indexing Strategy

Index definitions live in the [Search Implementation Spec](../implementation-specs/search.md).

### Query Optimization

- **Prepared Statements**: All search queries use prepared statements
- **Result Limiting**: Maximum 100 results per search
- **Pagination**: Efficient offset-based pagination
- **Caching**: Redis cache for popular search terms

## Rationale

### PostgreSQL FTS Benefits

- **Performance**: Excellent performance for modest data sizes
- **Simplicity**: No additional infrastructure required
- **Integration**: Seamless integration with existing queries
- **Ranking**: Built-in relevance ranking

### Evolution Strategy

- **Start Simple**: PostgreSQL meets initial requirements
- **Monitor Performance**: Track search performance metrics
- **Gradual Migration**: Can add Elasticsearch without replacing PostgreSQL if needed

## Alternatives Considered

- **Elasticsearch from Start**: Rejected due to operational complexity for MVP
- **Application-Level Search**: Rejected due to performance and scalability concerns
- **External Search Service**: Rejected due to cost and data privacy concerns

## Consequences

### Positive

- Fast search performance for individual users
- Low operational overhead
- Strong integration with existing data
- Clear evolution path for advanced features

### Negative

- Limited to PostgreSQL search capabilities
- Potential scaling challenges with large datasets
- Complex query optimization for advanced filters

## Implementation Notes

- Set up proper GIN indexes for full-text search
- Implement search result caching in Redis
- Monitor search performance and optimize queries
- Plan for Elasticsearch migration if PostgreSQL limits are reached
- Implement search analytics to understand user behavior
