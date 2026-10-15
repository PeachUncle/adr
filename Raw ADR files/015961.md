---
status: accepted
date: 2025-08-22
---

# ADR-002: Data Access Patterns - Lean Server Actions

## Context
With RPC-style server actions and Drizzle ORM, we need to decide on our data access architecture:
1. Direct database access in server actions
2. Traditional service/repository layers
3. Hybrid approach with extracted query functions

Key considerations:
- Server actions already provide RPC endpoints
- Drizzle already provides type-safe database abstraction
- TypeScript ensures end-to-end type safety
- We want to avoid premature abstraction

## Decision
We adopt a **lean, progressive approach**: start with direct database access in server actions, extract reusable queries as needed.

## Rationale

### Why Not Service Layers
- **Server actions ARE the service layer** - they handle validation, authorization, business logic, and data access
- Adding another service layer creates unnecessary indirection
- Drizzle already provides a good abstraction over SQL
- TypeScript already ensures type safety

### Why Not Repository Pattern
- We're not switching databases (committed to D1)
- Drizzle queries are already testable
- Repository pattern often leads to anemic implementations that just wrap ORM methods

### Why This Approach Works
- **Simplicity**: One place to look for endpoint logic
- **Clarity**: Easy to trace data flow
- **Performance**: No unnecessary abstraction overhead
- **Flexibility**: Can refactor when patterns emerge

## Implementation

### Default Pattern: Direct Access
```typescript
// src/app/pages/items/functions.ts
"use server";
import { db } from "@/db";
import { items } from "@/db/schema";

export async function createItem(data: unknown) {
  const validation = validate(itemSchema, data);
  if (!validation.success) {
    return { success: false, errors: validation.errors };
  }
  
  const [item] = await db.insert(items)
    .values(validation.data)
    .returning();
    
  return { success: true, item };
}
```

### Extract Complex Queries
When the same complex query is used 3+ times, extract to `db/queries/`:

```typescript
// src/db/queries/items.ts
export async function getItemWithRelations(itemId: string) {
  return db.select({
    item: items,
    author: users,
    category: categories,
  })
  .from(items)
  .leftJoin(users, eq(items.userId, users.id))
  .leftJoin(categories, eq(items.categoryId, categories.id))
  .where(eq(items.id, itemId));
}

// Use in server action
import { getItemWithRelations } from "@/db/queries/items";
```

### Business Logic Stays in Server Actions
```typescript
export async function publishItem(itemId: string) {
  const { user } = await requireAuth();
  
  const [item] = await db.select()
    .from(items)
    .where(eq(items.id, itemId));
  
  // Business rules
  if (item.userId !== user.id) {
    return { error: "Unauthorized" };
  }
  
  if (!item.title || !item.description) {
    return { error: "Item must have title and description" };
  }
  
  // Update
  const [published] = await db.update(items)
    .set({ 
      status: 'published',
      publishedAt: new Date()
    })
    .where(eq(items.id, itemId))
    .returning();
    
  return { success: true, item: published };
}
```

## Consequences

### Positive
- Minimal boilerplate
- Easy to understand and modify
- Fast development speed
- Clear ownership of logic
- No artificial boundaries

### Negative
- Some query duplication initially
- Business logic mixed with data access
- Harder to unit test without database

## Exceptions

Consider adding abstraction when:

1. **Complex domain logic** emerges that's reused across multiple actions
2. **Cross-cutting concerns** like audit logging or caching are needed
3. **Multiple data sources** need to be coordinated
4. **Query complexity** warrants isolation for testing

Example of warranted abstraction:
```typescript
// src/services/archive.service.ts
export async function archiveItemAndDependencies(itemId: string) {
  return db.transaction(async (tx) => {
    // Complex multi-table updates
    await tx.update(items).set({ status: 'archived' })...
    await tx.update(comments).set({ visible: false })...
    await tx.insert(auditLog).values(...)...
    // Warranted because it's complex and reusable
  });
}
```

## Review Indicators

Revisit this decision if:
- We find ourselves copying the same query logic 5+ times
- Testing becomes difficult due to database coupling
- We need to coordinate multiple data sources
- Team grows and needs stronger boundaries

## References
- [Server Actions as API Endpoints](https://rwsdk.com/docs/server-actions)
- [Drizzle ORM Philosophy](https://orm.drizzle.team/docs/philosophy)
- [Against Service Layers](https://www.ben-morris.com/why-the-service-layer-anti-pattern-is-so-common/)