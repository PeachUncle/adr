# ADR-003: Trait System Design

**Status**: Accepted
**Date**: 2025-12-04
**Decision Makers**: Lead Architect, Backend Lead
**Supersedes**: N/A

---

## Context

**What is the issue or problem we're addressing?**

The current simulation engine relies primarily on numerical attributes (0-99) to determine outcomes. While this provides a solid statistical foundation, it fails to capture the unique "personality" and specialized skills of elite players.

For example:

- A "Field General" QB like Peyton Manning affects his teammates' performance, not just his own throws.
- A "Ball Hawk" DB takes risks to get interceptions, which isn't just a high "Catching" rating.
- A "Clutch" kicker performs better in high-pressure situations.

We need a system to model these qualitative differentiators to increase strategic depth, replayability, and narrative immersion (the "RPG" element of the simulation).

---

## Decision

**What change are we making?**

We will implement a **Trait System** as a core layer of the player model.

1. **Data Structure**: Traits are distinct entities defined in a `traits` table, linked to players via a many-to-many relationship (`player_traits`).
2. **Definition**: Traits are defined by:
   - **Name & Description**: Flavor text.
   - **Acquisition Method**: How a player gets it (Auto-unlock, Stat threshold, Coaching, etc.).
   - **Activation Triggers**: Contexts where it applies (e.g., "3rd Down", "Red Zone", "Vs Blitz").
   - **Effects**: Specific modifiers to attributes or probability calculations.
3. **Service Layer**: A `TraitService` will handle:
   - Eligibility checks.
   - Granting/Removing traits.
   - Calculating active effects during gameplay.
4. **Integration**: The `PlayResolver` and `MatchContext` will query the `TraitService` to apply modifiers before resolving play outcomes.

---

## Rationale

**Why are we making this decision?**

1. **Emergent Narrative**: Traits give players "character." A QB with "Gunslinger" tells a different story than one with "Game Manager," even if their overall ratings are similar.
2. **Strategic Depth**: Users must build teams considering trait synergies (e.g., pairing a "Field General" QB with "Route Technician" WRs).
3. **Extensibility**: New traits can be added via the database/catalog without rewriting the core physics engine.
4. **Visual Feedback**: Traits provide clear UI badges (Gold, Silver, Elite) that make roster management more rewarding.

---

## Consequences

**What becomes easier or more difficult because of this decision?**

### Positive Consequences

- **Differentiation**: Players feel unique.
- **Replayability**: Different roster builds feel significantly different to play.
- **UI/UX**: Provides high-value visual indicators of player quality.

### Negative Consequences

- **Complexity**: The simulation logic becomes more complex. We must check for trait triggers on every play.
- **Balancing**: Traits can easily become overpowered (OP). "Game-breaking" traits must be carefully tuned.
- **Performance**: Additional database lookups or in-memory checks during the simulation loop.

### Neutral Consequences

- **Data Management**: Requires maintaining a catalog of trait definitions and their effects.

---

## Alternatives Considered

**What other options did we evaluate?**

### Alternative 1: Extended Attribute Cap (0-120)

- **Description**: Allow elite players to exceed the 99 cap in specific attributes.
- **Pros**: Simple to implement. No new database tables.
- **Cons**: Doesn't capture _situational_ bonuses (e.g., "Clutch"). Doesn't convey flavor.
- **Reason for rejection**: Too linear; lacks the RPG feel we are targeting.

### Alternative 2: Hidden Attributes

- **Description**: Add hidden columns like `clutch_rating`, `consistency_rating`, `leadership_rating`.
- **Pros**: Easy to calculate in the engine.
- **Cons**: Invisible to the user. Reduces the "fun" of team building if you can't see why a player is good.
- **Reason for rejection**: We want explicit, visible differentiators.

### Alternative 3: Perk Trees (Skill Trees)

- **Description**: Players earn points to spend in a branching tree of upgrades.
- **Pros**: Deep progression system.
- **Cons**: Extremely complex to implement and balance for an MVP. High UI overhead.
- **Reason for rejection**: Scope creep. Traits are a flatter, more manageable implementation of this idea.

---

## Implementation Notes

**How will this decision be implemented?**

1. **Database**: Create `Trait` and `PlayerTrait` models (SQLAlchemy).
2. **Service**: Implement `TraitService` with a hardcoded `TRAIT_CATALOG` for Phase 1.
3. **API**: Endpoints to view and manage traits.
4. **Engine**: Inject `TraitService` into `PlayResolver`.
   - _Step 1_: `PreGame` - Apply static boosts (e.g., "Mentor").
   - _Step 2_: `PrePlay` - Check triggers (e.g., "Red Zone").
   - _Step 3_: `Resolution` - Apply modifiers to the RNG or attributes.

---

## Validation Criteria

**How will we know this decision was correct?**

- **Technical**: Trait queries add <5ms overhead to play simulation.
- **Gameplay**: A team with "Elite" traits statistically outperforms a team with identical attributes but no traits by a measurable margin (e.g., +5-10% win rate).
- **User**: Users can clearly identify "Trait Players" in the UI.

---

## References

- `docs/specs/trait_system_spec.md`
- `backend/app/services/trait_service.py`
