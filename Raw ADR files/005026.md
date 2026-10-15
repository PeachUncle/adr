# ADR-001: Use Fastify for API Server

**Status:** Accepted
**Date:** 2025-11-14
**Deciders:** Alice (Architect), Charlie (Developer)
**Technical Story:** Epic 6 - Story 6-1 (API Infrastructure & Type System)

## Context and Problem Statement

The Agent Orchestrator requires a REST API server to provide remote access and monitoring capabilities. We need a Node.js web framework that provides excellent TypeScript support, high performance, and built-in features for API development.

## Decision Drivers

* Native TypeScript support without extensive configuration
* Built-in schema validation capabilities
* Performance requirements (handling multiple concurrent connections)
* Developer experience and productivity
* Active maintenance and community support
* OpenAPI/Swagger documentation support

## Considered Options

* **Option 1:** Fastify
* **Option 2:** Express.js
* **Option 3:** Koa.js
* **Option 4:** Nest.js

## Decision Outcome

**Chosen option:** "Fastify", because it provides native TypeScript support, built-in schema validation with JSON Schema, exceptional performance (2x faster than Express in benchmarks), and first-class OpenAPI/Swagger support.

### Positive Consequences

* Native TypeScript support reduces configuration overhead
* JSON Schema validation provides type safety at runtime
* 2x performance improvement over Express reduces server costs
* Built-in plugins for CORS, Helmet, JWT, Rate Limiting
* OpenAPI plugin generates Swagger docs automatically
* Large ecosystem of community plugins

### Negative Consequences

* Smaller community compared to Express (but growing rapidly)
* Team needs to learn Fastify-specific patterns (minor learning curve)
* Some Express middleware requires adapters

## Pros and Cons of the Options

### Option 1: Fastify

Native TypeScript web framework with built-in schema validation and plugin architecture.

**Pros:**
* Built for TypeScript from the ground up
* JSON Schema validation built-in
* 2x faster than Express (benchmarks: ~65,000 req/sec vs ~30,000 req/sec)
* Excellent plugin ecosystem
* First-class OpenAPI/Swagger support
* Async/await friendly

**Cons:**
* Smaller community than Express
* Fewer third-party middleware options
* Team learning curve (minor)

### Option 2: Express.js

The de-facto standard Node.js web framework, mature and widely adopted.

**Pros:**
* Largest community and ecosystem
* Most third-party middleware available
* Well-known patterns, easy to hire for
* Extensive documentation and tutorials

**Cons:**
* Callback-based API (not async/await native)
* No built-in schema validation
* TypeScript support requires extra configuration
* Lower performance (30,000 req/sec in benchmarks)
* Manual OpenAPI schema maintenance

### Option 3: Koa.js

Modern, minimalist web framework from Express team using async/await.

**Pros:**
* Async/await native
* Smaller, more modern codebase
* Good middleware composition
* Better error handling than Express

**Cons:**
* Smaller ecosystem than Express
* No built-in schema validation
* Less mature plugin system
* Manual TypeScript configuration
* Performance similar to Express

### Option 4: Nest.js

Enterprise-grade TypeScript framework with Angular-inspired architecture.

**Pros:**
* Excellent TypeScript support
* Dependency injection built-in
* Enterprise patterns (controllers, services, modules)
* GraphQL support out of the box
* Large, active community

**Cons:**
* Heavy framework (significant boilerplate)
* Opinionated architecture may be overkill
* Steeper learning curve
* Larger bundle size
* Uses Express or Fastify under the hood (abstraction layer)

## Links

* [Fastify Official Docs](https://www.fastify.io/)
* [Fastify Benchmarks](https://www.fastify.io/benchmarks/)
* [Fastify TypeScript Guide](https://www.fastify.io/docs/latest/Reference/TypeScript/)
* [Epic 6 Retrospective](../epics/epic-6-retrospective.md)
* Story Implementation: `backend/src/api/server.ts`

## Implementation Notes

### Setup Details
- Fastify 4.x with TypeScript 5.x
- Plugins used: @fastify/cors, @fastify/helmet, @fastify/jwt, @fastify/rate-limit
- OpenAPI via @fastify/swagger and @fastify/swagger-ui
- JSON Schema validation for all routes

### Migration Path
- No migration needed (greenfield implementation)
- All API endpoints built on Fastify from day one

### Performance Results
- Benchmark: 65,000+ requests/second (local testing)
- WebSocket connections: 1,000+ concurrent connections handled smoothly
- Memory usage: ~50MB baseline, stable under load

## Review and Update History

| Date | Reviewer | Change |
|------|----------|--------|
| 2025-11-14 | Alice, Charlie | Initial decision (Story 6-1) |
| 2025-11-16 | Bob | Documented in ADR (Epic 6 retrospective) |
