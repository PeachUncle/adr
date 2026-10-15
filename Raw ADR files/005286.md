# ADR-002: Use PostgreSQL + Prisma for Data Layer

## Status

✅ **Accepted**

**Date:** 27. Oktober 2025

## Context

Die AI-Freelancer-Plattform braucht eine robuste Datenbank für:

- User-Accounts (Freelancer, Firmen, Admin)
- Profile (detaillierte Informationen, Skills)
- Projekte (Beschreibungen, Status, Matching)
- Bookings (Trial Period, Payments, Status-Transitions)
- Messages (1-to-1 Chat)
- Invoices (Abrechnung, Provision)

**Requirements:**

- Relational Data Model (Users → Profiles → Projects → Bookings)
- ACID Transactions (kritisch für Payments)
- DSGVO-Compliance (EU Data Residency)
- TypeScript-Integration (Type Safety)
- Migrations (Schema-Evolution)
- Performance (Indexes, Queries)
- V1.0: Vector Search (für AI-Matching mit Embeddings)

## Decision

Ich verwende **PostgreSQL 15** als Datenbank und **Prisma 5.x** als ORM.

### Warum PostgreSQL?

**Database-Ebene:**

- ✅ **Relational Model:** Perfekt für User → Profile → Project → Booking Beziehungen
- ✅ **ACID Compliance:** Transaktionen für Payments
- ✅ **Mature & Stable:** 30+ Jahre Entwicklung, Production-Proven
- ✅ **Open Source:** Keine Lizenzkosten
- ✅ **AWS RDS:** Managed Service (Backups, Monitoring, Scaling)
- ✅ **pgvector Extension:** V1.0 für AI-Matching (Vector Search)
- ✅ **Full-Text Search:** Für Projekt-/Freelancer-Suche (später)
- ✅ **JSON Support:** Flexibel für zukünftige Features

### Warum Prisma?

**ORM-Ebene:**

- ✅ **Type Safety:** End-to-end TypeScript (DB ↔ Code)
- ✅ **Auto-Completion:** IDE Support, weniger Fehler
- ✅ **Migrations:** Prisma Migrate (versioniert, reproducible)
- ✅ **Query Builder:** Intuitive API, type-safe
- ✅ **Connection Pooling:** Built-in (wichtig für Serverless/ECS)
- ✅ **Prisma Studio:** GUI für DB-Entwicklung
- ✅ **Great DX:** Developer Experience ist exzellent

## Alternatives Considered

### Alternative 1: MySQL + Prisma

**Pros:**

- ✅ Ähnlich zu PostgreSQL (relational)
- ✅ Weit verbreitet
- ✅ Prisma unterstützt MySQL

**Cons:**

- ❌ Keine pgvector (für AI-Features)
- ❌ JSON Support schlechter
- ❌ Full-Text Search schwächer

**Warum nicht gewählt:**
PostgreSQL ist technisch überlegen (pgvector, JSON, Full-Text Search). Für AI-Features ist pgvector essentiell.

### Alternative 2: MongoDB (NoSQL)

**Pros:**

- ✅ Flexibles Schema (JSON-Documents)
- ✅ Horizontal Scaling einfacher
- ✅ Gute Performance bei einfachen Queries

**Cons:**

- ❌ **KEIN ACID** (Transaktionen komplexer)
- ❌ Joins sind schwach/teuer
- ❌ Weniger Type Safety
- ❌ Nicht ideal für relationale Daten (User → Profile → Project → Booking)

**Warum nicht gewählt:**
Unser Datenmodell ist stark relational. ACID-Transaktionen sind kritisch für Payments. PostgreSQL ist besser geeignet.

### Alternative 3: PostgreSQL + TypeORM

**Pros:**

- ✅ Mature ORM (seit 2016)
- ✅ Active Queries (komplexe Queries einfacher)
- ✅ Migrations Support

**Cons:**

- ❌ Weniger Type Safety als Prisma
- ❌ Schlechtere DX (mehr Boilerplate)
- ❌ Decorator-Syntax (komplexer)
- ❌ Weniger moderne API

**Warum nicht gewählt:**
Prisma hat bessere TypeScript-Integration, modernere API, bessere DX. Für Solo-Dev ist DX wichtig.

### Alternative 4: PostgreSQL + Drizzle ORM

**Pros:**

- ✅ Sehr type-safe (ähnlich Prisma)
- ✅ Lightweight (kleiner Bundle)
- ✅ SQL-ähnliche API (weniger Abstraktion)

**Cons:**

- ❌ Jünger als Prisma (kleineres Ecosystem)
- ❌ Weniger Tooling (kein Studio)
- ❌ Migrations komplexer

**Warum nicht gewählt:**
Prisma ist etablierter, hat besseres Tooling (Prisma Studio), größeres Ecosystem. Für MVP ist Stability wichtiger.

### Alternative 5: PostgreSQL + Raw SQL (kein ORM)

**Pros:**

- ✅ Maximale Kontrolle
- ✅ Kein ORM-Overhead
- ✅ Performance-optimiert

**Cons:**

- ❌ **Kein Type Safety**
- ❌ SQL Injection Risiko (wenn nicht sorgfältig)
- ❌ Viel Boilerplate
- ❌ Migrations manuell

