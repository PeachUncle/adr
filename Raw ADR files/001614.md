# ADR-20251015-use-drizzle-orm

## Status
Accepted

## Context
ExvoRed requires type-safe database access with schema management capabilities. The application uses TypeScript throughout the stack (both frontend and backend), making type safety a critical requirement. The database schema includes complex relationships: one-to-many (exvoto to SEM), many-to-many (catalog to exvoto, SEM to divinity), and self-referential relationships (exvoto has three separate SEM references).

The development workflow requires frequent schema changes during active development, necessitating a migration system that balances speed (for development iterations) with safety (for production deployments). The team needs automatic type inference to ensure frontend and backend types stay synchronized with the database schema. Bundle size is a concern for the React frontend, so the ORM must not leak into client-side bundles. The ORM must provide excellent SQLite support, including blob handling for image storage and full ACID transaction support.

## Decision
Use Drizzle ORM version 0.44.2 as the data access layer. Define all tables in `api/db/schema.ts` using Drizzle's schema-first approach. Use `$inferSelect` and `$inferInsert` to automatically generate TypeScript types from the schema. During development, use `npm run db:push` for instant schema updates without migrations. For production deployments, use `npm run db:generate` to create SQL migrations, followed by `npm run db:migrate` to apply them safely.

## Consequences

### Positive
- Type inference with zero boilerplate: Types are automatically generated from schema definitions using `$inferSelect` and `$inferInsert`, eliminating manual type synchronization
- Schema-first design: `api/db/schema.ts` serves as the single source of truth for database structure, types, and relationships
- Lightweight: No runtime overhead; Drizzle compiles to native SQL queries without an abstraction penalty
- Excellent SQLite support: First-class blob handling for images, synchronous operations via better-sqlite3, and optimal query generation
- Developer experience: Fast iteration with `db:push` (instant schema updates), and production-safe migrations with `db:generate`
- Relational queries: Built-in support for joins and relation loading via `relations()` API, simplifying complex queries like "get exvoto with offering SEM and conservation SEM"
- Migration control: SQL migrations are human-readable and can be reviewed before deployment, unlike black-box migrations in some ORMs

### Negative
- Manual frontend type synchronization: Frontend types in `src/types.ts` must be manually updated to match backend types; no automatic cross-package type sharing
- Smaller ecosystem: Fewer plugins and community resources compared to Prisma; less extensive documentation for edge cases
- Migration management complexity: Two workflows (`db:push` for dev, `db:generate` for prod) require discipline to use correctly; accidental `db:push` in production could bypass migration tracking
- Learning curve: Drizzle's schema-first API differs from ActiveRecord-style ORMs; developers familiar with Sequelize or TypeORM need to learn new patterns
- Limited query builder features: No built-in soft deletes, no automatic timestamp management (must handle `updated_at` manually), and no model lifecycle hooks

### Neutral
- Schema changes require code changes: Unlike code-first ORMs, every database change starts with modifying the schema file (this is intentional for type safety)
- Backend-only: Drizzle cannot be used in frontend bundles (intentional separation of concerns)

## Alternatives Considered

### Alternative 1: Prisma
**Rejected because:** Prisma generates a large client bundle (2-5MB before tree-shaking) and uses a heavyweight query engine that runs as a separate binary process. While Prisma has excellent documentation and tooling (Prisma Studio), its schema-first approach with client generation adds a compilation step to every schema change, slowing down development velocity. Prisma's type generation is more opinionated, making it harder to customize types for specific use cases like partial date handling. Additionally, Prisma's migration workflow is more rigid, with less flexibility for manual SQL intervention when needed.

### Alternative 2: TypeORM
**Rejected because:** TypeORM uses a decorator-based, code-first approach that couples database schema to TypeScript classes, creating circular dependency issues when sharing types between frontend and backend. TypeORM has had maintenance concerns with infrequent updates and unresolved bugs in GitHub issues. Its entity-based architecture encourages loading entire objects into memory, which is inefficient for image blobs. TypeORM's migration system is less transparent than Drizzle's SQL-based approach, making it harder to review and optimize database changes. TypeScript type inference is weaker, often requiring manual type annotations.

### Alternative 3: Raw SQL with Prepared Statements
**Rejected because:** While raw SQL provides maximum control and zero abstraction overhead, it lacks compile-time type safety. Every query result must be manually typed, creating opportunities for type mismatches between database schema and TypeScript interfaces. Managing schema changes requires manually writing SQL migrations without automatic change detection. Relational queries (joining exvotos with SEMs, catalogs, and images) require verbose SQL with manual JOIN construction. No built-in protection against SQL injection beyond parameterized queries. Refactoring table or column names requires manual find-replace across all query strings.

## References
- Drizzle ORM Documentation: https://orm.drizzle.team/docs/overview
- Drizzle Kit CLI Documentation: https://orm.drizzle.team/kit-docs/overview
- Project schema definition: `/home/marcos/Documentos/Programming/JavaScript/ExvoRed/api/db/schema.ts`
- Related ADR: ADR-20251015-use-sqlite-database.md
