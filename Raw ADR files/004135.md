# ADR-004: Attribute Interaction Model

**Status**: Accepted
**Date**: 2025-12-04
**Decision Makers**: Lead Architect, Simulation Engineer
**Supersedes**: N/A

---

## Context

**What is the issue or problem we're addressing?**

In a sports simulation, outcomes are rarely determined by a single variable. Currently, our simulation might compare `WR.speed` vs `CB.speed` to determine if a receiver gets open. However, this is an oversimplification.

Real football interactions are multivariate:

- A WR's release off the line depends on `WR.release` vs `CB.press`.
- _If_ the WR wins the release, _then_ `WR.speed` vs `CB.speed` matters.
- _If_ the QB is under pressure (`OL.blocking` vs `DL.rush`), the throw accuracy decreases.

We need a standardized way to model these "Compound Interactions" without writing thousands of nested `if/else` statements in the main game loop.

---

## Decision

**What change are we making?**

We will implement an **Attribute Interaction Engine (AIE)**.

1.  **Interaction Definition**: We will define interactions as structured objects containing:
    - **Primary Pair**: The main attributes being opposed (e.g., `PassBlock` vs `PowerMoves`).
    - **Secondary Modifiers**: Other attributes that influence the outcome (e.g., `Strength`, `Weight`).
    - **Contextual Multipliers**: Situational factors (e.g., "3rd & Long").
2.  **Interaction Score**: The engine will output a normalized "Interaction Score" (e.g., -1.0 to +1.0) representing the degree of win/loss for the offensive player.
3.  **Decoupling**: The `PlayResolver` will request an outcome from the AIE (e.g., `resolve_pass_protection(ol, dl)`) rather than doing the math itself.

---

## Rationale

**Why are we making this decision?**

1.  **Realism**: Allows for "Rock-Paper-Scissors" dynamics. A small, fast WR might beat a slow, strong CB on a "Go Route" but lose on a "Slant" against press coverage.
2.  **Maintainability**: Centralizes the math. If we want to tweak how much "Strength" matters in blocking, we change it in one place (the AIE), not in every play type logic.
3.  **Tuning**: We can easily adjust weights/coefficients to balance the game.

---

## Consequences

**What becomes easier or more difficult because of this decision?**

### Positive Consequences

- **Granular Control**: We can fine-tune specific matchups (e.g., "Elite Pass Rushers are too dominant").
- **Testing**: We can unit test interactions in isolation (e.g., "Does a 99 STR lineman beat a 50 STR rusher 99% of the time?").
- **Scalability**: Adding new interactions (e.g., "Route Running vs Zone Coverage") follows a standard pattern.

### Negative Consequences

- **Computational Cost**: More math per play. We are moving from `A > B` to `(A * w1 + C * w2) > (B * w3 + D * w4)`.
- **Complexity**: Debugging "why did this play fail?" requires looking at the AIE logs, not just the play logic.

---

## Alternatives Considered

**What other options did we evaluate?**

### Alternative 1: Simple Thresholds

- **Description**: `if offense.rating > defense.rating + 10: win`.
- **Pros**: Extremely fast.
- **Cons**: Produces "cliffs" where 1 point makes a huge difference. Fails to model nuance.
- **Reason for rejection**: Too arcade-like.

### Alternative 2: Physics-Based Simulation

- **Description**: Model player mass, velocity, and vector collisions.
- **Pros**: Ultimate realism.
- **Cons**: Requires a physics engine (Unity/Unreal) or massive custom code. Too slow for a management sim that might sim years in minutes.
- **Reason for rejection**: Overkill for a text/2D sim.

---

## Implementation Notes

**How will this decision be implemented?**

1.  **Class**: Create `AttributeInteractionEngine` class.
2.  **Methods**:
    - `calculate_interaction_score(attacker, defender, interaction_type)`
    - `resolve_matchup(attacker, defender, context)`
3.  **Configuration**: Define weights for interactions in a config file or constant dictionary (e.g., `INTERACTION_WEIGHTS`).
4.  **Integration**: Update `PlayResolver` to instantiate AIE and call it during play execution.

---

## Validation Criteria

**How will we know this decision was correct?**

- **Statistical Accuracy**: The distribution of outcomes (sacks, completions, yards per carry) matches NFL historical averages when using average player data.
- **Outliers**: Elite vs Poor matchups result in decisive wins (>80% win rate for the elite player).
- **Performance**: The AIE calculation takes negligible time (<1ms per interaction).

---

## References

- `docs/specs/attribute_interaction_spec.md` (Proposed)
- `backend/app/engine/play_resolver.py`
