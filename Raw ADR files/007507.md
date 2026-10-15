# ADR-019 – API Design Pattern: Controller-Based REST

**Status:** Accepted  
**Date:** 2025-12-01  
**Author:** Niklas Häll

---

## Context

The application requires a REST API to support the Blazor Server frontend and potentially external integrations. The API design choice affects:
- Code organization and maintainability
- Developer experience and onboarding
- Testing and testability
- Integration with authentication and authorization
- API documentation and discoverability
- Future extensibility and versioning

**Alternatives Considered:**
- **Controller-based API** - Traditional ASP.NET Core controllers with `[ApiController]` attribute
- **Minimal APIs** - .NET 6+ lightweight API endpoints using `MapGet`, `MapPost`, etc.
- **GraphQL** - Query-based API with flexible data fetching
- **gRPC** - High-performance RPC framework

---

## Decision

The application uses **Controller-based REST API** with ASP.NET Core controllers. All API endpoints are organized in controller classes using the `[ApiController]` attribute and RESTful routing conventions.

**Key Characteristics:**
- **Controller Classes** - Each resource/domain has its own controller class
- **RESTful Routing** - Standard `api/[controller]` route pattern
- **HTTP Verb Attributes** - `[HttpGet]`, `[HttpPost]`, `[HttpPut]`, `[HttpDelete]` for action methods
- **Authorization Attributes** - `[Authorize]` and role-based `[Authorize(Roles = "...")]` for security
- **No API Versioning** - Single version API (no `/api/v1/` or `/api/v2/` prefixes)
- **JSON Responses** - All responses use JSON format (configured via `[ApiController]`)

---

## Consequences

**Advantages:**
- **Familiar Pattern** - Standard ASP.NET Core pattern, well-documented and widely understood
- **Separation of Concerns** - Controllers handle HTTP concerns, services handle business logic
- **Built-in Features** - `[ApiController]` provides automatic model validation, error handling, and content negotiation
- **Dependency Injection** - Controllers support constructor injection for services, logging, and configuration
- **Authorization Integration** - Seamless integration with ASP.NET Core authorization attributes
- **Testability** - Controllers can be easily unit tested with mocking frameworks
- **Code Organization** - Clear organization by resource/domain (BookingsController, UsersController, etc.)
- **IntelliSense Support** - Strong typing and IDE support for controller actions
- **Error Handling** - Consistent error handling via `ControllerBase` and exception filters

**Disadvantages:**
- **More Boilerplate** - Controllers require class definitions and attribute decorations (more verbose than minimal APIs)
- **File Proliferation** - Each controller is a separate file (acceptable trade-off for organization)
- **No API Versioning** - Current implementation doesn't support versioning (can be added later if needed)
- **Slightly More Overhead** - Controllers have more overhead than minimal APIs (negligible for this scale)

---

## Risks / Mitigations

- **Risk:** Controllers might become bloated with too many actions.  
  **Mitigation:** Keep controllers focused on a single resource/domain. If a controller grows too large, consider splitting into multiple controllers or extracting common logic to base classes.

- **Risk:** API versioning might be needed in the future.  
  **Mitigation:** Can add versioning later using route constraints, query parameters, or headers. Current single-version approach is sufficient for MVP.

- **Risk:** Inconsistent REST conventions across controllers.  
  **Mitigation:** This ADR documents the standard conventions. Code reviews ensure consistency. All controllers follow the same pattern.

- **Risk:** Minimal APIs might be more suitable for simple endpoints.  
  **Mitigation:** Controller-based approach provides consistency across all endpoints. The slight overhead is acceptable for maintainability and organization benefits.

---

## Alternatives

- **Minimal APIs** - Use `app.MapGet()`, `app.MapPost()`, etc. for lightweight endpoints.  
  **Rejected:** While minimal APIs are simpler for basic endpoints, controllers provide better organization, testability, and integration with authorization. For a multi-endpoint API, controllers offer better maintainability and consistency.

- **GraphQL** - Use GraphQL for flexible query-based API.  
  **Rejected:** Over-engineered for MVP requirements. REST API is sufficient and more familiar to developers. GraphQL adds complexity (schema, resolvers, query parsing) without clear benefit for this use case.

