# ADR-017 – Service/Component Organization Pattern: Code Structure and Separation of Concerns

**Status:** Accepted  
**Date:** 2025-12-01  
**Author:** Niklas Häll

---

## Context

As the application grew, it became necessary to establish a clear organizational structure for code files. Without a defined pattern, code could become scattered, making it difficult to:
- Locate specific functionality
- Understand dependencies between components
- Maintain separation of concerns
- Onboard new developers
- Scale the application

The project needed a consistent directory structure that clearly separates:
- Business logic (services)
- API endpoints (controllers)
- Reusable UI components (Blazor components)
- Utility functions (helpers)
- Application startup configuration (extensions)
- Authentication logic
- Page-level components

---

## Decision

The application follows a **layered directory structure** with clear separation of concerns:

**Directory Organization:**

| Directory | Purpose | Examples |
|-----------|---------|----------|
| **`Services/`** | Business logic layer - interfaces and implementations | `IBookingService`, `BookingService`, `IUserService`, `UserService`, `IOutboxService`, `OutboxService`, `ITelemetryService`, `ApplicationInsightsTelemetryService` |
| **`Controllers/`** | API endpoints - REST API controllers | `BookingsController`, `UsersController`, `FeatureFlagController`, `HealthController`, `ApplicationInsightsController` |
| **`Helpers/`** | Static utility classes - stateless helper methods | `NavigationHelper`, `PriceCalculationHelper`, `CosmosJsonSerializer` |
| **`Components/`** | Reusable Blazor components - shared UI components | `BookingManagement.razor` |
| **`Pages/`** | Blazor pages - route-level pages | `Index.razor`, `Login.razor`, `AdminLandingPage.razor`, `UserLandingPage.razor`, `Bookings.razor`, `Demo.razor` |
| **`Extensions/`** | Extension methods - application startup configuration | `ServiceCollectionExtensions`, `ConfigurationExtensions`, `WebApplicationExtensions` |
| **`Authentication/`** | Authentication-specific classes | `TicketStore`, `CookieAuthenticationPostConfigureOptions` |
| **`Shared/`** | Shared Blazor components - layout components | `MainLayout.razor` |

**Key Principles:**
1. **Interface-Based Design** - Services define interfaces (`IBookingService`) and implementations (`BookingService`) in the same directory
2. **Dependency Injection** - All services registered in `ServiceCollectionExtensions` with appropriate lifetimes
3. **Separation of Concerns** - Controllers delegate to services, services contain business logic, helpers provide utilities
4. **Single Responsibility** - Each class/component has a single, well-defined purpose
5. **Namespace Alignment** - Namespaces match directory structure (`Ticketing.Web.Services`, `Ticketing.Web.Controllers`, etc.)

---

## Consequences

**Advantages:**
- **Clear Organization** - Developers can quickly locate code by its purpose (service, controller, helper, etc.)
- **Separation of Concerns** - Business logic separated from API layer, utilities separated from business logic
- **Testability** - Interface-based services enable easy mocking and unit testing
- **Maintainability** - Changes to business logic don't affect controllers, changes to controllers don't affect services
- **Scalability** - Easy to add new services, controllers, or components without cluttering existing files
- **Onboarding** - New developers can quickly understand the codebase structure
- **Dependency Management** - Clear dependency flow: Controllers → Services → Data Access
- **Reusability** - Components and helpers can be reused across pages and controllers

**Disadvantages:**
- **File Navigation** - More directories to navigate (mitigated by clear naming and IDE navigation)
- **Potential Over-Engineering** - Simple utilities might seem over-structured (acceptable trade-off for consistency)
- **Initial Setup** - Requires discipline to maintain structure as codebase grows

---

## Risks / Mitigations

- **Risk:** Developers might place code in wrong directories, breaking the pattern.  
  **Mitigation:** Clear documentation (this ADR), code review process, and consistent naming conventions help maintain structure.

- **Risk:** Services directory might become too large with many services.  
  **Mitigation:** If services grow significantly, consider subdirectories by domain (e.g., `Services/Bookings/`, `Services/Users/`). Current scale doesn't require this.

- **Risk:** Helpers might become a "catch-all" for miscellaneous code.  
  **Mitigation:** Helpers should be stateless utility classes. If a helper grows complex or has state, consider promoting it to a service.

- **Risk:** Controllers might contain business logic instead of delegating to services.  
  **Mitigation:** Code reviews and clear guidelines. Controllers should be thin - they handle HTTP concerns (routing, validation, response formatting) and delegate to services.

---

## Alternatives

- **Feature-Based Organization** - Organize by feature (e.g., `Bookings/`, `Users/`) with controllers, services, and components together.  
  **Rejected:** Works well for microservices but creates duplication in a monolithic application. Current structure provides better separation of concerns.

- **Flat Structure** - All files in root directory with naming conventions.  
  **Rejected:** Becomes unmanageable as codebase grows. Directory structure provides better organization and navigation.

- **Domain-Driven Design (DDD) Structure** - Organize by domain with bounded contexts.  
  **Rejected:** Over-engineered for MVP scale. Current structure provides sufficient organization without DDD complexity.

- **MVC-Style Separation** - Separate `Models/`, `Views/`, `Controllers/` directories.  
  **Rejected:** Blazor Server uses component-based architecture, not traditional MVC. Current structure aligns better with Blazor patterns.

---

## Implementation Details

### Service Layer Pattern

