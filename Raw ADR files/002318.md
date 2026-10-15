# ADR-005: Refit for API Clients

**Status:** Accepted

**Date:** 2025-01-15

**Decision Makers:** JumpStart Core Team

## Context

Modern applications frequently need to consume HTTP APIs, particularly when:

- **Blazor Server** applications call separate Web APIs
- **Microservices** communicate with each other
- **Mobile apps** integrate with backend services
- **Desktop applications** connect to cloud services
- **Batch jobs** consume REST endpoints

Traditional approaches to HTTP API consumption present challenges:

- **Manual HttpClient Code** - Verbose, error-prone, repetitive
- **Boilerplate** - Serialization, deserialization, error handling duplicated
- **No Type Safety** - String-based URLs and dynamic types
- **Poor Discoverability** - No IntelliSense for API endpoints
- **Testing Difficulty** - Hard to mock HTTP calls
- **Maintenance Burden** - Changes to API require updating multiple places

We needed a solution that:
- Provides type-safe API client generation
- Reduces boilerplate code dramatically
- Integrates with ASP.NET Core dependency injection
- Supports authentication handlers (JWT, OAuth, etc.)
- Enables easy mocking for testing
- Follows REST conventions naturally
- Works seamlessly with JumpStart patterns

## Decision

We will use **Refit** as the primary HTTP client library with JumpStart-specific extension methods for streamlined registration.

### 1. Refit API Client Interfaces

Define strongly-typed interfaces decorated with Refit attributes:

**Simple Entity API Client:**
```csharp
public interface IProductApiClient : ISimpleApiClient<ProductDto, CreateProductDto, UpdateProductDto>
{
    // Base CRUD operations inherited from ISimpleApiClient
    // - Task<ProductDto?> GetByIdAsync(Guid id)
    // - Task<IEnumerable<ProductDto>> GetAllAsync()
    // - Task<PagedResult<ProductDto>> GetPagedAsync(QueryOptions<ProductDto> options)
    // - Task<ProductDto> CreateAsync(CreateProductDto dto)
    // - Task<ProductDto> UpdateAsync(Guid id, UpdateProductDto dto)
    // - Task DeleteAsync(Guid id)

    // Custom endpoints specific to products
    [Get("/featured")]
    Task<IEnumerable<ProductDto>> GetFeaturedAsync();

    [Get("/category/{categoryId}")]
    Task<IEnumerable<ProductDto>> GetByCategoryAsync(Guid categoryId);

    [Post("/{id}/activate")]
    Task ActivateAsync(Guid id);
}
```

**Advanced Entity API Client (Custom Key Types):**
```csharp
public interface ILegacyOrderApiClient : IAdvancedApiClient<OrderDto, CreateOrderDto, UpdateOrderDto, int>
{
    // Base CRUD with int key type
    
    [Get("/customer/{customerId}")]
    Task<IEnumerable<OrderDto>> GetByCustomerAsync(int customerId);
}
```

### 2. Base API Client Interfaces

JumpStart provides base interfaces for standard CRUD operations:

```csharp
public interface ISimpleApiClient<TDto, TCreateDto, TUpdateDto>
    : IAdvancedApiClient<TDto, TCreateDto, TUpdateDto, Guid>
    where TDto : SimpleEntityDto
    where TCreateDto : ICreateDto
    where TUpdateDto : IUpdateDto<Guid>
{
}

public interface IAdvancedApiClient<TDto, TCreateDto, TUpdateDto, TKey>
    where TDto : EntityDto<TKey>
    where TCreateDto : ICreateDto
    where TUpdateDto : IUpdateDto<TKey>
    where TKey : struct
{
    [Get("/{id}")]
    Task<TDto?> GetByIdAsync(TKey id);

    [Get("")]
    Task<IEnumerable<TDto>> GetAllAsync();

    [Post("/paged")]
    Task<PagedResult<TDto>> GetPagedAsync([Body] QueryOptions options);

    [Post("")]
    Task<TDto> CreateAsync([Body] TCreateDto dto);

    [Put("/{id}")]
    Task<TDto> UpdateAsync(TKey id, [Body] TUpdateDto dto);

    [Delete("/{id}")]
    Task DeleteAsync(TKey id);
}
```

