# 004 – Database Choice (PostgreSQL + TypeORM)

## Status  
Accepted | 2025-05-26

---

## Context  
The Parking Reservation System requires a database that can:

1. Store **reservations** with composite keys (`slotId` + `dateRange`) and maintain a **complete history**.  
2. Manage **users** (employees, secretaries, managers) and enforce **role-based access**.  
3. Guarantee **transactional consistency** (e.g., reservation creation + message publication).  
4. Support **schema evolution** via reliable migrations across sprints.

### Technical evaluation criteria
- Mature ecosystem with robust TypeScript support  
- Seamless integration with NestJS  
- Strong migration & seeding tools  
- Performance and reliability under moderate load  
- Manageable learning curve for the team  

---

## Decision  
We choose **PostgreSQL** as the DBMS and **TypeORM** as the ORM.

---

## Why PostgreSQL?

- **ACID transactions & integrity**: full support for multi-statement transactions, composite primary keys, foreign key constraints.  
- **Advanced indexing & JSONB**: B-tree, GIN indexes plus JSONB fields for flexible metadata without sacrificing performance.  
- **Mature migration tooling**: TypeORM CLI or integrated extensions ensure versioned, repeatable schema changes.  
- **Extensive community & tooling**: strong TypeScript typings, monitoring integrations, proven reliability.

## Why TypeORM?

- **Native NestJS integration** via `@nestjs/typeorm`.  
- **Decorator-based entities** in TypeScript, with relation and index support.  
- **Dual patterns** (Data Mapper or Active Record) as needed.  
- **Built-in migrations**: automatic generation and robust CLI.  
- **Rich query capabilities**: QueryBuilder, transactions, custom repositories.

---

## Alternatives Considered

### MongoDB (NoSQL)
- **Pros**  
  - Schema flexibility: dynamic documents with arbitrary fields.  
  - Horizontal scaling: built-in sharding.

- **Cons**  
  - **Lacks composite primary keys** natively—requires extra indexing or application logic for `slotId + dateRange`.  
  - **Weaker transactional guarantees**: multi-document transactions exist but are more complex and less performant.  
  - **Eventual consistency** can lead to race conditions in reservation workflows.  
  - Team unfamiliar with MongoDB best practices in TypeScript.

**Conclusion:** PostgreSQL’s strong consistency, relational constraints, and mature tooling make it the best fit for enforcing critical reservation rules.

---

## Consequences

### Advantages
- Reliable transactional workflow for reservations.  
- Clear enforcement of entity relationships & constraints.  
- Versioned migrations for safe schema evolution.  
- End-to-end type safety reduces runtime errors.

### Disadvantages
- More rigid schema vs. NoSQL flexibility.  
- Extra setup for JSONB use cases.  
- Relational DB infrastructure requires additional maintenance.

---