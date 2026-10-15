---
title: "ADR-005: Prefer Minimal APIs over Controller-Based APIs"
date: 2025-11-13
status: Accepted
tags: [aspnet-core, minimal-apis, api-design, web-apis]
---

# ADR-005: Prefer Minimal APIs over Controller-Based APIs

## Status

Accepted

## Date

2025-11-13

## Context

ASP.NET Core provides two primary approaches for building HTTP APIs:

1. **Controller-based APIs**: The traditional MVC pattern using `[ApiController]` classes with action methods
2. **Minimal APIs**: A lightweight approach introduced in .NET 6, using endpoint routing with direct lambda expressions or local functions

As our organization modernizes its .NET applications and builds new services, we need to establish a consistent approach to API development. The choice between these patterns affects:
- Code organization and maintainability
- Development velocity
- Performance characteristics
- Testing strategies
- Learning curve for new developers
- Alignment with modern .NET practices

Controller-based APIs have been the standard for years, but Minimal APIs represent Microsoft's modern, performance-focused direction. Many teams continue using controllers out of habit or familiarity, while Minimal APIs offer advantages for most scenarios.

## Decision

We have decided to **prefer Minimal APIs as the default approach** for building HTTP APIs in ASP.NET Core applications.

### Requirements

**New API projects SHOULD use Minimal APIs** unless there is a specific, documented reason to use controllers.

**Existing controller-based APIs MAY remain unchanged**, but:
- New endpoints added to existing projects SHOULD follow the established pattern of that project
- During major refactoring, teams are ENCOURAGED to migrate to Minimal APIs
- Migration is OPTIONAL and should be based on cost/benefit analysis

**Controllers are DISCOURAGED but ALLOWED** when:
- Complex model binding scenarios require controller features
- Extensive use of filters that are tightly coupled to controller pipeline
- Team explicitly documents technical justification

### Minimal API Design Guidelines

#### 1. Organize Endpoints by Feature

Group related endpoints using extension methods:

```csharp
// Features/Users/UserEndpoints.cs
public static class UserEndpoints
{
    public static IEndpointRouteBuilder MapUserEndpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/users")
            .WithTags("Users")
            .WithOpenApi();

        group.MapGet("/", GetAllUsers)
            .WithName("GetAllUsers")
            .Produces<IEnumerable<UserDto>>();

        group.MapGet("/{id}", GetUserById)
            .WithName("GetUserById")
            .Produces<UserDto>()
            .Produces(404);

        group.MapPost("/", CreateUser)
            .WithName("CreateUser")
            .Produces<UserDto>(201)
            .ProducesValidationProblem();

        group.MapPut("/{id}", UpdateUser)
            .WithName("UpdateUser")
            .Produces(204)
            .Produces(404)
            .ProducesValidationProblem();

        group.MapDelete("/{id}", DeleteUser)
            .WithName("DeleteUser")
            .Produces(204)
            .Produces(404);

        return app;
    }

    private static async Task<Ok<IEnumerable<UserDto>>> GetAllUsers(
        IUserService userService)
    {
        var users = await userService.GetAllAsync();
        return TypedResults.Ok(users);
    }

    private static async Task<Results<Ok<UserDto>, NotFound>> GetUserById(
        string id,
        IUserService userService)
    {
        var user = await userService.GetByIdAsync(id);
        return user is not null
            ? TypedResults.Ok(user)
            : TypedResults.NotFound();
    }

    private static async Task<Results<Created<UserDto>, ValidationProblem>> CreateUser(
        CreateUserRequest request,
        IUserService userService,
        IValidator<CreateUserRequest> validator)
    {
        var validationResult = await validator.ValidateAsync(request);
        if (!validationResult.IsValid)
        {
            return TypedResults.ValidationProblem(validationResult.ToDictionary());
        }

        var user = await userService.CreateAsync(request);
        return TypedResults.Created($"/api/users/{user.Id}", user);
    }

    private static async Task<Results<NoContent, NotFound, ValidationProblem>> UpdateUser(
        string id,
        UpdateUserRequest request,
        IUserService userService,
        IValidator<UpdateUserRequest> validator)
    {
        var validationResult = await validator.ValidateAsync(request);
        if (!validationResult.IsValid)
        {
            return TypedResults.ValidationProblem(validationResult.ToDictionary());
        }

        var success = await userService.UpdateAsync(id, request);
        return success
            ? TypedResults.NoContent()
            : TypedResults.NotFound();
    }

    private static async Task<Results<NoContent, NotFound>> DeleteUser(
        string id,
        IUserService userService)
    {
        var success = await userService.DeleteAsync(id);
        return success
            ? TypedResults.NoContent()
            : TypedResults.NotFound();
    }
}
```

#### 2. Use Typed Results

Always use `TypedResults` or `Results<>` for type-safe responses:

