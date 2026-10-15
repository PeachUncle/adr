# ADR-003: Shared Contracts Package Strategy

**Status:** ✅ Accepted  
**Date:** 2025-12-14  
**Deciders:** Platform Architecture Team, All Team Leads  
**Technical Story:** Type safety and API contracts across MFE boundaries

## Context

With microfrontend architecture (ADR-001) and Module Federation (ADR-002), MFEs can be deployed independently. However, this independence creates challenges:

### Problems Without Contracts

1. **Breaking Changes**: Products MFE changes event payload structure → Cart MFE breaks
2. **No Type Safety**: Shell imports remote component but TypeScript can't verify props
3. **Discovery**: Developers don't know what events are available or what they expect
4. **Version Compatibility**: No way to know if MFEs are compatible with each other
5. **Runtime Errors**: Issues only discovered in production when MFEs interact

### Real Example
```typescript
// Products MFE publishes event
eventBus.publish('cart:add', { id: '123', qty: 1 });

// Cart MFE expects different structure (BREAKS!)
eventBus.subscribe('cart:add', (data) => {
  const { productId, quantity } = data; // ❌ undefined!
});
```

### Requirements

- **Type Safety**: Compile-time checks for event payloads, component props, API responses
- **Single Source of Truth**: One place to define contracts
- **Versioning**: Manage breaking changes gracefully
- **Discoverability**: Developers can easily find available contracts
- **IDE Support**: Autocomplete, inline docs, go-to-definition
- **Minimal Overhead**: Shouldn't slow down development

## Decision

We will create a shared **`@shopping-app/mfe-contracts`** NPM package containing TypeScript contracts for:

1. **Domain Models**: Product, Cart, User, Order, etc.
2. **Event Contracts**: All event names and payload types
3. **Component Props**: Contracts for federated components
4. **API Responses**: Backend API types
5. **Configuration**: Shared config types

### Package Structure

```
packages/mfe-contracts/
├── src/
│   ├── events/           # Event contracts
│   │   ├── cart.events.ts
│   │   ├── wishlist.events.ts
│   │   ├── search.events.ts
│   │   └── index.ts
│   ├── models/           # Domain models
│   │   ├── product.model.ts
│   │   ├── cart.model.ts
│   │   ├── user.model.ts
│   │   └── index.ts
│   ├── components/       # Component prop contracts
│   │   ├── product-grid.contract.ts
│   │   ├── cart-widget.contract.ts
│   │   └── index.ts
│   ├── config/          # Configuration types
│   │   ├── mfe-config.ts
│   │   └── index.ts
│   ├── analytics/       # Analytics events
│   │   └── analytics.types.ts
│   ├── health/          # Health check contracts
│   │   └── health.types.ts
│   ├── a11y/            # Accessibility contracts
│   │   └── a11y.types.ts
│   └── index.ts         # Main entry point
├── package.json
├── tsconfig.json
└── README.md
```

### Contract Examples

```typescript
// models/product.model.ts
export interface Product {
  id: string;
  name: string;
  price: number;
  currency: string;
  imageUrl: string;
  description: string;
  inStock: boolean;
  rating?: number;
}

// events/cart.events.ts
export interface CartAddEvent {
  productId: string;
  quantity: number;
  timestamp: number;
}

export interface CartRemoveEvent {
  productId: string;
  timestamp: number;
}

export type CartEvents = {
  'cart:add': CartAddEvent;
  'cart:remove': CartRemoveEvent;
  'cart:clear': {};
};

// components/product-grid.contract.ts
export interface ProductGridProps {
  products: Product[];
  onProductClick: (productId: string) => void;
  loading?: boolean;
  columns?: 2 | 3 | 4;
}
```

### Usage in MFEs

