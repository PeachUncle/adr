---
title: "ADR-006: Adoption of CQRS Pattern"
date: 2025-11-13
status: Accepted
tags: [cqrs, architecture, patterns, command-query-separation]
---

# ADR-006: Adoption of CQRS Pattern

## Status

Accepted

## Date

2025-11-13

## Context

Modern application development requires clear separation of concerns, testability, and maintainability. As our applications grow in complexity, we need a consistent pattern for handling requests that modify state (commands) versus requests that query state (queries).

Command Query Responsibility Segregation (CQRS) is a pattern that separates read operations from write operations. This separation provides several benefits:

- **Clear Intent**: Commands represent actions/operations, queries represent data retrieval
- **Single Responsibility**: Each handler does one thing well
- **Testability**: Handlers can be tested independently with mocked dependencies
- **Scalability**: Commands and queries can be optimized and scaled independently
- **Audit Trail**: Commands provide natural boundaries for tracking changes
- **Simplified Controllers/Endpoints**: API handlers become thin orchestration layers

Without a standardized approach, our codebase risks inconsistency, with some teams putting logic directly in controllers, others in service layers, and no clear pattern for complex operations.

## Decision

We have decided to **mandate the use of the CQRS pattern for all new projects** that handle business logic beyond simple CRUD operations.

### Requirements

**All new projects MUST implement CQRS pattern** with the following structure:

1. **DTOs (Data Transfer Objects)** arrive at the HTTP endpoint as C# records
2. **HTTP handler** creates a Command or Query from the DTO
3. **Command/Query** is passed to an appropriate Handler
4. **Handler** executes business logic and returns a result (optionally a DTO)
5. **HTTP handler** returns the result in the HTTP response

### CQRS Flow Diagram

```
HTTP Request (DTO)
      ↓
HTTP Handler (Minimal API/Controller)
      ↓
Command/Query Creation
      ↓
Command/Query Handler
      ↓
Business Logic Execution
      ↓
Result (Optional DTO)
      ↓
HTTP Response
```

### Base Classes and Interfaces

All CQRS implementations MUST use the following base classes and interfaces.

#### Base Command and Query

```csharp
// Commands represent state changes (write operations)
public interface ICommand<TResult>
{
}

public interface ICommand : ICommand<Unit>
{
}

// Queries represent data retrieval (read operations)
public interface IQuery<TResult>
{
}

// Unit type for commands that don't return a value
public readonly record struct Unit
{
    public static readonly Unit Value = new();
}
```

#### Base Handlers

```csharp
// Command handler that returns a result
public interface ICommandHandler<in TCommand, TResult> 
    where TCommand : ICommand<TResult>
{
    Task<TResult> HandleAsync(TCommand command, CancellationToken cancellationToken = default);
}

// Command handler that returns no result (void)
public interface ICommandHandler<in TCommand> 
    where TCommand : ICommand
{
    Task HandleAsync(TCommand command, CancellationToken cancellationToken = default);
}

// Query handler
public interface IQueryHandler<in TQuery, TResult> 
    where TQuery : IQuery<TResult>
{
    Task<TResult> HandleAsync(TQuery query, CancellationToken cancellationToken = default);
}
```

### Implementation Guidelines

#### Handler Invocation

**Handlers MUST be invoked directly through dependency injection**, not through a mediator library. The HTTP endpoint receives the handler as a dependency and calls it directly.

**Benefits of direct invocation:**
- **Explicit**: Clear dependency chain, easy to trace
- **Performance**: No reflection or dynamic dispatch overhead
- **Simplicity**: No additional libraries or configuration
- **Debugging**: Straightforward debugging and stack traces
- **Type Safety**: Full compile-time checking of handler signatures

#### 1. Define Commands as Records

Commands should be immutable records representing an intent to change state:

```csharp
// Commands/CreateOrderCommand.cs
public sealed record CreateOrderCommand(
    string CustomerId,
    IReadOnlyList<OrderItemDto> Items,
    PaymentInfoDto PaymentInfo) : ICommand<OrderDto>;

public sealed record UpdateOrderStatusCommand(
    string OrderId,
    OrderStatus NewStatus) : ICommand;

public sealed record DeleteOrderCommand(string OrderId) : ICommand;
```

#### 2. Define Queries as Records

Queries should be immutable records representing an intent to retrieve data:

