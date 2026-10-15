# ADR-004: Local Database Design for MVP

**Author: JP + 2025-06-16**
**Status**: Accepted
**Date**: 2025-06-16

## Context

The AI Marketing Campaign Post Generator platform requires persistent data storage for the MVP phase. The solution needs to be self-contained, easy to deploy locally, and scalable to cloud-based solutions in the future. We need to define the database schema, data structures, and storage strategy that aligns with our Agentic AI architecture and campaign management requirements.

## Decision

We have decided to implement **SQLite as the local database solution** for the MVP phase with a well-defined schema that supports the complete campaign lifecycle and user management.

### Database Choice: SQLite

**Primary Database**: SQLite 3.x for local MVP deployment
**Future Migration Path**: PostgreSQL for cloud production deployment

### Core Data Structures

#### 1. Users Table
```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,                    -- UUID v4 format
    username TEXT UNIQUE NOT NULL,         -- Unique username for login
    email TEXT UNIQUE NOT NULL,            -- Email address (unique)
    password_hash TEXT NOT NULL,           -- Bcrypt hashed password
    first_name TEXT,                       -- User's first name
    last_name TEXT,                        -- User's last name
    profile_data TEXT,                     -- JSON: preferences, settings
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,                  -- Track user activity
    is_active BOOLEAN DEFAULT TRUE,        -- Soft delete capability
    
    -- Constraints
    CONSTRAINT users_email_format CHECK (email LIKE '%@%.%'),
    CONSTRAINT users_username_length CHECK (length(username) >= 3)
);
```

#### 2. Campaigns Table
```sql
CREATE TABLE campaigns (
    id TEXT PRIMARY KEY,                    -- UUID v4 format
    name TEXT NOT NULL,                     -- Campaign name
    business_description TEXT,              -- Business context description
    objective TEXT,                         -- Campaign objective
    campaign_type TEXT DEFAULT 'general',  -- 'product', 'service', 'brand', 'event', 'general'
    creativity_level INTEGER DEFAULT 5,    -- 1-10 scale for AI creativity
    target_audience TEXT,                   -- Target audience description
    
    -- Business Context URLs
    business_website TEXT,                  -- Primary business website
    about_page_url TEXT,                   -- About page URL
    product_service_url TEXT,              -- Product/service page URL
    
    -- Campaign Configuration
    preferred_design TEXT,                  -- Design preferences
    brand_voice TEXT,                      -- Brand voice guidelines
    campaign_settings TEXT,                -- JSON: additional settings
    
    -- AI Generated Context
    ai_summary TEXT,                       -- AI-generated business summary
    business_context TEXT,                 -- JSON: comprehensive business analysis
    suggested_themes TEXT,                 -- JSON: array of suggested themes
    suggested_tags TEXT,                   -- JSON: array of suggested tags
    selected_themes TEXT,                  -- JSON: user-selected themes
    selected_tags TEXT,                    -- JSON: user-selected tags
    
    -- Metadata
    user_id TEXT NOT NULL,                 -- Foreign key to users table
    status TEXT DEFAULT 'draft',           -- 'draft', 'active', 'completed', 'archived'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,                -- When campaign was completed
    
    -- Foreign Key Constraints
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Check Constraints
    CONSTRAINT campaigns_name_length CHECK (length(name) >= 1),
    CONSTRAINT campaigns_creativity_range CHECK (creativity_level BETWEEN 1 AND 10),
    CONSTRAINT campaigns_status_values CHECK (status IN ('draft', 'active', 'completed', 'archived')),
    CONSTRAINT campaigns_type_values CHECK (campaign_type IN ('product', 'service', 'brand', 'event', 'general'))
);
```

