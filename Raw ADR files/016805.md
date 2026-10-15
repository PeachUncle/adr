# ADR-004: Event-Driven MFE Communication

**Status:** ✅ Accepted  
**Date:** 2025-12-14  
**Deciders:** Platform Architecture Team, Frontend Leads  
**Technical Story:** Inter-MFE communication pattern

## Context

Microfrontends need to communicate with each other for coordination:

### Communication Scenarios

1. **Cart Updates**: When product is added, cart badge needs to update
2. **Search Results**: When user searches, products MFE shows filtered results
3. **Authentication**: When user logs in, all MFEs need to know
4. **Navigation**: When user navigates, relevant MFEs activate
5. **State Sync**: When wishlist changes, multiple views update

### Challenges

- **Coupling**: Direct imports between MFEs create tight coupling
- **Deployment Independence**: Changes in one MFE shouldn't require redeploying others
- **Team Autonomy**: Teams should work independently
- **Runtime Composition**: MFEs loaded dynamically at runtime
- **Debugging**: Need visibility into cross-MFE interactions

### Anti-Pattern Example

```typescript
// ❌ BAD: Direct dependency
import { CartStore } from 'mfe-cart/store'; // Creates coupling!

function ProductCard() {
  const handleClick = () => {
    CartStore.addItem(product); // Tight coupling to cart internals
  };
}
```

## Decision

We will use an **Event-Driven Architecture** with a type-safe pub/sub pattern for all inter-MFE communication.

### Core Principles

1. **No Direct Imports**: MFEs never import from each other (except contracts)
2. **Publish/Subscribe**: Event emitters publish, subscribers react
3. **Type Safety**: All events defined in contracts package
4. **Loose Coupling**: Publishers don't know about subscribers
5. **Async by Default**: Events processed asynchronously

### Event Bus Implementation

```typescript
// packages/mfe-contracts/src/events/event-bus.ts
import { EventMap } from './event-types';

type EventHandler<T = any> = (payload: T) => void;

class MFEEventBus {
  private handlers: Map<string, Set<EventHandler>> = new Map();
  private eventHistory: Array<{ event: string; payload: any; timestamp: number }> = [];

  /**
   * Subscribe to an event
   */
  subscribe<K extends keyof EventMap>(
    event: K,
    handler: EventHandler<EventMap[K]>
  ): () => void {
    if (!this.handlers.has(event as string)) {
      this.handlers.set(event as string, new Set());
    }
    
    this.handlers.get(event as string)!.add(handler);
    
    // Return unsubscribe function
    return () => {
      this.handlers.get(event as string)?.delete(handler);
    };
  }

  /**
   * Publish an event
   */
  publish<K extends keyof EventMap>(
    event: K,
    payload: EventMap[K]
  ): void {
    // Log for debugging
    this.eventHistory.push({
      event: event as string,
      payload,
      timestamp: Date.now(),
    });
    
    // Keep only last 100 events
    if (this.eventHistory.length > 100) {
      this.eventHistory.shift();
    }
    
    // Call all handlers
    const handlers = this.handlers.get(event as string);
    if (handlers) {
      handlers.forEach((handler) => {
        try {
          handler(payload);
        } catch (error) {
          console.error(`Error in event handler for ${event}:`, error);
        }
      });
    }
  }

  /**
   * Get event history for debugging
   */
  getHistory(): Array<{ event: string; payload: any; timestamp: number }> {
    return [...this.eventHistory];
  }

  /**
   * Clear all handlers (useful for testing)
   */
  clear(): void {
    this.handlers.clear();
    this.eventHistory = [];
  }
}

// Global singleton
export const eventBus = new MFEEventBus();
```

### Event Contracts

```typescript
// packages/mfe-contracts/src/events/event-types.ts
export interface CartAddEvent {
  productId: string;
  quantity: number;
  timestamp: number;
  source: 'products' | 'wishlist' | 'search';
}

export interface CartRemoveEvent {
  productId: string;
  timestamp: number;
}

export interface WishlistToggleEvent {
  productId: string;
  action: 'add' | 'remove';
  timestamp: number;
}

export interface SearchQueryEvent {
  query: string;
  filters?: Record<string, any>;
  timestamp: number;
}

export interface AuthStateChangeEvent {
  isAuthenticated: boolean;
  userId?: string;
  timestamp: number;
}

export interface NavigationEvent {
  path: string;
  params?: Record<string, string>;
  timestamp: number;
}

// Master event map
export interface EventMap {
  // Cart events
  'cart:add': CartAddEvent;
  'cart:remove': CartRemoveEvent;
  'cart:clear': {};
  'cart:updated': { itemCount: number };
  
  // Wishlist events
  'wishlist:toggle': WishlistToggleEvent;
  'wishlist:updated': { itemCount: number };
  
  // Search events
  'search:query': SearchQueryEvent;
  'search:clear': {};
  
  // Auth events
  'auth:login': AuthStateChangeEvent;
  'auth:logout': AuthStateChangeEvent;
  'auth:token-refresh': { token: string };
  
  // Navigation events
  'navigation:change': NavigationEvent;
}
```

