# ADR-001: Adopt Inversify for Dependency Injection

**Date**: 2025-10-27
**Status**: Accepted
**Epic**: Epic 005 - Backend Service Refactoring
**Related ADRs**: [ADR-006 (TypeScript Strict Mode)](./ADR-006-typescript-strict-mode.md), [ADR-008 (Jest Testing)](./ADR-008-jest-testing.md)

## Context

The Sovren backend services were growing in complexity with increasing dependencies between components. Manual dependency management led to:

- **Tight Coupling**: Services directly instantiated their dependencies, making changes difficult
- **Testing Challenges**: Mocking dependencies required complex setup and was error-prone
- **Configuration Complexity**: Environment-specific configurations scattered across codebase
- **Lifecycle Management**: No standardized approach for singleton vs transient instances
- **Circular Dependencies**: Risk of circular dependencies with no framework protection

We needed a robust dependency injection (DI) framework to:
- Enforce loose coupling through interfaces
- Simplify testing with automatic mock injection
- Centralize configuration and bootstrapping
- Provide lifecycle management (singleton, scoped, transient)
- Support TypeScript decorators for clean syntax

## Decision

We will use **Inversify** as our dependency injection container for all backend services.

**Implementation Approach**:
```typescript
// services/container.ts - IoC Container setup
import { Container } from 'inversify';
import { TYPES } from './types';

const container = new Container();

// Bind services
container.bind<IPaymentService>(TYPES.PaymentService).to(PaymentService).inSingletonScope();
container.bind<IUserService>(TYPES.UserService).to(UserService).inSingletonScope();
container.bind<ICacheService>(TYPES.CacheService).to(RedisCacheService).inSingletonScope();

// Service implementation with decorator injection
@injectable()
class PaymentService implements IPaymentService {
  constructor(
    @inject(TYPES.LightningService) private lightningService: ILightningService,
    @inject(TYPES.CacheService) private cacheService: ICacheService,
    @inject(TYPES.EventBus) private eventBus: IEventBus
  ) {}

  async createInvoice(amount: number): Promise<Invoice> {
    // Dependencies automatically injected
  }
}
```

**Key Features Adopted**:
1. **Decorator-Based Injection**: `@injectable()` and `@inject()` for clean syntax
2. **Interface Binding**: Services bound to interfaces, not concrete implementations
3. **Lifecycle Scopes**:
   - `inSingletonScope()`: Single instance across application (caches, event bus)
   - `inRequestScope()`: One instance per HTTP request (repositories)
   - `inTransientScope()`: New instance every time (factories, utilities)
4. **Symbol-Based Identifiers**: Type-safe dependency identifiers using symbols
5. **Modular Containers**: Feature-specific container modules for organization

## Consequences

### Positive

1. **Testability**: Easy to inject mocks in tests
   ```typescript
   // Test setup
   container.rebind(TYPES.LightningService).toConstantValue(mockLightningService);
   const service = container.get<PaymentService>(TYPES.PaymentService);
   ```

2. **Loose Coupling**: Services depend on interfaces, not implementations
   - Can swap Redis cache for in-memory cache without changing service code
   - Easy to add decorators (logging, caching) without modifying services

3. **Centralized Configuration**: All bindings defined in one place
   - Easy to see all dependencies at a glance
   - Environment-specific configurations managed centrally

4. **Type Safety**: TypeScript decorators with strict type checking
   - Compile-time errors for missing dependencies
   - IntelliSense support for injected dependencies

5. **Lifecycle Management**: Explicit control over instance lifecycles
   - Singletons ensure shared state (event bus, cache connections)
   - Request scopes prevent memory leaks in long-running processes

### Negative

1. **Learning Curve**: Team needs to learn Inversify patterns
   - Mitigation: Comprehensive documentation and examples
   - Onboarding guide in developer documentation

2. **Decorator Dependency**: Requires `experimentalDecorators` in TypeScript
   - Already enabled in our strict TypeScript config
   - Industry-standard pattern for DI frameworks

3. **Boilerplate Code**: Need to define symbols and bindings
   - Mitigated by organized `types.ts` and `container.ts` structure
   - One-time setup cost, ongoing benefits

4. **Runtime Overhead**: Minimal reflection overhead at startup
   - Negligible impact compared to benefits
   - Container built once at application startup

5. **Debugging Complexity**: Stack traces include framework code
   - Mitigated by sourcemaps and clear error messages
   - Benefits of clean architecture outweigh minor debugging complexity

## Alternatives Considered

### 1. NestJS Framework
**Pros**:
- Full-featured framework with built-in DI
- Excellent TypeScript support
- Large ecosystem and community

**Cons**:
- Too opinionated for our existing Express setup
- Would require complete rewrite of existing code
- Heavier framework than needed
- Lock-in to NestJS patterns

**Why Rejected**: Too much migration effort for existing Express codebase. Inversify provides DI without requiring framework migration.

### 2. Awilix
**Pros**:
- Simpler API than Inversify
- Good TypeScript support
- Smaller bundle size

**Cons**:
- Less mature ecosystem
- Fewer features (no request scoping)
- String-based identifiers less type-safe
- Less active maintenance

**Why Rejected**: Inversify's symbol-based identifiers and mature feature set provide better long-term stability and type safety.

### 3. Manual Dependency Injection
**Pros**:
- No framework dependency
- Full control over injection
- Zero learning curve

**Cons**:
- Requires manual wiring in every service
- No standardized lifecycle management
- Testing requires manual mock setup
- Prone to circular dependency issues

**Why Rejected**: Doesn't scale well as codebase grows. Manual DI becomes maintenance burden and source of bugs.

### 4. TSyringe (Microsoft)
**Pros**:
- Lightweight and simple
- Microsoft backing
- Good TypeScript integration

**Cons**:
- Less feature-rich than Inversify
- Smaller community
- Limited lifecycle management options
- Less documentation

**Why Rejected**: Inversify's maturity and feature completeness better suited for complex application needs.

## Implementation Notes

**Container Organization**:
```
services/
├── container.ts           # Main container setup
├── types.ts              # Symbol definitions
└── modules/
    ├── payment.module.ts  # Payment service bindings
    ├── user.module.ts     # User service bindings
    └── cache.module.ts    # Cache service bindings
```

**Testing Pattern**:
```typescript
describe('PaymentService', () => {
  let container: Container;
  let mockLightning: jest.Mocked<ILightningService>;

  beforeEach(() => {
    container = new Container();
    mockLightning = createMockLightningService();

    container.bind(TYPES.LightningService).toConstantValue(mockLightning);
    container.bind(TYPES.PaymentService).to(PaymentService);
  });

  it('should create invoice', async () => {
    const service = container.get<IPaymentService>(TYPES.PaymentService);
    await service.createInvoice(1000);
    expect(mockLightning.createInvoice).toHaveBeenCalled();
  });
});
```

## Related Documentation

- [Inversify Documentation](https://inversify.io/)
- [Backend Developer Guide](/docs/development/backend-developer-guide.md) - Section on DI patterns
- [Service Architecture Diagram](/docs/architecture/diagrams/epic-005-service-architecture.mmd)
- [Testing Guide](/docs/development/testing-guide.md) - DI testing patterns

## Revision History

- **2025-10-27**: Initial decision documented for Epic 005
