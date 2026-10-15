# ADR-0001: Use Express Framework

**Status:** Accepted  
**Date:** 2026-01-XX  
**Context:** Backend POC-2 - REST API Framework Selection  
**Decision Makers:** Backend Team

---

## Context

We need to choose a web framework for building REST APIs in our Node.js backend. The framework will be used across all microservices (Auth, Payments, Admin, Profile) and the API Gateway. This decision affects developer experience, performance, ecosystem, and long-term maintainability.

**Requirements:**

- Production-ready and battle-tested
- Excellent TypeScript support
- Large ecosystem of middleware
- Good performance
- Easy to learn and maintain
- Works well with microservices architecture
- Active maintenance and community support

---

## Decision

We will use **Express 4.x** as the web framework for all backend services.

**Rationale:**

- **Industry standard** - Most popular Node.js framework, used by major companies
- **Large ecosystem** - Extensive middleware and plugins available
- **Production-ready** - Battle-tested, proven in production at scale
- **Excellent TypeScript support** - Full type definitions, excellent IDE support
- **Easy to learn** - Simple API, good documentation, large community
- **Flexibility** - Unopinionated, allows us to structure services as needed
- **Microservices-friendly** - Works well with microservices architecture

---

## Alternatives Considered

### 1. Fastify

**Pros:**
- Faster than Express (2x-3x performance improvement)
- Built-in TypeScript support
- Modern async/await API
- Plugin system

**Cons:**
- Smaller ecosystem than Express
- Less middleware available
- Smaller community
- Less documentation and examples
- Team familiarity may be lower

**Decision:** Not chosen - Ecosystem and community support are more important than raw performance for POC-2.

---

### 2. Koa

**Pros:**
- More modern than Express
- Better async/await support
- Cleaner middleware API
- Smaller core

**Cons:**
- Less popular than Express
- Smaller ecosystem
- Less middleware available
- Team familiarity may be lower
- Migration from Express ecosystem can be challenging

**Decision:** Not chosen - Express ecosystem and community support outweigh modern features.

---

### 3. NestJS

**Pros:**
- Opinionated structure (good for teams)
- Built-in dependency injection
- Excellent TypeScript support
- Built-in support for microservices
- Decorators for routes

**Cons:**
- More complex than Express
- Steeper learning curve
- More opinionated (less flexibility)
- Heavier framework
- May be overkill for POC-2

**Decision:** Not chosen - Complexity and learning curve outweigh benefits for POC-2. Express provides sufficient flexibility.

---

## Trade-offs

### Pros

- ✅ **Ecosystem** - Largest ecosystem of middleware and plugins
- ✅ **Community** - Large community, extensive documentation
- ✅ **Familiarity** - Most developers are familiar with Express
- ✅ **Flexibility** - Unopinionated, structure services as needed
- ✅ **Production-ready** - Battle-tested at scale
- ✅ **TypeScript support** - Excellent type definitions

### Cons

- ⚠️ **Performance** - Not as fast as Fastify (but sufficient for our needs)
- ⚠️ **Modern features** - Less modern than Koa (but ecosystem compensates)
- ⚠️ **Structure** - Less opinionated than NestJS (but flexibility is valuable)

---

## Consequences

### Positive

- ✅ **Developer Experience** - Easy to learn, extensive documentation
- ✅ **Ecosystem** - Access to large middleware ecosystem
- ✅ **Community Support** - Large community for help and examples
- ✅ **Flexibility** - Can structure services as needed
- ✅ **Production Readiness** - Proven at scale

### Negative

- ⚠️ **Performance** - May need optimization for high-traffic scenarios (but sufficient for POC-2)
- ⚠️ **Structure** - Need to establish our own patterns (but flexibility is valuable)

### Neutral

- 🔄 **Migration Path** - Can migrate to Fastify or Koa later if needed (but unlikely)
- 🔄 **Learning Curve** - Low learning curve (positive for team)

---

## Implementation Notes

- Use Express 4.x (latest stable)
- Structure services with Express Router
- Use middleware for cross-cutting concerns (auth, logging, error handling)
- Follow Express best practices
- Use TypeScript for type safety

---

## Related Decisions

- **ADR-0002: Use Prisma ORM** - Express works well with Prisma
- **ADR-0005: JWT Authentication** - Express middleware for JWT validation
- Frontend ADRs are independent (frontend uses React, not Express)

---

## References

- [Express.js Official Documentation](https://expressjs.com/)
- `docs/backend-poc2-tech-stack.md` - Complete tech stack documentation
- `docs/backend-poc2-architecture.md` - Architecture documentation

---

**Last Updated:** 2026-01-XX

