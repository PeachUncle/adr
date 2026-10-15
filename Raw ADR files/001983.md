# ADR-032: bible_db as Single Source of Truth (Roadmap)

## Status

Proposed

## Context

The current system maintains separate data models for biblical text reference (bible_db) and derived analysis results (gematria database). This creates synchronization challenges, data consistency issues, and complexity in maintaining referential integrity. Adopting bible_db as the single source of truth would ensure all derived data maintains direct traceability to authoritative biblical text.

## Decision

Adopt bible_db schema as the single source of truth across all nodes and edges. All derived data must maintain foreign key relationships to bible_db identifiers, ensuring complete traceability and data consistency.

## Rationale

- **Data Integrity**: Single authoritative source eliminates synchronization issues
- **Traceability**: All derived data maintains direct links to source text
- **Consistency**: Unified data model prevents conflicting representations
- **Maintainability**: Single schema reduces complexity and maintenance overhead
- **Auditability**: Complete lineage from source text through all transformations

## Alternatives Considered

1. **Current Architecture**: Separate databases with manual synchronization
   - Pros: Existing implementation, immediate functionality
   - Cons: Data drift, synchronization complexity, referential integrity issues

2. **Unified Database**: Merge both datasets into single database
   - Pros: Single connection, easier queries
   - Cons: Schema complexity, potential performance issues, mixing reference and derived data

3. **API-based Access**: bible_db accessed through service layer
   - Pros: Clean abstraction, service evolution
   - Cons: Network overhead, caching complexity, additional infrastructure

## Consequences

### Implementation Requirements
- Extend bible_db schema to support derived data relationships
- Create compatibility views for existing consumers
- Implement dual-export capability during transition
- Update all pipeline components to reference bible_db IDs
- Add comprehensive referential integrity constraints

### Positive Outcomes
- Complete data lineage and traceability
- Elimination of data synchronization issues
- Simplified architecture and maintenance
- Enhanced data consistency and integrity
- Better support for advanced analytics and reporting

### Risks and Mitigations
- **Consumer Breakage**: Existing consumers may break during transition (mitigated by compatibility views)
- **Performance Impact**: Additional joins may affect query performance (mitigated by indexing and optimization)
- **Migration Complexity**: Large-scale data migration required (mitigated by phased approach)

### Timeline
- **M1**: Data model PRD and schema design
- **M2**: Compatibility views and dual-export implementation
- **M3**: Staged cut-over with rollback capability
- **M4**: UI and consumer migration completion

Non-goals: Immediate cut-over. Current pipeline remains the production path during transition.