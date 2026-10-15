# 6. SSA in Next.js Override to Avoid Over-Engineering

Date: 2025-09-12

## Status

Accepted

supercedes [4. GraphQL API with PostGraphile View-First Approach](0004-graphql-api-with-postgraphile-view-first-approach.md)

## Context

After implementing the PostGraphile GraphQL API (ADR-0004), the team realized that:

- The GraphQL API was over-engineered for the portfolio's needs
- PostGraphile added unnecessary complexity for a simple portfolio site
- The database-first approach was too rigid for rapid iteration
- Next.js Server-Side Actions (SSA) provide sufficient API capabilities
- The portfolio doesn't require complex real-time features or subscriptions

The portfolio's actual requirements are:

- Simple CRUD operations for portfolio content
- Basic authentication and user management
- No complex data relationships requiring GraphQL
- Need for rapid development and iteration
- Simple deployment and maintenance

## Decision

Override the PostGraphile approach and implement Server-Side Actions (SSA) in Next.js:

- **Next.js Server Actions** for API endpoints
- **Direct database queries** using Drizzle ORM
- **Simplified authentication** with Auth0
- **RESTful patterns** instead of GraphQL
- **Type safety** through TypeScript and Drizzle

## Consequences

### Positive

- **Simplicity**: Much simpler architecture and development process
- **Faster development**: No need to learn PostGraphile or GraphQL concepts
- **Better performance**: Direct database queries without GraphQL overhead
- **Easier debugging**: Clear request/response flow
- **Lower maintenance**: Fewer moving parts and dependencies

### Negative

- **Less type safety**: No automatic schema generation
- **Manual API design**: Need to design REST endpoints manually
- **No real-time features**: No built-in subscriptions
- **More boilerplate**: Need to write more code for API endpoints
- **Less standardization**: No enforced API patterns

### Risks

- **API inconsistency**: Without GraphQL schema, API may become inconsistent
- **Scalability concerns**: SSA may not scale as well as dedicated API services
- **Feature limitations**: May need to add GraphQL back for complex features
- **Team knowledge**: Team needs to understand Next.js SSA patterns