- **gRPC** - Use gRPC for high-performance RPC-style API.  
  **Rejected:** REST API is more suitable for web applications. gRPC requires HTTP/2, protocol buffers, and is better suited for microservices communication. REST provides better browser compatibility and tooling support.

- **Hybrid Approach** - Use controllers for complex endpoints, minimal APIs for simple ones.  
  **Rejected:** Consistency is more valuable than mixing patterns. All endpoints using controllers provides uniform structure and maintainability.

---

## Implementation Details

### Controller Structure

**Standard Controller Pattern:**
```csharp
[ApiController]
[Route("api/[controller]")]
[Authorize]
public class BookingsController : ControllerBase
{
    private readonly IBookingService _bookingService;
    private readonly ILogger<BookingsController> _logger;

    public BookingsController(
        IBookingService bookingService,
        ILogger<BookingsController> logger)
    {
        _bookingService = bookingService ?? throw new ArgumentNullException(nameof(bookingService));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    [HttpPost]
    [Authorize(Roles = "Admin,Inspector,User")]
    public async Task<ActionResult<Booking>> CreateBooking([FromBody] Booking booking)
    {
        // Implementation...
    }
}
```

**Key Attributes:**
- `[ApiController]` - Enables automatic model validation, 400 responses for invalid models, and content negotiation
- `[Route("api/[controller]")]` - Standard REST route pattern (e.g., `api/bookings`, `api/users`)
- `[Authorize]` - Controller-level authorization (can be overridden at action level)
- `[Authorize(Roles = "...")]` - Role-based authorization for specific actions

### REST Conventions

**HTTP Verbs and Actions:**

| HTTP Verb | Convention | Example | Controller Method |
|-----------|------------|---------|-------------------|
| **GET** | Retrieve resource(s) | `GET /api/bookings/customer/{customerId}` | `GetBookingsByCustomer(string customerId)` |
| **POST** | Create resource | `POST /api/bookings` | `CreateBooking([FromBody] Booking booking)` |
| **PUT** | Update resource | `PUT /api/users/{id}` | `UpdateUser(string id, [FromBody] User user)` |
| **DELETE** | Delete resource | `DELETE /api/bookings/{bookingId}` | `DeleteBooking(string bookingId)` |

**Route Patterns:**
- **Collection:** `api/[controller]` - e.g., `api/bookings`, `api/users`
- **Resource by ID:** `api/[controller]/{id}` - e.g., `api/users/{id}`, `api/bookings/{bookingId}`
- **Nested Resources:** `api/[controller]/customer/{customerId}` - e.g., `api/bookings/customer/{customerId}`
- **Custom Actions:** `api/[controller]/action` - e.g., `api/featureflag/mini-health`, `api/auth/login`

**Response Types:**
- **200 OK** - Successful GET, PUT operations
- **201 Created** - Successful POST operations (with `CreatedAtAction`)
- **204 No Content** - Successful DELETE operations
- **400 Bad Request** - Validation errors, invalid input
- **401 Unauthorized** - Missing or invalid authentication
- **403 Forbidden** - Authenticated but insufficient permissions
- **404 Not Found** - Resource not found
- **500 Internal Server Error** - Server errors (handled by global exception handler)

### Controller Organization

**Controllers by Domain:**

| Controller | Purpose | Routes |
|------------|---------|--------|
| **BookingsController** | Booking management | `api/bookings` |
| **UsersController** | User management (Admin only) | `api/users` |
| **AuthController** | Authentication endpoints | `api/auth` |
| **FeatureFlagController** | Feature flag management (Admin only) | `api/featureflag` |
| **HealthController** | Health check endpoint | `api/health` |
| **ApplicationInsightsController** | Application Insights queries (Admin only) | `api/applicationinsights` |

**Naming Conventions:**
- Controller names: `{Resource}Controller` (e.g., `BookingsController`, `UsersController`)
- Action names: Verb-based (e.g., `CreateBooking`, `GetBookingsByCustomer`, `UpdateUser`)
- Route parameters: Match action parameters (e.g., `{id}`, `{customerId}`, `{bookingId}`)

