# ADR 0005: Database Schema for Repository Configurations and Document Management

## Status

Accepted (Updated: 2025-11-24)

## Context

ADR 0004 established PostgreSQL as the chosen database for OpsCore. This ADR originally defined the initial database schema for external repository configurations. 

**Domain Model Redesign (2025-11)**

Following the domain model redesign and ADR 0016 (Document Domain Model Design), this ADR has been updated to reflect:
- Corrections to align with actual implementation
- Document aggregate schema based on ADR 0016 design decisions
- Metadata placement in DocumentVersion (per-version metadata)
- Simplified AccessScope model (public/private)
- Execution records and user/group management tables
- Comprehensive indexing strategy

Related ADRs:
- ADR 0013: Document Variable Definition and Substitution
- ADR 0014: Execution Record and Evidence Management
- ADR 0016: Document Domain Model Design
- ADR 0017: Application-Level Data Validation

## Decision

### Existing Tables (Corrected from Initial Implementation)

#### `repositories` Table

Stores details about configured external Git repositories.

**Discrepancies from Original ADR:**
- Table name: `repositories` (not `repository_configurations`) - shortened for better usability
- Column name: `url` (not `repository_url`) - simplified naming convention
- Column name: `access_token` (not `credentials`) - more specific and accurate
- No `provider_type` column - provider is derived from URL, avoiding redundancy
- URL length: VARCHAR(255) (not 2048) - sufficient for practical Git repository URLs

**Schema:**
```sql
CREATE TABLE repositories (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(255) NOT NULL UNIQUE,
    access_token TEXT, -- Encrypted using AES-256-GCM at application level
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Rationale for Changes:**
- **Table name:** Shorter, more conventional name following PostgreSQL best practices
- **URL length:** 255 characters is sufficient for GitHub/GitLab URLs and improves index performance
- **access_token:** Replaces `credentials`; encrypted at application level using AES-256-GCM
- **No provider_type:** Git provider can be determined from URL pattern (github.com, gitlab.com, etc.)

#### `managed_files` Table

**Note:** With the introduction of the `documents` and `document_versions` tables, the purpose and necessity of the `managed_files` table needs to be reconsidered. Document versions now track file paths and commit hashes directly. This table may be deprecated in future versions.

**Current Schema (for backward compatibility):**
```sql
CREATE TABLE managed_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id UUID NOT NULL,
    file_path TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (repository_id) REFERENCES repositories(id) ON DELETE CASCADE,
    UNIQUE (repository_id, file_path)
);
```

**Future Consideration:** This table may be removed once all file tracking functionality is migrated to the Document aggregate.

### New Tables (Domain Model Redesign)

#### `documents` Table

Stores document aggregate root information (per ADR 0016).

**Key Design Decision (ADR 0016):**
- Document metadata (title, type, tags, variables) moved to `document_versions` table
- Metadata is per-version because it comes from file frontmatter and can change between versions
- Document table contains only repository-level management metadata

**Schema:**
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_id UUID NOT NULL,
    owner VARCHAR(255) NOT NULL,
    is_published BOOLEAN NOT NULL DEFAULT false,
    is_auto_update BOOLEAN NOT NULL DEFAULT false,
    access_scope VARCHAR(50) NOT NULL CHECK (access_scope IN ('public', 'private')),
    current_version_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (repository_id) REFERENCES repositories(id) ON DELETE CASCADE
);

CREATE INDEX idx_documents_repository_id ON documents(repository_id);
CREATE INDEX idx_documents_is_published ON documents(is_published);
CREATE INDEX idx_documents_access_scope ON documents(access_scope);
```

**Note:** `current_version_id` foreign key to `document_versions` is added after `document_versions` table creation to avoid circular dependency issues.

#### `document_versions` Table

Stores version history for documents with file-specific metadata (per ADR 0016).

**Key Design Decision (ADR 0016):**
- File metadata (title, type, tags, variables) stored per version
- Enables tracking metadata changes across versions
- DocumentSource combines file_path and commit_hash as version identifier

