# ADR-003: ORM Selection

## Status

Accepted

## Context

We need an ORM/query builder for the NestJS backend to interact with PostgreSQL. The application requires:

- Type-safe database queries
- Schema migrations
- Complex queries (joins, aggregations for financial reports)
- Good developer experience
- Performance (will handle modest load: ~60 bookings/year initially)

## Decision Drivers

- **Type safety**: Compile-time validation of queries
- **Modern approach**: Current best practices in 2025
- **Resume relevance**: Technologies that employers are adopting
- **Developer experience**: Productive and maintainable
- **Performance**: Efficient queries, minimal overhead
- **Ecosystem fit**: Works well with NestJS + PostgreSQL

## Options Considered

### Option A: Drizzle ORM

**Pros:**

- ✅ **Lightweight & fast** - minimal runtime overhead
- ✅ **SQL-first approach** - write queries close to raw SQL
- ✅ **Excellent TypeScript support** - inferred types from schema
- ✅ **Modern & trending** - gaining rapid adoption in 2025
- ✅ **Great DX** - intuitive query builder
- ✅ **Resume value** - shows awareness of current tooling trends
- ✅ **Flexible** - supports both ORM-style and SQL-style queries
- ✅ **Schema migrations** - built-in migration system

**Cons:**

- ⚠️ **Newer ecosystem** - fewer resources than Prisma/TypeORM
- ⚠️ **Less NestJS integration examples** - need to wire up manually

### Option B: Prisma

**Pros:**

- ✅ **Mature ecosystem** - large community, many resources
- ✅ **Excellent tooling** - Prisma Studio for DB inspection
- ✅ **Type-safe** - generated client with full type safety
- ✅ **Great migrations** - declarative schema, auto-migrations
- ✅ **NestJS integration** - official `@nestjs/prisma` package

**Cons:**

- ❌ **Heavier** - generates large client, slower than Drizzle
- ❌ **Schema language** - separate Prisma Schema Language (not TypeScript)
- ❌ **Less flexible** - harder to write custom SQL
- ❌ **Generated client** - adds build step, potential type mismatches

### Option C: TypeORM

**Pros:**

- ✅ **Traditional ORM** - ActiveRecord/DataMapper patterns
- ✅ **NestJS default** - extensive official docs
- ✅ **Decorator-based** - fits NestJS style
- ✅ **Mature** - battle-tested

**Cons:**

- ❌ **Outdated patterns** - ActiveRecord considered anti-pattern
- ❌ **Weaker type safety** - runtime decorators, less compile-time safety
- ❌ **Slower** - heavier than modern alternatives
- ❌ **Less maintained** - slower development than Drizzle/Prisma

## Decision

**We will use Drizzle ORM.**

### Rationale

1. **Best type safety** - Full TypeScript inference from schema definitions
2. **Modern approach** - Represents current best practices in Node ecosystem
3. **Performance** - Lightweight, minimal overhead, fast queries
4. **Resume building** - Shows adoption of modern tooling (valuable signal)
5. **SQL control** - Can write complex financial queries efficiently
6. **Future-proof** - Momentum in community, active development

### Implementation Notes

```tsx
// Example Drizzle schema
import { pgTable, uuid, varchar, timestamp } from 'drizzle-orm/pg-core'

export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: varchar('email', { length: 255 }).notNull().unique(),
  firstName: varchar('first_name', { length: 100 }).notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
})

// Type inference works automatically
type User = typeof users.$inferSelect
```

**NestJS Integration:**

- Create `DatabaseModule` with Drizzle connection
- Inject Drizzle instance into services
- Use repository pattern for data access layer

## Consequences

### Positive

- Excellent type safety catches errors at compile time
- Fast query execution and minimal runtime overhead
- SQL-first approach gives full control for complex queries
- Modern tooling on resume shows technical awareness
- TypeScript-native schema definitions (no separate DSL)
- Easy to optimize queries when needed

### Negative

- Less documentation/examples than Prisma
- Need to manually set up NestJS integration (no official package)
- Smaller community (but growing rapidly)

### Risks

- **Learning curve**: Team (future contributors) may be unfamiliar
  - _Mitigation_: Drizzle docs are excellent; SQL knowledge transfers directly
- **Breaking changes**: Newer library, API could change
  - _Mitigation_: Library is stable; major patterns unlikely to change

## Follow-up Actions

- [ ] Install Drizzle ORM: `pnpm add drizzle-orm pg`
- [ ] Install Drizzle Kit: `pnpm add -D drizzle-kit`
- [ ] Create `DatabaseModule` in NestJS
- [ ] Define initial schema in `src/db/schema/`
- [ ] Configure Drizzle migrations
- [ ] Create example repository service pattern
- [ ] Document query patterns in code
