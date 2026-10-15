# 2. Routing as Projection

Date: 2025-12-29  
Status: Accepted  
Deciders: Core Team

## Context

In traditional web applications, routing is **primary**: URLs define what content is shown, and navigation drives application state. This creates several problems:

1. **State management complexity** — Application state must be derived from URLs
2. **Coupling** — Semantic entities become coupled to URL structure
3. **Activation ambiguity** — Unclear if activation is a navigation event or state change
4. **Bookmarking issues** — URLs may not fully capture semantic state

Since we adopted a card-based architecture (see ADR-001), we needed to decide: Do routes control cards, or do cards control routes?

## Decision

**The URL is a reflection of the active card's ID; navigation is implemented by activating cards.**

Routing is **downstream** of card activation:

```
User Action → Card.activate() → State Change → URL Update
                                               ↓
                                         (Reflection)
```

Not:
```
User Action → URL Change → Route Handler → Card Activation
```

**Core Principle:** "The URL reflects the active card's `id`; navigation is a projection of card state."

### Implementation Rules

1. **Activation is the only way to make a card active** — Call `card.activate(ctx)`, not `navigate(url)`
2. **The router observes card activation** — Updates URL to reflect the active card ID
3. **URL parsing resolves to card ID** — On page load, URL maps to card ID, then activates that card
4. **Cards don't know about URLs** — They only know their own ID
5. **Routing is reversible** — ID → URL → ID must be lossless

## Consequences

### Positive

- **Semantic Clarity** — Activation is a first-class operation, not a navigation side effect
- **Testability** — Cards can be activated in tests without mocking routing
- **Decoupling** — Cards don't depend on URL structure
- **Programmatic Control** — Cards can activate other cards directly
- **State Source of Truth** — Card state is authoritative, not URL state

### Negative

- **Mental Model Shift** — Developers must think "activate card" not "navigate to URL"
- **Router Implementation Complexity** — Must observe card activation and update URL reactively
- **Debugging** — URL changes are effects, not causes, which can be surprising
- **Framework Expectations** — React Router and similar libraries assume URL-first routing

### Neutral

- **Bookmarks Still Work** — URL parsing resolves to card and activates it
- **Back Button Works** — Browser history is updated, just driven by card activation
- **Deep Linking Works** — URLs map to card IDs reliably

## Implementation

### Router Setup (Conceptual)

```typescript
// location.ts - Router observes card activation
export function reflectCardToURL(card: ZetaCardContract) {
  const url = encodeCardID(card.id);
  history.pushState(null, "", url);
}

// On card activation
card.activate = (ctx) => {
  // ... card's activation logic
  reflectCardToURL(card); // Update URL as reflection
};

// On page load
const cardID = decodeURL(window.location.pathname);
const card = CardRegistry[cardID];
if (card) {
  card.activate({ reason: "route_reflection", from: "url" });
}
```

### Activation Context

```typescript
export type CardActivationContext = {
  reason?: "user_selected" | "route_reflection" | "programmatic";
  from?: CardID; // which card initiated activation
  timestamp?: number;
};
```

## Related Decisions

- [ADR-001: Card-Based Architecture](001-card-based-architecture.md) — Why cards are primary
- [ADR-004: Contract-First Card Design](004-contract-first-card-design.md) — Activation is part of the contract

## Implementation References

- `src/location.ts` — Route reflection implementation
- `src/cardContract.ts` — `activate(ctx)` method
- `README.md` — "Unified Navigation Grammar" section

## Alternatives Considered

1. **URL-First Routing (Traditional)**
   - Rejected: Makes cards dependent on routing library
   - URL structure becomes part of card contract
   - Hard to test without mocking router

2. **Dual Control (URL and Card Activation)**
   - Rejected: Creates ambiguity and potential conflicts
   - Which is authoritative?
   - Synchronization bugs

3. **No URLs at All (Pure SPA)**
   - Rejected: Breaks bookmarking and sharing
   - Browser history doesn't work
   - Not web-native

## Validation

Success criteria:
- ✅ Cards can be activated without touching the router
- ✅ URL always reflects the active card ID
- ✅ Bookmarks and deep links work correctly
- ✅ Browser back/forward buttons work
- ✅ Cards can activate other cards programmatically
- ✅ `id → URL → id` round-trip is lossless

## Examples

### Traditional Routing (What We Avoid)

```typescript
// URL-first (traditional)
<Route path="/cards/:id" component={CardView} />

// In CardView component:
function CardView() {
  const { id } = useParams();
  const card = CardRegistry[id];
  // Card is passive; routing drives everything
}
```

### Routing as Projection (Our Approach)

```typescript
// Card-first (our approach)
const card = CardRegistry["ζ.card.spectral.heartbeat"];
card.activate({ reason: "user_selected", from: "ζ.card.omni" });

// Router observes and reflects:
// URL becomes: /ζ.card.spectral.heartbeat

// On page load:
const cardID = decodeURL(location.pathname);
CardRegistry[cardID]?.activate({ reason: "route_reflection" });
```

## Failure Modes

Cards should check for routing reversibility:

```typescript
getFailures(): CardFailure[] {
  const encoded = encodeCardID(this.id);
  const decoded = decodeCardID(encoded);
  
  if (decoded !== this.id) {
    return [{
      code: "non_reversible_route",
      message: "Router cannot encode/decode ID losslessly",
      severity: "error"
    }];
  }
  
  return [];
}
```

## Notes

This inversion (routing as projection) is inspired by:
- **Redux DevTools** — Time-travel debugging shows state, not URL changes
- **Event Sourcing** — URL is a materialized view, not the source of truth
- **Unix Philosophy** — Small tools with clear data flow: card → state → URL

The key insight: **Navigation is a UI concern, activation is a semantic operation.**