```csharp
// ❌ Avoid - No type safety
app.MapGet("/users/{id}", async (string id, IUserService service) =>
{
    var user = await service.GetByIdAsync(id);
    return user is not null ? Results.Ok(user) : Results.NotFound();
});

// ✅ Prefer - Type-safe with explicit return types
app.MapGet("/users/{id}", async Task<Results<Ok<UserDto>, NotFound>> (
    string id,
    IUserService service) =>
{
    var user = await service.GetByIdAsync(id);
    return user is not null
        ? TypedResults.Ok(user)
        : TypedResults.NotFound();
});
```

#### 3. Use Endpoint Groups for Common Configuration

```csharp
var apiGroup = app.MapGroup("/api")
    .RequireAuthorization()
    .AddEndpointFilter<ValidationFilter>()
    .WithOpenApi();

apiGroup.MapUserEndpoints();
apiGroup.MapOrderEndpoints();
apiGroup.MapProductEndpoints();
```

#### 4. Leverage Endpoint Filters

Replace controller filters with endpoint filters:

```csharp
public class ValidationFilter<T> : IEndpointFilter
{
    public async ValueTask<object?> InvokeAsync(
        EndpointFilterInvocationContext context,
        EndpointFilterDelegate next)
    {
        var validator = context.HttpContext.RequestServices
            .GetService<IValidator<T>>();

        if (validator is not null)
        {
            var request = context.Arguments
                .OfType<T>()
                .FirstOrDefault();

            if (request is not null)
            {
                var result = await validator.ValidateAsync(request);
                if (!result.IsValid)
                {
                    return TypedResults.ValidationProblem(result.ToDictionary());
                }
            }
        }

        return await next(context);
    }
}
```

#### 5. Use Extension Methods for Registration

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddUserServices();
builder.Services.AddOrderServices();

var app = builder.Build();

app.MapUserEndpoints();
app.MapOrderEndpoints();
app.MapProductEndpoints();

app.Run();
```

#### 6. Handle Complex Scenarios

For complex operations, extract to handler classes:

```csharp
// Handlers/CreateOrderHandler.cs
public class CreateOrderHandler
{
    private readonly IOrderService _orderService;
    private readonly IInventoryService _inventoryService;
    private readonly IPaymentService _paymentService;
    private readonly ILogger<CreateOrderHandler> _logger;

    public CreateOrderHandler(
        IOrderService orderService,
        IInventoryService inventoryService,
        IPaymentService paymentService,
        ILogger<CreateOrderHandler> logger)
    {
        _orderService = orderService;
        _inventoryService = inventoryService;
        _paymentService = paymentService;
        _logger = logger;
    }

    public async Task<Results<Created<OrderDto>, ValidationProblem, BadRequest<string>>> ExecuteAsync(
        CreateOrderRequest request)
    {
        using var activity = Activity.Current?.Source.StartActivity("CreateOrder");
        activity?.SetTag("order.items.count", request.Items.Count);

        // Check inventory
        var inventoryCheck = await _inventoryService.CheckAvailabilityAsync(request.Items);
        if (!inventoryCheck.AllAvailable)
        {
            return TypedResults.BadRequest($"Items not available: {string.Join(", ", inventoryCheck.UnavailableItems)}");
        }

        // Process payment
        var paymentResult = await _paymentService.ProcessAsync(request.PaymentInfo);
        if (!paymentResult.Success)
        {
            return TypedResults.BadRequest("Payment processing failed");
        }

        // Create order
        var order = await _orderService.CreateAsync(request);
        
        _logger.LogInformation("Order {OrderId} created successfully", order.Id);
        
        return TypedResults.Created($"/api/orders/{order.Id}", order);
    }
}

