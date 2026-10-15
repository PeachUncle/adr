# 1. Card-Based Architecture

Date: 2025-12-29  
Status: Accepted  
Deciders: Core Team

## Context

Traditional web applications are organized around pages and routes, with navigation as the primary interaction model. However, our application deals with semantic entities that:

- Have persistent identity across sessions
- Can exist without being rendered
- Need introspectable state and failure modes
- Require programmatic activation beyond user clicks

Pages are UI constructs; we needed a more fundamental abstraction that could represent both UI and headless entities.

## Decision

We adopt a **card-based architecture** where:

1. **Cards are the fundamental unit** — Not pages, not components, but semantic entities
2. **Exactly one card is active at a time** — Single locus of computation
3. **Cards implement ZetaCardContract** — Standard interface for identity, state, activation, and introspection
4. **UI components are views over card state** — Separation of model and view
5. **Cards can be headless** — No requirement to render (pure operators allowed)

**Core Principle:** "The system maintains semantic cards; views are projections."

## Consequences

### Positive

- **Semantic Clarity** — Cards have clear identity and purpose beyond UI
- **State Ownership** — Cards own their state; views are stateless projections
- **Testability** — Cards can be tested without mounting React components
- **Introspection** — Cards declare failure modes and dependencies explicitly
- **Composition** — Cards can reference and activate other cards
- **Headless Operation** — Background processes are first-class entities

### Negative

- **Learning Curve** — Developers must understand cards vs. pages distinction
- **Boilerplate** — Each card requires implementing the full contract
- **Registry Management** — All cards must be registered for discoverability
- **Migration Cost** — Existing page-based code requires restructuring

### Neutral

- **React Still Used** — For views, but not the architectural foundation
- **Routing Still Exists** — But as a reflection of card state (see ADR-002)
- **Component Libraries Compatible** — Can use existing React patterns for views

## Related Decisions

- [ADR-002: Routing as Projection](002-routing-as-projection.md)
- [ADR-004: Contract-First Card Design](004-contract-first-card-design.md)

## Implementation References

- `src/cardContract.ts` — ZetaCardContract interface
- `src/cardRegistry.ts` — Card registration and discovery
- `src/zetacard.ts` — Reference implementation
- `README.md` — Card Contract section

## Examples

```typescript
// Card (semantic entity)
export class SpectralHeartbeatCard implements ZetaCardContract<CardState> {
  readonly id = "ζ.card.spectral.heartbeat";
  readonly meta = { /* ... */ };
  
  private state: CardState;
  
  getState(): CardState { return {...this.state}; }
  activate(ctx?: CardActivationContext): void { /* ... */ }
  getFailures(): CardFailure[] { /* ... */ }
}

// View (projection over card state)
function SpectralHeartbeatView({ card }: { card: SpectralHeartbeatCard }) {
  const state = card.getState();
  return <div>{/* Render state */}</div>;
}
```

## Alternatives Considered

1. **Page-Based Architecture**
   - Rejected: Couples semantic entities to navigation
   - Pages don't have identity independent of URLs
   - Can't model headless entities

2. **Component-Based Architecture**
   - Rejected: Components are UI constructs
   - State ownership unclear (props vs. context vs. hooks)
   - Hard to test without rendering

3. **MVC/MVVM Patterns**
   - Considered but adapted: Cards are models, views are React components
   - Added: Explicit contracts and failure mode introspection

## Validation

Success criteria:
- ✅ Cards can be activated programmatically
- ✅ Cards can exist without rendering
- ✅ Card state is testable without UI
- ✅ Omnibox can discover and invoke cards
- ✅ Multiple cards can compose and reference each other

## Notes

The card metaphor was chosen over "entity" or "agent" to emphasize:
- Cards are flat, discrete, and stackable (not nested hierarchies)
- Cards are tangible and manipulable (not abstract concepts)
- "Zetacard" as the project name reinforces this central abstraction

The concept draws inspiration from:
- HyperCard (Apple, 1987) — Cards as semantic units
- Semantic Web — RDF resources with stable identities
- Actor Model — Entities with behavior and state
- Unix Philosophy — Small, composable, introspectable units
