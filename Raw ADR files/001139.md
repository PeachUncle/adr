# ADR 0003: Functional Programming Principles with Entity Framework Core

## Status
Accepted

## Date
2025-10-18

## Context
The Coates Village Club Server constitution mandates functional programming principles (Principle II):
- Methods MUST be stateless and pure where possible
- Side effects MUST be isolated and explicitly defined
- Functions MUST return new state rather than modify existing state
- Immutable data structures MUST be preferred
- Methods MUST have predictable outputs for given inputs
- State changes MUST be handled through explicit state management
- Shared state MUST be avoided unless absolutely necessary
- Functions MUST be composable and single-purpose

However, we are building microservices with C# .NET 8 and Entity Framework Core, which has inherent tensions with pure functional programming:

1. **EF Core Change Tracking**: EF Core tracks changes to mutable entities. Creating new entity instances breaks identity tracking and causes issues with relationship management.

2. **C# Language Constraints**: While C# 12 has record types and improved immutability, EF Core entities don't work well with immutable types due to proxy generation and change tracking requirements.

3. **Performance Considerations**: Pure functional approaches with immutable collections can have significant performance overhead for database-heavy applications.

4. **Ecosystem Patterns**: The ASP.NET Core and Azure Functions ecosystems follow imperative patterns with dependency injection and mutable service state.

## Decision
We adopt the **"Functional Core, Imperative Shell"** pattern as the pragmatic interpretation of constitutional functional programming requirements:

### Functional Core (Pure Business Logic)
These components MUST be pure functions with no side effects:

1. **Domain Logic Services**
   - `PasswordHashService.HashPassword()` - deterministic hashing
   - `PasswordHashService.VerifyPassword()` - deterministic verification
   - `JwtTokenService.GenerateAccessToken()` - deterministic token creation
   - `JwtTokenService.ValidateToken()` - deterministic validation
   - All FluentValidation validators - pure business rules

2. **Data Transformations**
   - `ToDto()` mapping methods - pure transformations
   - All DTO conversions - no side effects
   - Query result transformations - functional pipeline operations

3. **Utility Functions**
   - String manipulation helpers
   - Date/time calculations
   - Format converters

### Imperative Shell (Side Effect Management)
These components orchestrate the functional core and handle side effects:

1. **Service Layer**
   - `AuthService`, `UserService`, etc. - orchestrate pure functions
   - Handle database I/O explicitly via EF Core
   - Manage transactions and state persistence
   - **Allowed**: Entity mutation for EF Core change tracking
   - **Required**: Clear method signatures indicating side effects (`async Task<T>`)

2. **Repository Pattern NOT Required**
   - EF Core DbContext IS the repository abstraction
   - Additional repository layer adds unnecessary indirection
   - DbContext is already unit-of-work pattern

3. **Entity Management**
   - Entities may be mutable for EF Core tracking
   - Property changes tracked via `UpdatedAt` timestamps
   - Change tracking isolated to service methods
   - No entity mutation outside service boundaries

### Implementation Guidelines

✅ **DO:**
- Write pure functions for business logic and transformations
- Keep services stateless (no instance state, only injected dependencies)
- Return new DTOs rather than mutating them
- Use LINQ for query composition (functional pipelines)
- Isolate side effects to clearly-named async methods
- Use `ImmutableArray` or `ImmutableList` for collections that don't change
- Prefer method chaining and fluent APIs

❌ **DON'T:**
- Create new entity instances just to satisfy functional purity (breaks EF Core)
- Share mutable state across service instances
- Mutate entities outside the service layer
- Return tracked entities from service methods (return DTOs)
- Mix business logic with I/O operations within the same method
- Use static mutable state

### Code Example - Compliant Pattern

