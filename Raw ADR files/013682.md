# ADR-0004: Separate Databases per Service

**Status:** Accepted  
**Date:** 2026-01-XX  
**Context:** Backend POC-3 - Microservices Database Architecture Migration  
**Decision Makers:** Backend Team

---

## Context

We need to migrate from the shared database architecture (POC-2) to separate databases per service (POC-3). This decision affects service isolation, scalability, operational complexity, and cross-service data access patterns. This is a critical architectural decision that impacts how services interact with data and each other.

**Requirements:**

- True service isolation
- Independent scaling per service
- Service-specific optimizations
- Reduced coupling between services
- Independent deployments
- Better fault isolation
- Production-ready microservices pattern

**Current State (POC-2):**

- Shared database with service-specific schemas
- Single PostgreSQL instance
- All services share database resources
- Easier transactions across services

---

## Decision

We will migrate to **separate databases per service** (one database per microservice) in POC-3.

**Rationale:**

- **True Service Isolation** - Each service has its own database, no shared resources
- **Independent Scaling** - Scale databases independently per service based on load
- **Service-Specific Optimizations** - Optimize each database for its service's specific needs
- **Reduced Coupling** - Services don't share database resources, reducing coupling
- **Independent Deployments** - Database changes in one service don't affect others
- **Better Fault Isolation** - Database failure in one service doesn't affect others
- **Production-Ready Pattern** - Aligns with microservices best practices
- **POC-3 Scope** - Since we may not extend to POC-4 before MVP, implement in POC-3

**Database Assignment:**

- **Auth Service** → `auth_db` (PostgreSQL)
- **Payments Service** → `payments_db` (PostgreSQL)
- **Admin Service** → `admin_db` (PostgreSQL)
- **Profile Service** → `profile_db` (PostgreSQL)

---

## Alternatives Considered

### 1. Continue with Shared Database (POC-2 Approach)

**Pros:**

- Simpler operations (single database)
- Easier transactions across services
- Lower operational overhead
- Already implemented in POC-2

**Cons:**

- Services share database resources (coupling)
- Database becomes single point of failure
- Cannot scale databases independently
- Less isolation between services
- Not aligned with microservices best practices

**Decision:** Not chosen - Need true service isolation for POC-3 production-ready infrastructure.

---

### 2. Separate Databases per Service (Chosen)

**Pros:**

- True service isolation
- Independent scaling per service
- Service-specific optimizations
- Reduced coupling
- Independent deployments
- Better fault isolation
- Production-ready microservices pattern

**Cons:**

- More complex to manage (4 databases instead of 1)
- Harder transactions across services (need distributed transactions or event-based)
- More operational overhead
- Cross-service data access requires API calls or events

**Decision:** Chosen - Benefits outweigh complexity for POC-3 production-ready infrastructure.

---

### 3. Hybrid Approach (Some Services Separate)

**Pros:**

- Gradual migration
- Less operational overhead initially

**Cons:**

- Inconsistent architecture
- Complex migration path
- Harder to maintain

**Decision:** Not chosen - All services should have separate databases for consistency.

---

## Trade-offs

### Pros

- ✅ **True Service Isolation** - Each service has its own database
- ✅ **Independent Scaling** - Scale databases independently per service
- ✅ **Service-Specific Optimizations** - Optimize each database for its service
- ✅ **Reduced Coupling** - Services don't share database resources
- ✅ **Independent Deployments** - Database changes don't affect other services
- ✅ **Better Fault Isolation** - Database failure in one service doesn't affect others
- ✅ **Production-Ready** - Aligns with microservices best practices

### Cons

- ⚠️ **Operational Complexity** - 4 databases to manage instead of 1
- ⚠️ **Cross-Service Data Access** - Requires API calls or event-based synchronization
- ⚠️ **No Cross-Service Transactions** - Cannot use database transactions across services
- ⚠️ **Migration Complexity** - Need to migrate data from shared to separate databases

---

## Consequences

### Positive

