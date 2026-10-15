# ADR 0001: Spring Boot 3 Migration Strategy

## Status

Accepted

## Context

We need to migrate our Spring Boot application from version 2.7.18 (javax) to Spring Boot 3.2.0 (jakarta) to maintain compatibility with modern Java ecosystem and receive security updates.

The application includes:
- REST API with CRUD operations (UserController)
- JPA entities and repositories
- H2 in-memory database
- Comprehensive test suite (JUnit + Cucumber)
- Java 1.8 → Java 17 upgrade required

## Decision

We will perform a **minimal changes migration** focusing on framework compatibility while preserving all existing functionality and API contracts.

### Migration Scope

**In Scope:**
1. Package namespace updates (javax.* → jakarta.*)
2. Spring Boot version update (2.7.18 → 3.2.0)
3. JDK version update (1.8 → 17)
4. Test framework compatibility updates
5. Dependency version updates

**Out of Scope:**
1. API endpoint changes (preserve all URLs)
2. Business logic changes
3. Database schema changes
4. New Spring Boot 3 features (can be added later)
5. Architecture changes

### Implementation Approach

**Phase 1: Dependencies**
- Update parent POM to Spring Boot 3.2.0
- Update Java source/target to 17
- Update Cucumber and test dependencies

**Phase 2: Package Migrations**
- javax.persistence.* → jakarta.persistence.*
- javax.validation.* → jakarta.validation.*
- javax.servlet.* → jakarta.servlet.* (if used)

**Phase 3: Validation**
- Ensure all unit tests pass
- Ensure all integration tests pass
- Verify API endpoints unchanged
- No deprecation warnings

## Rationale

**Why minimal changes approach:**
- Reduces risk of introducing bugs
- Faster migration completion
- Easier to validate correctness
- Separates framework upgrade from feature work
- Can adopt new Spring Boot 3 features incrementally

**Alternatives considered:**
- **Option B: Aggressive modernization** - Also adopt new Spring Boot 3 patterns (ProblemDetail, SecurityFilterChain, etc.)
  - Rejected: Increases scope and risk, harder to validate
- **Option C: Stay on Spring Boot 2** - Continue with 2.7.x
  - Rejected: EOL approaching, missing security updates

## Consequences

### Positive

- ✅ Application compatible with modern Java ecosystem
- ✅ Receives security updates and bug fixes
- ✅ Foundation for future Spring Boot 3 feature adoption
- ✅ Minimal code changes reduces regression risk
- ✅ Clear success criteria (tests pass, APIs unchanged)

### Negative

- ❌ Not using new Spring Boot 3 features yet
- ❌ Requires JDK 17 (infrastructure update needed)
- ❌ Some third-party library updates may be required

### Migration Risks

- **Low risk:** Package renames (automated refactoring)
- **Low risk:** Dependency updates (well-documented)
- **Medium risk:** Third-party library compatibility
- **Low risk:** Configuration changes (minimal in Spring Boot 3)

## Validation Criteria

Migration is successful when:
1. [ ] Application compiles with Spring Boot 3.2.0
2. [ ] All unit tests pass (UserServiceTest, UserControllerTest)
3. [ ] All integration tests pass (Cucumber scenarios)
4. [ ] All API endpoints return expected responses
5. [ ] No @Deprecated warnings in code
6. [ ] Application starts successfully on JDK 17

## References

- Spring Boot 3.0 Migration Guide: https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migration-Guide
- Jakarta EE Migration: https://jakarta.ee/
- This ADR informs: UserController migration, Service layer migration, Test updates

## Notes

This ADR can be referenced in AI prompts:
```
"Follow ADR 0001 migration strategy, migrate UserController.java"
```

Future enhancements (e.g., adopting ProblemDetail for error handling) should be tracked in separate ADRs.