```csharp
// Queries/GetOrderByIdQuery.cs
public sealed record GetOrderByIdQuery(string OrderId) : IQuery<OrderDto?>;

public sealed record GetOrdersByCustomerQuery(
    string CustomerId,
    int Page = 1,
    int PageSize = 20) : IQuery<PagedResult<OrderDto>>;

public sealed record SearchOrdersQuery(
    string? SearchTerm,
    OrderStatus? Status,
    DateOnly? FromDate,
    DateOnly? ToDate) : IQuery<IReadOnlyList<OrderDto>>;
```

#### 3. Implement Command Handlers

Command handlers contain business logic for state changes:

```csharp
// Handlers/CreateOrderCommandHandler.cs
public sealed class CreateOrderCommandHandler : ICommandHandler<CreateOrderCommand, OrderDto>
{
    private readonly IOrderRepository _orderRepository;
    private readonly IInventoryService _inventoryService;
    private readonly IPaymentService _paymentService;
    private readonly ILogger<CreateOrderCommandHandler> _logger;

    public CreateOrderCommandHandler(
        IOrderRepository orderRepository,
        IInventoryService inventoryService,
        IPaymentService paymentService,
        ILogger<CreateOrderCommandHandler> logger)
    {
        _orderRepository = orderRepository;
        _inventoryService = inventoryService;
        _paymentService = paymentService;
        _logger = logger;
    }

    public async Task<OrderDto> HandleAsync(
        CreateOrderCommand command,
        CancellationToken cancellationToken = default)
    {
        using var activity = Activity.Current?.Source.StartActivity("CreateOrder");
        activity?.SetTag("customer.id", command.CustomerId);
        activity?.SetTag("items.count", command.Items.Count);

        // Validate inventory
        var inventoryCheck = await _inventoryService.CheckAvailabilityAsync(
            command.Items,
            cancellationToken);

        if (!inventoryCheck.AllAvailable)
        {
            throw new InsufficientInventoryException(inventoryCheck.UnavailableItems);
        }

        // Process payment
        var paymentResult = await _paymentService.ProcessAsync(
            command.PaymentInfo,
            cancellationToken);

        if (!paymentResult.Success)
        {
            throw new PaymentFailedException(paymentResult.ErrorMessage);
        }

        // Create order
        var order = Order.Create(
            command.CustomerId,
            command.Items.Select(i => new OrderItem(i.ProductId, i.Quantity, i.Price)).ToList(),
            paymentResult.TransactionId);

        await _orderRepository.AddAsync(order, cancellationToken);
        await _orderRepository.SaveChangesAsync(cancellationToken);

        _logger.LogInformation("Order {OrderId} created for customer {CustomerId}",
            order.Id, command.CustomerId);

        return MapToDto(order);
    }

    private static OrderDto MapToDto(Order order) => new(
        order.Id,
        order.CustomerId,
        order.Items.Select(i => new OrderItemDto(i.ProductId, i.Quantity, i.Price)).ToList(),
        order.Status,
        order.CreatedAt);
}
```

#### 4. Implement Query Handlers

Query handlers contain logic for data retrieval:

```csharp
// Handlers/GetOrderByIdQueryHandler.cs
public sealed class GetOrderByIdQueryHandler : IQueryHandler<GetOrderByIdQuery, OrderDto?>
{
    private readonly IOrderRepository _orderRepository;
    private readonly ILogger<GetOrderByIdQueryHandler> _logger;

    public GetOrderByIdQueryHandler(
        IOrderRepository orderRepository,
        ILogger<GetOrderByIdQueryHandler> logger)
    {
        _orderRepository = orderRepository;
        _logger = logger;
    }

    public async Task<OrderDto?> HandleAsync(
        GetOrderByIdQuery query,
        CancellationToken cancellationToken = default)
    {
        using var activity = Activity.Current?.Source.StartActivity("GetOrderById");
        activity?.SetTag("order.id", query.OrderId);

        var order = await _orderRepository.GetByIdAsync(query.OrderId, cancellationToken);

        if (order is null)
        {
            _logger.LogWarning("Order {OrderId} not found", query.OrderId);
            return null;
        }

        return new OrderDto(
            order.Id,
            order.CustomerId,
            order.Items.Select(i => new OrderItemDto(i.ProductId, i.Quantity, i.Price)).ToList(),
            order.Status,
            order.CreatedAt);
    }
}
```

#### 5. Wire Up in Minimal API Endpoints

