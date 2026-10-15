## [2025-05-16] Decision: Client and Schema Management

**Context**: 
We need a more structured way to manage client organizations and their associated schemas, particularly for managing LLM preferences and other configuration at the schema level. This replaces the previous `site_preferences` table with a more flexible and well-structured approach.

**Decision**:
Create three new tables to manage clients and their schemas:

1. `clients` - Represents client organizations
   - `id` - Primary key
   - `name` - Client/organization name (unique)
   - `created_at` - Timestamp of creation

2. `client_schemas` - Associates schemas with clients
   - `id` - Primary key
   - `client_id` - Reference to clients.id
   - `schema_name` - Name of the PostgreSQL schema (unique)
   - `created_at` - Timestamp of creation

3. `client_schema_preferences` - Replaces site_preferences
   - `id` - Primary key
   - `client_schema_id` - Reference to client_schemas.id
   - `preference_type_id` - Reference to public.preference_types.id
   - `preference_value` - The preference value (text)
   - `created_at` - Timestamp of creation
   - Unique constraint on (client_schema_id, preference_type_id)

**Status**: Implemented

**Impact**:
- New database tables need to be created
- Existing site_preferences data needs to be migrated
- Application code needs to be updated to use the new tables
- LLM selection logic will use client schema preferences

**Example**:
```sql
-- Create tables
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE client_schemas (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    schema_name VARCHAR(63) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE client_schema_preferences (
    id SERIAL PRIMARY KEY,
    client_schema_id INTEGER NOT NULL REFERENCES client_schemas(id) ON DELETE CASCADE,
    preference_type_id INTEGER NOT NULL REFERENCES public.preference_types(id) ON DELETE CASCADE,
    preference_value TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(client_schema_id, preference_type_id)
);

-- Create indexes for performance
CREATE INDEX idx_client_schemas_client_id ON client_schemas(client_id);
CREATE INDEX idx_client_schema_preferences_client_schema_id ON client_schema_preferences(client_schema_id);
CREATE INDEX idx_client_schema_preferences_preference_type ON client_schema_preferences(preference_type_id);
```

**Related**:
- [LLM Preference Hierarchy](./2025-05-16-llm-preference-hierarchy.md)

