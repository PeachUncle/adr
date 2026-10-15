# 4. Contract-First Card Design

Date: 2025-12-29  
Status: Accepted  
Deciders: Core Team

## Context

With card-based architecture (ADR-001), we need a way to ensure consistency across all cards. Questions arose:

- How do we ensure all cards have stable identity?
- How do we make cards introspectable?
- How do we test card implementations?
- How do we prevent cards from violating system invariants?

Without a formal contract, each card would be implemented differently, making integration and maintenance difficult.

## Decision

**All cards must implement `ZetaCardContract<State>`, a minimal interface defining:**

1. **Identity** — `id` and `meta` (title, description, tags)
2. **State Management** — `getState()` and `setState(next)`
3. **Activation** — `activate(ctx?)` method
4. **Introspection** — Optional `getFailures()` for observable failure states
5. **Semantic Payload** — Optional `zeta` array for spectral fingerprints
6. **View Projection** — Optional `View` component

```typescript
export interface ZetaCardContract<State = unknown> {
  readonly id: CardID;
  readonly meta: CardMeta;
  readonly io?: CardIO;
  
  getState(): State;
  setState(next: State): void;
  activate(ctx?: CardActivationContext): void;
  
  readonly zeta?: number[];
  getFailures?(): CardFailure[];
  View?: React.ComponentType<{ card: ZetaCardContract<State> }>;
}
```

**Registry Requirement:** All cards must be registered in `CardRegistry` with:
- Identity and metadata
- Implementation path
- Documented invariants
- Declared failure modes

## Consequences

### Positive

- **Consistency** — All cards follow the same patterns
- **Discoverability** — Cards can be found via registry
- **Testability** — Contract can be validated programmatically
- **Documentation** — Failure modes and invariants are explicit
- **Type Safety** — TypeScript enforces the contract at compile time
- **Interoperability** — Cards can reference and compose each other

### Negative

- **Boilerplate** — Every card needs to implement the full contract
- **Rigidity** — Can't easily add card-specific methods without extending
- **Learning Curve** — New developers must understand the contract
- **Registry Maintenance** — Must keep registry in sync with implementations

### Neutral

- **Contract Evolution** — Can add optional fields without breaking existing cards
- **Testing Requirements** — Contract compliance can be automated
- **Documentation Overhead** — Registry serves as living documentation

## Implementation

### Minimal Card

```typescript
export class MinimalCard implements ZetaCardContract<MinimalState> {
  readonly id = "ζ.card.minimal";
  readonly meta = {
    title: "Minimal Card",
    description: "Smallest valid card implementation",
    tags: ["example"],
  };
  
  private state: MinimalState = { value: 0 };
  
  getState(): MinimalState {
    return { ...this.state };
  }
  
  setState(next: MinimalState): void {
    this.state = { ...next };
  }
  
  activate(ctx?: CardActivationContext): void {
    console.log(`[${this.id}] activated`, ctx);
  }
}
```

### Contract Validation

```typescript
export function validateCardContract(card: ZetaCardContract): CardFailure[] {
  const failures: CardFailure[] = [];
  
  if (!card.id || typeof card.id !== "string") {
    failures.push(CardFailureRegistry.MISSING_ID);
  }
  
  if (typeof card.activate !== "function") {
    failures.push({
      code: "missing_activate",
      message: "Card must implement activate() method",
    });
  }
  
  // ... more checks
  
  return failures;
}
```

### Registry Entry

```typescript
export const CardRegistry: Record<CardID, CardRegistryEntry> = {
  "ζ.card.minimal": {
    id: "ζ.card.minimal",
    meta: { /* ... */ },
    implementationPath: "src/cards/minimalCard.ts",
    invariants: [
      "State is immutable: getState() returns a copy",
      "Activation is idempotent: can be called multiple times",
    ],
    failureModes: [], // No failure modes for minimal card
  },
};
```

## Related Decisions

- [ADR-001: Card-Based Architecture](001-card-based-architecture.md)
- [ADR-002: Routing as Projection](002-routing-as-projection.md)
- [ADR-005: Gradient Invariant Principle](005-gradient-invariant-principle.md)

## Implementation References

- `src/cardContract.ts` — ZetaCardContract interface and validation
- `src/cardRegistry.ts` — Card registration and metadata
- `src/zetacard.ts` — Reference implementation
- `src/cards/omnicard.ts` — Minimal example
- `CONTRIBUTING.md` — Card implementation guidelines

## Contract Invariants

All cards must satisfy:

1. **Stable Identity** — `id` is globally unique and stable across sessions
2. **Separability** — Card can exist without any React component mounted
3. **Inspectable Semantics** — Card describes what it is, does, depends on, and how it fails
4. **Explicit Activation** — Activation is the ONLY way a card becomes active
5. **State Immutability** — `getState()` returns a copy; `setState()` doesn't mutate

## Failure Mode Registry

Common failure modes cards should check:

```typescript
export const CardFailureRegistry = {
  MISSING_ID: { code: "missing_id", message: "Card has no stable ID" },
  NON_REVERSIBLE_ROUTE: {
    code: "non_reversible_route",
    message: "Router cannot encode/decode ID losslessly",
  },
  VIEW_OWNS_STATE: {
    code: "view_owns_state",
    message: "View mutates state without routing through card model",
  },
  FLAT_SPECTRUM: {
    code: "flat_spectrum",
    message: "Spectral energy too uniform; no dominant modes detected",
  },
  MISSING_INPUT: {
    code: "missing_input",
    message: "Required input dependency not available",
  },
};
```

## Extension: Gradient-Aware Cards

Cards can optionally implement `ZetaGradientCardContract` for field-based dynamics:

```typescript
export interface ZetaGradientCardContract<State> extends ZetaCardContract<State> {
  potentialField(state: State): number;
  gradient(state: State): Vec;
  coercionForce?: CoercionRecord;
  reshapeField?(delta: PotentialModifier): ReshapeResult;
}
```

See [ADR-005: Gradient Invariant Principle](005-gradient-invariant-principle.md).

## Alternatives Considered

1. **Duck Typing (No Contract)**
   - Rejected: No consistency guarantees
   - Testing becomes ad-hoc
   - Discovery is impossible

2. **Abstract Base Class**
   - Rejected: TypeScript interfaces are more flexible
   - Doesn't enforce registration
   - Can't extend from multiple bases

3. **Convention Over Configuration**
   - Rejected: Too implicit
   - Failure modes not discoverable
   - No compile-time safety

## Validation

Success criteria:
- ✅ All cards implement ZetaCardContract
- ✅ Contract validation runs in tests
- ✅ Registry has entry for every card
- ✅ Documentation generated from registry
- ✅ Failure modes are introspectable
- ✅ Cards are type-safe

## Testing Pattern

```typescript
describe("MyCard", () => {
  let card: MyCard;
  
  beforeEach(() => {
    card = new MyCard();
  });
  
  it("satisfies ZetaCardContract", () => {
    const failures = validateCardContract(card);
    expect(failures).toHaveLength(0);
  });
  
  it("is registered in CardRegistry", () => {
    const entry = CardRegistry[card.id];
    expect(entry).toBeDefined();
    expect(entry.implementationPath).toBe("src/cards/myCard.ts");
  });
  
  it("declares failure modes", () => {
    const failures = card.getFailures?.() || [];
    // Check expected failures
  });
});
```

## Notes

The contract is deliberately minimal:
- Optional fields allow specialized cards
- No view requirement (headless cards allowed)
- No storage requirement (in-memory state is valid)
- No network requirement (offline-first)

The philosophy: **"Make illegal states unrepresentable."** The contract enforces semantic correctness at the type level.