### 3. JumpStart Extension Methods

Simplified registration with automatic JWT authentication:

```csharp
public static class SimpleApiClientExtensions
{
    public static IHttpClientBuilder AddSimpleApiClient<TClient>(
        this IServiceCollection services,
        string baseUrl)
        where TClient : class
    {
        return services.AddRefitClient<TClient>()
            .ConfigureHttpClient(c => c.BaseAddress = new Uri(baseUrl));
    }
}

// Usage in Program.cs
builder.Services.AddSimpleApiClient<IProductApiClient>("https://api.example.com/api/products")
    .AddHttpMessageHandler<JwtAuthenticationHandler>();
```

### 4. Automatic API Controller Base

Controllers that expose Refit-compatible endpoints:

```csharp
[ApiController]
[Route("api/[controller]")]
public abstract class SimpleApiControllerBase<TEntity, TDto, TCreateDto, TUpdateDto>
    : ControllerBase
    where TEntity : class, ISimpleEntity
    where TDto : SimpleEntityDto
    where TCreateDto : ICreateDto
    where TUpdateDto : IUpdateDto<Guid>
{
    protected readonly ISimpleRepository<TEntity> _repository;
    protected readonly IMapper _mapper;

    [HttpGet("{id}")]
    public virtual async Task<ActionResult<TDto>> GetByIdAsync(Guid id)
    {
        var entity = await _repository.GetByIdAsync(id);
        if (entity == null) return NotFound();
        return Ok(_mapper.Map<TDto>(entity));
    }

    [HttpGet]
    public virtual async Task<ActionResult<IEnumerable<TDto>>> GetAllAsync()
    {
        var entities = await _repository.GetAllAsync();
        return Ok(_mapper.Map<IEnumerable<TDto>>(entities));
    }

    [HttpPost("paged")]
    public virtual async Task<ActionResult<PagedResult<TDto>>> GetPagedAsync(
        [FromBody] QueryOptions options)
    {
        var result = await _repository.GetPagedAsync(options);
        return Ok(new PagedResult<TDto>
        {
            Items = _mapper.Map<IEnumerable<TDto>>(result.Items),
            TotalCount = result.TotalCount,
            PageNumber = result.PageNumber,
            PageSize = result.PageSize
        });
    }

    [HttpPost]
    public virtual async Task<ActionResult<TDto>> CreateAsync([FromBody] TCreateDto dto)
    {
        var entity = _mapper.Map<TEntity>(dto);
        var created = await _repository.AddAsync(entity);
        return CreatedAtAction(nameof(GetByIdAsync), new { id = created.Id }, 
            _mapper.Map<TDto>(created));
    }

    [HttpPut("{id}")]
    public virtual async Task<ActionResult<TDto>> UpdateAsync(Guid id, [FromBody] TUpdateDto dto)
    {
        var entity = await _repository.GetByIdAsync(id);
        if (entity == null) return NotFound();
        
        _mapper.Map(dto, entity);
        var updated = await _repository.UpdateAsync(entity);
        return Ok(_mapper.Map<TDto>(updated));
    }

    [HttpDelete("{id}")]
    public virtual async Task<IActionResult> DeleteAsync(Guid id)
    {
        var success = await _repository.DeleteAsync(id);
        if (!success) return NotFound();
        return NoContent();
    }
}
```

### 5. Complete Example

**API Controller:**
```csharp
[Authorize]
public class ProductsController : SimpleApiControllerBase<Product, ProductDto, CreateProductDto, UpdateProductDto>
{
    public ProductsController(ISimpleRepository<Product> repository, IMapper mapper)
        : base(repository, mapper)
    {
    }

    [HttpGet("featured")]
    public async Task<ActionResult<IEnumerable<ProductDto>>> GetFeaturedAsync()
    {
        // Custom endpoint implementation
        var products = await ((IProductRepository)_repository).GetFeaturedAsync();
        return Ok(_mapper.Map<IEnumerable<ProductDto>>(products));
    }
}
```

