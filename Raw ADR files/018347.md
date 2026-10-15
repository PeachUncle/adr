# Local Development Database

## Status

Accepted

## Context

The Taskify MVP uses Cloudflare D1 (SQLite) in production as defined in the stack decision, and we need a local development database solution that closely mirrors production while providing a smooth development experience. Developers need to be able to run migrations, seed data, and test database interactions locally without affecting production data. The solution must integrate with the established development environment (Node.js LTS, Wrangler CLI, TypeScript) and support the testing strategy (Vitest, Cucumber.js) while maintaining consistency with the three-tier environment strategy (development → staging → production).

## Decision

- Use Wrangler CLI local mode (`wrangler dev`) for local D1 database development (aligning with development environment tooling)
- Configure `preview_database_id` in wrangler.toml for local staging database to support three-tier environment strategy
- Use Wrangler's built-in data persistence across development sessions for reliable local development
- Use `wrangler d1 migrations apply --local` for local database migrations management
- Use `wrangler d1 execute --local` for local database seeding and data management
- Set up separate database IDs for development, staging, and production environments (supporting environment strategy)
- Use Wrangler's `unstable_dev()` API for programmatic testing with local D1 (integrating with Vitest and Cucumber.js testing)
- Configure local database persistence with `--persist-to` for team collaboration and consistent development experience
- Use Drizzle ORM for type-safe database schema and query management (supporting TypeScript development environment)
- Ensure local database setup supports established testing frameworks (Vitest unit tests, Cucumber.js E2E tests)

## Consequences

Local development will use Wrangler's native D1 local mode, ensuring perfect parity with production D1 behavior as defined in the stack decision. Data persists across development sessions by default in Wrangler v3+, eliminating the need for separate local database setup while supporting the consistent development environment. Developers can work offline and have full control over their local database state, enabling efficient development cycles as outlined in the development environment strategy. The `--local` flag ensures safe separation between local and production data, supporting the three-tier environment strategy (development → staging → production). Initial setup requires understanding of Wrangler CLI and D1 commands, but provides the most accurate local development experience aligned with the established development environment (Node.js LTS, Wrangler CLI, TypeScript). Using `unstable_dev()` API enables robust programmatic testing with local D1 databases, integrating seamlessly with the testing strategy (Vitest, Cucumber.js, Svelte Testing Library). The TypeScript integration through Drizzle ORM provides type safety that aligns with the code quality standards and development environment decisions.

## Urls

- [Cloudflare D1 Local Development](https://developers.cloudflare.com/d1/best-practices/local-development/)
- [Wrangler CLI Documentation](https://developers.cloudflare.com/workers/wrangler/)
- [D1 Migrations](https://developers.cloudflare.com/d1/reference/migrations/)
- [Wrangler unstable_dev API](https://developers.cloudflare.com/workers/wrangler/api/)
- [Drizzle ORM Documentation](https://orm.drizzle.team/)
- [Cloudflare D1 Documentation](https://developers.cloudflare.com/d1/)
- [Miniflare D1 Support](https://miniflare.dev/storage/d1)
- [Environment Strategy Documentation](../docs/environment-strategy.md)
- [Stack ADR](./stack.md)
- [Development Environment ADR](./development-environment.md)
- [Testing Strategy ADR](./testing-strategy.md)
