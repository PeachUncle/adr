---
title: "ADR-004: Adoption of OpenTelemetry for Observability"
date: 2025-11-13
status: Accepted
tags: [opentelemetry, observability, telemetry, monitoring, tracing]
---

# ADR-004: Adoption of OpenTelemetry for Observability

## Status

Accepted

## Date

2025-11-13

## Context

Modern distributed applications require comprehensive observability to effectively monitor, troubleshoot, and optimize system performance. As our organization builds increasingly complex systems with microservices, APIs, and distributed architectures, we need a standardized approach to collecting telemetry data including traces, metrics, and logs.

OpenTelemetry (OTel) has emerged as the industry-standard observability framework, providing:
- Vendor-neutral instrumentation
- Automatic and manual tracing capabilities
- Standardized semantic conventions
- Rich ecosystem support across platforms and languages
- Native integration with .NET and Aspire

Without a standardized telemetry approach, our teams face:
- Inconsistent observability across services
- Difficulty troubleshooting distributed transactions
- Limited visibility into performance bottlenecks
- Vendor lock-in with proprietary monitoring solutions
- Increased time to diagnose production issues

## Decision

We have decided to adopt OpenTelemetry as the **required** observability standard for all Wigo4it projects.

### Requirements

**All projects MUST use OpenTelemetry**, with the following specific requirements:

#### 1. Mandatory for Web-Enabled Projects
- **All web applications, APIs, and HTTP services MUST implement OpenTelemetry**
- This includes ASP.NET Core applications, Web APIs, gRPC services, and any HTTP-based services
- No exceptions without explicit architectural approval

#### 2. Aspire-Based Configuration (Recommended)
- **OpenTelemetry SHOULD be configured through .NET Aspire** when Aspire is used for the project
- Aspire provides automatic OpenTelemetry setup with sensible defaults
- Projects using Aspire get OTLP exporters, console exporters, and proper service instrumentation automatically
- Manual configuration is only necessary for non-Aspire projects

#### 3. Automatic HTTP Activity Creation
- **A main activity MUST be created automatically for each incoming HTTP request**
- ASP.NET Core automatically creates activities for incoming requests when OpenTelemetry is configured
- This activity represents the entire request/response lifecycle
- Activity naming should follow OpenTelemetry semantic conventions (e.g., `HTTP GET /api/users`)

#### 4. Manual Activity Instrumentation
- **Developers MUST decorate code with appropriate sub-activities** to provide detailed tracing
- Create activities for:
  - Database queries and data access operations
  - External API calls and HTTP client requests
  - Business logic operations that take significant time
  - Critical workflow steps
  - Background processing and message handling

#### 5. State Information and Tags
- **Developers MUST add relevant state information to activities** where appropriate
- Include:
  - **Tags**: Key-value pairs for searchable metadata (user ID, tenant ID, correlation IDs)
  - **Events**: Important occurrences during activity execution (cache hits, retries, errors)
  - **Status**: Success or error status with descriptions
  - **Baggage**: Cross-service contextual information when needed
- Avoid adding sensitive information (passwords, tokens, PII) to activities

### Implementation Guidelines

#### Basic Activity Creation

```csharp
using System.Diagnostics;

// Define ActivitySource at class level
private static readonly ActivitySource ActivitySource = new("Wigo4it.MyService");

public async Task<User> GetUserAsync(string userId)
{
    using var activity = ActivitySource.StartActivity("GetUser");
    activity?.SetTag("user.id", userId);
    
    try
    {
        var user = await _repository.GetByIdAsync(userId);
        activity?.SetTag("user.found", user != null);
        return user;
    }
    catch (Exception ex)
    {
        activity?.SetStatus(ActivityStatusCode.Error, ex.Message);
        throw;
    }
}
```

#### Nested Activities for Complex Operations