```csharp
// Endpoints/OrderEndpoints.cs
public static class OrderEndpoints
{
    public static IEndpointRouteBuilder MapOrderEndpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/orders")
            .WithTags("Orders")
            .WithOpenApi();

        // Command: Create order
        group.MapPost("/", CreateOrder)
            .WithName("CreateOrder")
            .Produces<OrderDto>(201)
            .ProducesValidationProblem()
            .Produces<ProblemDetails>(400);

        // Command: Update order status
        group.MapPatch("/{id}/status", UpdateOrderStatus)
            .WithName("UpdateOrderStatus")
            .Produces(204)
            .Produces(404);

        // Query: Get order by ID
        group.MapGet("/{id}", GetOrderById)
            .WithName("GetOrderById")
            .Produces<OrderDto>()
            .Produces(404);

        // Query: Get orders by customer
        group.MapGet("/customer/{customerId}", GetOrdersByCustomer)
            .WithName("GetOrdersByCustomer")
            .Produces<PagedResult<OrderDto>>();

        return app;
    }

    private static async Task<Results<Created<OrderDto>, ValidationProblem, ProblemHttpResult>> CreateOrder(
        CreateOrderRequest request,
        ICommandHandler<CreateOrderCommand, OrderDto> handler,
        IValidator<CreateOrderRequest> validator,
        CancellationToken cancellationToken)
    {
        // Validate DTO
        var validationResult = await validator.ValidateAsync(request, cancellationToken);
        if (!validationResult.IsValid)
        {
            return TypedResults.ValidationProblem(validationResult.ToDictionary());
        }

        // Create command from DTO
        var command = new CreateOrderCommand(
            request.CustomerId,
            request.Items,
            request.PaymentInfo);

        try
        {
            // Execute command via handler
            var result = await handler.HandleAsync(command, cancellationToken);
            return TypedResults.Created($"/api/orders/{result.Id}", result);
        }
        catch (InsufficientInventoryException ex)
        {
            return TypedResults.Problem(
                title: "Insufficient Inventory",
                detail: ex.Message,
                statusCode: StatusCodes.Status400BadRequest);
        }
        catch (PaymentFailedException ex)
        {
            return TypedResults.Problem(
                title: "Payment Failed",
                detail: ex.Message,
                statusCode: StatusCodes.Status400BadRequest);
        }
    }

    private static async Task<Results<NoContent, NotFound>> UpdateOrderStatus(
        string id,
        UpdateOrderStatusRequest request,
        ICommandHandler<UpdateOrderStatusCommand> handler,
        CancellationToken cancellationToken)
    {
        var command = new UpdateOrderStatusCommand(id, request.NewStatus);

        try
        {
            await handler.HandleAsync(command, cancellationToken);
            return TypedResults.NoContent();
        }
        catch (OrderNotFoundException)
        {
            return TypedResults.NotFound();
        }
    }

    private static async Task<Results<Ok<OrderDto>, NotFound>> GetOrderById(
        string id,
        IQueryHandler<GetOrderByIdQuery, OrderDto?> handler,
        CancellationToken cancellationToken)
    {
        var query = new GetOrderByIdQuery(id);
        var result = await handler.HandleAsync(query, cancellationToken);

        return result is not null
            ? TypedResults.Ok(result)
            : TypedResults.NotFound();
    }

    private static async Task<Ok<PagedResult<OrderDto>>> GetOrdersByCustomer(
        string customerId,
        int page,
        int pageSize,
        IQueryHandler<GetOrdersByCustomerQuery, PagedResult<OrderDto>> handler,
        CancellationToken cancellationToken)
    {
        var query = new GetOrdersByCustomerQuery(customerId, page, pageSize);
        var result = await handler.HandleAsync(query, cancellationToken);
        return TypedResults.Ok(result);
    }
}
```

#### 6. Register Handlers with Dependency Injection

```csharp
// ServiceCollectionExtensions.cs
public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddOrderHandlers(this IServiceCollection services)
    {
        // Register command handlers
        services.AddScoped<ICommandHandler<CreateOrderCommand, OrderDto>, CreateOrderCommandHandler>();
        services.AddScoped<ICommandHandler<UpdateOrderStatusCommand>, UpdateOrderStatusCommandHandler>();
        services.AddScoped<ICommandHandler<DeleteOrderCommand>, DeleteOrderCommandHandler>();

        // Register query handlers
        services.AddScoped<IQueryHandler<GetOrderByIdQuery, OrderDto?>, GetOrderByIdQueryHandler>();
        services.AddScoped<IQueryHandler<GetOrdersByCustomerQuery, PagedResult<OrderDto>>, GetOrdersByCustomerQueryHandler>();

        return services;
    }
}

// Program.cs
builder.Services.AddOrderHandlers();
```

