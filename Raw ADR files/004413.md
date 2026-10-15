---
ADR #: 0401
Title: Prohibition of Ephemeral Databases in Production and Security-Critical Test Environments
Date: 2025-11-08
Status: Accepted
Authors: UCF Governance / EHDC Lab Team
---

# 1. Context

During the final security validation of the XRPL WebAuth integration in the **EHDC Lab** (Pillar IV), a critical failure occurred that exposed a fundamental infrastructure flaw: **security features that depend on persistent state cannot be reliably tested or deployed on ephemeral database infrastructure.**

## The EHDC Security Validation Failure

The EHDC debugging marathon culminated in the successful implementation of the two-step cryptographic challenge/verify pattern for wallet authentication (documented in ADR-0601). However, the final security validation revealed a catastrophic failure mode:

### Failure Sequence

1. **Challenge Generation**: User initiates wallet authentication via `POST /api/auth/wallet/challenge`
2. **Server Response**: Challenge record created in database, nonce and message returned to client
3. **Development Iteration**: Developer makes code change, triggering automatic server restart (standard Codespace/development workflow)
4. **Database Wipe**: SQLite in-memory/file-based database cleared on server restart
5. **Verification Attempt**: User submits signed message via `POST /api/auth/wallet/verify`
6. **Fatal Error**: Server responds with `{"error":"Not Found","message":"Challenge not found"}`

### Root Cause

The security flow **requires persistent state** between the challenge generation and verification steps. The `WalletChallenge` record must survive server restarts, code deployments, and container cycling to function correctly.

**Ephemeral databases** (SQLite in-memory mode, file-based SQLite in temporary directories, or any database that does not persist beyond process lifecycle) **fundamentally cannot support stateful security primitives.**

## Forces at Play

* **Security Criticality**: Wallet authentication, session management, and cryptographic challenge flows are security-critical features that must function reliably.
* **Development Velocity**: Modern development workflows (hot reload, automatic restarts, container orchestration) frequently restart application processes.
* **State Persistence**: Security features often require state that spans multiple HTTP requests and must survive application restarts.
* **Testing Realism**: Tests of security features must use infrastructure that mirrors production constraints.
* **Infrastructure Cost**: Persistent databases (especially managed services) incur additional cost compared to ephemeral alternatives.

## Problem Statement

How do we ensure that security-critical features are developed, tested, and deployed on infrastructure that guarantees state persistence across application lifecycle events?

## Constraints

* **Technical**: Security primitives requiring multi-step flows cannot function on ephemeral storage.
* **Operational**: Development and test environments must mirror production architecture to catch integration failures early.
* **Business**: Failures in production security features can lead to user lockouts, authentication bypasses, or data loss.
* **Compliance**: Security testing must use realistic infrastructure to validate real-world behavior.

# 2. Decision

**The UCF prohibits the use of ephemeral (in-memory or non-persistent file-based) databases in all production environments and in any test environment used for security-critical feature validation.**

## Mandated Infrastructure

### For Production Environments
All production deployments MUST use **persistent, externally-hosted databases** that guarantee:
- Data persistence across application restarts
- Data persistence across container/VM recycling
- Backup and recovery capabilities
- High availability and redundancy

**Approved database types for production:**
- PostgreSQL (managed services: Supabase, Neon, AWS RDS, Google Cloud SQL, Azure Database)
- MySQL/MariaDB (managed services: PlanetScale, AWS RDS, Google Cloud SQL)
- MongoDB (MongoDB Atlas)
- Any other ACID-compliant database with persistent external storage

**Prohibited for production:**
- SQLite in-memory mode (`:memory:`)
- SQLite file-based in temporary directories (`/tmp`, container ephemeral storage)
- Redis used as primary database (acceptable for caching/sessions only)
- Any database that loses data on process restart

### For Security-Critical Test Environments
Any test environment used to validate security features (authentication, authorization, cryptographic flows, session management) MUST use the same class of persistent database as production.

