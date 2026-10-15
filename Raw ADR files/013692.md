# ADR-0001: Event Bus for Inter-MFE Communication

**Status:** Accepted  
**Date:** 2026-01-XX  
**Deciders:** Architecture Team  
**Context:** POC-2

---

## Context

POC-2 requires decoupled inter-MFE communication. In POC-1, we used shared Zustand stores which created coupling between MFEs. Requirements:
- Decouple MFEs (no shared state dependencies)
- Loose coupling (MFEs don't need to know about each other)
- Scalable (easy to add/remove MFEs)
- Production-ready pattern
- Event-based communication

## Decision

Use custom event bus for inter-MFE communication in POC-2. Remove shared Zustand stores and use Zustand only for MFE-local state.

## Alternatives Considered

### Option 1: Shared Zustand Stores (POC-1)

- **Pros:**
  - Simple implementation
  - Works immediately
  - No additional infrastructure
- **Cons:**
  - Creates coupling between MFEs
  - MFEs must know about shared stores
  - Harder to test MFEs in isolation
  - Not scalable
- **Why Not:** Creates coupling between MFEs. Not ideal for production at scale. We used this in POC-1 but need to migrate for POC-2.

### Option 2: Context API

- **Pros:**
  - Built into React
  - No dependencies
  - Good for React components
- **Cons:**
  - Doesn't work across MFEs (MFEs are independent)
  - Requires provider wrapping
  - Not scalable
- **Why Not:** Doesn't work for microfrontends. MFEs are independent and can't share React context directly.

### Option 3: Custom Event Bus (Chosen)

- **Pros:**
  - Decouples MFEs (no shared state dependencies)
  - Loose coupling (MFEs don't need to know about each other)
  - Scalable (easy to add/remove MFEs)
  - Production-ready pattern (industry standard for microfrontends)
  - Simple implementation
  - Easy to test
- **Cons:**
  - Need to implement event bus
  - More setup than shared stores
- **Why Chosen:** Best solution for decoupled inter-MFE communication. Provides all required features with excellent scalability.

## Trade-offs

- **Pros:**
  - Decouples MFEs
  - Scalable architecture
  - Production-ready pattern
  - Easy to test
- **Cons:**
  - Need to implement event bus
  - More setup than shared stores
- **Risks:**
  - Low risk - Event bus is a well-established pattern
  - Need to ensure proper event typing and documentation

## Consequences

- **Positive:**
  - Decoupled MFEs
  - Scalable architecture
  - Easy to add/remove MFEs
  - Better testability
- **Negative:**
  - Need to implement event bus
  - Migration from shared stores required
- **Neutral:**
  - Can enhance event bus later (e.g., persistence, replay)

## Migration from POC-1

1. Implement event bus library
2. Migrate authentication state to event bus
3. Remove shared Zustand stores
4. Use Zustand only for MFE-local state
5. Update all MFEs to use event bus

## Related Decisions

- `docs/mfe-poc2-architecture.md` - Section 4.3 Event Bus
- `docs/mfe-poc2-tech-stack.md` - Event Bus details
- `docs/state-management-evolution.md` - Evolution from POC-1 to POC-2
- ADR-0005 (POC-1): Shared Zustand Stores in POC-1

---

**Last Updated:** 2026-01-XX