#### 3. Generated Content Table
```sql
CREATE TABLE generated_content (
    id TEXT PRIMARY KEY,                    -- UUID v4 format
    campaign_id TEXT NOT NULL,             -- Foreign key to campaigns table
    content_type TEXT NOT NULL,            -- 'idea', 'social_post', 'video_prompt', 'hashtags'
    platform TEXT,                        -- 'linkedin', 'twitter', 'instagram', 'facebook', 'tiktok', 'general'
    
    -- Content Data
    title TEXT,                            -- Content title/headline
    content_text TEXT,                     -- Main content text
    content_data TEXT,                     -- JSON: complete content structure
    
    -- AI Generation Context
    generation_prompt TEXT,                -- Prompt used to generate content
    ai_model TEXT,                         -- AI model used (e.g., 'gemini-2.0-flash')
    generation_parameters TEXT,            -- JSON: temperature, max_tokens, etc.
    
    -- Content Metadata
    hashtags TEXT,                         -- JSON: array of hashtags
    mentions TEXT,                         -- JSON: array of mentions
    media_urls TEXT,                       -- JSON: array of media URLs
    engagement_score REAL,                 -- Predicted engagement score (0-1)
    
    -- User Interaction
    is_selected BOOLEAN DEFAULT FALSE,     -- User selected this content
    is_published BOOLEAN DEFAULT FALSE,    -- Content has been published
    user_edits TEXT,                       -- JSON: user modifications
    user_rating INTEGER,                   -- User rating 1-5
    
    -- Scheduling
    scheduled_for TIMESTAMP,               -- When content is scheduled to publish
    published_at TIMESTAMP,                -- When content was actually published
    platform_post_id TEXT,                -- External platform post ID
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
    
    -- Check Constraints
    CONSTRAINT content_type_values CHECK (content_type IN ('idea', 'social_post', 'video_prompt', 'hashtags', 'summary')),
    CONSTRAINT platform_values CHECK (platform IN ('linkedin', 'twitter', 'instagram', 'facebook', 'tiktok', 'general') OR platform IS NULL),
    CONSTRAINT user_rating_range CHECK (user_rating BETWEEN 1 AND 5 OR user_rating IS NULL),
    CONSTRAINT engagement_score_range CHECK (engagement_score BETWEEN 0 AND 1 OR engagement_score IS NULL)
);
```

#### 4. Uploaded Files Table
```sql
CREATE TABLE uploaded_files (
    id TEXT PRIMARY KEY,                    -- UUID v4 format
    campaign_id TEXT NOT NULL,             -- Foreign key to campaigns table
    user_id TEXT NOT NULL,                 -- Foreign key to users table
    
    -- File Information
    original_filename TEXT NOT NULL,       -- Original uploaded filename
    stored_filename TEXT NOT NULL,         -- Stored filename (UUID-based)
    file_path TEXT NOT NULL,               -- Relative path to file
    file_size INTEGER NOT NULL,            -- File size in bytes
    mime_type TEXT NOT NULL,               -- MIME type
    file_category TEXT NOT NULL,           -- 'image', 'document', 'campaign_asset', 'other'
    
    -- File Analysis
    analysis_status TEXT DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    analysis_results TEXT,                 -- JSON: AI analysis results
    extracted_text TEXT,                   -- Extracted text from documents
    image_analysis TEXT,                   -- JSON: image analysis results
    
    -- Metadata
    upload_source TEXT,                    -- 'web_upload', 'drag_drop', 'api'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Check Constraints
    CONSTRAINT file_category_values CHECK (file_category IN ('image', 'document', 'campaign_asset', 'other')),
    CONSTRAINT analysis_status_values CHECK (analysis_status IN ('pending', 'processing', 'completed', 'failed')),
    CONSTRAINT file_size_positive CHECK (file_size > 0)
);
```

#### 5. Campaign Templates Table
```sql
CREATE TABLE campaign_templates (
    id TEXT PRIMARY KEY,                    -- UUID v4 format
    name TEXT NOT NULL,                     -- Template name
    description TEXT,                       -- Template description
    category TEXT NOT NULL,                -- 'product_launch', 'brand_awareness', 'event_promotion', 'custom'
    
    -- Template Configuration
    template_data TEXT NOT NULL,           -- JSON: complete template structure
    default_settings TEXT,                 -- JSON: default campaign settings
    prompt_templates TEXT,                 -- JSON: AI prompt templates
    
    -- Usage Tracking
    usage_count INTEGER DEFAULT 0,         -- How many times template was used
    is_public BOOLEAN DEFAULT FALSE,       -- Available to all users
    created_by TEXT,                       -- User ID who created template
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    
    -- Check Constraints
    CONSTRAINT template_category_values CHECK (category IN ('product_launch', 'brand_awareness', 'event_promotion', 'custom')),
    CONSTRAINT template_name_length CHECK (length(name) >= 1)
);
```

#### 6. User Sessions Table
```sql
CREATE TABLE user_sessions (
    id TEXT PRIMARY KEY,                    -- Session ID (UUID v4)
    user_id TEXT NOT NULL,                 -- Foreign key to users table
    session_token TEXT UNIQUE NOT NULL,    -- Secure session token
    
    -- Session Data
    session_data TEXT,                     -- JSON: session information
    ip_address TEXT,                       -- Client IP address
    user_agent TEXT,                       -- Client user agent
    
    -- Session Lifecycle
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,         -- Session expiration
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Foreign Key Constraints
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Check Constraints
    CONSTRAINT session_expires_future CHECK (expires_at > created_at)
);
```

### Database Indexes for Performance