**Approved approaches:**
- **Development**: Docker Compose with persistent volumes for PostgreSQL/MySQL
- **CI/CD**: GitHub Actions with PostgreSQL service containers
- **Integration Tests**: Testcontainers with persistent database images
- **Staging**: Managed database services (Supabase free tier, Neon free tier, etc.)

**Prohibited for security testing:**
- SQLite (any mode)
- In-memory databases
- Mock/stub databases that don't persist state

### For Non-Security-Critical Testing
Unit tests that do not involve security-critical flows MAY use ephemeral databases for speed, but must be clearly segregated from integration/security tests.

## Reasoning

The EHDC failure demonstrates that **ephemeral databases create a false sense of security**. Tests may pass, code may work in simple scenarios, but the system fails catastrophically when subjected to real-world operational events (restarts, deployments, scaling).

**Security features require infrastructure that mirrors their criticality.** If wallet authentication is critical enough to require cryptographic proofs, it is critical enough to require persistent infrastructure.

The additional cost and complexity of persistent databases is **trivial compared to the cost of production authentication failures**, user lockouts, or security breaches.

## EHDC Lab PostgreSQL Migration: Validation of the Solution

Following the SQLite failure, the EHDC Lab executed a complete migration to PostgreSQL (Supabase) that definitively validated this architectural mandate.

### Migration Details (EHDC PR #12, November 8-9, 2025)

**From**: SQLite file-based database with ephemeral storage
**To**: PostgreSQL 15+ on Supabase (managed service)

### Critical Configuration Discovery

The migration revealed important implementation details for Prisma ORM + PostgreSQL:

**Dual-Database URL Pattern** (Required for Supabase/Prisma):
```prisma
datasource db {
  provider  = "postgresql"
  url       = env("DATABASE_URL")      // Pooled connection (port 6543)
  directUrl = env("DIRECT_URL")        // Direct connection (port 5432)
}
```

**Port Configuration**:
- **DATABASE_URL**: Pooled connection (`*.pooler.supabase.com:6543`) - Used for application runtime
- **DIRECT_URL**: Direct connection (`*.supabase.com:5432`) - Required for migrations

**Critical**: Using only the pooled connection causes Prisma migrations to hang indefinitely. The `directUrl` configuration is **mandatory** for migration execution.

### Data Model Improvements

The PostgreSQL migration enabled native array support, eliminating JSON serialization workarounds:

**Before (SQLite)**:
```typescript
keyPoints: JSON.stringify(data.keyPoints)  // Manual serialization required
```

**After (PostgreSQL)**:
```prisma
keyPoints String[]  // Native array support
```

```typescript
keyPoints: data.keyPoints  // Direct array assignment
```

### Validation Results

After migration to PostgreSQL:
1. ✅ **Challenge persistence**: WalletChallenge records survive server restarts
2. ✅ **End-to-end flow**: Complete challenge/verify cycle works across code changes
3. ✅ **Development parity**: Development environment matches production infrastructure
4. ✅ **Security validation**: No "Challenge not found" errors on verification

The wallet authentication flow (ADR-0601) was successfully validated end-to-end on persistent infrastructure.

### Documentation

The EHDC Lab created comprehensive migration documentation:
- `MIGRATION_GUIDE.md`: Supabase configuration, port selection, common issues
- `README-dev.md`: Complete development environment setup (600+ lines)
- `docs/XRPL-WALLET-VERIFICATION.md`: End-to-end integration testing guide

# 3. Consequences

## Positive Consequences

* **Reliability**: Security features function correctly across application lifecycle events (restarts, deployments, scaling).
* **Early Failure Detection**: Development and test environments catch persistence-related failures before production deployment.
* **Production Parity**: Test environments mirror production infrastructure, increasing confidence in test results.
* **Operational Clarity**: Teams know immediately that persistent databases are required, eliminating ambiguity in infrastructure choices.
* **Security Posture**: Reduces risk of authentication bypass, session hijacking, or data loss due to infrastructure failures.
* **User Trust**: Users can rely on authentication flows working consistently without mysterious "challenge not found" errors.

