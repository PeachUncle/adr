# ADR 001: Supabase Setup and Configuration

**Status**: In Progress
**Date**: 2025-10-08
**Decision Makers**: Development Team

## Context

PortalForge requires a database solution and authentication system for the MVP. We need to set up Supabase to provide:
- PostgreSQL database
- Authentication and authorization
- Row Level Security (RLS)
- Real-time capabilities (future)

## Decision

Use Supabase as the Backend-as-a-Service (BaaS) platform for:
1. PostgreSQL database hosting
2. Authentication (Supabase Auth)
3. API generation
4. Future real-time features

## Database Schema Design

### Core Tables

#### users (Supabase Auth table - managed by Supabase)
```sql
-- Managed by Supabase Auth
-- id (uuid, PK)
-- email
-- encrypted_password
-- created_at
-- updated_at
-- last_sign_in_at
```

#### employees
```sql
CREATE TABLE employees (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) UNIQUE,
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  phone VARCHAR(50),
  position_id UUID REFERENCES positions(id) NOT NULL,
  department_id UUID REFERENCES departments(id) NOT NULL,
  supervisor_id UUID REFERENCES employees(id),
  photo_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_employees_department ON employees(department_id);
CREATE INDEX idx_employees_supervisor ON employees(supervisor_id);
CREATE INDEX idx_employees_email ON employees(email);
```

#### departments
```sql
CREATE TABLE departments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL UNIQUE,
  description TEXT,
  parent_department_id UUID REFERENCES departments(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_departments_parent ON departments(parent_department_id);
```

#### positions
```sql
CREATE TABLE positions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(100) NOT NULL UNIQUE,
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### user_roles
```sql
CREATE TYPE user_role AS ENUM ('Admin', 'Manager', 'HR', 'Marketing', 'Employee');

CREATE TABLE user_roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  role user_role NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),

  UNIQUE(user_id, role)
);

-- Indexes
CREATE INDEX idx_user_roles_user ON user_roles(user_id);
```

#### events
```sql
CREATE TABLE events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(200) NOT NULL,
  description TEXT,
  event_date TIMESTAMPTZ NOT NULL,
  location VARCHAR(200),
  created_by UUID REFERENCES auth.users(id) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_events_date ON events(event_date);