```csharp
// ✅ CORRECT: Functional core with imperative shell
public class AuthService : IAuthService
{
    private readonly MembershipDbContext _context;
    private readonly IJwtTokenService _jwtTokenService; // Pure function provider
    private readonly IPasswordHashService _passwordHashService; // Pure function provider
    
    // Imperative shell: Orchestrates pure functions and handles side effects
    public async Task<AuthResponse?> LoginAsync(LoginRequest request)
    {
        // Query (side effect - clearly async)
        var user = await _context.Users
            .FirstOrDefaultAsync(u => u.Email == request.Email);
        
        if (user == null) return null;
        
        // Pure function: Password verification
        if (!_passwordHashService.VerifyPassword(request.Password, user.PasswordHash))
        {
            return null;
        }
        
        // Pure function: Token generation
        var accessToken = _jwtTokenService.GenerateAccessToken(
            user.Id, user.Email, user.Role.ToString(), user.CommitteeRole?.ToString());
        
        // Pure function: Token generation
        var refreshToken = _jwtTokenService.GenerateRefreshToken();
        
        // Imperative: Create new entity (EF Core will track)
        var refreshTokenEntity = new RefreshToken
        {
            Id = Guid.NewGuid(),
            UserId = user.Id,
            Token = refreshToken,
            ExpiresAt = DateTime.UtcNow.AddDays(30),
            CreatedAt = DateTime.UtcNow,
        };
        
        // Imperative: Mutate entity (EF Core change tracking)
        user.LastLoginAt = DateTime.UtcNow;
        user.UpdatedAt = DateTime.UtcNow;
        
        // Imperative: Persist changes (side effect)
        _context.RefreshTokens.Add(refreshTokenEntity);
        await _context.SaveChangesAsync();
        
        // Pure function: DTO mapping
        return new AuthResponse
        {
            AccessToken = accessToken,
            RefreshToken = refreshToken,
            ExpiresAt = DateTime.UtcNow.AddMinutes(15),
            User = ToDto(user), // Pure transformation
        };
    }
    
    // Pure function: Entity to DTO transformation
    private static UserDto ToDto(User user) => new()
    {
        Id = user.Id,
        Email = user.Email,
        FirstName = user.FirstName,
        LastName = user.LastName,
        Role = user.Role,
        CommitteeRole = user.CommitteeRole,
        Status = user.Status,
        CreatedAt = user.CreatedAt,
    };
}
```

## Consequences

### Positive
1. **Testability**: Pure functions (password hashing, token generation, validations) are trivially testable without mocks
2. **Predictability**: Business logic is deterministic and side-effect-free
3. **Maintainability**: Clear separation between pure logic and I/O operations
4. **Performance**: No overhead from unnecessary immutability where EF Core requires mutation
5. **Pragmatism**: Works with existing .NET ecosystem and libraries
6. **Constitutional Compliance**: Satisfies functional programming requirements where it matters most (business logic)

### Negative
1. **Not Pure FP**: Entities are mutable, services have side effects
2. **Learning Curve**: Developers must understand when to apply FP principles vs. when to use imperative patterns
3. **Discipline Required**: No compiler enforcement of pure vs. impure boundaries

### Neutral
1. **Hybrid Approach**: Mix of functional and imperative patterns based on pragmatic needs
2. **Context-Dependent**: Purity enforced where it provides value (business logic), relaxed where it causes friction (EF Core)

## Alternatives Considered

### 1. Strict Functional Programming with Immutable Entities
**Rejected**: Would require abandoning EF Core change tracking, implementing custom persistence layer, significant performance overhead, and fighting the framework.

### 2. Full Repository Pattern with Anemic Domain Model
**Rejected**: Adds unnecessary abstraction layer on top of EF Core, which already implements Unit of Work and Repository patterns.

### 3. CQRS with Separate Read/Write Models
**Deferred**: May be appropriate for individual services as they scale, but overkill for initial implementation. Can be adopted service-by-service as needed.

### 4. F# for Service Implementation
**Rejected**: Team expertise is in C#, mixing languages adds complexity, Azure Functions tooling is C#-first.

## Compliance Verification

This approach is verified through:
1. **Unit Tests**: Pure functions (validators, transformations) tested without mocks
2. **Code Reviews**: Verify side effects are isolated and clearly marked
3. **Static Analysis**: Enforce statelessness of services (no instance fields except injected dependencies)
4. **Integration Tests**: Verify overall behavior including side effects

## References
- [Functional Core, Imperative Shell](https://www.destroyallsoftware.com/screencasts/catalog/functional-core-imperative-shell)
- [Mark Seemann: From Dependency Injection to Dependency Rejection](https://blog.ploeh.dk/2017/02/02/dependency-rejection/)
- [EF Core Change Tracking](https://learn.microsoft.com/en-us/ef/core/change-tracking/)
- Constitution Principle II: Code Quality Standards

## Review History
- 2025-10-18: Initial version (Jamie D. Wright)