### React Hooks

```typescript
// packages/mfe-contracts/src/hooks/useMFEEvent.ts
import { useEffect } from 'react';
import { eventBus, EventMap } from '../events';

/**
 * Subscribe to MFE events
 */
export function useMFEEvent<K extends keyof EventMap>(
  event: K,
  handler: (payload: EventMap[K]) => void,
  deps: any[] = []
) {
  useEffect(() => {
    const unsubscribe = eventBus.subscribe(event, handler);
    return unsubscribe;
  }, [event, ...deps]);
}

/**
 * Publish MFE events
 */
export function useMFEPublish() {
  return <K extends keyof EventMap>(event: K, payload: EventMap[K]) => {
    eventBus.publish(event, payload);
  };
}
```

### Usage Examples

#### Publishing Events

```typescript
// apps/mfe-products/components/ProductCard.tsx
import { useMFEPublish } from '@shopping-app/mfe-contracts';

export function ProductCard({ product }: Props) {
  const publish = useMFEPublish();
  
  const handleAddToCart = () => {
    publish('cart:add', {
      productId: product.id,
      quantity: 1,
      timestamp: Date.now(),
      source: 'products',
    });
  };
  
  return (
    <button onClick={handleAddToCart}>Add to Cart</button>
  );
}
```

#### Subscribing to Events

```typescript
// apps/mfe-cart/components/CartBadge.tsx
import { useMFEEvent } from '@shopping-app/mfe-contracts';
import { useState } from 'react';

export function CartBadge() {
  const [count, setCount] = useState(0);
  
  useMFEEvent('cart:add', (payload) => {
    setCount((prev) => prev + payload.quantity);
  });
  
  useMFEEvent('cart:remove', () => {
    setCount((prev) => Math.max(0, prev - 1));
  });
  
  useMFEEvent('cart:clear', () => {
    setCount(0);
  });
  
  return <span className="badge">{count}</span>;
}
```

#### Complex Event Chain

```typescript
// apps/mfe-search/hooks/useSearchSync.ts
import { useMFEEvent, useMFEPublish } from '@shopping-app/mfe-contracts';

export function useSearchSync() {
  const publish = useMFEPublish();
  
  // Listen to search bar input
  useMFEEvent('search:query', (payload) => {
    // Fetch results...
    const results = await fetchSearchResults(payload.query);
    
    // Publish to products MFE
    publish('products:filter', {
      products: results,
      timestamp: Date.now(),
    });
  });
}
```

## Consequences

### Positive ✅

- **Loose Coupling**: MFEs don't depend on each other's internals
- **Independent Deployment**: Change event handler without redeploying publisher
- **Team Autonomy**: Teams own their event handlers
- **Testability**: Easy to test by publishing mock events
- **Debuggability**: Event history shows what happened
- **Flexibility**: Easy to add new subscribers
- **Type Safety**: Compile-time checks for event payloads
- **Replayability**: Can replay events for debugging

### Negative ❌

- **Indirection**: Harder to trace flow from publisher to subscriber
- **No Return Values**: Can't get response synchronously
- **Event Flooding**: Too many events can hurt performance
- **Debugging**: Need tools to visualize event flow
- **Ordering**: No guaranteed order if multiple subscribers
- **Memory Leaks**: Forgetting to unsubscribe causes leaks

### Neutral ⚖️

- **Learning Curve**: Developers need to understand pub/sub pattern
- **Event Naming**: Need conventions for event names
- **Event Versioning**: Need strategy for changing event structure

## Alternatives Considered

### 1. Direct Function Calls
**Rejected because:**
```typescript
// ❌ Creates tight coupling
import { addToCart } from 'mfe-cart';
addToCart(product);
```
- Tight coupling between MFEs
- Can't deploy independently
- Defeats purpose of microfrontends