// OrderEndpoints.cs
public static class OrderEndpoints
{
    public static IEndpointRouteBuilder MapOrderEndpoints(this IEndpointRouteBuilder app)
    {
        app.MapPost("/api/orders", async (
            CreateOrderRequest request,
            CreateOrderHandler handler) =>
            await handler.ExecuteAsync(request));

        return app;
    }
}
```

### Testing Minimal APIs

#### Unit Testing Handlers

```csharp
public class CreateOrderHandlerTests
{
    [Fact]
    public async Task ExecuteAsync_WithValidRequest_ReturnsCreatedResult()
    {
        // Arrange
        var orderService = new Mock<IOrderService>();
        var inventoryService = new Mock<IInventoryService>();
        var paymentService = new Mock<IPaymentService>();
        var logger = new Mock<ILogger<CreateOrderHandler>>();

        var handler = new CreateOrderHandler(
            orderService.Object,
            inventoryService.Object,
            paymentService.Object,
            logger.Object);

        var request = new CreateOrderRequest { /* ... */ };

        // Setup mocks...

        // Act
        var result = await handler.ExecuteAsync(request);

        // Assert
        Assert.IsType<Created<OrderDto>>(result.Result);
    }
}
```

#### Integration Testing

```csharp
public class UserEndpointsTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;

    public UserEndpointsTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory;
    }

    [Fact]
    public async Task GetUser_ReturnsOkWithUser()
    {
        // Arrange
        var client = _factory.CreateClient();

        // Act
        var response = await client.GetAsync("/api/users/123");

        // Assert
        response.EnsureSuccessStatusCode();
        var user = await response.Content.ReadFromJsonAsync<UserDto>();
        Assert.NotNull(user);
    }
}
```

## Rationale

### Why Prefer Minimal APIs?

1. **Performance**: Minimal APIs have lower overhead, faster startup, and reduced memory footprint
   - No controller instantiation
   - Direct routing without MVC middleware
   - Faster request processing

2. **Simplicity**: Less ceremony and boilerplate code
   - No base classes or attributes required
   - Direct mapping from routes to handlers
   - Easier to understand for new developers

3. **Modern .NET Direction**: Aligns with Microsoft's strategic direction
   - Featured in .NET templates
   - Active development and improvements
   - Better integration with new features (Aspire, Native AOT)

4. **Type Safety**: Better compile-time checking with typed results
   - `Results<T1, T2, T3>` provides explicit return type unions
   - Compile-time verification of response types
   - Better IntelliSense and tooling support

5. **Testability**: Easier to test handlers independently
   - Handlers are just methods or classes
   - No controller context required
   - Simple dependency injection

6. **Cloud Native**: Better suited for serverless and container scenarios
   - Faster cold starts
   - Lower memory usage
   - Smaller deployment size

7. **OpenAPI Integration**: First-class OpenAPI support
   - Built-in `.WithOpenApi()` support
   - Automatic schema generation
   - Better Swagger/OpenAPI integration

### Why Discourage Controllers?

1. **Overhead**: Controllers add unnecessary abstraction for most APIs
   - Base class inheritance
   - Model binding complexity
   - Action filter pipeline overhead

2. **Verbosity**: More boilerplate code required
   - Class and method declarations
   - Attributes for routing and validation
   - ControllerBase inheritance

3. **Legacy Pattern**: Controllers are a legacy pattern from MVC
   - Designed for server-side rendering
   - Carries baggage from view-focused architecture
   - Not optimized for modern API scenarios

4. **Tight Coupling**: Controllers tend to accumulate too many responsibilities
   - Often become "god objects"
   - Harder to maintain single responsibility principle
   - More difficult to refactor

## Consequences

### Positive

- **Better Performance**: Reduced overhead and faster response times
- **Simplified Codebase**: Less boilerplate and easier to understand
- **Modern Development**: Aligned with current .NET best practices
- **Easier Testing**: Simpler unit and integration testing
- **Smaller Deployment**: Reduced memory footprint and faster startup
- **Type Safety**: Better compile-time guarantees with typed results
- **Future-Proof**: Ready for Native AOT and other modern .NET features

### Negative

- **Learning Curve**: Developers familiar with controllers need to learn new patterns
- **Migration Effort**: Existing controller-based APIs may need refactoring
- **Organizational Friction**: Some advanced controller features not directly available
- **Pattern Change**: Need to establish new conventions and practices
- **Tooling Gaps**: Some third-party tools may have better controller support

### Neutral

- **Different Organization**: File and folder structure differs from controller approach
- **Filter Mechanism**: Different filter implementation (endpoint filters vs action filters)
- **Testing Approach**: Different testing patterns and strategies
- **Documentation**: Need to update guidelines and examples

## Alternatives Considered

### Keep Using Controllers (Rejected)

- **Pros**: Familiar to team, existing knowledge, no migration needed
- **Cons**: Misses performance benefits, not aligned with modern .NET direction, more boilerplate
- **Reason for rejection**: Controllers represent legacy pattern; Minimal APIs are the future

### Mixed Approach - Both Patterns (Rejected)

- **Pros**: Maximum flexibility, gradual transition
- **Cons**: Inconsistent codebase, confusion about which to use, double the patterns to maintain
- **Reason for rejection**: Inconsistency leads to maintenance burden and developer confusion

### Require Immediate Migration of All Controllers (Rejected)

- **Pros**: Instant consistency, immediate performance benefits
- **Cons**: High migration cost, risk of introducing bugs, disrupts ongoing work
- **Reason for rejection**: Cost outweighs benefits; gradual adoption is more pragmatic

## Implementation

### Phase 1: Immediate (New Projects)
- All new API projects MUST use Minimal APIs
- Provide templates and examples
- Document patterns and best practices
- Conduct training sessions

### Phase 2: Gradual Adoption (Existing Projects - 12 Months)
- New endpoints in existing projects MAY continue using existing pattern
- During refactoring, CONSIDER migrating to Minimal APIs
- No forced migration unless cost-justified
- Share success stories and lessons learned

### Phase 3: Long-term (Ongoing)
- Continue refining Minimal API patterns
- Build shared libraries for common scenarios
- Evaluate migration of legacy controllers on case-by-case basis

## References

- [Minimal APIs Overview](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis/overview)
- [Minimal APIs vs Controllers](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/apis)
- [Minimal API Filters](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis/min-api-filters)
- [TypedResults](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis/responses)
- [Testing Minimal APIs](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis/test-min-api)

## Related ADRs

- **ADR-001**: Migration to .NET 10 - Minimal APIs work best with modern .NET versions
- **ADR-002**: Adoption of Aspire - Aspire templates use Minimal APIs by default
- **ADR-004**: OpenTelemetry - Both patterns work well with OpenTelemetry
