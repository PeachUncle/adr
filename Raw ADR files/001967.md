# ADR-001: Two-DB Safety (bible_db RO; gematria RW)

## Status

Accepted

## Context

The project requires access to both application data (gematria analysis results) and reference biblical text data. These serve different purposes and have different data management requirements. The application database needs read-write access for storing analysis results, while the Bible database should remain read-only to preserve data integrity.

## Decision

Implement a two-database architecture with explicit safety measures:
1. `bible_db` - Read-only reference database with biblical text
2. `gematria` - Read-write application database for analysis results

## Rationale

- **Data Integrity**: Bible database remains immutable and authoritative
- **Safety**: Explicit RO adapter prevents accidental writes to reference data
- **Performance**: Separate databases allow optimized schemas for different use cases
- **Maintainability**: Clear separation of concerns between reference and application data

## Alternatives Considered

1. **Single Database**: Combine both datasets
   - Pros: Simpler architecture, single connection
   - Cons: Risk of corrupting reference data, schema conflicts, performance issues

2. **Views/Tables in Single DB**: Reference data as views
   - Pros: Single database management
   - Cons: Still risk of accidental modification, complex permissions

3. **External Reference Service**: API access to Bible data
   - Pros: Clean separation, external management
   - Cons: Network dependency, caching complexity, slower access

## Consequences

### Implementation Requirements
- Create RO database adapter that fails on write attempts
- Implement separate connection management for each database
- Add validation to prevent cross-database operations
- Update all database access code to specify target database

### Positive Outcomes
- Eliminates risk of corrupting biblical reference data
- Enables confident development with application data
- Supports future scaling of analysis capabilities
- Provides clear data ownership and access patterns

### Risks and Mitigations
- **Connection Complexity**: Multiple database connections (mitigated by connection pooling)
- **Migration Coordination**: Schema changes across databases (mitigated by separate migration scripts)
- **Development Overhead**: Explicit database specification (mitigated by clear naming conventions)