```typescript
// Products MFE - Publishing event
import { CartAddEvent } from '@shopping-app/mfe-contracts';

const handleAddToCart = (product: Product) => {
  const payload: CartAddEvent = {
    productId: product.id,
    quantity: 1,
    timestamp: Date.now(),
  };
  eventBus.publish('cart:add', payload); // ✅ Type-safe!
};

// Cart MFE - Subscribing to event
import { CartAddEvent } from '@shopping-app/mfe-contracts';

eventBus.subscribe<CartAddEvent>('cart:add', (payload) => {
  // payload is fully typed ✅
  const { productId, quantity } = payload;
});
```

### Versioning Strategy

We'll use **Semantic Versioning (semver)**:

- **MAJOR**: Breaking changes (e.g., remove field, change type)
- **MINOR**: New features (e.g., add optional field, new event)
- **PATCH**: Bug fixes, docs (e.g., fix typo in JSDoc)

```json
{
  "name": "@shopping-app/mfe-contracts",
  "version": "1.2.0",
  "description": "Shared contracts for Shopping App MFEs"
}
```

All MFEs specify compatible version range:
```json
{
  "dependencies": {
    "@shopping-app/mfe-contracts": "^1.2.0"
  }
}
```

## Consequences

### Positive ✅

- **Type Safety**: Compile-time errors instead of runtime failures
- **Self-Documenting**: Types serve as API documentation
- **IDE Support**: Autocomplete, inline docs, refactoring support
- **Breaking Change Detection**: TypeScript errors when contracts change
- **Centralized**: One place to find all contracts
- **Versioning**: Can manage compatibility explicitly
- **Faster Development**: Less time debugging integration issues
- **Better Onboarding**: New developers see all available APIs

### Negative ❌

- **Extra Dependency**: All MFEs depend on contracts package
- **Version Coordination**: Must keep contracts version in sync
- **Two-Step Updates**: Change contracts → then update MFE
- **Build Overhead**: Contracts must build before MFEs
- **Breaking Changes Cascade**: Breaking change affects all consumers
- **Monorepo Benefit Reduced**: Less useful outside monorepo context

### Neutral ⚖️

- **Publishing**: Need process to publish contracts to NPM registry
- **Local Development**: Use npm link or workspace for local dev
- **Documentation**: Contracts are code but still need usage examples

## Alternatives Considered

### 1. No Contracts (Runtime Only)
**Rejected because:**
- Too many runtime errors in production
- No IDE support
- Hard to discover available APIs
- Breaking changes go unnoticed until runtime

### 2. Contracts in Each MFE
**Rejected because:**
- Duplication across MFEs
- No single source of truth
- Versions drift apart
- Still no cross-MFE type safety

### 3. Contracts Generated from OpenAPI
**Considered but not chosen:**
- Good for backend APIs
- Doesn't solve frontend event contracts
- More complex toolchain
- Could revisit for API types specifically

### 4. GraphQL Schema as Contracts
**Rejected because:**
- We don't use GraphQL
- Overkill for our needs
- Doesn't cover component props or events

### 5. Contract Testing Tools (Pact)
**Complementary, not alternative:**
- Pact is for testing contracts are met
- Doesn't replace TypeScript contracts
- Could use alongside for runtime validation

## Implementation Notes

### Package Setup

```json
// packages/mfe-contracts/package.json
{
  "name": "@shopping-app/mfe-contracts",
  "version": "1.2.0",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "files": ["dist"],
  "scripts": {
    "build": "tsc",
    "dev": "tsc --watch",
    "test": "jest",
    "lint": "eslint src/"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "@types/node": "^20.0.0"
  }
}
```

### TypeScript Configuration

```json
// packages/mfe-contracts/tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "declaration": true,
    "outDir": "./dist",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

### Development Workflow

1. **Make Change**: Edit contract in `packages/mfe-contracts`
2. **Update Version**: Bump version in package.json (following semver)
3. **Build**: Run `npm run build`
4. **Update CHANGELOG**: Document the change
5. **Publish**: `npm publish` (or CI/CD handles it)
6. **Update MFEs**: Update contracts version in MFE package.json
7. **Fix Type Errors**: Update MFE code to match new contracts

### Local Development (Monorepo)

Using npm workspaces:
```json
// Root package.json
{
  "workspaces": [
    "packages/*",
    "apps/*"
  ]
}
```

MFEs automatically get latest local contracts version.

### Change Process

#### Non-Breaking Change (Minor/Patch)
```typescript
// ✅ Add optional field
export interface Product {
  id: string;
  name: string;
  price: number;
  newField?: string; // OK: Optional
}