**Interface Definition:**
```csharp
// Services/IBookingService.cs
namespace Ticketing.Web.Services;

public interface IBookingService
{
    Task<Booking> CreateBookingAsync(Booking booking, CancellationToken cancellationToken = default);
    Task<IEnumerable<Booking>> GetBookingsByCustomerIdAsync(string customerId, CancellationToken cancellationToken = default);
    Task<IEnumerable<Booking>> GetAllBookingsAsync(CancellationToken cancellationToken = default);
    Task DeleteBookingAsync(string bookingId, string customerId, CancellationToken cancellationToken = default);
}
```

**Implementation:**
```csharp
// Services/BookingService.cs
namespace Ticketing.Web.Services;

public class BookingService : IBookingService
{
    private readonly CosmosClient _cosmosClient;
    private readonly ILogger<BookingService> _logger;
    
    // Implementation...
}
```

**Registration (in `ServiceCollectionExtensions.cs`):**
```csharp
services.AddScoped<IBookingService, BookingService>();
```

### Controller Pattern

**Thin Controllers - Delegation to Services:**
```csharp
// Controllers/BookingsController.cs
[ApiController]
[Route("api/[controller]")]
[Authorize]
public class BookingsController : ControllerBase
{
    private readonly IBookingService _bookingService;
    private readonly IUserService _userService;
    private readonly IOutboxService _outboxService;
    // ... other dependencies
    
    [HttpPost]
    public async Task<ActionResult<Booking>> CreateBooking([FromBody] BookingRequest request)
    {
        // Validation, authorization checks
        // Delegate to service
        var booking = await _bookingService.CreateBookingAsync(...);
        return Ok(booking);
    }
}
```

### Helper Pattern

**Stateless Utility Classes:**
```csharp
// Helpers/NavigationHelper.cs
namespace Ticketing.Web.Helpers;

public static class NavigationHelper
{
    public static string GetLandingPageUrl(ClaimsPrincipal? user)
    {
        // Stateless utility method
        // No dependencies, no state
    }
}
```

### Component Pattern

**Reusable Blazor Components:**
```razor
@* Components/BookingManagement.razor *@
@namespace Ticketing.Web.Components

<div class="booking-management">
    @* Component implementation *@
</div>
```

**Usage in Pages:**
```razor
@* Pages/Demo.razor *@
<BookingManagement OnBookingCreated="RefreshInsights" />
```

### Dependency Injection Lifetimes

**Service Registration Patterns:**
- **Scoped** - Services with per-request state (`IBookingService`, `IUserService`, `IOutboxService`)
- **Singleton** - Stateless services or shared resources (`ITelemetryService`, `CosmosClient`, `ServiceBusClient`)
- **Transient** - Lightweight, stateless services (rarely used in this project)

**Example:**
```csharp
// ServiceCollectionExtensions.cs
services.AddScoped<IBookingService, BookingService>();        // Scoped - per request
services.AddSingleton<ITelemetryService, ApplicationInsightsTelemetryService>();  // Singleton - shared
services.AddSingleton<CosmosClient>(sp => new CosmosClient(...));  // Singleton - shared connection
```

### Dependency Flow

```
Pages/Components (UI Layer)
    ↓ (inject)
Controllers (API Layer)
    ↓ (inject)
Services (Business Logic Layer)
    ↓ (inject)
CosmosClient, ServiceBusClient, etc. (Data/Infrastructure Layer)
```

**Key Rules:**
- Controllers depend on Services (not on data access directly)
- Services depend on Infrastructure (Cosmos DB, Service Bus, etc.)
- Helpers are stateless and have no dependencies
- Components depend on Services or Controllers (via HttpClient)

---

## Relationship to Other ADRs

- **[ADR-009 - Extension Methods Pattern](./ADR-009-extension-methods-pattern.md)** - The `Extensions/` directory contains extension methods for application startup configuration. This ADR complements ADR-009 by documenting the overall code organization, while ADR-009 focuses specifically on the extension methods pattern for startup.

- **[ADR-006 - Event-Driven Architecture](./ADR-006-eventdriven.md)** - Services like `OutboxService`, `OutboxProcessorService`, and `ServiceBusEventPublisher` implement the event-driven architecture patterns documented in ADR-006.

- **[ADR-015 - Application Insights Telemetry Strategy](./ADR-015-application-insights-telemetry-strategy.md)** - The `ITelemetryService` interface and `ApplicationInsightsTelemetryService` implementation in the `Services/` directory implement the telemetry strategy.

- **[ADR-016 - Managed Identity & RBAC Strategy](./ADR-016-managed-identity-rbac-strategy.md)** - Services use `DefaultAzureCredential` for authentication, implementing the managed identity strategy.

---

## References
- [ADR-009 - Extension Methods Pattern](./ADR-009-extension-methods-pattern.md) - Extension methods for startup configuration
- [ADR-006 - Event-Driven Architecture](./ADR-006-eventdriven.md) - Event-driven service implementations
- [ADR-015 - Application Insights Telemetry Strategy](./ADR-015-application-insights-telemetry-strategy.md) - Telemetry service implementation
- [ADR-016 - Managed Identity & RBAC Strategy](./ADR-016-managed-identity-rbac-strategy.md) - Authentication in services
- [ADR-018 - Error Handling & Logging Strategy](./ADR-018-error-handling-logging-strategy.md) - Error handling in controllers and services
- [ADR-019 - API Design Pattern](./ADR-019-api-design-pattern-controller-based-rest.md) - Controller-based REST API design
- [Microsoft Docs – Dependency Injection in ASP.NET Core](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection)
- [Microsoft Docs – Blazor Components](https://learn.microsoft.com/en-us/aspnet/core/blazor/components/)
- [Clean Architecture Principles](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