### 2. Shared Redux/Zustand Store
**Rejected because:**
```typescript
// ❌ Creates shared state coupling
import { cartStore } from '@shopping-app/shared-state';
cartStore.addItem(product);
```
- Still couples MFEs through shared state
- Harder to version and deploy independently
- Global state is anti-pattern for MFEs

### 3. Browser CustomEvents
**Considered but not chosen:**
```typescript
// Could work but less type-safe
window.dispatchEvent(new CustomEvent('cart:add', { detail: payload }));
```
- Native browser API (no dependencies)
- But: No TypeScript support
- But: Harder to debug
- But: Can't easily replay events
- Could revisit if need cross-origin communication

### 4. Message Channel API
**Rejected because:**
- More complex API
- Overkill for same-origin communication
- No significant benefits over our approach

### 5. Service Workers / Broadcast Channel
**Rejected because:**
- Adds complexity
- Not needed for same-page communication
- Better for cross-tab communication

## Implementation Notes

### Event Naming Convention

```
<domain>:<action>[:detail]

Examples:
- cart:add
- cart:remove
- cart:updated
- wishlist:toggle
- auth:login
- auth:logout
- navigation:change
```

### Error Handling

```typescript
// Global error handler for events
eventBus.subscribe('error', (payload) => {
  console.error('MFE Event Error:', payload);
  // Send to error tracking service
  Sentry.captureException(payload.error, {
    extra: {
      event: payload.event,
      mfe: payload.mfe,
    },
  });
});
```

### Performance Optimization

```typescript
// Debounce high-frequency events
import { debounce } from 'lodash';

const debouncedPublish = debounce((query: string) => {
  publish('search:query', {
    query,
    timestamp: Date.now(),
  });
}, 300);
```

### Testing

```typescript
// test/ProductCard.test.tsx
import { eventBus } from '@shopping-app/mfe-contracts';
import { render, fireEvent } from '@testing-library/react';

test('publishes cart:add event', () => {
  const publishSpy = jest.spyOn(eventBus, 'publish');
  
  const { getByText } = render(<ProductCard product={mockProduct} />);
  fireEvent.click(getByText('Add to Cart'));
  
  expect(publishSpy).toHaveBeenCalledWith('cart:add', {
    productId: mockProduct.id,
    quantity: 1,
    timestamp: expect.any(Number),
    source: 'products',
  });
});
```

### DevTools Integration

```typescript
// Debug panel to visualize events
if (process.env.NODE_ENV === 'development') {
  window.__MFE_EVENT_BUS__ = eventBus;
  
  // Log all events
  Object.keys(EventMap).forEach((event) => {
    eventBus.subscribe(event as any, (payload) => {
      console.log(`[MFE Event] ${event}`, payload);
    });
  });
}
```

## Migration from Direct Calls

### Before (Tightly Coupled)
```typescript
import { CartService } from 'mfe-cart';

function ProductCard() {
  const handleClick = () => {
    CartService.addItem(product);
  };
}
```

### After (Event-Driven)
```typescript
import { useMFEPublish } from '@shopping-app/mfe-contracts';

function ProductCard() {
  const publish = useMFEPublish();
  
  const handleClick = () => {
    publish('cart:add', {
      productId: product.id,
      quantity: 1,
      timestamp: Date.now(),
      source: 'products',
    });
  };
}
```

## Event Flow Diagrams

### Example: Add to Cart Flow

```
User clicks "Add to Cart"
         ↓
ProductCard.onClick()
         ↓
publish('cart:add', {...})
         ↓
    Event Bus
         ↓
    ┌────┴────┐
    ↓         ↓
CartBadge  CartDrawer
updates    updates
count      items list
```

## Monitoring

Track these metrics:
- Event frequency per type
- Handler execution time
- Failed handlers (errors)
- Average subscribers per event
- Event payload size

## References

- [Event-Driven Architecture](https://martinfowler.com/articles/201701-event-driven.html)
- [Publish-Subscribe Pattern](https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern)
- [Observer Pattern](https://refactoring.guru/design-patterns/observer)

## Related ADRs

- [ADR-001: Adopting Microfrontend Architecture](001-microfrontend-architecture.md) - Why loose coupling matters
- [ADR-003: Shared Contracts Package Strategy](003-shared-contracts-package.md) - Event contract types
- [ADR-006: Shared State Management Approach](006-shared-state-management.md) - When NOT to use events
