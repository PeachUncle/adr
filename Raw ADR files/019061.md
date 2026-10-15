# ADR-002: Database Design

## Status

Accepted

## Context

TodoList application membutuhkan database schema yang mendukung:

- Multi-user dengan ownership yang jelas
- Task management dengan categories, priorities, due dates
- Team collaboration dan task sharing
- Audit trail untuk tracking changes
- Reminder system

## Decision

### 1. Database Schema

```sql
-- Users Table
users
├── id (UUID, PK)
├── email (VARCHAR, UNIQUE, NOT NULL)
├── password_hash (VARCHAR, NOT NULL)
├── full_name (VARCHAR, NOT NULL)
├── is_email_verified (BOOLEAN, DEFAULT FALSE)
├── verification_token (VARCHAR, NULLABLE)
├── reset_password_token (VARCHAR, NULLABLE)
├── reset_password_expiry (DATETIME, NULLABLE)
├── created_at (DATETIME, NOT NULL)
├── updated_at (DATETIME, NOT NULL)
└── last_login_at (DATETIME, NULLABLE)

-- Tasks Table
tasks
├── id (UUID, PK)
├── user_id (UUID, FK -> users.id, NOT NULL)
├── team_id (UUID, FK -> teams.id, NULLABLE)
├── title (VARCHAR(200), NOT NULL)
├── description (TEXT, NULLABLE)
├── status (ENUM: TODO, IN_PROGRESS, DONE)
├── priority (ENUM: LOW, MEDIUM, HIGH, URGENT)
├── category_id (UUID, FK -> categories.id, NULLABLE)
├── due_date (DATETIME, NULLABLE)
├── completed_at (DATETIME, NULLABLE)
├── is_archived (BOOLEAN, DEFAULT FALSE)
├── created_at (DATETIME, NOT NULL)
├── updated_at (DATETIME, NOT NULL)
├── created_by (UUID, FK -> users.id, NOT NULL)
└── updated_by (UUID, FK -> users.id, NOT NULL)

-- Categories Table
categories
├── id (UUID, PK)
├── user_id (UUID, FK -> users.id, NOT NULL)
├── name (VARCHAR(100), NOT NULL)
├── color (VARCHAR(7), DEFAULT '#3B82F6') -- Hex color
├── icon (VARCHAR(50), NULLABLE)
├── created_at (DATETIME, NOT NULL)
└── UNIQUE(user_id, name)

-- Teams Table
teams
├── id (UUID, PK)
├── name (VARCHAR(100), NOT NULL)
├── description (TEXT, NULLABLE)
├── owner_id (UUID, FK -> users.id, NOT NULL)
├── created_at (DATETIME, NOT NULL)
└── updated_at (DATETIME, NOT NULL)

-- Team Members Table
team_members
├── id (UUID, PK)
├── team_id (UUID, FK -> teams.id, NOT NULL)
├── user_id (UUID, FK -> users.id, NOT NULL)
├── role (ENUM: OWNER, MEMBER, VIEWER)
├── joined_at (DATETIME, NOT NULL)
└── UNIQUE(team_id, user_id)

-- Task Assignments Table
task_assignments
├── id (UUID, PK)
├── task_id (UUID, FK -> tasks.id, NOT NULL)
├── assigned_to (UUID, FK -> users.id, NOT NULL)
├── assigned_by (UUID, FK -> users.id, NOT NULL)
├── assigned_at (DATETIME, NOT NULL)
└── UNIQUE(task_id, assigned_to)

-- Task Comments Table
task_comments
├── id (UUID, PK)
├── task_id (UUID, FK -> tasks.id, NOT NULL)
├── user_id (UUID, FK -> users.id, NOT NULL)
├── comment_text (TEXT, NOT NULL)
├── created_at (DATETIME, NOT NULL)
└── updated_at (DATETIME, NOT NULL)

-- Task Reminders Table
task_reminders
├── id (UUID, PK)
├── task_id (UUID, FK -> tasks.id, NOT NULL)
├── user_id (UUID, FK -> users.id, NOT NULL)
├── remind_at (DATETIME, NOT NULL)
├── is_sent (BOOLEAN, DEFAULT FALSE)
├── sent_at (DATETIME, NULLABLE)
├── reminder_type (ENUM: EMAIL, IN_APP)
└── created_at (DATETIME, NOT NULL)

-- Activity Log Table
activity_logs
├── id (UUID, PK)
├── task_id (UUID, FK -> tasks.id, NOT NULL)
├── user_id (UUID, FK -> users.id, NOT NULL)
├── action (VARCHAR(50), NOT NULL) -- created, updated, completed, deleted, assigned, commented
├── description (TEXT, NULLABLE)
├── created_at (DATETIME, NOT NULL)
└── INDEX(task_id, created_at DESC)
```

### 2. Indexing Strategy

