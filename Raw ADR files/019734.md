# ADR-005: Entity Immutability

## Status
Accepted

## Context

Entities wrap database records and are returned from repository/service methods. Without immutability constraints, several problems arise:

**Unintended Mutations:**
```javascript
const account = await accountService.getById(123);
account.balance = 9999;  // Accidental mutation
// Balance changed in memory but not in database
// Inconsistent state
```

**Hidden Side Effects:**
```javascript
function processOrder(order) {
  order.status = 'completed';  // Mutates caller's object
  // Caller doesn't expect their object to change
}
```

**Testing Challenges:**
```javascript
const user = await userService.getById(1);
someFunction(user);
// Did someFunction mutate user? Can't tell without inspecting internals
```

**Debugging Difficulty:**
```javascript
// Which function changed account.balance?
const account = await accountService.getById(123);
doSomething(account);
doSomethingElse(account);
doAnotherThing(account);
// Balance changed somewhere, but where?
```

**Requirements:**
- Prevent accidental mutations of entity data
- Make data flow explicit and traceable
- Ensure entity state matches database state
- Enable confident parallel operations
- Simplify debugging and testing

## Decision

Freeze all entity instances after construction, making them immutable.

### Implementation

Entities are frozen via `Object.freeze()` in constructor:

```javascript
// src/common/BaseEntity.js
class BaseEntity {
  constructor(data = {}, entityOptions = {}) {
    // ... filter hidden fields, assign data ...
    Object.assign(this, filteredData);
    Object.freeze(this);  // Make immutable
  }
}
```

### Update Pattern

Updates require explicit cloning:

```javascript
// Create new instance with updated values
const updated = entity.cloneWith({ balance: 100 });

// Original entity unchanged
console.log(entity.balance);   // 0
console.log(updated.balance);  // 100
```

### Service Layer Pattern

Services convert entities to plain objects before database updates:

```javascript
// src/common/BaseService.js
async update(id, data, { trx } = {}) {
  // Convert entity to POJO if needed
  const plainData = this.isEntity(data) ? data.toJSON() : data;
  return await this.repository.update(id, plainData, { trx });
}
```

This allows:
```javascript
const account = await accountService.getById(123);
const updated = account.cloneWith({ balance: 100 });
await accountService.update(123, updated);  // Accepts entity or POJO
```

## Consequences

### Positive

**No Unintended Mutations:**
```javascript
const account = await accountService.getById(123);
account.balance = 9999;  // TypeError: Cannot assign to read only property
```
Bugs from accidental mutations eliminated at runtime.

**Explicit Data Flow:**
```javascript
// Clear that new instance created
const updated = account.cloneWith({ status: 'active' });
await accountService.update(account.id, updated);
```
Intent explicit in code, easier to reason about.

**Deterministic Testing:**
```javascript
const account = new AccountEntity({ balance: 100 });
processOrder(account);
expect(account.balance).toBe(100);  // Always true, no hidden mutations
```
Tests more reliable, no need to deep clone test data.

**Safe Concurrent Operations:**
```javascript
const account = await accountService.getById(123);
await Promise.all([
  operation1(account),
  operation2(account),
  operation3(account)
]);
// No race conditions from mutations
```

**Simplified Debugging:**
```javascript
// Entity state can't change after creation
const user = await userService.getById(1);
// user.email is same value throughout function
// No need to suspect it changed
```

**State Consistency:**
```javascript
const account = await accountService.getById(123);
// account.balance matches database value
// Can't drift out of sync with DB
```

### Negative

**Performance Overhead:**
```javascript
// Each update creates new object
let account = await accountService.getById(123);
account = account.cloneWith({ balance: 100 });  // Allocates new object
account = account.cloneWith({ status: 'active' });  // Allocates another
```

**Mitigation:**
- Negligible for typical web API workloads (< 1ms per allocation)
- Object pooling possible if needed (not implemented)
- Update operations batch multiple changes: `cloneWith({ balance: 100, status: 'active' })`

**Learning Curve:**
```javascript
// Developers must learn immutable pattern
const account = await accountService.getById(123);
// This doesn't work:
account.balance = 100;
// Must use this instead:
const updated = account.cloneWith({ balance: 100 });
```

