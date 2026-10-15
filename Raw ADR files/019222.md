# ADR-0001: Local JSON vs SQLite for Data Storage

**Status**: Accepted
**Date**: 2025-08-05
**Context**: Travel Memory Journal requires local data storage for travel memories with zero cloud dependencies and simple deployment.

## Problem Statement
What storage mechanism should we use for persisting travel memories locally on macOS with requirements for simplicity, zero dependencies, and ability to handle 1000+ memories efficiently?

## Decision Drivers
- **Business Requirements**: Local-only storage, zero cloud dependencies, simple user setup
- **Technical Constraints**: Single user application, 1000+ memories (~1MB total), macOS deployment
- **Team Constraints**: Rapid MVP development (<1 hour), minimal complexity
- **Non-Functional Requirements**: App launch <3s, memory search <2s, data integrity

## Options Considered

### Option 1: Local JSON Files (Recommended)
**Pros**:
- Zero external dependencies - pure Python stdlib
- Human-readable and debuggable data format
- Simple backup and restore (copy files)
- Perfect alignment with MVP timeline requirements
- Easy to implement atomic writes with file operations
- No database setup or migration complexity

**Cons**:
- Linear search performance for large datasets
- Manual data integrity management
- No built-in indexing or query optimization

**Implementation Effort**: S (Small)
**Operational Complexity**: Low

### Option 2: SQLite Database
**Pros**:
- Structured querying and indexing capabilities
- ACID compliance and data integrity guarantees
- Better performance for complex queries and large datasets
- Built-in backup and recovery mechanisms

**Cons**:
- Additional dependency and complexity
- Database schema management and migrations
- Overkill for simple CRUD operations on 1000 records
- Slower MVP development cycle

**Why Not Chosen**: Adds unnecessary complexity for MVP requirements and 1000-record dataset size

### Option 3: Embedded Key-Value Store (e.g., LMDB)
**Pros**:
- High performance for read/write operations
- Memory-mapped file access

**Cons**:
- External dependency requirement
- Binary format reduces debuggability
- Unnecessary complexity for use case

**Why Not Chosen**: Overkill for dataset size and adds deployment complexity

## Decision
We will use **Local JSON Files** for data storage.

**Rationale**: JSON storage best serves our MVP objectives by eliminating dependencies, enabling rapid development, and providing sufficient performance for our 1000-memory dataset. The human-readable format aligns with our local-first, user-controlled data philosophy.

## Consequences
**Positive**:
- Fastest path to MVP with zero setup complexity
- Complete user control over data format and location
- Easy debugging and data inspection by users
- Simple backup strategy (file copy)
- No database corruption or schema migration issues

**Negative**:
- Linear search performance may degrade with very large datasets (>10k memories)
- Manual implementation of data integrity checks
- No built-in query optimization or indexing

**Implementation Notes**:
- Implement atomic file writes using temp files and rename operations
- Add automatic backup before each write operation
- Use Pydantic models for data validation and serialization
- Consider in-memory caching for frequently accessed data
- Monitor performance and consider SQLite migration if dataset grows beyond 5k memories

## Migration Path
If performance becomes an issue with larger datasets:
1. Implement SQLite storage layer with same Pydantic models
2. Add migration utility to convert JSON to SQLite
3. Maintain JSON export capability for data portability