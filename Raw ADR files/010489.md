# ADR-002: Database Technology

## Status
Accepted

## Context
The linz.community platform needs a database that supports the event coordination features while aligning with operational simplicity goals. The expected usage patterns include:
- Moderate write volume (events created/updated by organizers)
- Mostly read operations (viewing calendar, browsing venues)
- Complex relationships (communities, events, venues, organizers)
- Full-text search capabilities (speaker opportunities, venues)
- Data export requirements (GDPR compliance)

Expected scale:
- 15-20 active communities
- ~30-50 events per month
- ~30 venues
- Modest concurrent user load

## Decision
**Use SQLite as the primary database.**

SQLite comes bundled with PocketBase and provides all necessary features for the platform's requirements while maintaining the single-binary deployment model.

## Consequences

### Positive
- **Zero operational overhead**: No separate database server to manage
- **Single file backup**: Entire database is one file, trivial to backup
- **Perfect for VPS deployment**: No memory overhead from database daemon
- **Excellent for development**: Identical local and production setup
- **Strong consistency**: ACID compliance without configuration
- **Sufficient performance**: Handles expected load easily
- **Simple migrations**: PocketBase handles schema evolution
- **Embeds with application**: Truly single-binary deployment

### Negative
- **Write concurrency limits**: Multiple simultaneous writes can cause contention
- **No built-in replication**: Scaling to multiple servers requires additional tooling
- **Less familiar to some developers**: Many expect PostgreSQL/MySQL

### Neutral
- **File-based storage**: Database grows as single file (not inherently good or bad)
- **Limited write scaling**: Acceptable for current requirements, could become constraint later

## Scaling Considerations

**When SQLite is sufficient** (current state):
- Single server deployment
- Moderate write load (dozens of events per day, not hundreds)
- Read-heavy workload
- Total database size under several GB

**Migration path if needed** (future):
- PocketBase supports PostgreSQL as backend database
- Migration possible without application code changes
- Only necessary if hitting write concurrency issues or need replication

**Current assessment**: SQLite is appropriate for Linz's scale for foreseeable future.

## Alternatives Considered

### PostgreSQL
- **Pros**: Better write concurrency, replication support, larger ecosystem
- **Cons**: Separate server process, more operational complexity, higher resource usage
- **Why rejected**: Overkill for current requirements, conflicts with operational simplicity goals
- **Note**: Can migrate later if needed without major rewrites

### MySQL/MariaDB
- **Pros**: Mature, widely known
- **Cons**: Same operational overhead as PostgreSQL without significant benefits
- **Why rejected**: Same reasons as PostgreSQL

### MongoDB/NoSQL
- **Pros**: Schema flexibility
- **Cons**: Unnecessary complexity, poor fit for relational event data
- **Why rejected**: Relational data model is natural fit for community/event relationships

## GDPR Considerations
SQLite fully supports GDPR compliance requirements:
- Complete data export (dump entire database)
- Selective deletion (standard SQL DELETE operations)
- Data portability (SQLite format is well-documented and portable)
- EU data residency (file stored on EU-based VPS)

## Implementation Notes
- Use PocketBase's collection system for data modeling
- Leverage SQLite's JSON functions for flexible metadata storage
- Implement full-text search using SQLite FTS5 extension
- Regular automated backups via simple file copying
- Consider write-ahead logging (WAL) mode for better concurrent read performance

## References
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [SQLite When To Use](https://www.sqlite.org/whentouse.html)
- [PocketBase Database](https://pocketbase.io/docs/going-to-production/#using-postgresql)
- [ADR-001: Backend Technology](./adr001-backend-technology.md)
- [ADR-004: Hosting & Deployment](./adr004-hosting-deployment.md)