### Testing CQRS Handlers

#### Unit Testing Command Handlers

```csharp
public class CreateOrderCommandHandlerTests
{
    [Fact]
    public async Task HandleAsync_WithValidCommand_CreatesOrder()
    {
        // Arrange
        var orderRepository = new Mock<IOrderRepository>();
        var inventoryService = new Mock<IInventoryService>();
        var paymentService = new Mock<IPaymentService>();
        var logger = new Mock<ILogger<CreateOrderCommandHandler>>();

        inventoryService
            .Setup(x => x.CheckAvailabilityAsync(It.IsAny<IReadOnlyList<OrderItemDto>>(), default))
            .ReturnsAsync(new InventoryCheckResult(true, []));

        paymentService
            .Setup(x => x.ProcessAsync(It.IsAny<PaymentInfoDto>(), default))
            .ReturnsAsync(new PaymentResult(true, "txn-123", null));

        var handler = new CreateOrderCommandHandler(
            orderRepository.Object,
            inventoryService.Object,
            paymentService.Object,
            logger.Object);

        var command = new CreateOrderCommand(
            "customer-123",
            new List<OrderItemDto> { new("product-1", 2, 10.00m) },
            new PaymentInfoDto("card", "****1234"));

        // Act
        var result = await handler.HandleAsync(command);

        // Assert
        Assert.NotNull(result);
        Assert.Equal("customer-123", result.CustomerId);
        orderRepository.Verify(x => x.AddAsync(It.IsAny<Order>(), default), Times.Once);
        orderRepository.Verify(x => x.SaveChangesAsync(default), Times.Once);
    }

    [Fact]
    public async Task HandleAsync_WithInsufficientInventory_ThrowsException()
    {
        // Arrange
        var orderRepository = new Mock<IOrderRepository>();
        var inventoryService = new Mock<IInventoryService>();
        var paymentService = new Mock<IPaymentService>();
        var logger = new Mock<ILogger<CreateOrderCommandHandler>>();

        inventoryService
            .Setup(x => x.CheckAvailabilityAsync(It.IsAny<IReadOnlyList<OrderItemDto>>(), default))
            .ReturnsAsync(new InventoryCheckResult(false, ["product-1"]));

        var handler = new CreateOrderCommandHandler(
            orderRepository.Object,
            inventoryService.Object,
            paymentService.Object,
            logger.Object);

        var command = new CreateOrderCommand(
            "customer-123",
            new List<OrderItemDto> { new("product-1", 2, 10.00m) },
            new PaymentInfoDto("card", "****1234"));

        // Act & Assert
        await Assert.ThrowsAsync<InsufficientInventoryException>(() =>
            handler.HandleAsync(command));
    }
}
```

#### Unit Testing Query Handlers

```csharp
public class GetOrderByIdQueryHandlerTests
{
    [Fact]
    public async Task HandleAsync_WithExistingOrder_ReturnsOrderDto()
    {
        // Arrange
        var orderRepository = new Mock<IOrderRepository>();
        var logger = new Mock<ILogger<GetOrderByIdQueryHandler>>();

        var order = Order.Create("customer-123", [], "txn-123");
        orderRepository
            .Setup(x => x.GetByIdAsync("order-123", default))
            .ReturnsAsync(order);

        var handler = new GetOrderByIdQueryHandler(orderRepository.Object, logger.Object);
        var query = new GetOrderByIdQuery("order-123");

        // Act
        var result = await handler.HandleAsync(query);

        // Assert
        Assert.NotNull(result);
        Assert.Equal("customer-123", result.CustomerId);
    }

    [Fact]
    public async Task HandleAsync_WithNonExistentOrder_ReturnsNull()
    {
        // Arrange
        var orderRepository = new Mock<IOrderRepository>();
        var logger = new Mock<ILogger<GetOrderByIdQueryHandler>>();

        orderRepository
            .Setup(x => x.GetByIdAsync("order-999", default))
            .ReturnsAsync((Order?)null);

        var handler = new GetOrderByIdQueryHandler(orderRepository.Object, logger.Object);
        var query = new GetOrderByIdQuery("order-999");

        // Act
        var result = await handler.HandleAsync(query);

        // Assert
        Assert.Null(result);
    }
}
```

### Shared Core Library

**When multiple projects use CQRS**, the base interfaces and types MUST be moved to a shared core library to avoid duplication.

#### Create Core Library

