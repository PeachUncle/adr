# ADR-0003: SQLite Database Design

**Status:** Accepted  
**Date:** 2025-11-26  
**Supersedes:** None  
**Superseded By:** N/A

---

## Context

We needed to design a database schema and select appropriate data persistence technology for the work productivity tracking application. Requirements included:

- Support for 7 core features (daily focus, learning journal, skills matrix, meetings, goals, feedback, energy tracking)
- Local-first architecture (privacy-focused, offline-capable)
- Single-user operation
- Data relationships and integrity
- Schema evolution support (migrations)
- Backup and recovery capability
- Performance for local queries

Key considerations:

- Database technology choice (local vs. server)
- Schema design and normalization
- Migration strategy for schema changes
- Backup automation
- Data portability

## Decision

We will use **SQLite** as our database with a **comprehensive normalized schema** (12+ tables), **Flask-Migrate for migrations**, and **automated backup strategy**.

### Core Design Decisions:

1. **Database Technology: SQLite**

   - Local file-based database
   - Zero configuration required
   - Perfect for single-user applications
   - Fast for local operations
   - Built-in to Python

2. **Schema Design: Normalized 12+ Tables**

   - Organizations (DRW, Apprenti)
   - Users (future-proofing)
   - People (contacts/relationships)
   - Tasks (daily focus)
   - Learnings (journal entries)
   - Skills + SkillProgress (matrix with history)
   - Meetings + MeetingAttendees
   - Goals + GoalMilestones
   - Feedback
   - ActionItems (from meetings/feedback)
   - EnergyCheckins
   - Tags (flexible categorization)

3. **Migration Strategy: Flask-Migrate (Alembic)**

   - Version-controlled schema changes
   - Automatic migration generation
   - Rollback capability
   - Incremental feature implementation

4. **Backup Strategy: Automated Daily Backups**

   - File-copy backups before first use each day
   - Keep last 7 daily backups
   - Keep last 4 weekly backups
   - Export capabilities (JSON, CSV, SQL)

5. **Data Integrity: Foreign Key Constraints**
   - Enable FK constraints (not default in SQLite)
   - Proper relationships between entities
   - Cascading deletes where appropriate
   - Unique constraints on natural keys

### Key Schema Patterns:

- **TimestampMixin**: created_at/updated_at on all tables
- **Soft Deletes**: Can add deleted_at column if needed
- **Hierarchical Goals**: Self-referencing for parent/child goals
- **Progress Tracking**: Separate tables for historical data (SkillProgress)
- **Many-to-Many**: Separate junction tables (MeetingAttendees, Tags)
- **Strategic Indexing**: Date fields, status fields, foreign keys

## Consequences

### Positive

- **Privacy**: Data stays on user's machine; no server required
- **Performance**: Fast local queries; no network latency
- **Simplicity**: Single file database; easy to back up (copy file)
- **Offline**: Works without internet connection
- **Zero Config**: No database server to install/manage
- **Portability**: SQLite file is cross-platform
- **Comprehensive Schema**: Supports all 7 features with proper relationships
- **Scalability**: Normalized design allows adding features without major refactoring
- **Data Integrity**: Foreign keys prevent orphaned records
- **Evolution**: Flask-Migrate handles schema changes cleanly
- **Backup**: Simple file operations enable automated backups

### Negative

- **Concurrency**: Not suitable for multi-user (not an issue for us)
- **Size Limitations**: SQLite degrades after ~100GB (unlikely for personal productivity data)
- **No Built-in Replication**: Can't replicate to multiple devices easily
- **Schema Complexity**: 12+ tables may seem heavy initially
- **Migration Management**: Requires discipline to manage migrations properly

**Mitigation:**

- Concurrency not an issue (single-user app)
- Size limits irrelevant (years of data still under 1GB)
- Multi-device sync can be added later if needed
- Implement tables incrementally (start with 3-4, add as features develop)
- Strong migration testing process and documentation

## Alternatives Considered

### Alternative 1: PostgreSQL

**Description:** Full-featured relational database server

**Pros:**

- Robust feature set
- Excellent for multi-user
- Advanced query capabilities
- Better concurrency handling