**Blazor Component:**
```csharp
@page "/products"
@inject IProductApiClient ProductApi

<h3>Products</h3>

@if (products == null)
{
    <p>Loading...</p>
}
else
{
    @foreach (var product in products)
    {
        <div>@product.Name - @product.Price.ToString("C")</div>
    }
}

@code {
    private IEnumerable<ProductDto>? products;

    protected override async Task OnInitializedAsync()
    {
        // Type-safe, IntelliSense-supported API call
        products = await ProductApi.GetAllAsync();
    }
}
```

## Consequences

### Positive Consequences

- **Type Safety** - Compile-time checking of endpoints, parameters, return types
- **IntelliSense Support** - Full IDE support for API discovery
- **Minimal Boilerplate** - Interface definition is all you need
- **Automatic Serialization** - JSON handling built-in
- **DI Integration** - First-class ASP.NET Core DI support
- **HttpClient Best Practices** - Uses IHttpClientFactory under the hood
- **Easy Mocking** - Interface-based design perfect for testing
- **Authentication Integration** - Works seamlessly with DelegatingHandler
- **Error Handling** - ApiException with status codes and response content
- **Developer Productivity** - Write less code, focus on business logic
- **Consistency** - Uniform API client pattern across application
- **Maintainability** - Changes to API reflected in interface

### Negative Consequences

- **Library Dependency** - Another third-party dependency to manage
- **Learning Curve** - Developers must learn Refit attributes and conventions
- **Limited Flexibility** - Some advanced HttpClient scenarios harder to implement
- **Magic** - Code generation can be confusing for debugging
- **Breaking Changes** - Refit updates may introduce breaking changes
- **Attribute Overhead** - Must learn and apply correct Refit attributes

### Neutral Consequences

- **Interface Required** - Must define interface even for simple clients
- **Runtime Generation** - Client implementation generated at runtime via dynamic proxy
- **JSON Only** - Primarily designed for JSON APIs (can be extended for other formats)

## Alternatives Considered

### 1. Manual HttpClient

Write HttpClient code manually for each endpoint.

**Pros:**
- No additional dependencies
- Full control over HTTP behavior
- No "magic" code generation

**Cons:**
- Massive boilerplate
- Error-prone
- No type safety
- Poor maintainability
- Hard to test

**Why Rejected:** Too much boilerplate for minimal benefit.

### 2. HttpClientFactory with Extension Methods

Use IHttpClientFactory with custom extension methods for common patterns.

**Pros:**
- ASP.NET Core native
- More control than Refit
- No magic

**Cons:**
- Still requires significant boilerplate
- No type-safe contract
- Custom extensions to maintain

**Why Rejected:** Refit provides better developer experience.

### 3. NSwag Client Generation

Generate clients from OpenAPI/Swagger specification.

**Pros:**
- Auto-generated from API spec
- Includes models and clients
- Great for consuming external APIs

**Cons:**
- Build-time code generation
- Generated code in source control or build step
- Less flexible for modifications
- Requires OpenAPI specification

**Why Rejected:** Runtime generation (Refit) is more flexible. NSwag can still be used for external APIs.

### 4. RestSharp

Popular REST client library.

**Pros:**
- Mature and battle-tested
- Flexible
- Large community

**Cons:**
- More verbose than Refit
- No interface-based clients
- Manual request building
- Not as DI-friendly

**Why Rejected:** Refit provides better developer experience and type safety.

### 5. gRPC

Use gRPC instead of REST.

**Pros:**
- Better performance
- Strong typing
- Bidirectional streaming

**Cons:**
- Not REST (different paradigm)
- Requires Protocol Buffers
- Browser support limited
- More complex infrastructure

**Why Rejected:** REST is more universal and easier for web applications. gRPC can be adopted later if needed.