## Negative Consequences

* **Infrastructure Cost**: Persistent databases (especially managed services) cost more than SQLite or in-memory alternatives.
  - **Mitigation**: Free tiers available (Supabase, Neon, PlanetScale) for development/small projects.
* **Setup Complexity**: Developers must configure external database connections instead of zero-config SQLite.
  - **Mitigation**: Docker Compose templates and setup scripts provided in Implementation Lab repositories.
* **Test Execution Speed**: Integration tests using persistent databases may be slower than in-memory alternatives.
  - **Mitigation**: Use database transactions with rollback for test isolation; reserve ephemeral databases for non-security unit tests.

## Neutral Consequences

* **Technology Standardization**: UCF Implementation Labs converge on PostgreSQL/MySQL as standard database technologies.
* **Tooling Investment**: Teams invest in database migration tools, backup strategies, and monitoring infrastructure earlier in development lifecycle.

# 4. Alternatives Considered

## Alternative A: Continue Using SQLite, Add State Persistence Layer
**Description**: Keep SQLite but implement a custom persistence layer that saves/restores state across restarts.

**Rejection Rationale**: This adds significant complexity and creates a non-standard architecture that must be maintained across all Implementation Labs. It also doesn't solve the fundamental problem: SQLite in ephemeral storage is still vulnerable to data loss in production container environments. The engineering effort required to make SQLite persistent is equivalent to just using PostgreSQL correctly.

## Alternative B: Use SQLite in Development, PostgreSQL in Production
**Description**: Allow SQLite for local development to reduce setup friction, but require PostgreSQL in production.

**Rejection Rationale**: This violates the production parity principle. The EHDC failure occurred in a development environment (Codespace) and would have been caught earlier if the development database matched production. Differences between development and production databases lead to "works on my machine" failures that waste significant debugging time.

## Alternative C: Document SQLite Limitations, Leave Decision to Implementation Labs
**Description**: Create guidelines recommending persistent databases but allow labs to choose based on their requirements.

**Rejection Rationale**: The EHDC failure proves this is not a best practice recommendation—it is a **constitutional mandate**. Security-critical features cannot function on ephemeral infrastructure. Leaving this as optional guidance creates risk that future labs repeat the same failure pattern. Strong architectural guardrails are necessary for security requirements.

## Alternative D: Use Redis with Persistence Enabled
**Description**: Use Redis with AOF (Append-Only File) or RDB snapshots for persistent state storage.

**Rejection Rationale**: While Redis can be configured for persistence, it is optimized for caching and high-speed key-value operations, not for ACID-compliant transactional workloads. Security features requiring complex queries, transactions, or relational integrity are better served by PostgreSQL/MySQL. Redis is acceptable for session storage and caching layers, but should not be the primary database for security-critical data.

# 5. Federation of Labs Promotion Pipeline