**Cons:**

- Requires server installation and management
- Overkill for single-user
- More complex deployment
- Network overhead (even locally)
- Harder for users to back up

**Why Not Chosen:** Unnecessary complexity for single-user local app. Would require users to install and manage database server. SQLite's simplicity better matches use case.

### Alternative 2: JSON Files

**Description:** Store data in JSON files on filesystem

**Pros:**

- Extremely simple
- Human-readable
- Easy to version control
- No database setup

**Cons:**

- No query capabilities
- No relationships/integrity
- Poor performance at scale
- No transactions
- Manual backup logic
- Concurrent access issues

**Why Not Chosen:** Doesn't scale beyond toy apps. No relationship support means duplicated data. Performance degrades quickly. Would need to rebuild database features manually.

### Alternative 3: MongoDB / Document Database

**Description:** NoSQL document-oriented database

**Pros:**

- Flexible schema
- JSON-like documents
- Good for rapidly changing requirements

**Cons:**

- Overkill for structured data
- Requires server (like PostgreSQL)
- Relationships less natural
- More complex queries
- Larger footprint

**Why Not Chosen:** Our data is highly relational (meetings have people, tasks link to goals, etc.). SQL better fits our needs. Would trade simplicity for flexibility we don't need.

### Alternative 4: Denormalized Single-Table Design

**Description:** Store all data in minimal tables with embedded JSON

**Pros:**

- Fewer tables
- Simpler queries initially
- Faster writes

**Cons:**

- Data duplication
- Update anomalies
- Difficult to maintain integrity
- Complicated queries as features grow
- Harder to add relationships later

**Why Not Chosen:** Would cause problems as features grow. Normalized design makes relationships clear and prevents duplication. Refactoring from denormalized to normalized is painful.

## Implementation Notes

1. **Incremental Rollout:**

   - **Phase 1 (MVP):** Users, Organizations, Tasks
   - **Phase 2:** Learnings, Skills, Tags
   - **Phase 3:** People, Meetings, Goals
   - **Phase 4:** Feedback, ActionItems, EnergyCheckins

2. **SQLite Configuration:**

   ```python
   # Enable foreign key constraints
   PRAGMA foreign_keys = ON;

   # Use WAL mode for better concurrency
   PRAGMA journal_mode = WAL;

   # Optimize for local use
   PRAGMA synchronous = NORMAL;
   PRAGMA cache_size = -64000;  # 64MB cache
   ```

3. **TimestampMixin Pattern:**

   ```python
   class TimestampMixin:
       created_at = db.Column(db.DateTime, default=datetime.utcnow)
       updated_at = db.Column(db.DateTime,
                             default=datetime.utcnow,
                             onupdate=datetime.utcnow)
   ```

4. **Migration Workflow:**

   ```bash
   # Create migration
   flask db migrate -m "Add tasks table"

   # Review auto-generated migration
   # Edit if needed

   # Apply migration
   flask db upgrade

   # Rollback if needed
   flask db downgrade
   ```

5. **Backup Service:**
   ```python
   def create_backup(db_path, backup_dir):
       timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
       backup_path = f"{backup_dir}/backup_{timestamp}.db"
       shutil.copy2(db_path, backup_path)
       cleanup_old_backups(backup_dir, keep_last=7)
   ```

## References

