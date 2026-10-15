# ADR-002: Mixin Pattern for Code Reuse

## Status
Accepted

## Context

Services across the system share common capabilities:
- **Caching**: Store frequently accessed data in Redis
- **Observability**: Emit events for audit trails
- **Soft Delete**: Mark records deleted without removing them
- **Activation**: Toggle records active/inactive
- **Pluggable Events**: Emit before/after/failed events for operations

However, not all services need all capabilities. For example:
- `AccountService` needs caching and events, but not soft delete
- `ImageService` needs events and soft delete, but not caching
- `UserService` needs all capabilities

Traditional inheritance creates rigid hierarchies:
```javascript
// Problem: Forces all services to inherit everything
class BaseService { }
class CacheableService extends BaseService { }
class PluggableService extends CacheableService { }  // Now has caching even if not needed
```

This violates the Interface Segregation Principle (clients shouldn't depend on interfaces they don't use).

## Decision

Use mixin functions that wrap base classes, enabling flexible composition of capabilities.

### Implementation

Mixins are functions that take a base class and return an extended class:

```javascript
// src/common/mixins/service/CacheableService.js
const CacheableService = (Base) => class extends Base {
  constructor(args) {
    super(args);
    this.cache = args.cache || { enabled: false };
  }

  async getById(id, { trx } = {}) {
    if (!this.cache.enabled) {
      return super.getById(id, { trx });
    }

    const cacheKey = `${this.entityClass.name}:${id}`;
    const cached = await this.cache.get(cacheKey);
    if (cached) return cached;

    const result = await super.getById(id, { trx });
    await this.cache.set(cacheKey, result, { ttl: this.cache.ttl });
    return result;
  }
};
```

### Composition

Services compose only the capabilities they need:

```javascript
// Service with caching and events
class AccountService extends withPluggableAndCacheable(BaseService) { }

// Service with events only
class ImageService extends withPluggable(BaseService) { }

// Service with soft delete only
class UserService extends withSoftDeletable(BaseService) { }
```

### Helper Functions

Convenience functions combine commonly-used mixins:

```javascript
// src/common/mixins/service/index.js
const withPluggableAndCacheable = (Base) =>
  Pluggable(Cacheable(Base));

const withFullStack = (Base) =>
  Pluggable(Cacheable(SoftDeletable(Activatable(Base))));
```

## Consequences

### Positive

**Flexible Composition:**
- Services include only capabilities they need
- Easy to add new capabilities without affecting existing code
- Clear declaration of service capabilities at class definition

**Code Reuse:**
- Common behavior written once in mixin
- Applied to multiple services via composition
- Changes to mixin propagate to all consumers

**Testing:**
- Runtime capability detection (check if method exists)
- Test contracts conditionally test capabilities
- No need to mock unused capabilities

**Maintainability:**
- Changes to one mixin don't affect unrelated services
- Single Responsibility Principle: each mixin has one purpose
- Clear dependency chain (readable from bottom to top)

**AI-Assisted Development:**
- Clear pattern for adding capabilities
- AI can suggest appropriate mixins based on requirements
- Explicit composition shows service capabilities

### Negative

**Method Resolution Order:**
- Must understand JavaScript prototype chain
- Debugging requires tracing through mixin layers
- Can be confusing for developers unfamiliar with pattern

**Capability Conflicts:**
- Potential for two mixins to override the same method
- Mitigated by: single-purpose mixins, explicit method names
- Example: `Cacheable` wraps methods, `Pluggable` wraps methods differently

**Runtime Detection Required:**
- Cannot statically analyze which methods exist
- Test contracts use `typeof service.method === 'function'`
- TypeScript would require complex type definitions

## Alternatives Considered

### Traditional Inheritance Hierarchy
**Approach:**
```javascript
BaseService
  ├── CacheableService
  │     └── PluggableService
  └── SoftDeletableService
```

**Rejected Because:**
- Forces services to inherit capabilities they don't need
- Creates "God Object" if all capabilities in base class
- Inflexible: can't combine CacheableService + SoftDeletableService without multiple inheritance

### Composition via Properties
**Approach:**
```javascript
class AccountService {
  constructor() {
    this.cache = new CacheManager();
    this.events = new EventManager();
  }
}
```

**Rejected Because:**
- Boilerplate in every service constructor
- Methods like `getById()` need manual integration
- No polymorphism benefits
- Harder to maintain consistent behavior

### Decorator Pattern (Object Composition)
**Approach:**
```javascript
const service = new AccountService();
const cachedService = new CacheDecorator(service);
const observableService = new ObservableDecorator(cachedService);
```

**Rejected Because:**
- Verbose setup for each service instance
- Type inference breaks (returns decorated wrapper, not service)
- Harder to test (multiple layers to mock)

## Implementation Notes

### Available Mixins

**Service Layer:**
- `Pluggable` - Emits before/after/failed events around operations
- `Cacheable` - Redis caching with configurable TTL
- `SoftDeletable` - `softDelete()` marks `is_deleted = true`
- `Activatable` - `activate()`, `deactivate()`, `toggleActive()`
- `Observable` - Lifecycle event emission for observability

**Repository Layer:**
- Currently none, but pattern supports repository mixins if needed

**Entity Layer:**
- Entities use factory pattern, not mixins (different design constraint)

### Mixin Location
```
src/common/mixins/
  ├── service/
  │   ├── PluggableService.js
  │   ├── CacheableService.js
  │   ├── SoftDeletableService.js
  │   ├── ActivatableService.js
  │   ├── ObservableService.js
  │   └── index.js              # Convenience exports
  └── repository/               # Future repository mixins
```

### Capability Detection in Tests

Tests detect capabilities at runtime:

```javascript
const service = initAccountService();
const supports = {
  cache: typeof service.clearCache === 'function',
  softDelete: typeof service.softDelete === 'function',
  activate: typeof service.activate === 'function',
};

if (supports.softDelete) {
  test('soft delete marks record deleted', async () => { ... });
}
```

This ensures tests only run for implemented capabilities, avoiding false failures.

## Related Decisions

- [ADR-001: Service-Oriented Architecture](./ADR-001-service-oriented-architecture.md) - Base service pattern
- [ADR-003: Event-Driven Architecture](./ADR-003-event-driven-architecture.md) - Uses PluggableService mixin
- [ADR-004: Contract-Based Testing](./ADR-004-contract-based-testing.md) - Tests mixin capabilities

## References

- Mixin implementation: `src/common/mixins/service/`
- Example usage: `src/accounts/AccountService.js`
- Test capability detection: `src/__tests__/contracts/service.contract.js`

---

**Date:** 2025-10-17
**Author:** Scott Lewis