### API Registration

**In `ServiceCollectionExtensions.cs`:**
```csharp
services.AddControllers();
```

**In `WebApplicationExtensions.cs`:**
```csharp
app.MapControllers();
```

**No Additional Configuration:**
- No API versioning configured
- No custom formatters (uses default JSON)
- No Swagger/OpenAPI (not needed for MVP, can be added later)

### Authorization Patterns

**Controller-Level Authorization:**
```csharp
[ApiController]
[Route("api/[controller]")]
[Authorize(Roles = "Admin")]  // All actions require Admin role
public class UsersController : ControllerBase
{
    // All actions inherit Admin requirement
}
```

**Action-Level Authorization:**
```csharp
[ApiController]
[Route("api/[controller]")]
[Authorize]  // Base authorization (any authenticated user)
public class BookingsController : ControllerBase
{
    [HttpPost]
    [Authorize(Roles = "Admin,Inspector,User")]  // Override for specific action
    public async Task<ActionResult<Booking>> CreateBooking(...)
    {
        // Implementation...
    }
}
```

**Anonymous Access:**
```csharp
[HttpPost("login")]
[AllowAnonymous]  // Override authorization for public endpoints
public async Task<IActionResult> Login(...)
{
    // Implementation...
}
```

### Error Response Format

**Standard Error Response:**
```json
{
  "error": "Customer email is required."
}
```

**Error Handling:**
- Validation errors return `400 Bad Request` with error message
- Authorization errors return `401 Unauthorized` or `403 Forbidden`
- Not found errors return `404 Not Found` with error message
- Server errors return `500 Internal Server Error` (production shows generic message, details in logs)

---

## Relationship to Other ADRs

- **[ADR-017 - Service/Component Organization Pattern](./ADR-017-service-component-organization-pattern.md)** - Controllers are organized in the `Controllers/` directory as documented in ADR-017. Controllers follow the thin controller pattern, delegating business logic to services.

- **[ADR-018 - Error Handling & Logging Strategy](./ADR-018-error-handling-logging-strategy.md)** - Controllers implement error handling patterns documented in ADR-018. Try-catch blocks, appropriate HTTP status codes, and structured logging are used throughout.

- **[ADR-002 - Authentication](./ADR-002-authentication.md)** - Controllers integrate with the authentication strategy (ASP.NET Identity + Entra ID) using `[Authorize]` attributes and role-based access control.

- **[ADR-015 - Application Insights Telemetry Strategy](./ADR-015-application-insights-telemetry-strategy.md)** - Controllers track custom telemetry events (e.g., `BookingCreated`) via `ITelemetryService` as documented in ADR-015.

---

## Future Considerations

**API Versioning (if needed):**
- Can be added using route constraints: `[Route("api/v{version:apiVersion}/[controller]")]`
- Or query parameter: `?api-version=1.0`
- Or header: `api-version: 1.0`
- Current single-version approach is sufficient for MVP

**API Documentation:**
- Swagger/OpenAPI can be added via `Swashbuckle.AspNetCore` package
- Not needed for MVP but can be added for future external integrations

**Rate Limiting:**
- Can be added using `Microsoft.AspNetCore.RateLimiting` middleware
- Not currently implemented but can be added if needed

---

## References
- [ADR-017 - Service/Component Organization Pattern](./ADR-017-service-component-organization-pattern.md) - Controller organization
- [ADR-018 - Error Handling & Logging Strategy](./ADR-018-error-handling-logging-strategy.md) - Error handling in controllers
- [ADR-002 - Authentication](./ADR-002-authentication.md) - Authorization in controllers
- [ADR-015 - Application Insights Telemetry Strategy](./ADR-015-application-insights-telemetry-strategy.md) - Telemetry in controllers
- [Microsoft Docs – Web API Controllers](https://learn.microsoft.com/en-us/aspnet/core/web-api/)
- [Microsoft Docs – ApiController Attribute](https://learn.microsoft.com/en-us/aspnet/core/web-api/#apicontroller-attribute)
- [Microsoft Docs – RESTful Web API Design](https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design)
- [REST API Design Best Practices](https://restfulapi.net/)

