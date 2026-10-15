# Transaction Management Fix

## Purpose
This document outlines the decision to fix the nested transaction issue in the search indexing system that causes the error: "cannot start a transaction within a transaction".

## Classification
- **Domain:** Technical
- **Stability:** Stable
- **Abstraction:** Implementation
- **Confidence:** High

## Content

### Problem Statement

The search indexing system is encountering an error during indexing operations:

```
Error during indexing: cannot start a transaction within a transaction
Error running indexing: Indexing failed: cannot start a transaction within a transaction
Initial indexing failed: Failed to run indexing: Indexing failed: cannot start a transaction within a transaction
```

This occurs because:

1. The `IndexingTrigger.runIndexing()` method starts a database transaction
2. Later, it calls `CitationGraph.buildFromArchives()` which also starts its own transaction
3. SQLite doesn't support nested transactions, resulting in the error

### Decision

We will modify the `CitationGraph.buildFromArchives()` method to accept a new parameter `manageTransaction` (defaulting to `true`) that controls whether the method should manage its own transaction. When called from `IndexingTrigger.runIndexing()`, we'll pass `false` for this parameter to prevent it from starting a nested transaction.

### Implementation Details

1. Update the `CitationGraph.buildFromArchives()` method signature:
   ```typescript
   buildFromArchives(options: {
     researchPath: string;
     urlContentPath: string;
     manageTransaction?: boolean;
   }): Citation[]
   ```

2. Modify the method implementation to only start/commit/rollback transactions when `manageTransaction` is true:
   ```typescript
   const { researchPath, urlContentPath, manageTransaction = true } = options;
   
   // Only start transaction if we're managing it
   if (manageTransaction) {
     this.db.beginTransaction();
   }
   
   try {
     // ... existing code ...
     
     // Only commit if we're managing the transaction
     if (manageTransaction) {
       this.db.commitTransaction();
     }
     
     return allCitations;
   } catch (error) {
     // Only rollback if we're managing the transaction
     if (manageTransaction) {
       this.db.rollbackTransaction();
     }
     throw error;
   }
   ```

3. Update the call in `IndexingTrigger.runIndexing()`:
   ```typescript
   const citations = this.citationGraph.buildFromArchives({
     researchPath,
     urlContentPath,
     manageTransaction: false // Don't start a new transaction
   });
   ```

### Benefits

1. Eliminates the "cannot start a transaction within a transaction" error
2. Maintains the ability for `CitationGraph.buildFromArchives()` to work independently
3. Preserves transaction integrity for the entire indexing operation
4. Minimal code changes required

## Relationships
- **Parent Nodes:** [elements/search_indexing/structure.md] - is-child-of - Search indexing structure
- **Related Nodes:** 
  - [elements/search_indexing/database_specification.md] - relates-to - Database transaction management
  - [elements/search_indexing/citation_graph_specification.md] - modifies - Citation graph implementation

## Navigation Guide
- **When to Use:** When fixing transaction-related issues in the search indexing system
- **Next Steps:** Implement the changes in the code and test the indexing process

## Metadata
- **Created:** May 26, 2025
- **Last Updated:** May 26, 2025
- **Updated By:** Architect Agent

## Change History
- May 26, 2025: Initial creation of transaction management fix decision