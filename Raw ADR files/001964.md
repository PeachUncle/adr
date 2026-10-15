# ADR-001: Two-Database Safety Architecture

## Status

Accepted

## Context

The Gematria system needs to integrate with existing biblical data while maintaining safety and performance. Key requirements:

- Access to comprehensive biblical text and linguistic data
- Safe separation between generated analysis and source data
- Performance optimization for different access patterns
- Clear data ownership and responsibility boundaries

## Decision

Implement a two-database architecture:

- **gematria** (read-write): Analysis results, generated insights, network data
- **bible_db** (read-only): Source biblical text, Hebrew/Greek words, linguistic data

## Rationale

### Safety Benefits

1. **Data Protection**: Source biblical data cannot be accidentally modified
2. **Backup Safety**: Analysis database can be rebuilt without touching source data
3. **Audit Trail**: Clear separation of generated vs source data
4. **Rollback Safety**: Failed analyses don't corrupt source data

### Performance Benefits

1. **Optimized Access Patterns**: Read-write DB tuned for analysis workloads
2. **Read-Only Optimizations**: Source DB can use read-optimized indexes
3. **Connection Pooling**: Different pools for different access patterns
4. **Caching**: Analysis results can be cached without affecting source data

### Maintenance Benefits

1. **Independent Scaling**: Databases can be scaled independently
2. **Backup Strategies**: Different backup frequencies and strategies
3. **Schema Evolution**: Analysis schema can evolve without affecting source
4. **Migration Safety**: Analysis DB migrations don't risk source data

## Alternatives Considered

### Single Database with Permissions

- **Pros**: Simpler architecture, single connection
- **Cons**: Risk of accidental source data modification, complex permissions
- **Rejected**: Safety concerns outweigh simplicity benefits

### Embedded SQLite for Analysis

- **Pros**: Simple, no server setup, file-based
- **Cons**: No concurrent access, limited performance, data sharing issues
- **Rejected**: Need concurrent access and performance for analysis workflows

### API-Only Access to Source Data

- **Pros**: Clean separation, versioned API
- **Cons**: Additional complexity, potential performance issues, dependency on external service
- **Not Chosen**: Prefer direct database access for performance

## Consequences

### Positive

- High safety for source biblical data
- Optimized performance for different workloads
- Clear data ownership boundaries
- Independent scalability and maintenance

### Negative

- More complex setup and configuration
- Two connection strings to manage
- Additional monitoring and maintenance overhead
- Slightly more complex application code

### Implementation Requirements

- Connection management for two databases
- Proper error handling for read-only violations
- Migration scripts for both databases
- Monitoring and alerting for both databases
- Backup and recovery procedures for both

## Schema Design

### Gematria Database (Read-Write)

- **concepts**: Core analysis results and metadata
- **books**: Book-level integration status
- **verse_noun_occurrences**: Bridge table to bible_db
- **network_metrics**: Generated network analysis
- **integration_log**: Audit trail of operations

### Bible Database (Read-Only)

- **bible.verses**: Complete biblical text (~116K verses)
- **bible.hebrew_ot_words**: Hebrew analysis (~283K words)
- **bible.hebrew_entries**: Lexicon/dictionary
- **bible.verse_embeddings**: Semantic search vectors

## Migration Strategy

1. Set up bible_db first (read-only)
2. Create gematria schema with foreign key references to bible_db
3. Implement safety triggers to prevent bible_db modification
4. Add monitoring for cross-database integrity

## Monitoring

- Connection health for both databases
- Query performance metrics
- Data consistency checks
- Backup status monitoring
- Read-only violation alerts

## Related ADRs

- ADR-000: State persistence in gematria DB
- ADR-003: Cross-database transaction handling (future)
