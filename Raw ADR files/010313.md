# ADR-003: Database Environment Strategy for Development Workflow

**Status:** Accepted
**Date:** 2025-09-19
**Context:** REQ-078 Hosting Environment Setup
**Supersedes:** None

## Context

During the implementation of REQ-078 (Hosting Environment Setup), we needed to decide on the database strategy for different environments. The Learning Platform uses Django with PostgreSQL in production, but we need to determine the optimal database configuration for local development, development environment, and production.

## Decision

We will implement **Option A: Local SQLite for Development** with the following environment-specific database strategy:

### Environment Configuration

| Environment | Database | Purpose | Rationale |
|-------------|----------|---------|-----------|
| **Local Development** | SQLite | Developer workstations | Fast, zero-config, no network dependencies |
| **Development Environment** (Railway) | Neon PostgreSQL | Integration testing | Production-like database for realistic testing |
| **Production Environment** (Railway) | Neon PostgreSQL | Production workloads | Managed PostgreSQL with auto-scaling |

### Technical Implementation

```python
# Django settings.py configuration
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",  # Fallback to SQLite
        conn_max_age=600,
        conn_health_checks=True,
    )
}
```

**Environment Variable Behavior:**
- **No `DATABASE_URL`** → SQLite used automatically
- **With `DATABASE_URL`** → PostgreSQL used (Railway environments)

## Alternatives Considered

### Option B: Neon PostgreSQL for Everything
```
Local Development: Neon PostgreSQL (separate database)
Development Environment: Neon PostgreSQL
Production Environment: Neon PostgreSQL
```

**Rejected because:**
- Network dependency for local development
- Slower local development experience
- Potential for accidental data pollution between environments
- Additional Neon database costs for each developer

### Option C: Docker PostgreSQL Locally
```
Local Development: Docker PostgreSQL
Development Environment: Neon PostgreSQL
Production Environment: Neon PostgreSQL
```

**Rejected because:**
- Additional complexity for developer setup
- Docker dependency and resource usage
- SQLite already handles Django ORM compatibility perfectly

## Advantages

### ✅ Chosen Strategy (Option A) Benefits

1. **Developer Experience**
   - Zero-config local development
   - Fast database operations (no network latency)
   - No external dependencies for basic development
   - Instant test database reset with `rm db.sqlite3`

2. **Cost Efficiency**
   - No additional database costs for local development
   - Single Neon instance for development environment
   - Single Neon instance for production environment

3. **Environment Isolation**
   - Complete isolation between local and remote environments
   - No risk of accidentally affecting development/production data
   - Easy to reset local state

4. **Testing Benefits**
   - Django tests run faster with SQLite
   - Parallel test execution works out of the box
   - No test database cleanup concerns

5. **Deployment Simplicity**
   - Railway automatically detects and configures PostgreSQL
   - Environment variables handle database switching seamlessly
   - No manual database setup for developers

## Disadvantages

### ⚠️ Known Limitations

1. **Database Feature Differences**
   - SQLite vs PostgreSQL feature differences (JSON fields, full-text search)
   - Potential for SQLite-specific bugs not caught locally
   - Different query performance characteristics

2. **Data Inconsistencies**
   - Local development data doesn't persist between deployments
   - Need to manually test PostgreSQL-specific features

### 🛡️ Mitigation Strategies

1. **PostgreSQL Testing**
   - CI/CD pipeline runs tests against PostgreSQL (Railway environment)
   - Optional local PostgreSQL connection for specific feature testing
   - Database migration testing in development environment

2. **Documentation**
   - Clear instructions for when to test against PostgreSQL
   - Migration guides for switching databases locally when needed

3. **Development Process**
   - Database-specific features tested in development environment
   - Regular synchronization of schema between environments

## Implementation Details

### Local Development Setup
```bash
# .env file (optional, defaults to SQLite)
DEBUG=True
SECRET_KEY=local-development-key
# DATABASE_URL commented out → uses SQLite
```

### Railway Development Environment
```bash
# Railway Environment Variables (set via Railway dashboard)
DATABASE_URL=postgresql://user:pass@ep-xxx.region.aws.neon.tech/dbname
DEBUG=False
SECRET_KEY=secure-development-key
```

### Railway Production Environment
```bash
# Railway Environment Variables (set via Railway dashboard)
DATABASE_URL=postgresql://user:pass@ep-xxx.region.aws.neon.tech/proddb
DEBUG=False
SECRET_KEY=secure-production-key
```

## Migration Strategy

### From Current State
1. ✅ Django settings already configured with `dj_database_url.config()`
2. ✅ SQLite fallback already implemented
3. ✅ `.env` file structure created with proper `.gitignore`
4. 🔄 Neon PostgreSQL setup for Railway environments (in progress)

### Future Considerations
- If team grows >5 developers: Consider shared development database
- If SQLite limitations become problematic: Switch to Docker PostgreSQL locally
- If cost becomes an issue: Evaluate database sharing strategies

## Compliance and Security

### Data Protection
- Local SQLite files in `.gitignore` (no sensitive data in repository)
- Production data never accessible from local development
- Environment isolation prevents data leakage

### Backup Strategy
- Local development: No backup needed (disposable data)
- Development environment: Neon automatic backups
- Production environment: Neon automatic backups + point-in-time recovery

## Success Metrics

### Developer Experience
- [ ] New developer onboarding <30 minutes (including database setup)
- [ ] Local development server starts in <10 seconds
- [ ] Database migrations apply successfully across all environments

### Environment Parity
- [ ] CI/CD tests pass against PostgreSQL
- [ ] Production deployments succeed without database issues
- [ ] No SQLite-specific bugs in production

### Cost Management
- [ ] Development database costs <$20/month total
- [ ] No per-developer database costs
- [ ] Production database scales cost-effectively

## Related Documents

- [REQ-078: Hosting Environment Setup](../requirements/REQ-078-hosting-environment-setup.md)
- [Vercel Deployment Best Practices](../vercel-deployment-best-practices.md)

## Decision History

**2025-09-19:** Initial decision - Option A selected for MVP implementation
**Future:** Review after 3 months of development or when team reaches 5+ developers