```
src/
  Core/
    Company.Product.Core/
      Company.Product.Core.csproj
      CQRS/
        ICommand.cs
        IQuery.cs
        ICommandHandler.cs
        IQueryHandler.cs
        Unit.cs
```

#### Core Library Content

```csharp
// Company.Product.Core/CQRS/ICommand.cs
namespace Company.Product.Core.CQRS;

/// <summary>
/// Represents a command that produces a result.
/// </summary>
/// <typeparam name="TResult">The type of result produced by the command.</typeparam>
public interface ICommand<TResult>
{
}

/// <summary>
/// Represents a command that does not produce a result.
/// </summary>
public interface ICommand : ICommand<Unit>
{
}

// Company.Product.Core/CQRS/IQuery.cs
namespace Company.Product.Core.CQRS;

/// <summary>
/// Represents a query that returns data.
/// </summary>
/// <typeparam name="TResult">The type of data returned by the query.</typeparam>
public interface IQuery<TResult>
{
}

// Company.Product.Core/CQRS/ICommandHandler.cs
namespace Company.Product.Core.CQRS;

/// <summary>
/// Handles a command that produces a result.
/// </summary>
/// <typeparam name="TCommand">The type of command to handle.</typeparam>
/// <typeparam name="TResult">The type of result produced.</typeparam>
public interface ICommandHandler<in TCommand, TResult>
    where TCommand : ICommand<TResult>
{
    /// <summary>
    /// Handles the specified command.
    /// </summary>
    /// <param name="command">The command to handle.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>The result of handling the command.</returns>
    Task<TResult> HandleAsync(TCommand command, CancellationToken cancellationToken = default);
}

/// <summary>
/// Handles a command that does not produce a result.
/// </summary>
/// <typeparam name="TCommand">The type of command to handle.</typeparam>
public interface ICommandHandler<in TCommand>
    where TCommand : ICommand
{
    /// <summary>
    /// Handles the specified command.
    /// </summary>
    /// <param name="command">The command to handle.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    Task HandleAsync(TCommand command, CancellationToken cancellationToken = default);
}

// Company.Product.Core/CQRS/IQueryHandler.cs
namespace Company.Product.Core.CQRS;

/// <summary>
/// Handles a query that returns data.
/// </summary>
/// <typeparam name="TQuery">The type of query to handle.</typeparam>
/// <typeparam name="TResult">The type of data returned.</typeparam>
public interface IQueryHandler<in TQuery, TResult>
    where TQuery : IQuery<TResult>
{
    /// <summary>
    /// Handles the specified query.
    /// </summary>
    /// <param name="query">The query to handle.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>The data requested by the query.</returns>
    Task<TResult> HandleAsync(TQuery query, CancellationToken cancellationToken = default);
}

// Company.Product.Core/CQRS/Unit.cs
namespace Company.Product.Core.CQRS;

/// <summary>
/// Represents a void return type for commands that don't return a value.
/// </summary>
public readonly record struct Unit
{
    /// <summary>
    /// Gets the singleton instance of Unit.
    /// </summary>
    public static readonly Unit Value = new();
}
```

#### Usage in Projects

```xml
<!-- Company.Product.Orders/Company.Product.Orders.csproj -->
<ItemGroup>
  <ProjectReference Include="..\Core\Company.Product.Core\Company.Product.Core.csproj" />
</ItemGroup>
```

```csharp
using Company.Product.Core.CQRS;

public sealed record CreateOrderCommand(...) : ICommand<OrderDto>;

public sealed class CreateOrderCommandHandler 
    : ICommandHandler<CreateOrderCommand, OrderDto>
{
    // Implementation
}
```

## Rationale

### Why CQRS?

1. **Separation of Concerns**: Clear distinction between reads and writes
2. **Single Responsibility**: Each handler does one specific thing
3. **Testability**: Handlers are easy to unit test with mocked dependencies
4. **Maintainability**: Easy to find and modify specific operations
5. **Scalability**: Commands and queries can be optimized independently
6. **Audit Trail**: Commands provide natural audit boundaries
7. **Performance**: Queries can be optimized differently from commands
8. **Team Productivity**: Reduces cognitive load by making code structure predictable

### Why Records for Commands/Queries?

1. **Immutability**: Records are immutable by default, preventing accidental changes
2. **Value Semantics**: Equality based on values, not references
3. **Concise Syntax**: Less boilerplate than classes
4. **Pattern Matching**: Better support for pattern matching scenarios
5. **Intent**: Clearly communicates that these are data transfer objects

### Why Mandatory for New Projects?

