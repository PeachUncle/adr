# ADR 003: Incremental Migration Strategy

## Status
Accepted

## Context
We are refactoring the codebase to Clean/Hexagonal Architecture while maintaining 100% backward compatibility. The application is actively used and must continue functioning during refactoring. We cannot afford a "big bang" rewrite.

Current challenges:
- ~12k LOC across 116 TypeScript files
- No existing test infrastructure
- Server actions directly coupled to database
- Business logic scattered across files
- Need to maintain functionality during migration

## Decision
We will use an incremental, behavior-preserving migration strategy:

### Phase-by-Phase Approach

#### Phase 1: Foundation (Completed ✅)
- Create layer directory structure
- Add architectural documentation (ADRs, READMEs)
- Establish patterns and conventions
- No code changes, pure documentation

#### Phase 2: Domain Layer Extraction (In Progress 🔄)
- Create value objects (Email, Price, TokenCount, Rating)
- Create domain services (TokenCalculator, RestaurantOpeningService)
- Extract business rules from infrastructure code
- **No behavior changes**: Existing code continues to work

#### Phase 3: Infrastructure Ports (In Progress 🔄)
- Define port interfaces in application layer
- Implement adapters in infrastructure layer
- Create dependency injection container
- Refactor existing utilities to use ports (e.g., logger)
- **No behavior changes**: Same functionality, better structure

#### Phase 4: Gradual Server Action Refactoring (Next)
- Refactor one action at a time
- Update to use domain services and value objects
- Maintain exact same API and behavior
- Test after each refactoring
- Pattern: `get-restaurants.ts` already updated ✅

#### Phase 5: Security Hardening
- Add authorization checks to all actions
- Centralize via AuthorizationService
- Add audit logging for sensitive operations
- Input validation with Zod (already exists)
- **Improves security without breaking functionality**

#### Phase 6: Repository Layer (Future)
- Create repository interfaces
- Implement Drizzle-based repositories
- Gradually move database access from actions to repositories
- One repository at a time

### Migration Principles

1. **Always Behavior-Preserving**
   - Every refactoring maintains exact same observable behavior
   - If behavior must change, do it in separate PR
   - Compile and lint after every change

2. **Small, Reversible Steps**
   - Each commit is a complete, working state
   - Easy to review and understand
   - Easy to revert if needed

3. **Test-Driven When Possible**
   - Add characterization tests before refactoring
   - But don't block on tests - incremental improvement
   - Focus tests on domain layer (pure functions)

4. **Coexistence Strategy**
   - Old and new patterns coexist during migration
   - No "flag day" where everything changes
   - Gradually increase percentage of code using new patterns

5. **Documentation First**
   - Document patterns before implementing
   - Examples in READMEs guide implementation
   - ADRs explain decisions

### File-by-File Strategy

For server actions (primary refactoring target):

```
Before: src/actions/get-restaurants.ts
- Direct database access
- Business logic inline
- No separation of concerns

After: src/actions/get-restaurants.ts (Step 1: Use domain services) ✅
- Uses TokenCalculator for price conversion
- Uses RestaurantOpeningService for hours
- Same API, same behavior
- Still has direct database access (to be migrated later)

After: src/actions/get-restaurants.ts (Step 2: Use repository) ⏳
- Calls GetRestaurantsUseCase
- Use case uses IRestaurantRepository port
- Complete separation of concerns
- Same API, same behavior
```

### Measuring Progress

Track migration progress with metrics:
- % of actions using domain services
- % of actions using use cases
- % of database access via repositories
- Test coverage percentage
- Cyclomatic complexity reduction

Current Status:
- Domain services created: 2/2 ✅
- Value objects created: 4/4 ✅
- Infrastructure ports defined: 3/5 🔄
- Actions refactored: 1/23 (4%)
- Repository layer: Not started

## Consequences

### Positive
- Zero downtime during refactoring
- Each step adds value independently
- Easy to review small changes
- Can stop/pause migration at any point
- Team learns patterns incrementally
- Reduced risk compared to big bang

### Negative
- Takes longer than full rewrite
- Temporary inconsistency in codebase
- Must maintain both patterns during transition
- Requires discipline to follow strategy

### Risks & Mitigations

**Risk**: Incomplete migration leaves technical debt
**Mitigation**: Each phase delivers value independently; even partial migration improves codebase

**Risk**: New code might not follow patterns during migration
**Mitigation**: Clear documentation in AGENTS.md; code review enforcement

**Risk**: Performance regression during refactoring
**Mitigation**: Maintain current patterns; measure after major changes

## Success Criteria

Migration is successful when:
1. ✅ Architecture documentation is complete and clear
2. 🔄 All actions use domain services where applicable (currently 4%)
3. ⏳ Authorization checks centralized via AuthorizationService
4. ⏳ Audit logging on sensitive operations
5. ⏳ At least 50% of actions refactored to use case pattern
6. ⏳ Test coverage > 70% on domain layer
7. ✅ No regressions in existing functionality
8. ⏳ CI pipeline passes all checks

## Timeline

- Week 1: ✅ Foundation & Domain layer
- Week 2: 🔄 Ports, adapters, basic refactoring
- Week 3: ⏳ Security hardening, more action refactoring
- Week 4: ⏳ Repository layer, comprehensive testing
- Ongoing: Continue incremental improvements

## References
- Martin Fowler - [Refactoring: Improving the Design of Existing Code](https://martinfowler.com/books/refactoring.html)
- Michael Feathers - [Working Effectively with Legacy Code](https://www.goodreads.com/book/show/44919.Working_Effectively_with_Legacy_Code)
- [Strangler Fig Pattern](https://martinfowler.com/bliki/StranglerFigApplication.html)