- [SQLite Database Design Research](../research/tech-stack/sqlite-database-design.md) - Comprehensive analysis (700+ lines)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Flask-SQLAlchemy Documentation](https://flask-sqlalchemy.palletsprojects.com/)
- [Flask-Migrate Documentation](https://flask-migrate.readthedocs.io/)

## Related ADRs

- **ADR-0001:** Flask Backend Architecture - Backend layer that interfaces with this database
- **ADR-0002:** React Frontend Architecture - Frontend layer that consumes this database via API
- **ADR-0004:** Flask-React Integration Strategy - Integration approach for accessing this database
- **ADR-0005:** Projects as Foundation Architecture - Strategic decision requiring Projects table addition (see Addendum below)

---

## 📝 Addendum: Projects-First Schema Update (2025-12-01)

**Superseded By:** [ADR-0005: Projects as Foundation Architecture](ADR-0005-projects-as-foundation-architecture.md)

Following the strategic pivot to Projects-First MVP (documented in ADR-0005), the database schema priorities have been updated:

### Schema Priority Changes

**Original Phase 1:** Users, Organizations, Tasks  
**Updated Phase 1:** Users, Organizations, **Projects**, projects_skills

### New Tables (Priority #1)

**Projects Table:**

```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    path TEXT,  -- Local filesystem path
    remote_url TEXT UNIQUE,  -- GitHub/GitLab URL (unique for deduplication)
    organization_id INTEGER,  -- DRW, Apprenti, Personal, NULL
    classification TEXT NOT NULL,  -- Work, Personal, Learning, Inactive
    status TEXT NOT NULL,  -- active, learning, archived, inactive

    -- Learning Sub-Classification (Critical for MVP)
    learning_type TEXT,  -- work_related, personal_dev, hybrid, NULL
    learning_context TEXT,  -- Free-form description of learning goals
    learning_status TEXT,  -- exploring, active_learning, completed, paused

    -- Tech Stack
    tech_stack JSON,  -- Array of languages/technologies

    -- Metadata
    description TEXT,
    last_worked_on DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    CHECK (classification IN ('Work', 'Personal', 'Learning', 'Inactive')),
    CHECK (learning_type IN ('work_related', 'personal_dev', 'hybrid') OR learning_type IS NULL),
    CHECK (learning_status IN ('exploring', 'active_learning', 'completed', 'paused') OR learning_status IS NULL)
);

-- Full-text search support
CREATE VIRTUAL TABLE projects_fts USING fts5(
    name,
    description,
    tech_stack,
    content=projects,
    content_rowid=id
);
```

**projects_skills Junction Table:**

```sql
CREATE TABLE projects_skills (
    project_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    proficiency_used TEXT,  -- beginner, intermediate, advanced, expert
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (project_id, skill_id),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);
```

### Updated Implementation Phases

**Phase 1 (MVP - Weeks 2-3):**

- Organizations
- Users
- **Projects** (with Learning sub-classification)
- Skills (seeded from 24 discovered technologies)
- projects_skills (many-to-many)
- Tags

**Phase 2 (Weeks 4-5):**

- Tasks (project-centric Daily Focus)
- EnergyCheckins

**Phase 3 (Weeks 6-7):**

- People
- Meetings + MeetingAttendees
- Learnings (associated with Learning projects)

**Phase 4 (Week 8+):**

- Goals + GoalMilestones
- Feedback
- ActionItems

### Key Changes from Original Design

1. **Projects Table Added:** Now Priority #1 (was "8th potential feature")
2. **Learning Classification:** Three new fields for Learning project sub-classification
3. **Tech Stack Tracking:** JSON field for discovered languages/technologies
4. **SQLite FTS5:** Full-text search table for project search/filtering
5. **projects_skills Relationship:** Many-to-many with Skills table
6. **Bootstrap Data:** Import 59 projects from inventory, 24 skills from discovered tech stack

### Migration Strategy

The phased implementation approach remains unchanged, but Phase 1 now focuses on Projects rather than Tasks:

```bash
# Phase 1 Migrations
flask db migrate -m "Create organizations table"
flask db migrate -m "Create users table"
flask db migrate -m "Create projects table with learning classification"  # NEW
flask db migrate -m "Create skills table"  # MOVED UP
flask db migrate -m "Create projects_skills junction table"  # NEW
flask db migrate -m "Create tags table"
flask db migrate -m "Setup SQLite FTS5 for projects"  # NEW
```

### References

- [ADR-0005: Projects as Foundation Architecture](ADR-0005-projects-as-foundation-architecture.md) - Strategic pivot decision
- [Learning Project Taxonomy](../research/data-models/learning-project-taxonomy.md) - Classification design
- [Projects Data Model Research](../research/research-register.md#20-projects-data-model) - Week 2 research topic

---

**Original Date:** 2025-11-26  
**Addendum Date:** 2025-12-01  
**Last Updated:** 2025-12-01  
**Status:** ✅ Accepted and Active (Updated with Projects-First schema)