- ✅ **True Service Isolation** - Each service is truly independent
- ✅ **Scalability** - Can scale each database independently based on service load
- ✅ **Optimization** - Can optimize each database for its service's specific needs
- ✅ **Fault Isolation** - Database failure in one service doesn't affect others
- ✅ **Production-Ready** - Aligns with microservices best practices
- ✅ **Team Autonomy** - Teams can manage their own database

### Negative

- ⚠️ **Operational Overhead** - 4 databases to manage, backup, monitor
- ⚠️ **Cross-Service Data Access** - Need API calls or event-based synchronization
- ⚠️ **No Cross-Service Transactions** - Cannot use database transactions across services
- ⚠️ **Migration Complexity** - Need careful data migration from shared to separate databases

### Neutral

- 🔄 **Performance** - Performance may improve (service-specific optimizations) or stay similar
- 🔄 **Development** - Development may be slightly more complex (separate database connections)

---

## Implementation Notes

### Database Setup

Each service has its own Prisma schema and database connection:

```prisma
// apps/backend/auth-service/prisma/schema.prisma
datasource db {
  provider = "postgresql"
  url      = env("AUTH_DATABASE_URL")
}

model User {
  id            String    @id @default(uuid())
  email         String    @unique
  passwordHash  String    @map("password_hash")
  // ... (auth service models only)
}
```

```prisma
// apps/backend/payments-service/prisma/schema.prisma
datasource db {
  provider = "postgresql"
  url      = env("PAYMENTS_DATABASE_URL")
}

model Payment {
  id          String   @id @default(uuid())
  userId      String   @map("user_id") // Reference to user ID (not FK)
  amount      Decimal
  // ... (payments service models only)
}
```

### Cross-Service Data Access

Since services now have separate databases, cross-service data access must use:

1. **API Calls (Synchronous)**

   ```typescript
   // Payments Service needs User data
   const user = await fetch(`http://auth-service/api/users/${userId}`, {
     headers: { Authorization: `Bearer ${token}` },
   });
   ```

2. **Event-Based (Asynchronous)**

   ```typescript
   // User data cached in Payments Service, updated via events
   const user = await userCache.get(userId);
   ```

3. **Caching**
   - Cache frequently accessed cross-service data
   - Invalidate cache on events

### Migration Strategy

1. **Phase 1: Setup Separate Databases**

   - Create separate PostgreSQL databases for each service
   - Setup Prisma clients for each service
   - Configure database connections

2. **Phase 2: Data Migration**

   - Migrate data from shared database to separate databases
   - Use event hub for data synchronization during migration
   - Validate data integrity

3. **Phase 3: Code Updates**

   - Update each service to use its own database
   - Update Prisma schemas to be service-specific
   - Remove cross-service database dependencies
   - Implement cross-service data access patterns

4. **Phase 4: Testing & Validation**
   - Integration tests for each service
   - End-to-end tests for cross-service operations
   - Performance testing
   - Data integrity validation

---

## Migration Path

### POC-2 → POC-3

- **POC-2:** Shared database with service-specific schemas
- **POC-3:** Separate databases per service (one database per microservice)
- **Migration:** Phased migration with data validation

### POC-3 → MVP

- Continue with separate databases
- Optimize each database for its service
- Monitor performance per database
- Scale databases independently as needed

### MVP → Production

- Continue with separate databases
- Add database replication for high availability
- Add database backups per service
- Add database monitoring per service

---

## Related Decisions

- **ADR-0003 (POC-2): Shared Database Strategy** - This ADR supersedes the migration path in ADR-0003
- **ADR-0002: Use Prisma ORM** - Prisma supports separate databases per service
- **ADR-0001: Use Express Framework** - Database strategy is independent of Express
- Frontend decisions are independent

---

## References

- [Prisma Multi-Database Documentation](https://www.prisma.io/docs/guides/database/multi-database)
- `docs/backend-poc2-architecture.md` - POC-2 architecture (shared database)
- `docs/backend-poc3-architecture.md` - POC-3 architecture (separate databases)
- `docs/backend-poc3-tech-stack.md` - POC-3 tech stack
- `docs/adr/backend/poc-2/0003-shared-database-strategy.md` - POC-2 database decision

---

**Last Updated:** 2026-01-XX
