# ADR-003: Database Selection (SQLite)

## Status
Accepted (Updated)

## Context
AutoDevHub needs to store user stories, feature descriptions, generated Gherkin scenarios, and metadata about AI processing. Given the capstone project constraints and development timeline, the database must:

- Handle structured data for stories, features, and metadata
- Enable rapid development and deployment
- Provide zero-configuration setup for development
- Support the 8-hour implementation timeline
- Maintain data integrity and relationships between entities
- Allow for easy testing and demonstration

The application will store:
- Feature descriptions submitted by users
- AI-generated Gherkin stories
- Timestamps and processing metadata
- User sessions and preferences (future enhancement)

## Decision
We will use SQLite as the primary database for AutoDevHub for both development and production deployment.

SQLite provides:
- **Zero Configuration** - File-based database requiring no setup or server
- **ACID compliance** - Data integrity for story generation workflow
- **JSON support** - Modern SQLite versions support JSON operations
- **Excellent Python integration** - Built into Python standard library
- **Rapid Development** - Perfect for capstone project timeline constraints
- **Easy Deployment** - Single file database simplifies deployment

## Consequences

### Positive Consequences
- **Zero Setup Time** - No database server installation or configuration required
- **Rapid Development** - Immediate database availability supports 8-hour timeline
- **Data Integrity** - ACID properties ensure story data consistency
- **Simplicity** - Single file database simplifies backup, deployment, and distribution
- **Built-in Support** - Python standard library includes SQLite3 module
- **Easy Testing** - In-memory databases for unit testing
- **Cross-Platform** - Works identically across all development environments

### Negative Consequences
- **Concurrent Writes** - Limited concurrent write operations (acceptable for demo)
- **Scalability Limits** - Not suitable for high-traffic production (post-capstone concern)
- **Advanced Features** - Fewer advanced features compared to PostgreSQL
- **Single File** - Database is a single point of failure (mitigated by Git version control)

### Risks
- **File Corruption** - Database corruption could affect entire application
- **Performance Limits** - May not handle very large datasets efficiently
- **Migration Path** - Future migration to PostgreSQL will require data migration

## Alternatives Considered

### PostgreSQL
- **Pros**: Advanced features, excellent scalability, robust JSON support
- **Cons**: Requires setup, configuration, and server management
- **Rejection Reason**: Setup complexity conflicts with 8-hour timeline constraint

### MongoDB
- **Pros**: Document-based, natural JSON storage, flexible schema
- **Cons**: Less structured than relational data, learning curve for team
- **Rejection Reason**: Overkill for structured story data, adds complexity

### MySQL
- **Pros**: Wide adoption, good performance, familiar to many developers
- **Cons**: Setup complexity, limited JSON support compared to modern SQLite
- **Rejection Reason**: Setup overhead and configuration complexity

### In-Memory Database
- **Pros**: Extremely fast, perfect for temporary data
- **Cons**: Data loss on restart, not suitable for persistent story storage
- **Rejection Reason**: Need persistent storage for generated stories

## Implementation Notes

### Development Setup
- SQLite database file: `autodevhub.db`
- SQLAlchemy ORM for database operations
- Alembic for schema migrations (optional for capstone)

### Production Configuration
- Single SQLite file deployment
- Regular file backups through Git commits
- Environment-based database file location

### Schema Design
```sql
-- Core story storage
CREATE TABLE user_stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feature_description TEXT NOT NULL,
    gherkin_output TEXT NOT NULL,
    metadata TEXT, -- JSON as TEXT in SQLite
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Future: User sessions and preferences
CREATE TABLE sessions (
    id TEXT PRIMARY KEY, -- UUID as TEXT
    user_id TEXT,
    preferences TEXT, -- JSON as TEXT
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Performance Considerations
- Index on created_at for chronological story retrieval
- Full-text search using SQLite FTS5 extension
- WAL mode for better concurrent read performance
- Regular VACUUM operations for optimal performance