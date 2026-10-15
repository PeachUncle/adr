# **11. Use Self-Contained Operations Pattern**
---
**Date:** 18-9-2025

## **Problem**  
---

The current approach of having separate property setters and a manual `SaveAsync()` method creates scalability issues and tight coupling problems, especially in higher orchestration classes. This pattern leads to:

1. **Transaction Management Complexity**: Higher-level classes must manage when to call save, creating potential for data inconsistency if save is forgotten or called at wrong times.

2. **Tight Coupling**: Classes become tightly coupled to the save mechanism, making it difficult to change persistence strategies or add cross-cutting concerns like validation, logging, or caching.

3. **Orchestration Burden**: Higher-level services must understand the internal state management of domain objects, violating encapsulation principles.

4. **Conflicting Data Risk**: Multiple operations on the same object without proper save coordination can lead to lost updates or inconsistent state.

5. **Scalability Limitations**: As the system grows, managing save operations across multiple related entities becomes increasingly complex and error-prone.

## **Decision**  
---

We will adopt a **Self-Contained Operations Pattern** where each business operation method handles its own persistence automatically. Instead of exposing property setters and requiring manual save calls, we will:

1. **Encapsulate Operations**: Each business method (e.g., `AddEmployeeSubjectSessions`) will handle the complete operation including validation, business logic, and persistence.

2. **Automatic Persistence**: Methods will automatically save changes at the end of successful operations, eliminating the need for external save coordination.

3. **Return Same Object**: Create and Update methods will return the same object instance (`this`) to enable method chaining while maintaining object identity. These methods are handled by factory or internal factory methods.

4. **Transaction Boundaries**: Each method defines its own transaction boundary, ensuring data consistency within the operation scope.

5. **Batch Operations**: Methods will have overloads that accept collections (e.g., `IEnumerable<EmployeeSessionDto>`) to handle multiple operations in a single database transaction, reducing database calls and improving performance.

### **Current Pattern (Problematic)**
```csharp
// Higher-level orchestration class
public async Task ProcessSessionReward()
{
	// Creates an object in memory
    var sessionReward = factory.Create(userId);
    
    // Multiple state changes
    sessionReward.Name = "Q1 2025";
    sessionReward.Percentage = 0.15f;
    sessionReward.Semester = 1;
    
    // Manual save - forced due to the higher possibility of casing bugs or errors
    // if the stat isn't saved to database
    await sessionReward.SaveAsync();
    
    // More operations
    await sessionReward.AddEmployeeSubjectSessions(dto1);
    await sessionReward.AddEmployeeSubjectSessions(dto2);
    
    // Manual save - easy to forget!
    await sessionReward.SaveAsync();
}
```

### **New Pattern (Self-Contained)**
```csharp
// Higher-level orchestration class
public async Task ProcessSessionReward()
{
	// Save Itself
    var sessionReward = await factory.CreateAsync(userId, "Q1 2025", 0.15f, 1);
    
    // More operations and each one handles it's own precedence     
    // If needs just one entry to DB
    await sessionReward.AddEmployeeSubjectSessions(dto1);
    await sessionReward.AddEmployeeSubjectSessions(dto2);
	
	// There is no need for SaveAsync method anymore
}
```

### **Bulk Operations**
```csharp
// Higher-level orchestration class
public async Task ProcessSessionReward()
{
	// Save Itself
    var sessionReward = await factory.CreateAsync(userId, "Q1 2025", 0.15f, 1);
    
    // More operations and each one handles it's own precedence     
    await sessionReward.AddEmployeeSubjectSessions(dtoList);	
}
```

## **Consequences/Implications**
---

- **Reduced Coupling**: Higher-level classes no longer need to understand when or how to save domain objects.

- **Improved Data Consistency**: Each operation is atomic and self-contained, reducing the risk of partial updates or forgotten saves.

- **Better Encapsulation**: Domain objects fully encapsulate their state management and persistence logic.

- **Simplified Orchestration**: Higher-level services can focus on business workflows rather than persistence coordination.

- **Enhanced Scalability**: Operations can be easily extended with cross-cutting concerns without affecting calling code.

- **Method Chaining Support**: Returning `this` enables fluent interfaces while maintaining object consistency.

- **Potential Performance Impact**: More frequent database calls, but acceptable given the improved maintainability and consistency guarantees.

- **Error Handling Clarity**: Failures are immediately apparent at the operation level rather than deferred to save time.