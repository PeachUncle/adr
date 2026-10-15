# ADR-009: Query Optimization Strategy for N+1 Problem

**Date:** 2025-07-15
**Status:** Pending
**Deciders:** Craig Banach
**Technical Story:** Optimize database queries to prevent N+1 problems while maintaining Clean Architecture

## Context

The current repository implementation uses Entity Framework's `.Include()` for loading related data, which can lead to performance issues:

- **N+1 Query Problems**: Loading full related entities when only partial data is needed
- **Over-fetching**: Transferring unnecessary data over the network
- **Memory Overhead**: Loading complete entities into memory when only specific fields are required
- **Performance Impact**: Especially noticeable with large datasets and complex relationships

### Current Implementation
```csharp
// TransactionRepository.cs
var query = _context.Transactions.Include(t => t.Category).Where(t => t.UserId == userId);
```

This loads full Category entities for every transaction, even when only category name might be needed for display.

## Decision

**Status: PENDING** - Need to choose between the following approaches:

### Option 1: Selective Loading (Recommended)
Add optional includes to repositories while keeping Clean Architecture intact:

```csharp
public async Task<IEnumerable<Transaction>> GetUserTransactionsAsync(
    string userId, 
    bool includeCategory = true)
{
    var query = _context.Transactions.Where(t => t.UserId == userId);
    
    if (includeCategory)
        query = query.Include(t => t.Category);
        
    return await query.ToListAsync();
}
```

### Option 2: Read Models in Core Layer
Create lightweight read models for specific query patterns:

```csharp
// Core/Models/ReadModels/TransactionListItem.cs
public class TransactionListItem
{
    public int Id { get; set; }
    public decimal Amount { get; set; }
    public string Description { get; set; }
    public DateTime TransactionDate { get; set; }
    public string CategoryName { get; set; }
    public string CategoryIcon { get; set; }
}
```

### Option 3: Query Objects Pattern
Implement specialized query objects for different use cases:

```csharp
// Core/Queries/GetTransactionListQuery.cs
public class GetTransactionListQuery
{
    public string UserId { get; set; }
    public int Page { get; set; }
    public int PageSize { get; set; }
    public bool IncludeFullCategory { get; set; } = false;
}
```

### Option 4: GraphQL/OData (Future Consideration)
Allow clients to specify exactly what data they need.

## Consequences

### If Option 1 (Selective Loading) is chosen:
- ✅ **Pros**: 
  - Maintains Clean Architecture
  - Simple to implement
  - Backward compatible
  - Repository stays focused on entities
- ❌ **Cons**: 
  - Still loads full entities when included
  - Multiple repository methods needed

### If Option 2 (Read Models) is chosen:
- ✅ **Pros**: 
  - Optimal data transfer
  - Clear intent for different use cases
  - Stays within Clean Architecture
- ❌ **Cons**: 
  - Additional models to maintain
  - Mapping complexity increases

### If Option 3 (Query Objects) is chosen:
- ✅ **Pros**: 
  - Highly flexible
  - Encapsulates query logic
  - Easy to extend
- ❌ **Cons**: 
  - More complex implementation
  - Learning curve for team

## Decision Criteria

Consider these factors when making the decision:

1. **Performance Requirements**: How critical is query performance?
2. **Team Complexity**: What's the team's comfort level with different patterns?
3. **Future Scalability**: Will the system need to handle much larger datasets?
4. **Maintenance Burden**: How much additional code complexity is acceptable?
5. **Clean Architecture Compliance**: Must not break layer dependencies

## Implementation Notes

Whichever option is chosen:

- **Keep repositories returning entities** - Don't break Clean Architecture
- **Measure performance impact** - Use profiling tools to validate improvements
- **Consider caching** - For frequently accessed reference data like categories
- **Document patterns** - Ensure team understands the chosen approach

## Next Steps

1. **Benchmark current performance** - Get baseline metrics
2. **Prototype chosen solution** - Implement small proof of concept
3. **Measure improvements** - Compare performance before/after
4. **Update all repositories** - Apply pattern consistently
5. **Update documentation** - Reflect new query patterns

## References

- [Clean Architecture by Robert Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Entity Framework Performance](https://docs.microsoft.com/en-us/ef/core/performance/)
- [Query Object Pattern](https://martinfowler.com/eaaCatalog/queryObject.html)