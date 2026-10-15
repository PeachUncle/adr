# ADR-0005: Shared Zustand Stores in POC-1

**Status:** Accepted (Temporary)  
**Date:** 2026-01-XX  
**Deciders:** Architecture Team  
**Context:** POC-1

---

## Context

POC-1 requires inter-MFE communication for authentication state sharing. Requirements:
- Share authentication state between shell and remotes
- Simple implementation (acceptable for POC)
- Production-ready patterns
- Easy to migrate to better solution later

**Note:** This is a temporary solution for POC-1. In POC-2, we'll migrate to event bus for inter-MFE communication to decouple MFEs.

## Decision

Use shared Zustand stores for inter-MFE communication in POC-1. Migrate to event bus in POC-2.

## Alternatives Considered

### Option 1: Event Bus (POC-2)

- **Pros:**
  - Decouples MFEs
  - Loose coupling
  - Scalable
  - Production-ready pattern
- **Cons:**
  - More complex to implement
  - Requires more setup
  - Overkill for POC-1
- **Why Not:** Overkill for POC-1. We'll implement this in POC-2 when we have more MFEs and need better decoupling.

### Option 2: Props Drilling

- **Pros:**
  - Simple
  - No dependencies
  - Explicit data flow
- **Cons:**
  - Doesn't work across MFEs (MFEs are independent)
  - Would require shell to pass props to all remotes
  - Not scalable
- **Why Not:** Doesn't work for microfrontends. MFEs are independent and can't share props directly.

### Option 3: Context API

- **Pros:**
  - Built into React
  - No dependencies
  - Good for React components
- **Cons:**
  - Doesn't work across MFEs (MFEs are independent)
  - Requires provider wrapping
  - Not scalable
- **Why Not:** Doesn't work for microfrontends. MFEs are independent and can't share React context directly.

### Option 4: Shared Zustand Stores (Chosen - Temporary)

- **Pros:**
  - Simple implementation
  - Works across MFEs (shared package)
  - Easy to set up
  - Acceptable for POC-1
  - Easy to migrate to event bus later
- **Cons:**
  - Creates coupling between MFEs
  - Not ideal for long-term
  - Will need to migrate in POC-2
- **Why Chosen:** Simple solution for POC-1. Acceptable coupling for POC phase. Easy to migrate to event bus in POC-2.

## Trade-offs

- **Pros:**
  - Simple implementation
  - Works for POC-1
  - Easy to migrate later
- **Cons:**
  - Creates coupling between MFEs
  - Not ideal for long-term
  - Will need to migrate in POC-2
- **Risks:**
  - Low risk - Acceptable for POC-1
  - Will need to migrate to event bus in POC-2 for decoupling

## Consequences

- **Positive:**
  - Simple implementation for POC-1
  - Works for authentication state sharing
  - Easy to migrate to event bus in POC-2
- **Negative:**
  - Creates coupling between MFEs (acceptable for POC-1)
  - Will need to refactor in POC-2
- **Neutral:**
  - Migration to event bus is planned for POC-2

## Migration Plan (POC-2)

1. Implement event bus
2. Migrate authentication state to event bus
3. Remove shared Zustand stores
4. Use Zustand only for MFE-local state

## Related Decisions

- `docs/mfe-poc1-architecture.md` - Section 4.4 State Management
- `docs/mfe-poc1-tech-stack.md` - Zustand 4.5.x details
- `docs/state-management-evolution.md` - Evolution from POC-1 to POC-2
- ADR-0002: Use Zustand for State Management
- `docs/mfe-poc2-architecture.md` - Event bus implementation (POC-2)

---

**Last Updated:** 2026-01-XX