**Schema:**
```sql
CREATE TABLE document_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL,
    version_number INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    commit_hash VARCHAR(64) NOT NULL,
    title VARCHAR(255) NOT NULL,
    doc_type VARCHAR(50) NOT NULL CHECK (doc_type IN ('procedure', 'knowledge')),
    tags TEXT[] NOT NULL DEFAULT '{}',
    variables JSONB, -- VariableDefinition[] schema
    content TEXT NOT NULL,
    published_at TIMESTAMPTZ NOT NULL,
    unpublished_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    UNIQUE (document_id, version_number),
    UNIQUE (document_id, file_path, commit_hash)
);

CREATE INDEX idx_document_versions_document_id ON document_versions(document_id);
CREATE INDEX idx_document_versions_doc_type ON document_versions(doc_type);
CREATE INDEX idx_document_versions_tags ON document_versions USING GIN(tags);
CREATE INDEX idx_document_versions_commit_hash ON document_versions(commit_hash);

-- Add foreign key after both tables exist
ALTER TABLE documents
ADD CONSTRAINT fk_documents_current_version
FOREIGN KEY (current_version_id) REFERENCES document_versions(id);
```

**Removed Fields (per ADR 0016):**
- `is_current_version`: Redundant with `documents.current_version_id`; single source of truth at Document level

#### `users` Table

Stores minimal user information. Full user management will be implemented later.

**Schema:**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Note:** Additional fields (name, email, role, etc.) will be added when user management features are implemented.

#### `groups` Table

Stores user groups for organizing users and managing access control.

**Schema:**
```sql
CREATE TABLE groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_groups_name ON groups(name);
```

#### `user_groups` Table

Junction table for many-to-many relationship between users and groups.

**Schema:**
```sql
CREATE TABLE user_groups (
    user_id UUID NOT NULL,
    group_id UUID NOT NULL,
    joined_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, group_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE
);

CREATE INDEX idx_user_groups_user_id ON user_groups(user_id);
CREATE INDEX idx_user_groups_group_id ON user_groups(group_id);
```

#### `execution_records` Table

Stores execution records for procedure executions with evidence tracking.

**Schema:**
```sql
CREATE TABLE execution_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL,
    document_version_id UUID NOT NULL,
    executor_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    variable_values JSONB, -- VariableValue[] schema
    notes TEXT,
    status VARCHAR(50) NOT NULL CHECK (status IN ('in_progress', 'completed', 'failed')),
    access_scope VARCHAR(50) NOT NULL CHECK (access_scope IN ('public', 'private')),
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (document_version_id) REFERENCES document_versions(id),
    FOREIGN KEY (executor_id) REFERENCES users(id),
    CONSTRAINT chk_execution_records_status CHECK (status IN ('in_progress', 'completed', 'failed')),
    CONSTRAINT chk_execution_records_access_scope CHECK (access_scope IN ('public', 'private'))
);

CREATE INDEX idx_execution_records_document_id ON execution_records(document_id);
CREATE INDEX idx_execution_records_executor_id ON execution_records(executor_id);
CREATE INDEX idx_execution_records_status ON execution_records(status);
CREATE INDEX idx_execution_records_started_at ON execution_records(started_at);
CREATE INDEX idx_execution_records_completed_at ON execution_records(completed_at);
CREATE INDEX idx_execution_records_variable_values ON execution_records USING GIN(variable_values);
```

**Note:** Sharing mechanism for private execution records will be implemented separately (similar to Document aggregate per ADR 0016).

#### `execution_steps` Table

Stores individual execution steps within an execution record.

**Schema:**
```sql
CREATE TABLE execution_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_record_id UUID NOT NULL,
    step_number INTEGER NOT NULL,
    description TEXT NOT NULL,
    notes TEXT,
    executed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (execution_record_id) REFERENCES execution_records(id) ON DELETE CASCADE,
    UNIQUE (execution_record_id, step_number)
);

CREATE INDEX idx_execution_steps_execution_record_id ON execution_steps(execution_record_id);
```

#### `attachments` Table

Stores metadata for files attached to execution steps (screenshots, evidence files).

**Schema:**
```sql
CREATE TABLE attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_record_id UUID NOT NULL,
    execution_step_id UUID NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(127) NOT NULL,
    storage_type VARCHAR(50) NOT NULL,
    storage_path TEXT NOT NULL,
    uploaded_by UUID NOT NULL,
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (execution_record_id) REFERENCES execution_records(id) ON DELETE CASCADE,
    FOREIGN KEY (execution_step_id) REFERENCES execution_steps(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id),
    CONSTRAINT chk_attachments_storage_type CHECK (storage_type IN ('local', 's3', 'minio'))
);

CREATE INDEX idx_attachments_execution_record_id ON attachments(execution_record_id);
CREATE INDEX idx_attachments_execution_step_id ON attachments(execution_step_id);
CREATE INDEX idx_attachments_uploaded_by ON attachments(uploaded_by);
```

