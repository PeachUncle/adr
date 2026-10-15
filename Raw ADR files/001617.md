# ADR-20251015-use-sqlite-database

## Status
Accepted

## Context
ExvoRed is a specialized web application for managing and cataloging votive offerings (exvotos) in academic research contexts. The system requires persistent data storage with full ACID compliance to ensure data integrity for historical records. The target deployment is a small academic research team (1-10 users) with occasional concurrent access. The database must support complex relationships between exvotos, sanctuaries (SEMs), catalogs, divinities, characters, and miracles.

Additionally, the system requires blob storage for images embedded within the database itself, and must be easily portable for backup and migration purposes. The development team is small and requires zero-configuration, embedded database solutions that can be version-controlled and deployed without complex infrastructure setup. The application needs to handle thousands of records (not millions), with primarily read operations and occasional batch updates during cataloging sessions.

## Decision
Use SQLite as the database engine, stored as a single file at `api/db/database.db`. The database uses better-sqlite3 as the Node.js driver, providing synchronous operations and excellent performance. All data, including blob images, is stored within the single database file.

## Consequences

### Positive
- Zero-configuration deployment: No database server installation or management required; database is a single file that travels with the application
- Portability: Entire database can be backed up by simply copying the database.db file; easy migration between development and production environments
- ACID compliance: Full transactional support ensures data integrity for critical historical records
- Performance: Synchronous operations via better-sqlite3 are extremely fast for single-user scenarios; sub-millisecond query times for typical operations
- Embedded images: Blob storage keeps all data atomic; no orphaned image files or file system dependencies
- Development velocity: Instant startup, no connection pooling complexity, ideal for rapid prototyping
- File-based backup: Simple backup strategy with rsync or S3 sync; no need for database-specific dump utilities

### Negative
- Write concurrency limitations: SQLite uses file-level locking, limiting concurrent writes to approximately 10 writes/second; not suitable for high-traffic multi-user web applications
- No clustering: Cannot scale horizontally across multiple servers; single point of failure
- Image bloat: Storing images as blobs increases database file size significantly (base64 encoding adds 33% overhead); large databases (50GB+) experience performance degradation
- Connection limits: Maximum 140TB database size is more than sufficient, but practical performance limits occur around 10-50GB depending on query patterns
- No native full-text search: While SQLite supports FTS5 extension, setup is more complex compared to PostgreSQL's built-in full-text search capabilities

### Neutral
- Server-side architecture required: SQLite cannot be accessed directly from browser; requires Express API layer (already part of architecture)
- Migration path exists: Can migrate to PostgreSQL if scaling requirements change, with Drizzle ORM providing abstraction layer

## Alternatives Considered

### Alternative 1: PostgreSQL
**Rejected because:** PostgreSQL is a client-server database requiring separate installation, configuration, and maintenance. For a small academic research team (1-10 users), the operational complexity of managing a PostgreSQL server outweighs the benefits. PostgreSQL excels at concurrent writes (100+ writes/second) and clustering, neither of which are requirements for ExvoRed's cataloging workflow. Additionally, PostgreSQL requires connection pooling, environment-specific configuration, and more complex backup strategies, increasing deployment friction for researchers who are not database administrators.

### Alternative 2: MySQL/MariaDB
**Rejected because:** Similar to PostgreSQL, MySQL requires server installation and management overhead. While MySQL has better blob storage performance than PostgreSQL for binary data, it still introduces unnecessary complexity compared to SQLite's embedded model. MySQL's replication features are not needed for the single-server deployment model. The operational burden of managing MySQL credentials, networking, and backups is unjustified for the target use case.

### Alternative 3: JSON Files
**Rejected because:** While JSON files offer simplicity and human-readability, they lack ACID transaction support, making data corruption likely during concurrent edits or application crashes. JSON files cannot efficiently handle relationships between entities (no foreign key constraints or joins), forcing complex application-level logic for data integrity. Image storage would require separate file system management, creating synchronization issues. Query performance degrades rapidly beyond a few hundred records, and there is no built-in indexing or query optimization.

## References
- SQLite Official Documentation: https://www.sqlite.org/docs.html
- Drizzle ORM SQLite Guide: https://orm.drizzle.team/docs/get-started-sqlite
- better-sqlite3 Documentation: https://github.com/WiseLibs/better-sqlite3
- Project schema definition: `/home/marcos/Documentos/Programming/JavaScript/ExvoRed/api/db/schema.ts`