```csharp
public async Task<Order> ProcessOrderAsync(OrderRequest request)
{
    using var activity = ActivitySource.StartActivity("ProcessOrder");
    activity?.SetTag("order.id", request.OrderId);
    activity?.SetTag("customer.id", request.CustomerId);
    
    // Sub-activity for validation
    using (var validationActivity = ActivitySource.StartActivity("ValidateOrder"))
    {
        await ValidateOrderAsync(request);
        validationActivity?.AddEvent(new ActivityEvent("Order validated"));
    }
    
    // Sub-activity for inventory check
    using (var inventoryActivity = ActivitySource.StartActivity("CheckInventory"))
    {
        var available = await _inventory.CheckAvailabilityAsync(request.Items);
        inventoryActivity?.SetTag("items.available", available);
    }
    
    // Sub-activity for payment
    using (var paymentActivity = ActivitySource.StartActivity("ProcessPayment"))
    {
        await _payment.ProcessAsync(request.PaymentInfo);
        paymentActivity?.AddEvent(new ActivityEvent("Payment processed"));
    }
    
    activity?.SetStatus(ActivityStatusCode.Ok);
    return await CreateOrderAsync(request);
}
```

#### Aspire Configuration Example

```csharp
// AppHost project
var builder = DistributedApplication.CreateBuilder(args);

var apiService = builder.AddProject<Projects.MyApi>("api")
    .WithEnvironment("OTEL_SERVICE_NAME", "my-api");

// Aspire automatically configures:
// - ActivitySource registration
// - OTLP exporter to Aspire dashboard
// - Console exporter for development
// - Propagation of trace context across services
```

#### Manual Configuration (Non-Aspire Projects)

```csharp
// Program.cs
builder.Services.AddOpenTelemetry()
    .WithTracing(tracing => tracing
        .AddAspNetCoreInstrumentation()
        .AddHttpClientInstrumentation()
        .AddEntityFrameworkCoreInstrumentation()
        .AddSource("Wigo4it.*")
        .AddOtlpExporter());
```

### What to Instrument

**High Priority - Always Instrument:**
- HTTP requests/responses
- Database operations
- External API calls
- Authentication/authorization
- Message queue operations
- Cache operations
- File I/O operations

**Medium Priority - Instrument When Significant:**
- Business logic operations (> 50ms)
- Data transformations
- Validation operations
- Background jobs

**Low Priority - Optional:**
- Simple CRUD operations
- In-memory operations
- Helper methods

### Best Practices

1. **Use Semantic Conventions**: Follow OpenTelemetry semantic conventions for naming and tags
2. **Keep Activity Names Short**: Use descriptive but concise names (e.g., "GetUser", not "GetUserFromDatabaseById")
3. **Add Context, Not Content**: Include identifiers and metadata, not full request/response bodies
4. **Don't Over-Instrument**: Too many activities can add overhead and noise
5. **Set Status Appropriately**: Always set Error status when exceptions occur
6. **Use Activity.Current**: For adding tags to current activity without passing it around
7. **Register ActivitySources**: Ensure all ActivitySources are registered with OpenTelemetry configuration

### Compliance and Verification

- Code reviews MUST verify proper OpenTelemetry implementation
- Web projects without OpenTelemetry configuration will fail architecture validation
- Key business operations MUST have appropriate activity instrumentation
- Performance tests should monitor telemetry overhead (should be < 5% impact)

## Rationale

### Why OpenTelemetry?

1. **Industry Standard**: OpenTelemetry is the CNCF standard for observability, backed by major vendors
2. **Vendor Neutral**: Avoid lock-in, export to any compatible backend (Jaeger, Prometheus, Azure Monitor, etc.)
3. **.NET Native Support**: First-class support in .NET with excellent performance
4. **Aspire Integration**: Seamless integration with .NET Aspire for distributed applications
5. **Automatic Instrumentation**: Many frameworks provide automatic tracing out of the box
6. **Distributed Tracing**: Essential for understanding request flow across microservices
7. **Future-Proof**: Active development and broad industry adoption

### Why Mandatory for Web Projects?

1. **Critical Services**: Web services are customer-facing and require high reliability
2. **Distributed Nature**: HTTP services typically call other services, making distributed tracing essential
3. **Production Diagnosis**: Telemetry is critical for diagnosing production issues quickly
4. **Performance Monitoring**: Identify performance bottlenecks and optimization opportunities
5. **SLA Compliance**: Monitor and ensure service level objectives are met