// ✅ Add new event
export type CartEvents = {
  'cart:add': CartAddEvent;
  'cart:updated': CartUpdatedEvent; // OK: New event
};
```

#### Breaking Change (Major)
```typescript
// ❌ Remove required field
export interface Product {
  id: string;
  name: string;
  // price: number; // BREAKING: Field removed
}

// ❌ Change type
export interface Product {
  id: string;
  name: string;
  price: string; // BREAKING: Was number
}
```

For breaking changes:
1. Version bump: 1.2.0 → 2.0.0
2. Migration guide in CHANGELOG
3. Coordinate deployment (might need backward compatibility)

### Validation at Runtime

While TypeScript provides compile-time safety, we also validate at runtime for robustness:

```typescript
import { Product } from '@shopping-app/mfe-contracts';
import { z } from 'zod';

// Zod schema matching TypeScript type
const ProductSchema = z.object({
  id: z.string(),
  name: z.string(),
  price: z.number().positive(),
  currency: z.string(),
  imageUrl: z.string().url(),
  description: z.string(),
  inStock: z.boolean(),
  rating: z.number().min(0).max(5).optional(),
});

// Runtime validation
export function validateProduct(data: unknown): Product {
  return ProductSchema.parse(data);
}
```

## Documentation Standards

Every contract includes:

```typescript
/**
 * Represents a product in the catalog.
 * 
 * @example
 * ```typescript
 * const product: Product = {
 *   id: 'prod-123',
 *   name: 'Laptop',
 *   price: 999.99,
 *   currency: 'USD',
 *   imageUrl: 'https://...',
 *   description: 'High-performance laptop',
 *   inStock: true,
 *   rating: 4.5,
 * };
 * ```
 */
export interface Product {
  /** Unique product identifier */
  id: string;
  /** Display name of the product */
  name: string;
  // ... etc
}
```

## Migration Guide

### v1.0.0 → v1.1.0 (Current)
**Non-breaking**: Added analytics, health check, and a11y contracts

```bash
# Update dependency
npm install @shopping-app/mfe-contracts@^1.1.0
```

No code changes required. New features available:
- Analytics tracking types
- Health check utilities
- Accessibility helpers

### v1.1.0 → v1.2.0 (Current)
**Non-breaking**: Added shared UI components and validators

```bash
npm install @shopping-app/mfe-contracts@^1.2.0
```

New features:
- Validation utilities
- Error reporting helpers
- Extended analytics

## Monitoring

### Contract Usage Metrics
- Number of MFEs using contracts: 6/6
- Contract version distribution across MFEs
- Breaking change impact (how many MFEs need updates)

### Build Metrics
- Contracts build time: ~10s
- Type checking time per MFE: ~15s
- Total compilation time saved (vs. no types): N/A (immeasurable)

## References

- [TypeScript Handbook - Declaration Files](https://www.typescriptlang.org/docs/handbook/declaration-files/introduction.html)
- [Semantic Versioning](https://semver.org/)
- [NPM Package Best Practices](https://docs.npmjs.com/packages-and-modules/contributing-packages-to-the-registry)
- [Consumer-Driven Contract Testing](https://martinfowler.com/articles/consumerDrivenContracts.html)

## Related ADRs

- [ADR-001: Adopting Microfrontend Architecture](001-microfrontend-architecture.md) - Why we need contracts
- [ADR-004: Event-Driven MFE Communication](004-event-driven-communication.md) - Event contracts usage
- [ADR-010: Testing Strategy for MFEs](010-testing-strategy.md) - Contract testing