**Mitigation:**
- Clear error messages guide developers
- Pattern documented in ARCHITECTURE.md
- Consistent across all entities (only one pattern to learn)

**Deep Updates More Verbose:**
```javascript
// Updating nested object requires reconstruction
const user = await userService.getById(1);
const updatedAddress = { ...user.address, city: 'Richmond' };
const updated = user.cloneWith({ address: updatedAddress });
```

**Mitigation:**
- Entities rarely have deeply nested structures
- Most updates are flat field changes
- Helper methods can simplify common patterns if needed

## Alternatives Considered

### Mutable Entities
**Approach:** Allow direct property assignment, track changes separately.

```javascript
const account = await accountService.getById(123);
account.balance = 100;
await accountService.update(account.id, account);
```

**Rejected Because:**
- No protection against accidental mutations
- Unclear whether entity has unsaved changes
- Testing harder (must clone objects)
- State can drift from database

### Copy-on-Write with Change Tracking
**Approach:** Track which fields changed, only save those.

```javascript
const account = await accountService.getById(123);
account.balance = 100;  // Records change
await account.save();    // Saves only changed fields
```

**Rejected Because:**
- Complex change tracking logic
- Entities coupled to persistence layer
- Unclear when changes applied
- Violates Entity-Repository separation

### Proxy-Based Immutability
**Approach:** Use ES6 Proxy to intercept mutations.

```javascript
const account = new Proxy(data, {
  set() { throw new Error('Immutable'); }
});
```

**Rejected Because:**
- Performance overhead (proxy trap on every access)
- Complicated debugging (harder to inspect)
- Less browser/runtime compatibility
- `Object.freeze()` achieves same goal more simply

### Immutable.js Library
**Approach:** Use Immutable.js data structures.

```javascript
const account = Immutable.Map({ balance: 100 });
const updated = account.set('balance', 200);
```

**Rejected Because:**
- Additional dependency
- Different API from plain objects
- Harder to serialize to JSON
- More learning curve for developers
- `Object.freeze()` sufficient for current needs

## Implementation Notes

### Deep Freeze

Repositories use deep freeze for nested objects:

```javascript
// src/common/BaseRepository.js
const deepFreeze = (value, seen = new WeakSet()) => {
  if (value == null || typeof value !== 'object' || seen.has(value)) {
    return value;
  }
  seen.add(value);
  Object.getOwnPropertyNames(value).forEach((key) => {
    const v = value[key];
    if (v && typeof v === 'object') deepFreeze(v, seen);
  });
  return Object.freeze(value);
};
```

This prevents mutations at any depth:
```javascript
const user = await userService.getById(1);
user.address.city = 'Richmond';  // TypeError
```

### Relations Materialized as Immutable

Related entities are also frozen:

```javascript
const account = await accountService.getOneWithRelations(
  { id: 123 },
  'user',
  { trx }
);

// Both frozen
account.user.email = 'new@example.com';  // TypeError
account.balance = 100;                   // TypeError
```

### Clone Implementation

```javascript
// src/common/BaseEntity.js
cloneWith(updates = {}) {
  return new this.constructor({ ...this, ...updates });
}
```

Spreads current properties, applies updates, creates new instance.

### Serialization

Frozen objects serialize normally:

```javascript
const account = new AccountEntity({ balance: 100 });
JSON.stringify(account);  // Works fine
// { "balance": 100 }
```

`toJSON()` method handles serialization:

```javascript
toJSON() {
  const json = {};
  for (const key of Object.getOwnPropertyNames(this)) {
    if (key === 'hiddenFields' || key === 'constructor') continue;
    json[key] = this[key];
  }
  return json;
}
```

## Related Decisions

- [ADR-001: Service-Oriented Architecture](./ADR-001-service-oriented-architecture.md) - Entity layer design
- [ADR-004: Contract-Based Testing](./ADR-004-contract-based-testing.md) - Tests validate immutability

## References

- Base entity implementation: `src/common/BaseEntity.js`
- Deep freeze implementation: `src/common/BaseRepository.js`
- Service normalization: `src/common/BaseService.js#toPlain()`

---

**Date:** 2025-10-17
**Author:** Scott Lewis