### Why Aspire for Configuration?

1. **Zero Config**: Aspire provides OpenTelemetry setup with no additional configuration
2. **Best Practices**: Pre-configured with recommended exporters and settings
3. **Dashboard Integration**: Automatic integration with Aspire dashboard for development
4. **Consistency**: Standardized configuration across all Aspire projects
5. **Updates**: Benefit from Aspire's maintained OpenTelemetry configuration

## Consequences

### Positive

- **Improved Observability**: Comprehensive visibility into distributed system behavior
- **Faster Troubleshooting**: Trace requests across services to identify issues quickly
- **Performance Insights**: Identify bottlenecks and optimization opportunities
- **Standardization**: Consistent telemetry approach across all projects
- **Vendor Flexibility**: Switch monitoring backends without code changes
- **Better Monitoring**: Foundation for effective alerts and dashboards
- **Production Confidence**: Better understanding of system behavior in production

### Negative

- **Learning Curve**: Developers need to learn OpenTelemetry concepts and APIs
- **Development Overhead**: Additional code for manual instrumentation
- **Runtime Overhead**: Small performance impact (typically < 5% when properly configured)
- **Testing Complexity**: Need to consider telemetry in testing scenarios
- **Initial Setup**: Effort required to add OpenTelemetry to existing projects

### Neutral

- **Dependency Addition**: OpenTelemetry packages added to all projects
- **Code Changes**: Existing code needs to be updated with activity instrumentation
- **Monitoring Backend**: Need to choose and configure an OpenTelemetry-compatible backend
- **Documentation**: Need to document telemetry practices and guidelines

## Alternatives Considered

### Application Insights SDK (Rejected)
- **Pros**: Native Azure integration, familiar to team
- **Cons**: Vendor lock-in, not compatible with OpenTelemetry standard, limited flexibility
- **Reason for rejection**: OpenTelemetry provides vendor neutrality and better long-term flexibility

### Prometheus Client Libraries (Rejected)
- **Pros**: Popular metrics solution, widely adopted
- **Cons**: Metrics only, no tracing, different instrumentation approach
- **Reason for rejection**: OpenTelemetry provides traces, metrics, and logs in one framework

### Custom Logging Only (Rejected)
- **Pros**: Simple, no additional dependencies
- **Cons**: No distributed tracing, no structured telemetry, difficult to correlate across services
- **Reason for rejection**: Insufficient for modern distributed applications

### Optional OpenTelemetry (Rejected)
- **Pros**: More flexibility for teams
- **Cons**: Inconsistent observability, some services would lack telemetry
- **Reason for rejection**: Observability is too critical to be optional for web services

## Implementation

### Phase 1: Immediate (New Projects)
- All new web projects MUST include OpenTelemetry from day one
- Use Aspire for configuration when applicable
- Document examples and best practices

### Phase 2: Migration (Existing Projects - 6 Months)
- Add OpenTelemetry to all existing web-enabled projects
- Prioritize high-traffic and critical services
- Provide migration guides and support

### Phase 3: Enhancement (Ongoing)
- Improve activity instrumentation based on production insights
- Add custom metrics and logs where beneficial
- Refine semantic conventions and naming standards

## References

- [OpenTelemetry Official Documentation](https://opentelemetry.io/docs/)
- [.NET OpenTelemetry Documentation](https://learn.microsoft.com/en-us/dotnet/core/diagnostics/observability-with-otel)
- [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)
- [.NET Aspire Telemetry](https://learn.microsoft.com/en-us/dotnet/aspire/fundamentals/telemetry)
- [ADR-002: Adoption of Aspire](./ADR-002-adoption-of-aspire-for-distributed-applications.md)

## Related ADRs

- **ADR-002**: Adoption of Aspire for Distributed Application Development - OpenTelemetry configuration should leverage Aspire
- **ADR-001**: Migration to .NET 10 - OpenTelemetry works best with latest .NET versions
