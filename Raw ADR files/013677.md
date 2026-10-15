# ADR-0003: Shared Database Strategy

**Status:** Accepted  
**Date:** 2026-01-XX  
**Context:** Backend POC-2 - Microservices Database Architecture  
**Decision Makers:** Backend Team

---

## Context

We need to decide on the database architecture for our microservices. The decision affects transaction management, data consistency, service coupling, scalability, and operational complexity. This is a critical architectural decision that impacts how services interact with data.

**Requirements:**

- Support transactions across services (if needed)
- Easy to manage and maintain
- Good performance
- Type-safe database access (Prisma)
- Can scale to separate databases later if needed
- Simple for POC-2/MVP

---

## Decision

We will use a **shared database with service-specific schemas** for POC-2.

**Rationale:**

- **Simpler for POC-2/MVP** - Easier to manage, single database
- **Easier transactions** - Can use database transactions across services
- **Prisma support** - Prisma supports schema separation
- **Can migrate later** - Can migrate to separate databases if needed
- **Lower operational complexity** - Single database to manage
- **Good for POC** - Validates architecture without database complexity

**Schema Organization:**

```sql
-- Service-specific schemas
CREATE SCHEMA auth;
CREATE SCHEMA payments;
CREATE SCHEMA admin;
CREATE SCHEMA profile;
```

---

## Alternatives Considered

### 1. Separate Databases per Service

**Pros:**
- True service isolation
- Independent scaling
- Service-specific optimizations
- Better for microservices (theoretical)

**Cons:**
- More complex to manage
- Harder transactions across services
- More operational overhead
- May be overkill for POC-2/MVP
- Distributed transactions are complex

**Decision:** Not chosen - Complexity outweighs benefits for POC-2. Can migrate later if needed.

---

### 2. Database per Service (Full Isolation)

**Pros:**
- Complete service isolation
- Independent deployments
- Service-specific database types (if needed)

**Cons:**
- Very complex to manage
- No cross-service transactions
- High operational overhead
- Overkill for POC-2/MVP
- Distributed transactions are very complex

**Decision:** Not chosen - Too complex for POC-2. Can migrate later if needed.

---

### 3. Shared Database with Service-Specific Schemas (Chosen)

**Pros:**
- Simpler to manage
- Can use transactions across services
- Prisma supports schema separation
- Can migrate to separate databases later
- Good for POC-2/MVP

**Cons:**
- Services share database (but schemas are separate)
- Database becomes single point of failure (but can add replication)
- Less isolation than separate databases

**Decision:** Chosen - Best balance of simplicity and functionality for POC-2.

---

## Trade-offs

### Pros

- ✅ **Simplicity** - Single database to manage
- ✅ **Transactions** - Can use database transactions across services
- ✅ **Prisma Support** - Prisma supports schema separation
- ✅ **Migration Path** - Can migrate to separate databases later
- ✅ **Operational Simplicity** - Less operational overhead
- ✅ **Good for POC** - Validates architecture without database complexity

### Cons

- ⚠️ **Coupling** - Services share database (but schemas are separate)
- ⚠️ **Single Point of Failure** - Database failure affects all services (but can add replication)
- ⚠️ **Scaling** - May need to scale database for all services (but can optimize per schema)

---

## Consequences

### Positive

- ✅ **Simpler Operations** - Single database to manage, backup, monitor
- ✅ **Transaction Support** - Can use database transactions across services
- ✅ **Easier Development** - Single database connection, simpler setup
- ✅ **Prisma Integration** - Prisma works well with schema separation
- ✅ **Migration Path** - Can migrate to separate databases later if needed

### Negative

- ⚠️ **Coupling** - Services share database (but mitigated by schema separation)
- ⚠️ **Scaling** - May need to scale database for all services (but can optimize)

### Neutral

- 🔄 **Migration Path** - Can migrate to separate databases later (Prisma supports this)
- 🔄 **Performance** - Performance is good for POC-2/MVP needs

---

## Implementation Notes

- Use PostgreSQL with service-specific schemas
- Prisma schema organized by service
- Each service has its own Prisma client (but same database)
- Can use transactions across services if needed
- Monitor database performance per schema
- Plan migration to separate databases if needed

**Example:**

```prisma
// packages/shared-db/prisma/schema.prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

// Auth Service Schema
model User {
  id    String @id @default(uuid())
  email String @unique
  // ...
  @@schema("auth")
}

// Payments Service Schema
model Payment {
  id     String @id @default(uuid())
  amount Decimal
  // ...
  @@schema("payments")
}
```

---

## Migration Path

### POC-2 → POC-3

- **Migrate to separate databases per service** (see ADR-0004 for POC-3)
- Each service gets its own database (auth_db, payments_db, admin_db, profile_db)
- Prisma supports this migration

### POC-3 → MVP

- Continue with separate databases
- Optimize each database for its service
- Scale databases independently

### MVP → Production

- May use separate databases for scalability
- Or continue with shared database with replication
- Decision based on performance and operational needs

---

## Related Decisions

- **ADR-0002: Use Prisma ORM** - Prisma supports schema separation
- **ADR-0001: Use Express Framework** - Database strategy is independent of Express
- **ADR-0004 (POC-3): Separate Databases per Service** - Migration to separate databases in POC-3
- Frontend decisions are independent

---

## References

- [Prisma Multi-Schema Documentation](https://www.prisma.io/docs/guides/database/multi-schema)
- `docs/backend-poc2-architecture.md` - Architecture documentation
- `docs/backend-poc2-tech-stack.md` - Tech stack documentation

---

**Last Updated:** 2026-01-XX