```sql
-- User table indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);

-- Campaign table indexes
CREATE INDEX idx_campaigns_user_id ON campaigns(user_id);
CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_campaigns_type ON campaigns(campaign_type);
CREATE INDEX idx_campaigns_created_at ON campaigns(created_at);

-- Generated content indexes
CREATE INDEX idx_content_campaign_id ON generated_content(campaign_id);
CREATE INDEX idx_content_type ON generated_content(content_type);
CREATE INDEX idx_content_platform ON generated_content(platform);
CREATE INDEX idx_content_selected ON generated_content(is_selected);
CREATE INDEX idx_content_published ON generated_content(is_published);

-- Uploaded files indexes
CREATE INDEX idx_files_campaign_id ON uploaded_files(campaign_id);
CREATE INDEX idx_files_user_id ON uploaded_files(user_id);
CREATE INDEX idx_files_category ON uploaded_files(file_category);
CREATE INDEX idx_files_analysis_status ON uploaded_files(analysis_status);

-- Session indexes
CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_sessions_expires ON user_sessions(expires_at);
CREATE INDEX idx_sessions_active ON user_sessions(is_active);
```

## Rationale

### Why SQLite for MVP?

1. **Self-Contained Deployment**: No external database server required
2. **Zero Configuration**: Works out of the box with Python
3. **ACID Compliance**: Full transaction support
4. **Cross-Platform**: Works on macOS, Linux, Windows
5. **Migration Path**: Easy to migrate to PostgreSQL later
6. **Performance**: Sufficient for MVP user load (< 100 concurrent users)

### Schema Design Principles

1. **UUID Primary Keys**: Globally unique, secure, migration-friendly
2. **JSON Columns**: Flexible storage for complex data structures
3. **Comprehensive Constraints**: Data integrity at database level
4. **Audit Trail**: Created/updated timestamps on all tables
5. **Soft Deletes**: Preserve data integrity with is_active flags
6. **Foreign Key Constraints**: Maintain referential integrity
7. **Performance Indexes**: Optimized for common query patterns

### Data Structure Rationale

#### Campaign-Centric Design
- **Campaigns** as the central entity around which all content revolves
- **Generated Content** linked to campaigns for complete traceability
- **Uploaded Files** associated with campaigns for context analysis

#### User Management
- **Simple Authentication**: Username/password with session management
- **Profile Flexibility**: JSON profile_data for extensible user preferences
- **Session Security**: Secure token-based session management

#### Content Versioning
- **Generation Context**: Track AI prompts and parameters used
- **User Modifications**: Store user edits separately from AI-generated content
- **Publishing Workflow**: Track content from generation to publication

## Consequences

### Positive
- **Rapid Development**: No database setup complexity
- **Data Integrity**: Comprehensive constraints prevent data corruption
- **Scalability**: Schema designed for future PostgreSQL migration
- **Flexibility**: JSON columns allow schema evolution without migrations
- **Performance**: Proper indexing for common access patterns

### Negative
- **Concurrent Users**: SQLite has limitations for high concurrency
- **File Storage**: Local file storage not suitable for distributed deployment
- **Backup Complexity**: File-based backup requires application-level coordination

### Risks
- **Data Loss**: Single file database requires careful backup strategy
- **Migration Complexity**: Moving to PostgreSQL will require data transformation
- **Scaling Limits**: Will need migration before reaching production scale

## Implementation Notes

### Database Initialization
```python
# Database initialization script
import sqlite3
import uuid
from datetime import datetime, timedelta

def initialize_database(db_path: str):
    """Initialize the SQLite database with schema and indexes."""
    conn = sqlite3.connect(db_path)
    
    # Execute schema creation
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    
    # Create default admin user
    admin_id = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO users (id, username, email, password_hash, first_name, last_name, is_active)
        VALUES (?, 'admin', 'admin@videventurelaunch.local', ?, 'Admin', 'User', TRUE)
    """, (admin_id, hash_password('admin123')))
    
    conn.commit()
    conn.close()
```

### Migration Strategy
1. **Phase 1**: SQLite for MVP (current)
2. **Phase 2**: Add PostgreSQL support alongside SQLite
3. **Phase 3**: Migration tools for data transfer
4. **Phase 4**: Deprecate SQLite for production

### Backup Strategy
```bash
# Automated backup script
#!/bin/bash
BACKUP_DIR="backups"
DB_FILE="data/video_venture_launch.db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cp $DB_FILE $BACKUP_DIR/video_venture_launch_$TIMESTAMP.db
```

## Review Date

This ADR should be reviewed when:
1. User load exceeds 50 concurrent users
2. Data size exceeds 1GB
3. Multi-server deployment is required
4. Advanced database features are needed (replication, clustering)

## Related ADRs

- ADR-001: Technology Stack Selection
- ADR-003: Backend ADK Implementation
- Future ADR: PostgreSQL Migration Strategy 