CREATE INDEX idx_events_created_by ON events(created_by);
```

#### event_tags
```sql
CREATE TABLE event_tags (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(50) NOT NULL UNIQUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### event_tag_mappings
```sql
CREATE TABLE event_tag_mappings (
  event_id UUID REFERENCES events(id) ON DELETE CASCADE,
  tag_id UUID REFERENCES event_tags(id) ON DELETE CASCADE,
  PRIMARY KEY (event_id, tag_id)
);
```

#### event_departments
```sql
CREATE TABLE event_departments (
  event_id UUID REFERENCES events(id) ON DELETE CASCADE,
  department_id UUID REFERENCES departments(id) ON DELETE CASCADE,
  PRIMARY KEY (event_id, department_id)
);
```

#### news
```sql
CREATE TABLE news (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(200) NOT NULL,
  content TEXT NOT NULL,
  image_url TEXT,
  event_id UUID REFERENCES events(id),
  created_by UUID REFERENCES auth.users(id) NOT NULL,
  published_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_news_published ON news(published_at);
CREATE INDEX idx_news_created_by ON news(created_by);
CREATE INDEX idx_news_event ON news(event_id);
```

#### audit_logs
```sql
CREATE TYPE audit_action AS ENUM ('CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT');

CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  action audit_action NOT NULL,
  entity_type VARCHAR(50) NOT NULL,
  entity_id UUID,
  old_values JSONB,
  new_values JSONB,
  ip_address INET,
  user_agent TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);
```

### Row Level Security (RLS) Policies

#### employees table
```sql
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;

-- All authenticated users can view employees
CREATE POLICY "Employees viewable by authenticated users"
  ON employees FOR SELECT
  TO authenticated
  USING (true);

-- Only Admin and HR can insert employees
CREATE POLICY "Employees insertable by Admin/HR"
  ON employees FOR INSERT
  TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM user_roles
      WHERE user_id = auth.uid()
      AND role IN ('Admin', 'HR')
    )
  );

-- Employees can update their own record, Admin/HR/Manager can update their department
CREATE POLICY "Employees updatable by self, Admin, HR, or Manager"
  ON employees FOR UPDATE
  TO authenticated
  USING (
    user_id = auth.uid()
    OR EXISTS (
      SELECT 1 FROM user_roles
      WHERE user_id = auth.uid()
      AND role IN ('Admin', 'HR')
    )
    OR EXISTS (
      SELECT 1 FROM user_roles ur
      JOIN employees e ON e.user_id = ur.user_id
      WHERE ur.user_id = auth.uid()
      AND ur.role = 'Manager'
      AND employees.department_id = e.department_id
    )
  );

-- Only Admin can delete employees
CREATE POLICY "Employees deletable by Admin only"
  ON employees FOR DELETE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM user_roles
      WHERE user_id = auth.uid()
      AND role = 'Admin'
    )
  );
```

#### events table
```sql
ALTER TABLE events ENABLE ROW LEVEL SECURITY;

-- All authenticated users can view events
CREATE POLICY "Events viewable by authenticated users"
  ON events FOR SELECT
  TO authenticated
  USING (true);

-- Admin, HR, Marketing can create events
CREATE POLICY "Events insertable by Admin/HR/Marketing"
  ON events FOR INSERT
  TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM user_roles
      WHERE user_id = auth.uid()
      AND role IN ('Admin', 'HR', 'Marketing')
    )
  );

-- Creator or Admin/HR/Marketing can update events
CREATE POLICY "Events updatable by creator or Admin/HR/Marketing"
  ON events FOR UPDATE
  TO authenticated
  USING (
    created_by = auth.uid()
    OR EXISTS (
      SELECT 1 FROM user_roles
      WHERE user_id = auth.uid()
      AND role IN ('Admin', 'HR', 'Marketing')
    )
  );

-- Only Admin can delete events
CREATE POLICY "Events deletable by Admin only"
  ON events FOR DELETE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM user_roles
      WHERE user_id = auth.uid()
      AND role = 'Admin'
    )
  );
```

#### news table (similar pattern)
```sql
ALTER TABLE news ENABLE ROW LEVEL SECURITY;

CREATE POLICY "News viewable by authenticated users"
  ON news FOR SELECT
  TO authenticated
  USING (published_at IS NOT NULL OR created_by = auth.uid());

CREATE POLICY "News insertable by Admin/HR/Marketing"
  ON news FOR INSERT
  TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM user_roles
      WHERE user_id = auth.uid()
      AND role IN ('Admin', 'HR', 'Marketing')
    )
  );

CREATE POLICY "News updatable by creator or Admin/HR/Marketing"
  ON news FOR UPDATE
  TO authenticated
  USING (
    created_by = auth.uid()
    OR EXISTS (
      SELECT 1 FROM user_roles
      WHERE user_id = auth.uid()
      AND role IN ('Admin', 'HR', 'Marketing')
    )
  );

CREATE POLICY "News deletable by Admin only"
  ON news FOR DELETE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM user_roles
      WHERE user_id = auth.uid()
      AND role = 'Admin'
    )
  );
```

## Supabase Configuration Steps

### 1. Create Project
1. Go to https://supabase.com/dashboard
2. Click "New Project"
3. Choose organization
4. Set project name: `portalforge`
5. Set strong database password (save to password manager)
6. Choose region (closest to users)
7. Choose plan: Free tier for development, Pro for production

### 2. Get API Keys
1. Go to Project Settings > API
2. Copy `Project URL` → Use in `NUXT_PUBLIC_SUPABASE_URL`
3. Copy `anon public` key → Use in `NUXT_PUBLIC_SUPABASE_KEY`
4. Copy `service_role` key (keep secret!) → Use server-side only

### 3. Configure Authentication
1. Go to Authentication > Providers
2. Enable Email authentication
3. Configure email templates (optional for MVP)
4. Set site URL in Authentication > URL Configuration
5. Add redirect URLs for localhost and production

### 4. Run Database Migrations
1. Go to SQL Editor
2. Create new query
3. Paste schema from above
4. Run migrations in order:
   - Create types (ENUM)
   - Create tables
   - Add indexes
   - Enable RLS
   - Create policies

### 5. Seed Initial Data
```sql
-- Insert default positions
INSERT INTO positions (title, description) VALUES
  ('CEO', 'Chief Executive Officer'),
  ('CTO', 'Chief Technology Officer'),
  ('Department Manager', 'Manages a department'),
  ('Team Lead', 'Leads a team'),
  ('Developer', 'Software Developer'),
  ('Designer', 'UI/UX Designer'),
  ('HR Specialist', 'Human Resources');

-- Insert default departments
INSERT INTO departments (name, description) VALUES
  ('Executive', 'Executive management'),
  ('IT', 'Information Technology'),
  ('HR', 'Human Resources'),
  ('Marketing', 'Marketing and Communications');

-- Insert default tags
INSERT INTO event_tags (name) VALUES
  ('#szkolenie'),
  ('#impreza'),
  ('#spotkanie'),
  ('#ogłoszenie'),
  ('#konferencja');
```

## Backend Integration (.NET)

### Connection String
```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=db.your-project-ref.supabase.co;Port=5432;Database=postgres;Username=postgres;Password=your-password"
  }
}
```

### Supabase Auth Integration
- Use Supabase Auth SDK or implement JWT validation
- Validate JWT tokens from `Authorization: Bearer <token>` header
- Extract user claims (user_id, email, role)
- Use `user_id` to query `user_roles` table for authorization

## Frontend Integration (Nuxt 3)

### Install Supabase Client
```bash
npm install @supabase/supabase-js
```

### Create Supabase Plugin
```typescript
// plugins/supabase.ts
import { createClient } from '@supabase/supabase-js'

export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()

  const supabase = createClient(
    config.public.supabaseUrl,
    config.public.supabaseKey
  )

  return {
    provide: {
      supabase
    }
  }
})
```

## Consequences

### Positive
- Managed PostgreSQL reduces ops overhead
- Built-in authentication saves development time
- RLS provides database-level security
- Real-time capabilities available for future features
- Automatic API generation with PostgREST

### Negative
- Vendor lock-in (mitigated by using standard PostgreSQL)
- Cost scales with usage (free tier sufficient for MVP)
- Learning curve for RLS policies

## Alternatives Considered

1. **Self-hosted PostgreSQL + custom auth**
   - Rejected: Too much ops overhead for MVP

2. **Firebase**
   - Rejected: NoSQL not ideal for relational data

3. **Auth0 + AWS RDS**
   - Rejected: Higher cost and complexity

## Next Steps

1. Create Supabase project
2. Run database migrations
3. Configure authentication providers
4. Test connection from backend
5. Test authentication from frontend
6. Implement first protected API endpoint
7. Document environment setup in README

---

**Related Documents**:
- [PRD](.ai/prd.md)
- [Tech Stack](.ai/tech-stack.md)
- [Backend Architecture](.ai/backend/README.md)
