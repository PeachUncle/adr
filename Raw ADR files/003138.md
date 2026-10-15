# ADR-0001: Monorepo Structure and Bounded Context Organization

**Date**: 2025-12-25  
**Status**: Accepted  
**Deciders**: Architecture Team  
**Tags**: architecture, monorepo, organization

## Context

The Sri Lanka Payroll Platform has grown organically with backend code in `/backend`, frontend in `/frontend`, and tests in `/qa-automation`. As we scale and add more features, we need a clear organizational structure that:

1. Supports multiple applications (web, mobile, admin portals)
2. Enables code sharing across applications
3. Maintains clear boundaries between domains
4. Facilitates AI-assisted development
5. Supports both Windows and Linux development environments
6. Allows gradual migration without breaking existing functionality

## Decision

We will adopt a **monorepo structure** with clear boundaries organized by bounded contexts from Domain-Driven Design.

### Target Structure

```
PayRoll/
├── src/                          # All source code
│   ├── apps/                     # Deployable applications
│   │   ├── web/                  # Angular SPA (customer-facing)
│   │   ├── api/                  # ASP.NET Core API
│   │   └── admin/                # Admin portal (future)
│   ├── services/                 # Background services
│   │   ├── jobs/                 # Scheduled jobs (future)
│   │   └── workers/              # Message processors (future)
│   └── libs/                     # Shared libraries
│       ├── domain/               # Domain entities & business rules
│       ├── application/          # Use cases & application logic
│       ├── infrastructure/       # Data access & external services
│       ├── shared/               # Common utilities
│       └── contracts/            # DTOs, events, API contracts
├── tests/                        # All test projects
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── e2e/                      # End-to-end tests
├── infra/                        # Infrastructure as Code
│   ├── docker/                   # Docker configurations
│   ├── bicep/                    # Azure Bicep templates
│   └── k8s/                      # Kubernetes manifests (future)
├── docs/                         # Documentation
│   ├── adr/                      # Architecture Decision Records
│   ├── architecture/             # Architecture diagrams
│   ├── api/                      # API documentation
│   └── product/                  # Product requirements
├── tools/                        # Development tools
│   ├── scripts/                  # Cross-platform scripts
│   └── generators/               # Code generators
└── .github/                      # GitHub workflows & templates
```

### Migration Strategy

**Phase 1: Non-Breaking Setup** (Current)
- Keep existing `/backend`, `/frontend`, `/qa-automation` folders
- Create new `/src`, `/tests`, `/infra`, `/tools` structure
- Add documentation (AGENTS.md, DEVELOPMENT.md, ARCHITECTURE.md)
- Add cross-platform scripts in `/tools`
- Update CI/CD to support both structures

**Phase 2: Gradual Migration** (Future)
- Move one bounded context at a time to `/src/libs`
- Update references incrementally
- Maintain backward compatibility
- Run both old and new structures in parallel

**Phase 3: Consolidation** (Future)
- Complete migration of all code
- Remove legacy folders
- Update all documentation
- Archive old structure

### Bounded Context Organization

Within `/src/libs`, code is organized by bounded contexts:

```
libs/
├── domain/
│   ├── Employees/
│   ├── Payroll/
│   ├── PayrollConfig/
│   ├── Organizations/
│   ├── Leave/
│   ├── Loans/
│   ├── Overtime/
│   ├── GeneralLedger/
│   └── Auditing/
├── application/
│   ├── Employees/
│   │   ├── Commands/
│   │   ├── Queries/
│   │   └── DTOs/
│   └── (same structure for other contexts)
└── infrastructure/
    ├── Persistence/
    ├── Identity/
    ├── Files/
    └── Notifications/
```

## Consequences

### Positive

1. **Clear Boundaries**: Each bounded context has a clear home
2. **Code Sharing**: Shared libraries reduce duplication
3. **Scalability**: Easy to add new apps/services
4. **AI-Friendly**: Clear structure helps AI agents navigate code
5. **Testability**: Tests organized by type and scope
6. **DevOps**: Infrastructure code co-located with application code
7. **Documentation**: Centralized documentation structure
8. **Cross-Platform**: Scripts work on Windows and Linux

### Negative

1. **Migration Effort**: Requires time to move existing code
2. **Learning Curve**: Team needs to understand new structure
3. **Build Complexity**: More projects to manage
4. **Tooling**: Need to update IDE configurations

### Neutral

1. **Monorepo vs Multi-Repo**: We chose monorepo for simplicity, but could split later if needed
2. **Folder Naming**: Using lowercase for consistency with npm/node conventions

## Alternatives Considered

### Alternative 1: Keep Current Structure
**Pros**: No migration needed  
**Cons**: Doesn't scale, unclear boundaries, hard for AI agents  
**Verdict**: Rejected - doesn't meet long-term needs

### Alternative 2: Multi-Repo (Separate repos for backend, frontend, etc.)
**Pros**: Independent versioning, smaller repos  
**Cons**: Code sharing is harder, version coordination complex, more overhead  
**Verdict**: Rejected - premature optimization

### Alternative 3: Feature-Based Organization
**Pros**: All code for a feature in one place  
**Cons**: Violates clean architecture, hard to share code  
**Verdict**: Rejected - breaks architectural principles

## Implementation Plan

### Immediate (This PR)
- [x] Create `/docs/adr` folder
- [x] Add AGENTS.md
- [x] Add DEVELOPMENT.md
- [x] Add ARCHITECTURE.md
- [x] Add this ADR
- [ ] Create `/tools/scripts` with cross-platform dev scripts
- [ ] Add `.editorconfig`
- [ ] Add `.gitattributes`
- [ ] Update `.gitignore`
- [ ] Add CI/CD skeleton

### Short-Term (Next 2 weeks)
- [ ] Create `/src` folder structure
- [ ] Move `Payroll.Shared` to `/src/libs/shared`
- [ ] Update solution file
- [ ] Test build process

### Medium-Term (Next month)
- [ ] Move one bounded context (e.g., PayrollConfig) to new structure
- [ ] Update all references
- [ ] Verify tests pass
- [ ] Document lessons learned

### Long-Term (Next quarter)
- [ ] Complete migration of all code
- [ ] Remove legacy folders
- [ ] Update all documentation
- [ ] Celebrate! 🎉

## References

- [Monorepo vs Multi-Repo](https://www.atlassian.com/git/tutorials/monorepos)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [ADR Template](https://github.com/joelparkerhenderson/architecture-decision-record)

## Notes

- This ADR can be superseded by future ADRs if we discover better approaches
- The migration is intentionally gradual to minimize risk
- We prioritize developer experience and AI-agent friendliness

---

**Approved By**: Architecture Team  
**Review Date**: 2026-03-25 (3 months from now)