1. **Consistency**: All new code follows the same pattern
2. **Onboarding**: New developers learn one clear pattern
3. **Code Reviews**: Easier to review when structure is standardized
4. **Tooling**: Can build tools and analyzers around consistent patterns
5. **Future-Proofing**: Easy to extend with mediator pattern, event sourcing, etc.

### Why Shared Core Library?

1. **DRY Principle**: Define base interfaces once, use everywhere
2. **Consistency**: All projects use identical base types
3. **Versioning**: Update CQRS infrastructure in one place
4. **Evolution**: Easy to enhance base types with new capabilities
5. **Documentation**: Single source of truth for CQRS implementation

## Consequences

### Positive

- **Clear Structure**: Predictable code organization across all projects
- **Better Testability**: Handlers are isolated and easy to test
- **Improved Maintainability**: Easy to find and modify specific operations
- **Reduced Coupling**: Dependencies are clear and explicit
- **Better Performance**: Queries can be optimized independently of commands
- **Audit Trail**: Command history provides natural audit log
- **Scalability**: Read and write paths can scale independently
- **Team Efficiency**: Developers know exactly where to find/add code

### Negative

- **Learning Curve**: Developers need to learn CQRS pattern
- **More Files**: Each operation requires command/query and handler files
- **Initial Overhead**: More upfront structure for simple CRUD operations
- **Boilerplate**: Some repetition in handler registration
- **Complexity**: May be overkill for very simple applications

### Neutral

- **File Organization**: Need consistent conventions for organizing commands/queries/handlers
- **Dependency Injection**: More services to register
- **Testing Strategy**: Different testing approach than traditional service layer
- **Documentation**: Need clear examples and guidelines

## Alternatives Considered

### Traditional Service Layer (Rejected)

- **Pros**: Familiar pattern, less files, simpler for small apps
- **Cons**: Services tend to grow too large, harder to test, unclear boundaries
- **Reason for rejection**: Doesn't scale well, leads to god objects

### MediatR Library (Explicitly Rejected)

- **Pros**: Industry-standard library, pipeline behaviors, automatic handler discovery
- **Cons**: External dependency, performance overhead, "magic" behavior, additional abstraction layer
- **Reason for rejection**: Adds unnecessary complexity and dependency. Direct handler invocation is simpler, more explicit, and performs better. The pattern works perfectly well with direct DI injection.

### Anemic Domain Model with Transaction Scripts (Rejected)

- **Pros**: Very simple, minimal structure
- **Cons**: No clear boundaries, business logic scattered, hard to maintain
- **Reason for rejection**: Leads to unmaintainable code over time

### Full Event Sourcing with CQRS (Rejected as Default)

- **Pros**: Complete audit trail, time travel, sophisticated patterns
- **Cons**: High complexity, steep learning curve, infrastructure requirements
- **Reason for rejection**: Too complex for most applications. Can be adopted later if needed

## Implementation

### Phase 1: Immediate (New Projects)
- All new projects MUST implement CQRS pattern
- Create shared core library with base interfaces
- Provide project templates and examples
- Conduct training sessions on CQRS basics

### Phase 2: Documentation (1 Month)
- Document patterns and best practices
- Create code snippets and templates
- Build sample applications demonstrating patterns
- Update project structure guidelines

### Phase 3: Tooling (3 Months)
- Create code generators for commands/queries/handlers
- Build Roslyn analyzers to enforce patterns
- Provide Visual Studio/Rider snippets
- Develop file templates for common scenarios

### Phase 4: Migration Guidance (Ongoing)
- Create migration guides for existing projects
- Identify candidates for gradual CQRS adoption
- Share lessons learned and best practices

## References

- [CQRS Pattern - Martin Fowler](https://martinfowler.com/bliki/CQRS.html)
- [CQRS Journey - Microsoft](https://learn.microsoft.com/en-us/previous-versions/msp-n-p/jj554200(v=pandp.10))
- [Command Query Separation Principle](https://en.wikipedia.org/wiki/Command%E2%80%93query_separation)
- [Domain-Driven Design](https://www.domainlanguage.com/ddd/)
- [Dependency Injection in .NET](https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection)

## Related ADRs

- **ADR-003**: Prefer Modular Monoliths - CQRS fits well within module boundaries
- **ADR-005**: Prefer Minimal APIs - CQRS works excellently with Minimal APIs
- **ADR-004**: OpenTelemetry - Handlers provide natural activity boundaries
- **Project Structure**: Commands, Queries, and Handlers should be organized by feature/module
