# **13. Use Shared Employee Lookup Service for Cross-Slice Communication**
---
**Date:** 18-12-2025

## **Problem**  
---

The Rewards slice needs access to employee salary information for reward calculations, but the Employee table exists in a separate schema/slice following vertical slice architecture principles. Direct database references between slices violate the architectural boundaries and coupling constraints established in previous decisions.

This creates a problem where:
1. Reward calculations require employee salary data
2. Direct database joins across slices break vertical slice isolation
3. Cross-slice data access needs to be managed without violating architectural boundaries
4. Future microservice extraction requires loose coupling between slices

## **Decision**  
---

We will implement a shared public contract `IEmployeeLookupService` in the Common folder that serves as a bridge between slices. This interface will be implemented within the same project initially, but can evolve into API calls if slices are extracted into separate projects.

The service will provide:
- **GetEmployee()**: Returns employee details (ID, name, salary, national number)
- **GetEmployeesSalaryById()**: Returns employee IDs with their salaries for bulk operations

### **Implementation Pattern**
```csharp
// Common contract
public interface IEmployeeLookupService
{
    Task<EmployeeDto?> GetEmployee(int employeeId);
    Task<IEnumerable<EmployeeSalaryDto>> GetEmployeesSalaryById(IEnumerable<int> employeeIds);
}

// Usage in Rewards slice
public class SessionRewards
{
    private readonly IEmployeeLookupService employeeLookup;
    
    public async Task CalculateRewardsAsync()
    {
        var employeeIds = GetEmployeeIdsFromSessions();
        var employeeSalaries = await employeeLookup.GetEmployeesSalaryById(employeeIds);
        // Calculate rewards using salary data
    }
}
```

## **Consequences/Implications**
---

- **Maintained Slice Isolation**: Slices remain decoupled while enabling necessary data access through well-defined contracts.

- **Future Microservice Ready**: Interface can be implemented as API calls when slices are extracted to separate projects.

- **Clear Boundaries**: Explicit contracts define what data can be accessed across slices, preventing architectural drift.

- **Testability**: Interface can be easily mocked for unit testing without database dependencies.

- **Performance Consideration**: Additional service layer introduces slight overhead, but enables bulk operations to minimize performance impact.

- **Dependency Management**: Rewards slice depends on Employee slice through interface, requiring careful dependency injection setup.

- **Evolution Path**: Provides clear migration path from in-process calls to distributed API calls as system scales.