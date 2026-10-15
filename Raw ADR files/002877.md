# ADR: 005 - Dynamic LINQ Queries for ProjectOneMil

## Context
The `ProjectOneMil` project requires the ability to build dynamic LINQ queries at runtime to support flexible data filtering and sorting. The team needs to decide on the library to be used for dynamic LINQ queries.

## Decision
We have decided to use the System.Linq.Dynamic.Core library for building dynamic LINQ queries in the `ProjectOneMil` project.

## Alternatives Considered
1. **Manually Constructed Expressions**:
   - Pros:
     - Full control over query construction.
     - No additional dependencies.
   - Cons:
     - Complex and error-prone.
     - Requires deep knowledge of expression trees.

2. **Dynamic LINQ (Microsoft)**:
   - Pros:
     - Simple and straightforward API.
     - Part of the .NET ecosystem.
   - Cons:
     - Limited functionality compared to System.Linq.Dynamic.Core.
     - Less active development and community support.

## Rationale
System.Linq.Dynamic.Core was chosen for the following reasons:
- **Flexibility**: Provides a powerful and flexible API for building dynamic LINQ queries at runtime.
- **Ease of Use**: Simplifies the construction of dynamic queries without the need for complex expression trees.
- **Community Support**: Actively maintained with a strong community and extensive documentation.
- **Compatibility**: Seamlessly integrates with Entity Framework Core and other LINQ providers.

## Consequences
- **Positive**:
  - Simplified construction of dynamic LINQ queries.
  - Enhanced flexibility for data filtering and sorting.
  - Strong community support and documentation.
- **Negative**:
  - Additional dependency in the project.
  - Potential learning curve for team members unfamiliar with dynamic LINQ.

## Implementation
The following steps will be taken to implement System.Linq.Dynamic.Core in the `ProjectOneMil` project:
1. **Install System.Linq.Dynamic.Core**: Add the System.Linq.Dynamic.Core package to the project via NuGet.
2. **Build Dynamic Queries**: Implement functionality to build dynamic LINQ queries using the library.
3. **Integrate with EF Core**: Ensure seamless integration with Entity Framework Core for querying the database.
4. **Optimize Performance**: Optimize dynamic queries to ensure performance and efficiency.

## References
- [System.Linq.Dynamic.Core Documentation](https://github.com/StefH/System.Linq.Dynamic.Core)
- [System.Linq.Dynamic.Core GitHub Repository](https://github.com/StefH/System.Linq.Dynamic.Core)
- [NuGet Package](https://www.nuget.org/packages/System.Linq.Dynamic.Core)
