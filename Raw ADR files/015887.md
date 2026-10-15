# ADR-001: Rule Content Classification System

## Status

Proposed

## Context

The current Riftbound rules data has a hierarchical structure with levels (0-3+), but the `level` alone doesn't distinguish between different _types_ of content:

1. **Section Headers** (e.g., "400. Draw") - Level 0 rules that serve as category containers
2. **Topic Headers** (e.g., "401. Exhaust") - Level 1 rules where `title === content`, essentially naming a concept
3. **Definition Rules** (e.g., "401.1. Exhausting is an action that marks...") - Level 2+ rules with actual content
4. **Sub-rules** (e.g., "401.1.a. To mark it, rotate the card...") - Nested within definitions

Currently, all of these are displayed identically as RuleCard components with chevrons, making it impossible for users to distinguish between a rule header and a rule with substantive content.

### Problem Examples

```json
// This is a TOPIC HEADER - title equals content
{
  "id": "401",
  "title": "Exhaust",
  "content": "Exhaust",
  "level": 1
}

// This is a DEFINITION - has actual explanatory content
{
  "id": "401.1",
  "title": "Exhausting is an action that marks a non-spell Game Object as \"spent.\"",
  "content": "Exhausting is an action that marks a non-spell Game Object as \"spent.\"\n401.1.a. To mark it, rotate the card...",
  "level": 2
}
```

## Options Considered

### Option A: Runtime Classification Based on Content Analysis

Classify rules at runtime by analyzing content patterns:

- `isHeader`: `title === content` AND has children
- `isDefinition`: `title !== content` (has explanatory body text)
- `isTerminal`: No children (leaf node)
- `hasSubRules`: Content contains embedded sub-rules (e.g., "401.1.a.")

**Pros:**

- No data migration needed
- Works with existing JSON structure
- Classification logic is transparent

**Cons:**

- Runtime overhead (minimal)
- Classification heuristics may have edge cases

### Option B: Add Classification Field to Data

Enhance rules.json with explicit `ruleType` field during parsing:

```json
{
  "id": "401",
  "ruleType": "topic-header",
  ...
}
```

**Pros:**

- Explicit, no heuristics
- Faster runtime (pre-computed)

**Cons:**

- Requires data migration
- Parser must be updated
- Data duplication (can be derived)

### Option C: Hybrid - Derive + Cache

Compute classifications at load time and store in the indexed data structure.

**Pros:**

- Best of both worlds
- Classifications available immediately
- No data file changes

**Cons:**

- Slightly more complex store logic

## Decision

We will implement **Option C: Hybrid - Derive + Cache**.

During `loadRules()`, we will compute and attach classification metadata to each rule in the index:

```typescript
interface RuleClassification {
  ruleType: "section" | "topic-header" | "definition" | "sub-rule";
  isHeader: boolean; // Has children, title === content
  hasSubContent: boolean; // Content contains embedded sub-rules (a., b., etc.)
  isTerminal: boolean; // No children (leaf node)
  contentLength: "empty" | "short" | "medium" | "long"; // For display decisions
}
```

Classification Logic:

1. **section**: `level === 0`
2. **topic-header**: `level >= 1` AND `title === content` (or content is just the title repeated)
3. **definition**: `level >= 1` AND `title !== content` AND has substantive content
4. **sub-rule**: Any rule where `parentId` points to a definition

## Consequences

### Positive

- UI can make informed display decisions based on rule type
- Topic headers can be visually distinct from definitions
- Reading experience can adapt to content type
- No changes to source data files
- Classifications are computed once at load time

### Negative

- Store complexity increases slightly
- Classification heuristics need testing against full dataset
- May need refinement as edge cases are discovered

### Neutral

- TypeScript types need to be extended
- Existing components need updates to use classifications
