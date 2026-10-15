# ADR 001: Multi-Repository Strategy

**Status:** ~~Accepted~~ → **Superseded** (by ADR-014)

**Date:** 2024-11-12

**Updated:** 2024-12-03

**Deciders:** Piotr Świderski

**Superseded By:** [ADR-014: Laravel-First Strategy](014-laravel-first-strategy.md)

**Technical Story:** BuildFlow needs to support multiple backend implementations (Laravel, Symfony, Next.js) while maintaining a single frontend and documentation.

**⚠️ IMPORTANT:** The multi-framework parallel implementation strategy from this ADR has been superseded by ADR-014, which pivots to a "Laravel-First" approach focusing on depth over breadth. The multi-repository structure itself remains valid, but implementation priorities have changed:
- **High Priority:** Laravel (enterprise-grade with DDD/Events/CQRS)
- **Low Priority:** Symfony, Next.js (optional future experiments)

See ADR-014 for full rationale and updated strategy.

---

## Context

BuildFlow is designed as a portfolio project that demonstrates full-stack development capabilities across multiple technology stacks. The project needs to:

### Current Situation
- Single developer building multiple implementations
- Need to showcase expertise in different frameworks
- Want to maintain consistency across implementations
- Documentation should be technology-agnostic

### Requirements
- Support Laravel, Symfony, and potentially Next.js backends
- Single React frontend that works with any backend
- Shared business logic and API contract
- Independent deployment of each implementation
- Clear separation for portfolio presentation
- Allow community contributions to specific stacks

---

## Decision

**We will use a multi-repository architecture with separate repositories for each implementation and a central documentation repository.**

### Repository Structure
```
buildflow-docs/              # Central documentation & API contract
buildflow-laravel-api/       # Laravel implementation
buildflow-symfony-api/       # Symfony implementation
buildflow-nextjs-api/        # Next.js implementation (future)
buildflow-react-web/         # React frontend (single)
buildflow-android/           # Android app (future)
buildflow-ios/               # iOS app (future)
```

### Implementation Details
1. **buildflow-docs** serves as single source of truth
   - OpenAPI 3.0 specification
   - Business requirements
   - Architecture documentation
   - Development roadmap

2. **Each backend** implements the same API contract
   - Must pass contract tests
   - Same endpoints, request/response formats
   - Same business logic outcomes
   - Technology-specific optimizations allowed

3. **Frontend** is backend-agnostic
   - Configurable API base URL
   - Auto-generated TypeScript types from OpenAPI
   - Works with any compliant backend

4. **Independent CI/CD** for each repository
   - Separate pipelines
   - Individual deployment strategies
   - Stack-specific testing

---

## Consequences

### Positive
- ✅ **Portfolio Value**: Each repo is standalone showcase
- ✅ **Independence**: Implementations evolve separately
- ✅ **Learning**: Compare different approaches to same problem
- ✅ **Clarity**: Clear separation of concerns
- ✅ **Deployment**: Deploy backends independently
- ✅ **CI/CD**: Faster builds, isolated failures
- ✅ **Team Work**: Different people can work on different stacks
- ✅ **Flexibility**: Easy to add new implementations

### Negative
- ⚠️ **Coordination**: API changes affect all repos
- ⚠️ **Duplication**: Some patterns repeated across repos
- ⚠️ **Maintenance**: More repos to manage
- ⚠️ **Synchronization**: Keeping implementations aligned
- ⚠️ **Complexity**: More moving parts

### Risks & Mitigation
- **Risk**: API contract changes break implementations
  - **Mitigation**: Contract tests, semantic versioning, changelog
  
- **Risk**: Implementations drift apart
  - **Mitigation**: Regular contract test runs, documentation updates
  
- **Risk**: Harder onboarding for contributors
  - **Mitigation**: Clear documentation, setup guides per stack

---

## Alternatives Considered

### Alternative 1: Monorepo
**Description:** Single repository with all implementations in subdirectories

**Pros:**
- Easier to coordinate changes
- Shared tooling and scripts
- Single version control history
- Atomic commits across implementations

**Cons:**
- Large repository size
- Slower CI/CD (must run all tests)
- Mixed concerns in issues/PRs
- Less clear for portfolio presentation
- Harder to deploy independently
- Tool conflicts (npm vs composer)

**Why rejected:** Portfolio presentation and independent deployment are priorities. Monorepo creates coupling we want to avoid.

### Alternative 2: Mono-repository with separate NPM packages
**Description:** One repo, but publish each implementation as separate packages

**Pros:**
- Coordinated versioning
- Shared infrastructure

**Cons:**
- Still have monorepo complexity
- Doesn't solve deployment independence
- Less clear separation for portfolio

**Why rejected:** Doesn't provide enough benefits over multi-repo while keeping monorepo downsides.

### Alternative 3: Single Implementation
**Description:** Choose one stack and focus only on that

**Pros:**
- Simplest to maintain
- Fastest to deliver
- No coordination needed

**Cons:**
- Portfolio shows only one stack
- No comparison learning
- Less flexibility for users
- Missed learning opportunities

**Why rejected:** Primary goal is portfolio diversity and learning across stacks.

---

## Related Decisions

- [ADR-002](002-api-first-approach.md) - Defines the contract-first approach
- [ADR-008](008-contract-testing-strategy.md) - How we verify implementations match contract
- [ADR-010](010-frontend-backend-separation.md) - Frontend-backend separation strategy

---

## References

- [Microservices Patterns](https://microservices.io/patterns/index.html)
- [GitHub's Approach to Repository Organization](https://github.blog/2015-06-30-scripts-to-rule-them-all/)
- [Google's Monorepo vs Multi-repo](https://cacm.acm.org/magazines/2016/7/204032-why-google-stores-billions-of-lines-of-code-in-a-single-repository/fulltext)
- [Uber's Multi-Repo Approach](https://www.uber.com/en-PL/blog/multitenancy-microservice-architecture/)

---

## Notes

~~This decision prioritizes portfolio value and learning over operational simplicity. As the project matures and if a SaaS business emerges, we may reconsider and consolidate to one production-ready implementation while keeping others as examples.~~

~~The multi-repo strategy also allows each implementation to have its own community and contributors without forcing them to understand all stacks.~~

### ⚠️ UPDATE (2024-12-03): Strategy Superseded

**This ADR's multi-framework approach has been superseded by [ADR-014: Laravel-First Strategy](014-laravel-first-strategy.md).**

**What Changed:**
- **Repository Structure** - Still valid ✅
- **Contract-First Approach** - Still valid ✅  
- **Implementation Priority** - Changed ❌

**New Strategy:**
- Laravel implementation is **primary focus** (100% effort)
- Symfony/Next.js are **low priority** optional future experiments
- Focus shifted from "framework comparison" to "enterprise patterns depth"

**Rationale:**
After creating comprehensive documentation (13 ADRs, domain analysis, implementation guides), realized that **depth > breadth** for portfolio value. One enterprise-grade Laravel implementation with DDD/Events/CQRS demonstrates more senior-level expertise than three shallow CRUD implementations.

See ADR-014 for complete rationale, consequences, and migration guide.

---

**Original Date:** 2024-11-12

**Superseded Date:** 2024-12-03

**Last Updated:** 2024-12-03