**Note:** `step_number` removed as it's redundant - can be derived from join with `execution_steps` table.

#### `view_history` Table

Records document view history for analytics and user convenience.

**Schema:**
```sql
CREATE TABLE view_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL,
    user_id UUID, -- NULL for anonymous users
    ip_address INET,
    user_agent TEXT,
    viewed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_view_history_document_id ON view_history(document_id);
CREATE INDEX idx_view_history_user_id ON view_history(user_id);
CREATE INDEX idx_view_history_viewed_at ON view_history(viewed_at);
```

#### Data Retention and Partitioning for `view_history`

To ensure the `view_history` table does not grow indefinitely and impact database performance, the following strategies are adopted:

- **Retention Policy:**  
  View history records will be retained for a maximum of 90 days. Records older than this will be purged on a scheduled basis (e.g., nightly or weekly job).

- **Partitioning Strategy:**  
  The `view_history` table should be partitioned by month using PostgreSQL's native partitioning features (e.g., `PARTITION BY RANGE (viewed_at)` with monthly partitions). This improves query performance and simplifies purging of old data.

- **Archive/Purge Strategy:**  
  Old records (older than 90 days) may be deleted directly or exported to cold storage for long-term analytics if required. Purging should be performed using partition drops for efficiency.

These strategies should be reviewed periodically to ensure they meet operational and compliance requirements.
#### `view_statistics` Table

Aggregates view statistics for documents.

**Schema:**
```sql
CREATE TABLE view_statistics (
    document_id UUID PRIMARY KEY,
    total_views BIGINT NOT NULL DEFAULT 0,
    unique_users INTEGER NOT NULL DEFAULT 0,
    last_viewed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);
```

### JSONB Field Schemas

#### `variables` Field (document_versions.variables)

Stores array of VariableDefinition objects for parameterized procedures (per ADR 0013).

**JSON Schema:**
```json
[
  {
    "name": "string",           // Variable identifier (alphanumeric + underscore)
    "label": "string",          // Human-readable label for UI
    "description": "string",    // Optional detailed explanation
    "type": "string",           // "string" | "number" | "boolean" | "date"
    "required": true,           // boolean - Whether variable is mandatory
    "defaultValue": "value"     // any - Optional default value matching type
  }
]
```

**Example:**
```json
[
  {
    "name": "server_name",
    "label": "サーバー名",
    "description": "バックアップ対象のサーバー名",
    "type": "string",
    "required": true,
    "defaultValue": "prod-db-01"
  },
  {
    "name": "retention_days",
    "label": "保持期間（日数）",
    "type": "number",
    "required": false,
    "defaultValue": 30
  }
]
```

#### `variable_values` Field (execution_records.variable_values)

Stores the actual values used during procedure execution (per ADR 0014).

**JSON Schema:**
```json
[
  {
    "name": "string",          // Variable name matching definition
    "value": "any"             // Actual value used
  }
]
```

**Example:**
```json
[
  {
    "name": "server_name",
    "value": "prod-db-01"
  },
  {
    "name": "retention_days",
    "value": 30
  },
  {
    "name": "enable_compression",
    "value": true
  }
]
```

### Access Control Model

**Simplified Access Scope (per ADR 0016):**

Documents and execution records use a simple VARCHAR field with values:
- `public`: Accessible to all users
- `private`: Owner-only by default

**Sharing Mechanism:**

For private resources that need to be shared with specific users or groups, a separate sharing mechanism will be implemented (e.g., DocumentShare or ExecutionRecordShare entity). This keeps the core model simple while maintaining flexibility.

**Note:** JSONB-based AccessScope with `sharedWith` arrays was replaced with this simpler model per ADR 0016 design decisions.

### Data Validation

While this ADR defines database-level constraints (NOT NULL, CHECK, foreign keys), application-level validation rules are documented in **ADR 0017: Application-Level Data Validation**. This includes:
- VariableDefinition validation (name format, type checking)
- VariableValue validation (type matching, required fields)
- DocumentVersion validation (path safety, commit hash format)
- ExecutionRecord validation (state machine transitions)

