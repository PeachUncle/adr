# ADR-002: Index Pattern for O(1) Rule Lookups

## Status

Accepted

## Context

With the hierarchical data model (ADR-001), we have a tree structure where rules can reference other rules via IDs. Common operations include:

- Finding a rule by ID for detail pages (`/rules/:id`)
- Looking up parent rules for breadcrumbs
- Resolving child rules for navigation
- Following cross-references between rules

The naive approach would be to store rules in an array and use `.find()` for lookups. However, with potentially hundreds or thousands of rules, this creates O(n) lookup complexity.

Performance considerations:

- Users need fast page loads when clicking rule links
- Breadcrumb rendering requires multiple lookups (parent → grandparent → etc.)
- Tree navigation needs to resolve child IDs quickly
- Search results need to display rule details for each match

## Options Considered

### Option A: Array with .find() Lookups

Store all rules in a flat array:

```typescript
interface RulesData {
  version: string;
  lastUpdated: string;
  sections: RuleSection[]; // All rules in array
}

// Usage
const rule = sections.find((r) => r.id === targetId); // O(n)
```

**Pros:**

- Simple data structure
- Easy to iterate over all rules
- Matches JSON array format naturally

**Cons:**

- O(n) lookup time for every rule access
- Repeated traversals for parent/child lookups
- Poor performance with large rule sets
- Slow breadcrumb rendering (multiple lookups per render)

### Option B: Normalized Store with Separate Index Object

Keep rules in an array plus maintain a separate lookup index:

```typescript
interface RulesData {
  version: string;
  lastUpdated: string;
  sections: RuleSection[];
  index: Record<string, RuleSection>; // ID → Rule mapping
}
```

**Pros:**

- O(1) lookup by ID
- Still easy to iterate all rules (use sections array)
- Minimal data duplication (just references)
- Fast breadcrumb and navigation rendering
- Index can be built once on load

**Cons:**

- Slightly more complex data structure
- Need to keep array and index in sync (during load only)
- Small memory overhead for the index

### Option C: Map Data Structure

Use a JavaScript Map instead of an object:

```typescript
interface RulesData {
  version: string;
  lastUpdated: string;
  sections: RuleSection[];
  index: Map<string, RuleSection>;
}
```

**Pros:**

- O(1) lookups
- Better performance for large datasets
- More idiomatic for lookup tables

**Cons:**

- Not JSON-serializable (requires conversion)
- More complex to work with in Zustand persist
- Not worth the complexity for this use case

## Decision

We will use **Option B: Normalized Store with Index Object**.

The `RulesData` structure will include both:

- `sections` array for iteration and bulk operations
- `index` object for O(1) lookups by ID

```typescript
interface RulesData {
  version: string;
  lastUpdated: string;
  sections: RuleSection[]; // Array for iteration
  index: Record<string, RuleSection>; // Object for O(1) lookup
}
```

The index will be:

- Built once when rules are loaded
- Populated from the sections array if not present in JSON
- Used by all lookup operations in the store and components

## Consequences

### Positive

- **Fast Lookups**: O(1) access to any rule by ID
- **Better UX**: Instant page loads and smooth navigation
- **Efficient Breadcrumbs**: Multiple parent lookups don't degrade performance
- **Scalable**: Performance doesn't degrade as rules dataset grows
- **Simple Usage**: `rulesData.index[id]` is clean and readable
- **JSON Compatible**: Standard object is easily serializable

### Negative

- **Memory Overhead**: Index duplicates references to all rules (~8 bytes per rule for the reference)
- **Build Cost**: Initial index build takes O(n) time, but only once
- **Sync Requirement**: Index must be kept in sync with sections array (handled at load time)

### Neutral

- The store's `loadRules` action builds the index automatically if not present
- Components use selector methods that internally use the index
- The index is transparent to most application code

### Implementation Notes

The store's `loadRules` function ensures the index exists:

```typescript
loadRules: async () => {
  const data: RulesData = await response.json();

  // Ensure index is populated if not present
  if (!data.index || Object.keys(data.index).length === 0) {
    data.index = {};
    for (const section of data.sections) {
      data.index[section.id] = section;
    }
  }

  set({ rulesData: data });
};
```

This approach allows the JSON file to optionally include the index (for even faster loads) or build it on-demand.
