# Bidirectional Link Storage

## Purpose
This document records the decision to store all links as bidirectional relationships in the database, regardless of how they were created.

## Classification
- **Domain:** Data Model
- **Stability:** Static
- **Abstraction:** Structural
- **Confidence:** Established

## Content

### Context

Links in Bartleby connect cards (e.g., a scene mentions a character, a chapter is located in a city). These connections can be created in multiple ways:

1. Wiki link in markdown: `[[Character Name]]`
2. Explicit UI action: "Add link" in link panel
3. Hierarchical relationship: Parent-child in tree

The question was how to model link directionality:
- Store as directional (A→B) and require reverse queries?
- Store as bidirectional (A↔B) explicitly?
- Store both directions as separate records?

### Decision

**Store all links as bidirectional:**

- Single Link record with `cardAId` and `cardBId`
- Both cards can traverse to the other
- `createdFrom` field tracks provenance (which side initiated)
- No concept of "source" vs "target" in queries

### Status

Accepted

### Consequences

**Positive:**
- Simpler queries (don't need UNION to find both directions)
- More intuitive UX (link visible from both cards)
- Easier network traversal (no directionality concerns)
- Matches author mental model (relationships vs. references)
- Better for "impact analysis" (what's affected by this character?)

**Negative:**
- Some relationships are naturally directional (e.g., "follows" in sequence)
- Can't enforce directionality at database level
- Slightly more complex to represent one-way relationships

**Risks:**
- User confusion about which "direction" a link goes
- Need UI hints for naturally directional relationships

**Trade-offs:**
- Flexibility and simplicity over enforced semantics
- User intent tracking (createdFrom) vs enforced directionality

### Alternatives Considered

#### Alternative 1: Directional Links (A→B)

Store as source and target with direction.

**Pros:**
- Natural for citations, references, sequences
- Clear semantic meaning
- Prevents accidental reverse interpretation

**Cons:**
- Requires UNION queries to find all connections
- Complex for truly symmetric relationships (mentions, located-at)
- Poor UX (link only visible from one side by default)
- More cognitive load (which direction is this link?)

#### Alternative 2: Two Records Per Link

Store both A→B and B→A as separate records.

**Pros:**
- Simple queries from either side
- Can track metadata separately per direction
- Clear provenance

**Cons:**
- Data duplication
- Synchronization issues (update one, forget the other)
- Deletion complexity (must delete both)
- Doubled storage

#### Alternative 3: Junction Table with Direction Flag

Single record with isDirectional boolean.

**Pros:**
- Flexible (supports both bidirectional and directional)
- Single source of truth

**Cons:**
- Queries must check direction flag
- More complex application logic
- Unclear when to use directional vs bidirectional

### Implementation Notes

1. **Link Schema:**
   ```sql
   CREATE TABLE links (
     id TEXT PRIMARY KEY,
     card_a_id TEXT NOT NULL,
     card_b_id TEXT NOT NULL,
     link_type TEXT NOT NULL,
     created_from TEXT NOT NULL,  -- 'A', 'B', 'inline-A', 'inline-B', 'explicit'
     metadata TEXT NOT NULL,       -- JSON
     created_at INTEGER NOT NULL
   );
   ```

2. **Querying Links for Card:**
   ```sql
   SELECT * FROM links
   WHERE card_a_id = ? OR card_b_id = ?
   ```

3. **Directional Hints in UI:**
   - Link types can specify `bidirectional: false` in config
   - UI shows arrow for directional types (e.g., "follows")
   - Network view uses directed edges for directional types

4. **Provenance Tracking:**
   - `createdFrom` field preserves creation context
   - Useful for cleanup (e.g., delete inline link when markdown changes)
   - Not used for query logic

5. **Special Case: Sequence Links**
   - Type `sequence` is directional by convention
   - UI enforces A comes before B in manuscript order
   - Still stored bidirectionally but UI presents as directional

## Relationships
- **Parent Nodes:** [foundation/principles.md]
- **Child Nodes:** None
- **Related Nodes:**
  - [data-model/overview.md] - implements - Link entity is bidirectional
  - [wiki-link-system/overview.md] - creates - Wiki links create bidirectional links
  - [frontend-app/overview.md] - displays - UI shows links from both sides

## Navigation Guidance
- **Access Context:** Reference when implementing link queries, network traversal, or link creation
- **Common Next Steps:** Review link schema, query patterns, UI presentation
- **Related Tasks:** Link panel implementation, network visualization, wiki link creation
- **Update Patterns:** Revisit if users consistently confused by bidirectionality or if directional semantics critical

## Metadata
- **Decision Number:** 002
- **Created:** 2025-11-14
- **Last Updated:** 2025-11-14
- **Updated By:** AI Agent (Claude)
- **Deciders:** Development team based on UX requirements

## Change History
- 2025-11-14: Initial decision record created