See ADR 0017 for complete validation specifications.

### Indexing Strategy

#### Standard B-tree Indexes

Used for:
- Primary keys (automatic)
- Foreign keys (for join performance)
- Frequently queried columns (type, status, email, etc.)
- Timestamp columns for range queries

**Rationale:** B-tree indexes are optimal for equality and range queries on scalar values.

#### GIN Indexes (Generalized Inverted Index)

Used for:
- **Array columns:** `document_versions.tags` - enables efficient tag filtering with `@>` operator
- **JSONB columns:** `document_versions.variables`, `execution_records.variable_values` - enables queries on JSON structure

**Example GIN Index Usage:**
```sql
-- Find document versions with specific tag
SELECT * FROM document_versions WHERE tags @> ARRAY['backup'];

-- Find execution records with specific variable name
SELECT * FROM execution_records 
WHERE variable_values @> '[{"name": "server_name"}]'::jsonb;

-- Find execution records with specific variable value (using jsonb_array_elements)
SELECT * FROM execution_records
WHERE EXISTS (
  SELECT 1 FROM jsonb_array_elements(variable_values) AS elem
  WHERE elem->>'name' = 'server_name' AND elem->>'value' = 'prod-db-01'
);
```

**Rationale:** GIN indexes are optimized for composite values where elements can be searched independently.

#### Index Maintenance Considerations

- GIN indexes have higher update costs but excellent query performance
- Suitable for read-heavy workloads (document browsing, search)
- JSONB GIN indexes support both containment (`@>`) and existence (`?`) operators
- Regular VACUUM operations maintain index efficiency

### Data Type Choices

- **UUID:** All primary keys use UUID for distributed system compatibility
- **TIMESTAMPTZ:** All timestamps include timezone for global deployment
- **TEXT vs VARCHAR:** 
  - TEXT for unbounded content (notes, content, file_paths)
  - VARCHAR with limits for controlled fields (names, access_scope values)
- **JSONB vs JSON:** JSONB for better query performance and indexing
- **INET:** Specialized type for IP addresses with built-in validation
- **TEXT[]:** Native array type for tags (better than junction table for simple lists)
- **VARCHAR for access_scope:** Simple enum-style field instead of complex JSONB (per ADR 0016)

## Consequences

### Pros

- **Aligned with ADR 0016:** Document schema follows domain model design decisions
- **Per-version metadata:** Complete history of metadata changes (title, type, tags, variables)
- **Simplified access control:** VARCHAR-based access_scope is easier to query and validate
- **No circular dependencies:** Deferred foreign key constraint for current_version_id
- **Flexible Data Structures:** JSONB for variables enables schema evolution
- **Strong Referential Integrity:** Foreign keys ensure data consistency
- **Performance Optimized:** Strategic indexing for common query patterns
- **Audit Trail:** Execution records provide complete traceability
- **Version Management:** Full version history with rollback capability

### Cons

- **Metadata duplication:** Title, type, tags stored per version instead of once per document
- **More complex version table:** DocumentVersion has more fields than before
- **Application validation required:** JSONB structures require validation per ADR 0017
- **Storage Requirements:** Version history and attachments increase storage needs
- **Migration Effort:** Existing code needs updates for new schema structure
- **Index Overhead:** GIN indexes consume more space and update time
- **Query Complexity:** Cross-aggregate queries may require careful optimization

### Migration Considerations

- New tables should be created in numbered migration files (following ADR 0006)
- Existing `repositories` and `managed_files` tables are unchanged
- Create `documents` table first, then `document_versions`, then add foreign key constraint
- Document metadata needs to be migrated from Document to DocumentVersion
- Consider creating tables in dependency order to avoid foreign key issues
- Production deployment should include data validation and rollback plan
- Circular dependency between `documents` and `document_versions` handled via deferred constraint

### Security Considerations

- `access_token` encrypted at application level (AES-256-GCM)
- Access control enforced at application layer using `access_scope` VARCHAR field
- Simple `public`/`private` model reduces attack surface compared to complex JSONB
- Administrators have implicit access to all resources
- Attachment storage paths must be validated to prevent directory traversal (see ADR 0017)
- JSONB validation critical to prevent injection attacks (see ADR 0017)