**Warum nicht gewählt:**
Für Solo-Dev ist Type Safety + DX wichtiger als maximale Performance. Prisma ist "gut genug".

## Rationale

### PostgreSQL Rationale

1. **Relational Model passt perfekt:**

   ```
   User → FreelancerProfile → ProjectBooking → Invoice
   User → CompanyProfile → Project → ProjectBooking
   ```

   Viele Foreign Keys, Joins sind notwendig.

2. **ACID für Payments:**

   ```sql
   BEGIN TRANSACTION;
     UPDATE project_bookings SET status='COMPLETED';
     INSERT INTO invoices (...);
     UPDATE users SET balance=...;
   COMMIT;
   ```

   Atomic transactions sind kritisch.

3. **pgvector für V1.0:**

   ```sql
   CREATE EXTENSION vector;
   CREATE TABLE embeddings (
     id UUID PRIMARY KEY,
     embedding vector(1536)
   );
   ```

   Für AI-Matching (semantische Suche).

4. **AWS RDS = Managed:**
   - Automated Backups (7 Tage Retention)
   - Multi-AZ (High Availability)
   - Monitoring (CloudWatch)
   - Easy Scaling

### Prisma Rationale

**Type Safety Example:**

```typescript
// ✅ Type-safe Query (Prisma)
const user = await prisma.user.findUnique({
  where: { email: email }, // TypeScript checks "email" exists
  include: {
    freelancerProfile: true, // Auto-completion!
  },
});

// user.freelancerProfile?.skills ist type-safe!

// ❌ NICHT Type-safe (Raw SQL)
const result = await db.query('SELECT * FROM users WHERE email = $1', [email]);
// result ist `any`, kein Type Safety
```

**Migration Example:**

```bash
# 1. Schema ändern (prisma/schema.prisma)
# 2. Migration generieren
pnpm prisma migrate dev --name add-trial-period

# 3. Migration wird automatisch angewendet
# 4. Prisma Client wird regeneriert (type-safe!)
```

## Consequences

### Positive

1. **Type Safety End-to-End**
   - DB Schema → TypeScript Types (automatisch)
   - Weniger Runtime-Errors
   - Bessere IDE-Unterstützung

2. **DSGVO-Compliant**
   - AWS RDS Frankfurt (eu-central-1)
   - Keine Daten außerhalb EU
   - Backups, Encryption at Rest

3. **Productive Development**
   - Prisma Studio (GUI für Entwicklung)
   - Einfache Migrations
   - Gute DX (weniger Boilerplate)

4. **V1.0 Ready**
   - pgvector für AI-Matching
   - JSON Support für flexible Features
   - Full-Text Search für Suche

### Negative

1. **ORM Overhead**
   - Prisma generiert SQL (nicht immer optimal)
   - Sehr komplexe Queries könnten ineffizient sein
   - **Mitigation:** Raw Queries möglich: `prisma.$queryRaw`

2. **Vendor Lock-in**
   - Prisma Schema ist Prisma-specific
   - Migration zu anderem ORM wäre aufwendig
   - **Mitigation:** Akzeptabel, Prisma ist stabil

3. **Connection Pooling Limits**
   - PostgreSQL hat Max Connections (RDS: 100-500)
   - Prisma Connection Pool: 10 (MVP) → 100 (Production)
   - **Mitigation:** AWS RDS Proxy (später)

## Implementation Notes

### Database Configuration

```yaml
# AWS RDS PostgreSQL
Instance: db.t3.micro (MVP) → db.t3.medium (Production)
Storage: 20 GB (General Purpose SSD)
Backups: Automated (7 days retention)
Multi-AZ: No (MVP) → Yes (Production)
Region: eu-central-1 (Frankfurt)
Encryption: At Rest (AWS KMS)
```

### Prisma Configuration

```prisma
// prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}
```

### Connection String

```bash
# .env
DATABASE_URL="postgresql://user:password@rds-endpoint.eu-central-1.rds.amazonaws.com:5432/freelancer_db?schema=public&sslmode=require"
```

### Indexing Strategy

```prisma
// Indexes auf häufig abgefragte Felder
model User {
  @@index([email])
}

model FreelancerProfile {
  @@index([status])
  @@index([experienceLevel])
}

model Project {
  @@index([companyId])
  @@index([status])
}

model ProjectBooking {
  @@index([projectId])
  @@index([freelancerId])
  @@index([status])
}
```

## Follow-up Actions

- [x] AWS RDS PostgreSQL Instance erstellen (Phase 3.6)
- [x] Prisma installieren (`pnpm add prisma @prisma/client`)
- [x] `prisma/schema.prisma` erstellen (siehe DATABASE_SCHEMA.md)
- [ ] Initial Migration: `pnpm prisma migrate dev --name init`
- [ ] Seed-Daten erstellen (`prisma/seed.ts`)

## References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Prisma Documentation](https://www.prisma.io/docs)
- [Prisma Best Practices](https://www.prisma.io/docs/guides/performance-and-optimization)
- [pgvector Extension](https://github.com/pgvector/pgvector)
- [AWS RDS PostgreSQL](https://aws.amazon.com/rds/postgresql/)

---

**Author:** Max Mustermann
**Date:** 27. Oktober 2025
**Status:** Accepted
