# ADR 002: Vertical Slice Architecture for Domains

**Status**: Accepted
**Date**: 2025-11-06
**Deciders**: Architecture Team

## Context

Traditional layered architecture organizes code by technical concerns:
```
services/
  authService.ts
  userService.ts
controllers/
  authController.ts
  userController.ts
repositories/
  authRepository.ts
  userRepository.ts
```

This creates several problems:
1. **Scattered Context**: Related code is far apart
2. **AI Comprehension**: Agents need to load many files to understand one feature
3. **Token Inefficiency**: More files means more tokens
4. **Coupling**: Changes often require touching many directories

## Decision

We will use **Vertical Slice Architecture** for domain packages, organizing code by feature/domain rather than technical layer.

### Structure

```
packages/domains/auth/
├── SPEC.md
├── src/
│   ├── entities/
│   │   └── user.entity.ts
│   ├── services/
│   │   └── userAuthentication.service.ts
│   ├── repositories/
│   │   └── user.repository.ts
│   ├── procedures/          # tRPC procedures
│   │   ├── login.procedure.ts
│   │   └── register.procedure.ts
│   ├── validators/          # Zod schemas
│   │   └── loginInput.validator.ts
│   └── types/
│       └── index.ts
└── tests/
```

### Key Principles

1. **Self-Contained Domains**
   - Each domain contains ALL code for that business capability
   - Minimal cross-domain dependencies

2. **Clear Boundaries**
   - Domains can only depend on platform and shared packages
   - Domain-to-domain dependencies are explicit and reviewed

3. **AI-Friendly**
   - AI can load entire domain context efficiently
   - Related code is co-located
   - Clear file naming indicates purpose

4. **Consistent Structure**
   - Every domain follows same pattern
   - AI can predict where code lives

## Alternatives Considered

### Traditional Layered Architecture
- **Pros**: Familiar, well-understood
- **Cons**: Code scattered, poor AI comprehension, high coupling
- **Reason not chosen**: Not optimized for AI agents

### Microservices
- **Pros**: Complete separation
- **Cons**: Deployment complexity, network overhead, harder to share code
- **Reason not chosen**: Too complex for our scale

### Feature Folders (Flat)
- **Pros**: Simple, everything in one place
- **Cons**: No structure, hard to find code as it grows
- **Reason not chosen**: Doesn't scale

## Consequences

### Positive
- **Better AI Comprehension**: AI can load entire domain context in fewer tokens
- **Faster Development**: Related code is easy to find
- **Clear Boundaries**: Domain responsibilities are explicit
- **Easy Testing**: Test entire domain in isolation
- **Parallel Development**: Teams can work on different domains independently

### Negative
- **Potential Duplication**: Same logic might be implemented in multiple domains
- **Learning Curve**: Developers need to understand the pattern
- **Refactoring**: Moving functionality between domains requires more thought

### Neutral
- **Standards Needed**: Must maintain SPEC.md and STANDARDS.md for each domain
- **Discipline Required**: Team must resist putting shared code in domains

## Implementation Notes

### Dependency Rules (enforced by ESLint)

```
Domain -> Platform ✅
Domain -> Shared ✅
Domain -> Domain ❌ (requires explicit approval)
Domain -> Runtime ❌ (never)
```

### SPEC.md Requirements

Every domain must have:
1. **Purpose**: What business capability does this domain handle?
2. **Boundaries**: What is in/out of scope?
3. **Dependencies**: What does this domain depend on?
4. **API**: What does this domain expose?

### Creating New Domain

Use NX generator (when available):
```bash
nx generate @iam/domain-generator --name=my-domain
```

Or manually follow template from existing domain.

## References

- [Vertical Slice Architecture](https://www.jimmybogard.com/vertical-slice-architecture/)
- [Feature Slices](https://feature-sliced.design/)
- [Domain-Driven Design](https://www.domainlanguage.com/ddd/)
