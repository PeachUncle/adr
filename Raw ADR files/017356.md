# ADR-007: Feature-Based Code Organization

**Date**: 2025-10-27
**Status**: Accepted
**Epic**: Epic 005 - Backend Service Refactoring
**Related ADRs**: [ADR-001 (Inversify DI)](./ADR-001-inversify-dependency-injection.md)

## Context

The codebase was organized by technical layer, making it difficult to understand and modify features:

```
Before (Type-Based):
src/
├── controllers/      # All controllers
├── services/        # All services
├── repositories/    # All repositories
├── models/          # All models
└── utils/           # All utilities
```

**Problems**:
- **Feature Sprawl**: Changing one feature requires editing 5+ directories
- **Cognitive Load**: Hard to understand feature boundaries
- **Merge Conflicts**: Multiple developers editing same directories
- **Scalability**: Directories grow to 50+ files each

## Decision

We will organize code by **business domain/feature** rather than technical type.

```typescript
After (Feature-Based):
packages/backend/src/
├── features/
│   ├── payments/
│   │   ├── payment.service.ts
│   │   ├── payment.repository.ts
│   │   ├── payment.controller.ts
│   │   ├── payment.types.ts
│   │   ├── __tests__/
│   │   └── index.ts              # Barrel export
│   ├── users/
│   │   ├── user.service.ts
│   │   ├── user.repository.ts
│   │   ├── user.controller.ts
│   │   └── index.ts
│   └── content/
│       └── ...
├── shared/                       # Cross-cutting concerns
│   ├── database/
│   ├── cache/
│   └── utils/
└── infrastructure/               # App-level setup
    ├── container.ts
    ├── server.ts
    └── config.ts
```

**Principles**:
1. **Feature Modules**: Self-contained features with all related code
2. **Barrel Exports**: Clean imports via `index.ts`
3. **Shared Code**: Common utilities in `shared/`
4. **Feature Independence**: Minimal coupling between features

## Consequences

### Positive

1. **Improved Discoverability**: All payment code in `features/payments/`
2. **Easier Onboarding**: New developers understand feature boundaries
3. **Parallel Development**: Teams work on different features independently
4. **Better Testing**: Test entire feature in isolation
5. **Scalability**: Add new features without impacting existing ones

### Negative

1. **Migration Effort**: Reorganizing existing codebase takes time
2. **Some Duplication**: Shared utilities might be duplicated initially
3. **Learning Curve**: Team needs to understand new structure

## Implementation Notes

```typescript
// Clean imports with barrel exports
import { PaymentService, PaymentRepository } from '@/features/payments';

// Instead of
import { PaymentService } from '@/services/payment.service';
import { PaymentRepository } from '@/repositories/payment.repository';
```

## Related Documentation

- [Feature Architecture Guide](/FEATURE_ARCHITECTURE_GUIDE.md)
- [Monorepo Organization](/docs/monorepo-organization.md)
- [Backend Developer Guide](/docs/development/backend-developer-guide.md#code-organization)

## Revision History

- **2025-10-27**: Initial decision documented for Epic 005