## Implementation Best Practices

### Error Handling

```csharp
public async Task<IEnumerable<ProductDto>> LoadProductsAsync()
{
    try
    {
        return await _productApi.GetAllAsync();
    }
    catch (ApiException ex) when (ex.StatusCode == HttpStatusCode.Unauthorized)
    {
        // Handle unauthorized (redirect to login, refresh token, etc.)
        await HandleUnauthorizedAsync();
        return Enumerable.Empty<ProductDto>();
    }
    catch (ApiException ex) when (ex.StatusCode == HttpStatusCode.NotFound)
    {
        // Handle not found
        return Enumerable.Empty<ProductDto>();
    }
    catch (ApiException ex)
    {
        // Handle other API errors
        _logger.LogError(ex, "API call failed: {StatusCode}", ex.StatusCode);
        throw;
    }
}
```

### Retry Policies with Polly

```csharp
builder.Services.AddSimpleApiClient<IProductApiClient>("https://api.example.com/api/products")
    .AddHttpMessageHandler<JwtAuthenticationHandler>()
    .AddTransientHttpErrorPolicy(policy => 
        policy.WaitAndRetryAsync(3, retryAttempt => 
            TimeSpan.FromSeconds(Math.Pow(2, retryAttempt))));
```

### Request/Response Logging

```csharp
public class LoggingHandler : DelegatingHandler
{
    private readonly ILogger<LoggingHandler> _logger;

    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, 
        CancellationToken cancellationToken)
    {
        _logger.LogInformation("Request: {Method} {Uri}", request.Method, request.RequestUri);
        
        var response = await base.SendAsync(request, cancellationToken);
        
        _logger.LogInformation("Response: {StatusCode}", response.StatusCode);
        
        return response;
    }
}

// Register
builder.Services.AddSimpleApiClient<IProductApiClient>(baseUrl)
    .AddHttpMessageHandler<LoggingHandler>()
    .AddHttpMessageHandler<JwtAuthenticationHandler>();
```

### Testing with Mock

```csharp
public class ProductServiceTests
{
    [Fact]
    public async Task GetProducts_ReturnsProducts()
    {
        // Arrange
        var mockApi = new Mock<IProductApiClient>();
        mockApi.Setup(x => x.GetAllAsync())
            .ReturnsAsync(new[] 
            { 
                new ProductDto { Id = Guid.NewGuid(), Name = "Product 1" } 
            });

        var service = new ProductService(mockApi.Object);

        // Act
        var result = await service.GetAllProductsAsync();

        // Assert
        Assert.Single(result);
        mockApi.Verify(x => x.GetAllAsync(), Times.Once);
    }
}
```

## Refit Features Used

### HTTP Methods
- `[Get]` - GET requests
- `[Post]` - POST requests
- `[Put]` - PUT requests
- `[Delete]` - DELETE requests
- `[Patch]` - PATCH requests

### Parameters
- `[Body]` - Request body (JSON serialized)
- `[Query]` - Query string parameter
- `[Header]` - Request header
- Route parameters - `{id}` in path

### Return Types
- `Task<T>` - Deserialized response
- `Task<IApiResponse<T>>` - Full response with headers/status
- `Task` - No response body expected
- `Task<HttpResponseMessage>` - Raw response

## References

- [Refit GitHub Repository](https://github.com/reactiveui/refit)
- [Refit Documentation](https://github.com/reactiveui/refit#readme)
- [IHttpClientFactory - Microsoft Docs](https://docs.microsoft.com/en-us/dotnet/architecture/microservices/implement-resilient-applications/use-httpclientfactory-to-implement-resilient-http-requests)
- [ADR-004: JWT Authentication](004-jwt-authentication.md)

## Related Documentation

- [How-To: Create API Clients](../../how-to/api-clients.md)
- [How-To: Test API Clients](../../how-to/test-api-clients.md)
- [API Reference: ISimpleApiClient](../../api/clients/isimpleapiclient.md)
