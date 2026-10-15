# ADR 002: Table Of Content (TOC) representation in C#

## Context

We need to represent a Table of Contents (ToC) in C# that allows:
- Hierarchical organization of items (nested chapters, sections, subsections, etc.).
- Fast lookups by unique identifiers (string-based IDs).
- Efficient tree traversal for rendering and searching.
- Scalability to handle deep nesting and a large number of entries.

A purely tree-based structure is inefficient for lookups, while a dictionary alone does not maintain hierarchy.
We require a hybrid approach that balances these concerns.

## Decision

We have chosen a hybrid data structure that combines:
- A `Dictionary<string, TableOfContentsItem>` for O(1) identifier-based lookups.
- A tree structure where each item maintains a list of child items for hierarchical organization.



## Alternatives Considered

### Pure Tree-Based Structure (Recursive Class Only)

Implementation: Each item contains a List<TableOfContentsItem> for sub-items, and all traversal is done recursively.

Pros:
- Simple and intuitive for hierarchical data.
- Natural representation of ToC.

Cons:
- Slow lookup (O(n) in worst case).
- Searching for an item by ID requires a full tree traversal.
- Difficult to manage updates when dealing with large datasets.

### Dictionary with Parent References Only (No Tree Structure)

Implementation: A `Dictionary<string, TableOfContentsItem>` is used, and each item has a ParentId field instead
of a SubItems list.

Pros:
- Fast lookup (O(1)).
- Less memory usage than a hybrid tree.

Cons:
- No natural hierarchy for rendering or traversal.
- Every traversal requires reconstructing the tree dynamically.
- Difficult to perform operations like rendering a full structured ToC.

## Consequences

Advantages:
- Fast Lookup: The dictionary provides O(1) retrieval of items by ID.
- Structured Hierarchy: The tree structure allows hierarchical nesting and traversal.
- Scalability: Can handle large and deeply nested ToC structures efficiently.
- Flexibility: Can support features like reordering, serialization, and search.

Limitations:
- Memory Usage: Storing references in both a dictionary and a tree increases memory consumption.
- Manual Parent Handling: When modifying the hierarchy, parent-child relationships must be managed manually.

## Conclusion

We selected the hybrid approach because it offers the best balance between lookup efficiency and hierarchical
representation. This ensures both fast access to any entry by ID and structured navigation for display and processing.

This decision aligns with our needs for a scalable, flexible, and high-performance Table of Contents management system in C#.
