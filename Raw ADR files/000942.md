# ADR-002 — Modular Monolith with Bounded Contexts (Records, Orders)

## Context

The current NestJS architecture conflates business logic with framework/persistence concerns (`src/api`), leading to **domain leakage** and tight coupling (e.g., to Mongoose). Introducing a new, independent `Orders` module requires a transition into a **Modular Monolith** organized by Bounded Contexts. Given the small initial scope, we will use a **Progressive DDD** approach to introduce structure incrementally, treating `Records` and `Orders` as separate **Bounded Contexts**. Cross-context communication must be explicit and ID-only.

---

## Decision: Progressive DDD Modular Monolith

Adopt a **domain-centric Modular Monolith** with the following structure and principles, implementing **selective DDD practices** to manage initial complexity while establishing clear boundaries.

### 1. Structure & Progressive Layering

- Establish **Bounded Contexts** for `Records` and `Orders`.
- Implement three clear layers within each context, but with differing levels of initial strictness:
  - **Domain**: (**Repository Interfaces**). Must be framework-agnostic.
  - **Application**: Use Cases orchestrate Domain logic and define Transactional Boundaries.
  - **Infrastructure**: Adapters (Mongoose implementations).

### 2. Hexagonal & Cross-Context Interaction

- **Repositories** are interfaces defined in the **Domain** and implemented in the **Infrastructure**.
- **Cross-context references are ID** (`Orders` holds `RecordId`).

### 3. Composition

- The Nest application will be composed solely of the **Infrastructure Modules** exposed by each Bounded Context (`app.module.ts`).

**High-Level Structure:**

- `src/contexts/records/{domain, application, infrastructure}/...`
- `src/contexts/orders/{domain, application, infrastructure}/...`

---

## Architecture Goals & Performance Linkage 🚀

This layered, domain-centric approach directly addresses key system performance and quality attributes:

| Goal/Concern           | Architectural Element                            | Benefit/Impact                                                                                                                                                                                                                                                     |
| :--------------------- | :----------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Search Performance** | **Repository Pattern + Infrastructure Adapters** | The Domain defines `RecordsRepository`, that when implemented on the Infrastructure layer, we can use indexes, projections and `lean()` queries for fast reads.                                                                                                    |
| **Scalability**        | **Domain Isolation (Bounded Contexts)**          | Isolating `Records` and `Orders` ensures independent development and deployment preparation. Each context can be scaled or eventually **split into a Microservice** without refactoring the other's domain logic. Loose coupling prevents performance bottlenecks. |

---

## Consequences

### Pros

- **Clear Boundaries**: Strong separation between `Records` and `Orders` via Bounded Contexts and explicit Ports.
- **Managed Complexity**: Reduces initial boilerplate and mapping overhead compared to full DDD, aligning effort with current scope.
- **High Testability**: Core domain logic and new context development (`Orders`) are highly testable.
- **Scalability Path**: Maintains the option to introduce stricter layering or split into microservices later.

### Cons

- **Inconsistent Design**: The `Records` context will initially have a hybrid structure (partial DDD) while `Orders` is fully layered, requiring careful documentation.
- **Layer Ambiguity**: The less strict initial layering in `Records` may risk **domain leakage** if developers aren't vigilant during refactoring.
- **Runtime Coupling**: Synchronous in-process ports introduce potential runtime coupling and require careful error handling.

---

## Alternatives Considered

| Alternative                         | Reasoning for Rejection                                                                             |
| :---------------------------------- | :-------------------------------------------------------------------------------------------------- |
| **Nest-centric Feature Modules**    | Leads to domain leakage, tight coupling to Mongoose/Nest, and unclear boundaries.                   |
| **Layered Architecture (No Ports)** | Weakens cross-context boundaries; risks hidden coupling and direct persistence access.              |
| **Microservices Split**             | Premature operational overhead and complexity; modular monolith is a suitable stepping stone.       |
| **Event-Driven Reservation**        | Higher complexity and eventual consistency concerns; prefer simpler synchronous integration for V1. |

---

## Migration Plan (High-Level)

1.  **Extract `Records` Context Incrementally**: Focus on moving logic into the new layers; **prioritize defining Repository Interfaces in the Domain** and implementing Mongoose adapters in Infrastructure first.
2.  **Implement `Orders` Context Fully**: Develop domain model, use cases, repository.
3.  Update `app.module.ts` to compose the application using the new infrastructure modules.
4.  Add unit and integration tests across layers and contexts.

---

## Concrete Read Model Strategy (NestJS + Mongoose)

To make the repository and read-model separation tangible with our stack (NestJS + MongoDB via Mongoose), we will:

- Define query-side repository interfaces in the domain (contracts only). Implementations live in infrastructure and leverage Mongoose indexes, projections, and `lean()` docs for high-performance reads.
- Maintain distinct write-side repositories focused on invariants and atomic updates (e.g., stock adjustments) using Mongoose update operators and optional transactions.

### Domain Interfaces (Query Side)

Example domain contract for a `RecordsReadRepository` to support catalog search:

```ts
// src/contexts/records/domain/repositories/RecordsReadRepository.ts
export type RecordSummary = Readonly<{
  id: string;
  title: string;
  artist: string;
  price: number;
  releasedAt: Date;
}>;

export interface RecordsReadRepository {
  search(params: {
    q?: string; // full-text search on title/artist
    genre?: string;
    sort?: 'relevance' | 'price' | 'releasedAt';
    page: number;
    pageSize: number;
  }): Promise<{ items: RecordSummary[]; total: number }>;
}
```

Orders can similarly depend on a read-side port if needed (e.g., list-able summaries), while write-side operations go through the domain/use cases.