| Attribute | Value |
| :--- | :--- |
| **Originating Lab:** | **EHDC** (Pillar IV - Ecosystem Health Data Commons) |
| **Originating Event:** | **EHDC Security Validation Failure** - Final act of the debugging marathon (November 8, 2025) |
| **Failure Context:** | The two-step cryptographic wallet authentication flow (ADR-0601) requires persistent storage of challenge records. When tested in a Codespace with SQLite, server restarts caused by code changes wiped the database, resulting in `{"error":"Not Found","message":"Challenge not found"}` on the verify endpoint. |
| **Validation Evidence:** | **Negative validation** (failure) + **Positive validation** (migration success): (1) The failure definitively proved that ephemeral databases cannot support stateful security primitives. (2) Migration to persistent PostgreSQL/Supabase (PR #12, November 8-9, 2025) resolved the issue immediately, with WalletChallenge records surviving server restarts and complete end-to-end wallet authentication flow validated on persistent infrastructure. |
| **Migration PRs:** | EHDC PR #12 (PostgreSQL migration), PR #17 (wallet verification validation) |
| **Promotion Rationale:** | This is a **constitutional infrastructure mandate** for the UCF Federation. All Implementation Labs implementing security-critical features (wallet authentication, session management, authorization flows) must use persistent databases. This prevents future labs from repeating the EHDC failure pattern and ensures infrastructure consistency across the Federation. |
| **Related ADRs:** | ADR-0601 (XRPL WebAuth Integration) - The security feature that exposed this infrastructure requirement |
| **Cross-Lab Applicability:** | Universal - applies to all four pillars whenever security-critical features are implemented |
| **Enforcement Status:** | Mandatory for all UCF Implementation Labs |

## Migration Path for Implementation Labs

Labs currently using ephemeral databases for security features must:

1. **Audit Current Infrastructure**: Identify all uses of SQLite, in-memory databases, or ephemeral storage for security-critical data
2. **Select Persistent Database**: Choose managed PostgreSQL/MySQL provider (recommendations: Supabase, Neon, PlanetScale)
3. **Update Development Environment**:
   - Add Docker Compose configuration for local PostgreSQL OR use managed service (Supabase/Neon)
   - Update connection strings in environment variables
   - **For Prisma + Supabase**: Configure dual-database URLs (see EHDC migration section above)
   - Test database connectivity
4. **Migrate Schema**:
   - Update Prisma schema with `provider = "postgresql"` and `directUrl` configuration
   - Export existing schema, import to persistent database
   - Run `prisma migrate dev` (requires `DIRECT_URL` for Supabase)
5. **Update CI/CD**: Configure persistent database service containers for integration tests
6. **Deploy to Production**: Update production environment with persistent database connection
7. **Validate End-to-End**: Test security features (especially multi-step flows) through server restart cycles

## Recommended Database Providers

**For Development (Free/Local)**:
- Docker Compose with PostgreSQL 15+ official image
- Local PostgreSQL installation (Postgres.app for macOS, official installer for Windows/Linux)

**For Production (Managed Services)**:
- **Supabase** (PostgreSQL, generous free tier, built-in auth/realtime features)
- **Neon** (Serverless PostgreSQL, branching for development workflows)
- **PlanetScale** (MySQL-compatible, excellent developer experience)
- **AWS RDS / Google Cloud SQL / Azure Database** (Enterprise-grade, full control)

**Not Recommended**:
- SQLite in any mode (unless for read-only reference data)
- Self-hosted databases without backup/recovery strategy
- Databases on non-persistent container storage

## Monitoring and Validation

Implementation Labs should implement monitoring to detect persistence failures:

- **Health Checks**: Verify database connectivity and persistence on application startup
- **Integration Tests**: Include tests that span server restarts (challenge/verify flow test with restart between steps)
- **Alerts**: Configure alerts for database connection failures or unexpected data loss
- **Backup Validation**: Regularly test database backup and restore procedures

## Exception Policy

The only acceptable use of ephemeral databases in UCF projects is:

1. **Unit tests** that do not involve security features or persistent state
2. **Read-only caches** where data loss is acceptable (with persistent backing store)
3. **Prototype/demo applications** explicitly marked as non-production and non-security-critical

Any exception must be documented with explicit justification and security review.

---

## Lessons Learned from EHDC Debugging Marathon

This ADR enshrines the core lesson from the EHDC security validation failure:

> **Infrastructure choices are architectural decisions with security consequences.**

The failure to use persistent infrastructure for stateful security features is not a minor configuration issue—it is an **architectural vulnerability** that causes cryptic, hard-to-debug failures in production.

By promoting this lesson to a constitutional mandate, the UCF ensures that all future Implementation Labs build on a foundation that can reliably support the security features required for decentralized, self-custodial identity and governance.

**The pattern is now part of the UCF Constitution**: Ephemeral databases are prohibited for security-critical features across all pillars of the Federation.
