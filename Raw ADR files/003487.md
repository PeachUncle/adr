# **Private User ID Retrieval Decision**  
---

**Date:** 10-8-2025

## **Problem**  
---

We need to retrieve the new internal `user id` (integer) for use as a foreign key in the database. This ID is not available from JWT claims because it is for private/internal use only. We must choose an approach that balances performance, scalability, maintainability, and architectural consistency.

The considered options are:

1. **Stored procedures** to directly fetch the internal `user id` from the database as doing the action.
    
2. **Coupling interfaces** between modules, bypassing navigation properties (violates vertical slice architecture and introduces high coupling).
    
3. **Interface-based service** to abstract how the internal `user id` is retrieved (could be via EF call or API if separated into another application).


## **Decision**  
---

The second option is rejected as it poses architectural risks and breaks the vertical slice architecture principles, introducing more danger than benefit.

While stored procedures (option 1) provide excellent performance and can simplify internal application logic, they separate business logic between the database and the codebase. This reduces maintainability and scalability, as each usage of the private `user id` would require a stored procedure.

We will adopt option 3 — **using an interface-based service** to retrieve the internal `user id`. This allows the retrieval mechanism to be swapped without affecting the rest of the codebase. If the application remains monolithic, the interface can call the database directly via EF; if split into separate services, the interface can call an API. The implementation changes, but the consuming code remains the same.


## **Consequences/Implications**
---

- Higher flexibility: retrieval method can change without touching other business logic.
    
- Greater maintainability: logic stays in the codebase, not split between DB and app.
    
- More scalable: works seamlessly even if the application is split into multiple services in the future.
    
- Slight performance overhead compared to stored procedures due to the abstraction layer, but acceptable within project constraints.