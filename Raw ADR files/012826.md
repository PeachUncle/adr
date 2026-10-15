# ADR-004: Database

# ADR-004: Database (PostgreSQL Everywhere)

## Status

Accepted

## Context

We need a database for the Ohana Booking System to store:

- Users, clients, performers, inquiries, bookings
- Financial data (payments, payouts, expenses)
- Audit logs and notifications

Key considerations:

- Relational data with foreign keys (bookings → performers, inquiries → clients)
- JSON storage needs (performer skills, audit log changes)
- Complex queries (financial reports, availability checks)
- Local development experience
- Production hosting

## Decision Drivers

- **Data model fit**: Relational data with strong consistency needs
- **Developer experience**: Easy local setup and development
- **Type safety**: Works well with Drizzle ORM
- **JSON support**: Modern Postgres features (jsonb columns)
- **Hosting options**: Wide availability on hosting platforms
- **Consistency**: Same database in dev and prod avoids surprises

## Options Considered

### Option A: PostgreSQL Everywhere

**Pros:**

- ✅ **Relational + JSON** - best of both worlds (jsonb columns)
- ✅ **Full-text search** - built-in search capabilities
- ✅ **JSON queries** - can query inside jsonb columns
- ✅ **ACID compliance** - strong consistency guarantees
- ✅ **Excellent Drizzle support** - first-class integration
- ✅ **Wide hosting options** - Railway, Supabase, Neon, AWS RDS
- ✅ **Docker for local dev** - simple docker-compose setup
- ✅ **No surprises** - same behavior in dev and prod
- ✅ **Mature ecosystem** - proven at scale

**Cons:**

- ⚠️ **Local setup requires Docker** - slight setup overhead
- ⚠️ **Resource usage** - heavier than SQLite locally

### Option B: SQLite (dev) → PostgreSQL (prod)

**Pros:**

- ✅ **Simple local dev** - no Docker needed, just a file
- ✅ **Fast local queries** - in-process database
- ✅ **Easy backup** - copy database file

**Cons:**

- ❌ **Subtle differences** - SQLite vs Postgres SQL dialects differ
- ❌ **Limited JSON support** - SQLite's JSON is weaker than Postgres
- ❌ **Testing risk** - behavior differences between dev/prod
- ❌ **Migration complexity** - Drizzle must support both
- ❌ **Production surprises** - queries work locally but fail in prod

### Option C: MongoDB

**Pros:**

- ✅ **Flexible schema** - JSON documents
- ✅ **Easy local setup** - Docker or cloud

**Cons:**

- ❌ **Not relational** - no foreign keys, join complexity
- ❌ **Weaker consistency** - eventual consistency by default
- ❌ **Overkill** - don't need document flexibility
- ❌ **Drizzle focus** - Drizzle primarily targets SQL databases

## Decision

**We will use PostgreSQL everywhere (local development and production).**

### Local Development Setup

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ohana_dev
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - '5432:5432'
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

**Alternative:** Use Railway/Supabase free tier for local dev (no Docker required)

### Production Hosting

**Primary Option:** Railway

- Managed Postgres included
- Automatic backups
- Simple connection string
- $5/month hobby plan

**Backup Options:** Supabase, Neon, AWS RDS

### Rationale

1. **Consistency** - Identical behavior in dev/staging/prod
2. **Rich features** - jsonb, full-text search, advanced queries
3. **Drizzle integration** - Excellent first-class support
4. **No surprises** - Test with real production database behavior
5. **Scaling path** - Postgres scales well if project grows

## Consequences

### Positive

- No dev/prod database differences to debug
- Can use advanced Postgres features (jsonb, full-text search, CTEs)
- Financial reports can use complex SQL queries efficiently
- Audit logs stored as jsonb (flexible querying)
- Wide hosting options if Railway becomes limiting
- Strong ACID guarantees for financial data

### Negative

- Requires Docker for local dev (or cloud dev database)
- Slightly heavier local resource usage than SQLite
- One more service to run locally

### Risks

- **Docker complexity**: Contributors must have Docker installed
  - _Mitigation_: Provide clear setup docs; alternatively, use Railway dev database
- **Cost in production**: Managed Postgres costs more than SQLite file
  - _Mitigation_: Railway hobby plan is $5/month; acceptable for business use

## Follow-up Actions

- [ ] Create `docker-compose.yml` for local Postgres
- [ ] Document local setup in README
- [ ] Configure Drizzle for Postgres connection
- [ ] Set up Railway project with Postgres addon
- [ ] Configure database connection env vars
- [ ] Set up automated backups in production
- [ ] Create seed script for local development data