```sql
-- Performance Indexes
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX idx_tasks_team_status ON tasks(team_id, status) WHERE team_id IS NOT NULL;
CREATE INDEX idx_tasks_due_date ON tasks(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_category ON tasks(category_id);

CREATE INDEX idx_reminders_pending ON task_reminders(remind_at) WHERE is_sent = FALSE;
CREATE INDEX idx_activity_logs_task ON activity_logs(task_id, created_at DESC);

-- Full-text search index
CREATE FULLTEXT INDEX idx_tasks_search ON tasks(title, description);
```

### 3. Data Types Choices

**UUID vs AUTO_INCREMENT:**

- UUID untuk semua primary keys
- Alasan: Security (tidak predictable), distributed-friendly, easier merging

**DATETIME vs TIMESTAMP:**

- DATETIME untuk semua date fields
- Alasan: No timezone conversion issues, more predictable behavior

**ENUM vs VARCHAR:**

- ENUM untuk status, priority, role (fixed values)
- Alasan: Type safety, better performance, smaller storage

**TEXT vs VARCHAR:**

- VARCHAR untuk short strings (< 500 chars)
- TEXT untuk long content (description, comments)

### 4. Constraints & Rules

**CASCADE Rules:**

```sql
-- Delete user → cascade delete all their tasks, categories, comments
ON DELETE CASCADE: tasks.user_id, categories.user_id, task_comments.user_id

-- Delete team → cascade delete team_members, but NOT tasks
ON DELETE CASCADE: team_members.team_id
ON DELETE SET NULL: tasks.team_id

-- Delete task → cascade delete comments, reminders, assignments
ON DELETE CASCADE: task_comments.task_id, task_reminders.task_id, task_assignments.task_id
```

**Check Constraints:**

```sql
-- Due date cannot be in the past when creating
ALTER TABLE tasks ADD CONSTRAINT check_due_date
CHECK (due_date IS NULL OR due_date > created_at);

-- Completed_at must be set when status = DONE
ALTER TABLE tasks ADD CONSTRAINT check_completed
CHECK ((status = 'DONE' AND completed_at IS NOT NULL) OR (status != 'DONE'));

-- Team owner must be a team member
ALTER TABLE teams ADD CONSTRAINT check_owner_is_member
-- (enforced by application logic)
```

### 5. Soft Delete Strategy

**Archived Tasks:**

- `is_archived` flag instead of hard delete
- Archived tasks excluded from default queries
- User can restore archived tasks
- Hard delete setelah 30 hari (scheduled job)

**Deleted Users:**

- No soft delete for users
- On user delete → anonymize their data (change email to `deleted_user_<uuid>@deleted.local`)
- Keep task history for audit trail

## Alternatives Considered

### Alternative 1: NoSQL (MongoDB)

**Kenapa tidak dipilih:**

- TodoList butuh strong relationships (users, tasks, teams)
- ACID transactions penting untuk data consistency
- MySQL query optimization lebih mature
- Relational model lebih natural untuk data structure ini

### Alternative 2: Single Table Inheritance

**Kenapa tidak dipilih:**

- Personal tasks vs team tasks di table yang sama lebih simple
- Menggunakan `team_id IS NULL` untuk personal tasks
- Lebih flexible untuk sharing personal task ke team nanti

### Alternative 3: Separate Tables for Personal/Team Tasks

**Kenapa tidak dipilih:**

- Code duplication di repository layer
- Sulit implement "share personal task to team"
- Join queries lebih complex
- Single table dengan `team_id` nullable lebih elegant

### Alternative 4: INT Primary Keys

**Kenapa tidak dipilih:**

- UUID lebih secure (no enumeration attacks)
- Better untuk distributed systems (future-proof)
- No collision risk jika butuh merge databases

## Consequences

### Positif

- **Data integrity:** Foreign keys & constraints enforce rules
- **Audit trail:** Activity log tracks all changes
- **Flexible querying:** Indexes support berbagai filter combinations
- **Scalable:** Schema support growth hingga 100K+ tasks
- **Clear ownership:** User/team relationship jelas

### Negatif

- **UUID storage:** 16 bytes vs 4 bytes (INT) → lebih besar
- **Complex queries:** Join banyak tables untuk team collaboration
- **Index maintenance:** Banyak indexes → slower writes (acceptable trade-off)

### Migration Strategy

- Flyway untuk versioned migrations
- All migrations reversible (UP/DOWN)
- Test migrations di staging dulu
- Backup before production migration

## Performance Expectations

**Expected Load (MVP):**

- 1000 users
- Average 50 tasks per user
- 100 concurrent users
- 10 queries per second

**Optimization Plan:**

- Monitor slow queries (> 100ms)
- Add indexes based on actual usage patterns
- Consider read replicas jika read load tinggi
- Partition activity_logs by month jika terlalu besar

## Review Date

Review schema setelah:

- Phase 3 selesai (collaboration features)
- Performance issues detected
- 10K+ tasks created
