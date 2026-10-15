# **12. Use DbContext Factory for Error Recovery**
---
**Date:** 18-12-2025

## **Problem**  
---

The SessionReward class encounters scenarios where database save operations fail, leaving the DbContext in an inconsistent or "dirty" state. When this happens, the context cannot be reliably used for subsequent operations and needs to be disposed and recreated. However, standard DbContext dependency injection doesn't support this pattern of disposing and recreating contexts within the same service lifetime.

This creates a problem where:
1. Failed save operations contaminate the DbContext state
2. Retry logic requires a clean DbContext instance
3. Standard DI container injection provides a single context instance per scope
4. Manual context disposal and recreation is needed for error recovery scenarios

## **Decision**  
---

We will implement `IRewardDbContextFactory` interface to provide DbContext creation capabilities to the SessionReward class. Instead of injecting the DbContext directly, we inject a factory that knows how to create new DbContext instances on demand.

The factory pattern allows:
- **Context Recreation**: Create fresh DbContext instances after failed operations
- **Error Recovery**: Dispose contaminated contexts and start with clean state
- **Flexible Lifetime Management**: Control context lifecycle independent of DI scope
- **Isolation**: Each operation can use its own context if needed

### **Implementation Pattern**
```csharp
public class SessionRewards : ISessionReward
{
    private readonly IRewardDbContextFactory contextFactory;
    
    public SessionRewards(IRewardDbContextFactory contextFactory)
    {
        this.contextFactory = contextFactory;
    }
    
    private async Task<bool> OperationWithRetry()
    {
        using var context = contextFactory.CreateDbContext();
        try
        {
            // Perform operations
            await context.SaveChangesAsync();
            return true;
        }
        catch
        {
            // Context is disposed automatically
            // Can create new context for retry if needed
            return false;
        }
    }
}
```

## **Consequences/Implications**
---

- **Improved Error Recovery**: Failed operations no longer contaminate subsequent operations since fresh contexts can be created.

- **Better Isolation**: Each critical operation can use its own context, preventing cross-operation state pollution.

- **Flexible Context Management**: Context lifetime is controlled by the business logic rather than DI container scope.

- **Retry Logic Support**: Failed operations can be retried with clean context state without affecting the overall service.

- **Slight Performance Overhead**: Creating new contexts has minimal overhead compared to the benefits of clean state management.

- **Dependency Change**: Services using this pattern depend on factory interface rather than direct DbContext, requiring factory registration in DI container.

- **Memory Management**: Proper disposal of contexts becomes more critical since they're created manually rather than managed by DI scope.