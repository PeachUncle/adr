# ADR 002: API-First Development Approach

**Status:** Accepted

**Date:** 2024-11-12

**Updated:** 2024-12-03

**Deciders:** Piotr Świderski

**Technical Story:** Need a development methodology that ensures consistency between backend API and frontend, with flexibility for potential future implementations.

**Related:** [ADR-014: Laravel-First Strategy](014-laravel-first-strategy.md)

---

## Context

BuildFlow uses an API-first approach to maintain clear separation between backend and frontend. While the primary focus is Laravel implementation (see ADR-014), the API contract remains framework-agnostic to:

### Current Situation
- Laravel as primary backend implementation (Phase 1)
- React frontend must work with backend
- Need clear contract for API structure
- Potential future implementations (Symfony, Next.js) as learning exercises
- Frontend should be decoupled from backend technology

### Requirements
- Frontend-backend contract is clear
- Changes are coordinated and versioned
- New developers can understand API quickly
- Automated validation of compliance
- Documentation stays synchronized
- Framework-agnostic API design

---

## Decision

**We will use an API-first approach where the OpenAPI specification is designed before any implementation and serves as the single source of truth.**

### Implementation Details

1. **Design Phase**
   - OpenAPI 3.0 specification designed first
   - Stored in `buildflow-docs/api-contract/openapi.yaml`
   - Reviewed and approved before implementation
   - Versioned semantically (v1, v2, etc.)

2. **Implementation Phase**
   - Backends implement spec exactly
   - Frontend generates types from spec
   - Contract tests validate compliance
   - No deviation without spec update

3. **Change Management**
   - API changes proposed as spec updates
   - Breaking changes require major version bump
   - All implementations update together
   - Changelog maintained in buildflow-docs

4. **Workflow**
   ```
   1. Design endpoint in OpenAPI spec
   2. Review and approve spec change
   3. Update spec in buildflow-docs
   4. Generate frontend types
   5. Implement in backend(s)
   6. Write contract tests
   7. Verify all implementations pass
   8. Deploy
   ```

### OpenAPI Spec Structure
```yaml
openapi: 3.0.0
info:
  title: BuildFlow API
  version: 1.0.0
  description: Construction Business Management System

servers:
  - url: http://localhost:8000/api/v1    # Laravel
  - url: http://localhost:8001/api/v1    # Symfony
  - url: http://localhost:3000/api/v1    # Next.js

paths:
  /clients:
    get:
      summary: List clients
      # ... full specification
    post:
      summary: Create client
      # ... full specification

components:
  schemas:
    Client:
      type: object
      properties:
        # ... full schema
```

---

## Consequences

### Positive
- ✅ **Single Source of Truth**: API spec is authoritative
- ✅ **Consistency**: All implementations must match
- ✅ **Documentation**: Spec is documentation
- ✅ **Type Safety**: Generate TypeScript types
- ✅ **Testing**: Automated contract validation
- ✅ **Coordination**: Clear process for changes
- ✅ **Tooling**: Swagger UI, Postman collections
- ✅ **Frontend Independence**: Works with any backend
- ✅ **Clear Communication**: Spec is contract between teams

### Negative
- ⚠️ **Upfront Design**: Must design before coding
- ⚠️ **Change Overhead**: Spec updates affect multiple repos
- ⚠️ **Learning Curve**: OpenAPI syntax to learn
- ⚠️ **Rigidity**: Less flexibility to experiment
- ⚠️ **Maintenance**: Spec must stay current

### Risks & Mitigation
- **Risk**: Spec becomes out of sync with implementations
  - **Mitigation**: Contract tests in CI, fail on mismatch
  
- **Risk**: Design decisions made without implementation knowledge
  - **Mitigation**: Iterative refinement, spike implementations
  
- **Risk**: Spec becomes bloated
  - **Mitigation**: Regular reviews, remove unused endpoints

---

## Alternatives Considered

### Alternative 1: Implementation-First
**Description:** Build one implementation, then extract API spec from it

**Pros:**
- Faster initial development
- Learn from actual implementation
- More flexibility to experiment

**Cons:**
- Hard to coordinate multiple implementations
- Spec becomes documentation, not contract
- Risk of inconsistency
- Frontend must adapt to changes

**Why rejected:** Doesn't solve our multi-implementation consistency problem. Priority is consistency over speed.

### Alternative 2: Code-First with Code Generation
**Description:** Define API in code, generate spec automatically

**Pros:**
- Keep code and spec in sync automatically
- DRY principle
- Type safety in implementation

**Cons:**
- Tied to one language/framework
- Generated specs often incomplete
- Harder to review spec changes
- Doesn't work across multiple languages

**Why rejected:** Doesn't work for multi-language implementations. Need language-agnostic spec.

### Alternative 3: GraphQL
**Description:** Use GraphQL instead of REST

**Pros:**
- Schema-first by default
- Strong typing
- Flexible queries
- Single endpoint

**Cons:**
- More complex for simple CRUD
- Harder for construction business integrations
- Less common in PHP ecosystem
- Steeper learning curve for contributors

**Why rejected:** REST is simpler for CRUD operations and more familiar. GraphQL is overkill for MVP.

---

## Related Decisions

- [ADR-001](001-multi-repository-strategy.md) - Multi-repo strategy this enables
- [ADR-008](008-contract-testing-strategy.md) - How we verify compliance
- [ADR-010](010-frontend-backend-separation.md) - Frontend consumes this API

---

## References

- [OpenAPI Specification](https://swagger.io/specification/)
- [API-First Development](https://swagger.io/resources/articles/adopting-an-api-first-approach/)
- [Stripe API Design](https://stripe.com/blog/payment-api-design)
- [GitHub API Design](https://docs.github.com/en/rest/guides/best-practices-for-integrators)
- [Contract Testing with Spectator](https://spectator.artisan.studio/)

---

## Notes

The API-first approach is critical for our multi-implementation strategy. Without it, keeping implementations consistent would be nearly impossible.

We chose OpenAPI 3.0 specifically because:
- Industry standard
- Excellent tooling support
- Language agnostic
- Good documentation generation
- Contract testing libraries available

Version 1.0 will be stabilized for MVP. Breaking changes will require v2.

---

**Last Updated:** 2024-11-12
