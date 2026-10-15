# ADR-018 – Error Handling & Logging Strategy: Exception Management and Observability

**Status:** Accepted  
**Date:** 2025-12-01  
**Author:** Niklas Häll

---

## Context

The application needs a consistent approach to handling errors, logging events, and surfacing information to users. Without a defined strategy:
- Errors might be handled inconsistently across different parts of the application
- Critical errors might not be logged, making troubleshooting difficult
- Users might receive confusing or unhelpful error messages
- Application Insights telemetry might miss important error context
- Development and production environments might handle errors differently

**Requirements:**
- Consistent error handling across controllers, services, and background processes
- Comprehensive logging for troubleshooting and monitoring
- User-friendly error messages without exposing sensitive information
- Integration with Application Insights for error tracking
- Graceful degradation when non-critical errors occur

---

## Decision

The application implements a **layered error handling strategy** with structured logging and user-friendly error responses:

**Error Handling Layers:**

1. **Global Exception Handler** - Catches unhandled exceptions at the application level
2. **Controller-Level Error Handling** - Try-catch blocks in controllers with appropriate HTTP status codes
3. **Service-Level Error Handling** - Services catch exceptions, log them, and either re-throw or handle gracefully
4. **Background Service Error Handling** - Background services continue processing other items when individual items fail

**Logging Strategy:**

- **Structured Logging** - Uses `ILogger<T>` throughout the application
- **Log Levels** - Error, Warning, Information (no Debug or Trace in production)
- **Application Insights Integration** - All logs sent to Application Insights for centralized monitoring
- **Contextual Information** - Logs include relevant context (IDs, user information, operation details)

**User-Facing Error Messages:**

- **API Endpoints** - Return JSON with error messages and appropriate HTTP status codes
- **Blazor Pages** - Display error messages in UI with user-friendly formatting
- **Authentication Errors** - Redirect to login page with error query parameter
- **Generic Error Page** - Fallback for unhandled exceptions in non-API requests

---

## Consequences

**Advantages:**
- **Consistent Error Handling** - All parts of the application handle errors in a predictable way
- **Comprehensive Observability** - All errors logged with context, enabling effective troubleshooting
- **User-Friendly Experience** - Users receive clear, actionable error messages
- **Production Safety** - Sensitive error details hidden from users, full details in logs
- **Graceful Degradation** - Non-critical errors don't break the entire application
- **Application Insights Integration** - Errors automatically tracked in telemetry for monitoring and alerting
- **Development vs Production** - Different error handling for development (detailed) vs production (user-friendly)

**Disadvantages:**
- **Code Verbosity** - Try-catch blocks add code to controllers and services
- **Potential Over-Logging** - Risk of logging too much information (mitigated by appropriate log levels)
- **Error Message Maintenance** - User-facing messages need to be maintained and kept user-friendly
- **Exception Swallowing Risk** - Background services might silently fail (mitigated by comprehensive logging)

---

## Risks / Mitigations

- **Risk:** Errors might be swallowed without proper logging.  
  **Mitigation:** All catch blocks include logging. Code reviews ensure no silent failures. Background services log errors but continue processing.

- **Risk:** Sensitive information might be exposed in error messages.  
  **Mitigation:** Production error handler returns generic messages. Detailed error information only in logs. No stack traces or connection strings in user-facing errors.

- **Risk:** Too much logging might impact performance or costs.  
  **Mitigation:** Appropriate log levels (Information, Warning, Error). Application Insights sampling can be configured if needed. Current MVP scale is minimal.

- **Risk:** Inconsistent error handling across different parts of the application.  
  **Mitigation:** This ADR documents the standard pattern. Code reviews ensure consistency. Examples provided for each layer.

- **Risk:** Background service errors might go unnoticed.  
  **Mitigation:** All background service errors are logged. Application Insights alerts can be configured for error rates. Health endpoint includes background service status.

---

## Alternatives

- **Exception Filters** - Use ASP.NET Core exception filters instead of try-catch in controllers.  
  **Rejected:** Try-catch in controllers provides more control and context-specific error handling. Exception filters are global and harder to customize per endpoint.

- **Result Pattern** - Return `Result<T>` objects instead of throwing exceptions.  
  **Rejected:** Adds complexity and changes API contracts. Exception handling is standard in .NET and works well with existing patterns.

- **Centralized Error Handler Only** - Rely solely on global exception handler without controller-level handling.  
  **Rejected:** Controller-level handling provides better context and appropriate HTTP status codes. Global handler is fallback for unhandled exceptions.

- **Separate Logging Library** - Use Serilog or NLog instead of built-in `ILogger<T>`.  
  **Rejected:** Built-in logging integrates seamlessly with Application Insights. No need for additional dependencies. `ILogger<T>` is sufficient for MVP.

---

## Implementation Details

### Global Exception Handler

**Location:** `Extensions/WebApplicationExtensions.cs`

```csharp
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler(errorApp =>
    {
        errorApp.Run(async context =>
        {
            var exceptionHandlerPathFeature = context.Features.Get<IExceptionHandlerPathFeature>();
            var exception = exceptionHandlerPathFeature?.Error;
            
            if (context.Request.Path.StartsWithSegments("/api"))
            {
                // API endpoints: Return JSON error
                context.Response.StatusCode = 500;
                context.Response.ContentType = "application/json";
                await context.Response.WriteAsJsonAsync(new
                {
                    error = exception?.Message ?? "An error occurred",
                    path = context.Request.Path
                });
            }
            else
            {
                // Non-API requests: Redirect to error page
                context.Response.Redirect("/Error");
            }
        });
    });
}
```

**Behavior:**
- **Production Only** - Only active in non-development environments
- **API vs UI** - Different handling for API endpoints (JSON) vs UI requests (redirect)
- **Generic Messages** - Returns generic error messages to users (detailed info in logs)

### Controller Error Handling Pattern

**Example:** `Controllers/BookingsController.cs`

```csharp
[HttpPost]
public async Task<ActionResult<Booking>> CreateBooking([FromBody] BookingRequest request)
{
    try
    {
        // Validation
        if (string.IsNullOrEmpty(request.CustomerEmail))
        {
            return BadRequest(new { error = "Customer email is required." });
        }
        
        // Business logic
        var booking = await _bookingService.CreateBookingAsync(...);
        
        // Logging
        _logger.LogInformation("Booking created: {BookingId}", booking.Id);
        
        return CreatedAtAction(...);
    }
    catch (Exception ex)
    {
        // Log error with context
        _logger.LogError(ex, "Error creating booking for customer {CustomerEmail}", 
            request.CustomerEmail);
        
        // Return user-friendly error
        return BadRequest(new { error = ex.Message });
    }
}
```

**Key Principles:**
- **Try-Catch Blocks** - Wrap business logic in try-catch
- **Validation First** - Return `BadRequest` for validation errors
- **Contextual Logging** - Include relevant context in log messages
- **User-Friendly Messages** - Return clear error messages (not stack traces)
- **Appropriate Status Codes** - Use correct HTTP status codes (400, 404, 500, etc.)

### Service Error Handling Patterns

**Pattern 1: Re-throw for Retry (ServiceBusEventPublisher)**
```csharp
try
{
    await sender.SendMessageAsync(message, cancellationToken);
}
catch (ServiceBusException ex)
{
    _logger.LogError(ex, "Service Bus error publishing event {EventType}: {ErrorMessage}",
        eventData.EventType, ex.Message);
    throw; // Re-throw for retry mechanism
}
```

**Pattern 2: Graceful Degradation (OutboxProcessorService)**
```csharp
foreach (var outboxEvent in pendingEvents)
{
    try
    {
        await ProcessEventAsync(outboxEvent, ...);
    }
    catch (Exception ex)
    {
        _logger.LogError(ex, "Failed to process outbox event {EventId}",
            outboxEvent.Id);
        // Continue processing other events
    }
}
```

**Pattern 3: Log and Continue (BookingsController - Outbox Creation)**
```csharp
try
{
    await _outboxService.CreateOutboxEventAsync(...);
}
catch (Exception ex)
{
    // Log error but don't fail the booking creation
    _logger.LogError(ex, "Failed to create outbox event for booking {BookingId}. " +
        "Booking was created successfully.", createdBooking.Id);
    // Continue - booking is already created
}
```

### Logging Configuration

**appsettings.json:**
```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  }
}
```

**Log Levels Used:**
- **Error** - Exceptions, failures, critical issues
- **Warning** - Non-critical issues, recoverable errors (e.g., App Configuration refresh failures)
- **Information** - Normal operations (booking creation, successful operations)

**Application Insights Integration:**
- Connection string configured via `APPLICATIONINSIGHTS_CONNECTION_STRING`
- All logs automatically sent to Application Insights
- Custom events tracked via `ITelemetryService` (see ADR-015)

### User-Facing Error Messages

**API Error Response Format:**
```json
{
  "error": "Customer email is required."
}
```

**Blazor Page Error Display:**
```razor
@if (!string.IsNullOrEmpty(errorMessage))
{
    <div class="error-message">
        <p>@errorMessage</p>
    </div>
}
```

**Authentication Error Handling:**
```csharp
options.Events.OnRemoteFailure = context =>
{
    var errorMessage = context.Failure?.Message ?? "Unknown error";
    var encodedError = Uri.EscapeDataString($"Authentication failed: {errorMessage}");
    context.Response.Redirect($"/login?error={encodedError}");
    return Task.CompletedTask;
};
```

### Error Page

**Location:** `Pages/Error.razor`

Simple error page that displays a generic error message and provides a link to return home. Used as fallback for unhandled exceptions in non-API requests.

---

## Relationship to Other ADRs

- **[ADR-015 - Application Insights Telemetry Strategy](./ADR-015-application-insights-telemetry-strategy.md)** - Logging integrates with Application Insights for centralized monitoring. Custom events tracked for business operations.

- **[ADR-017 - Service/Component Organization Pattern](./ADR-017-service-component-organization-pattern.md)** - Error handling patterns implemented in Controllers and Services layers as documented in ADR-017.

- **[ADR-006 - Event-Driven Architecture](./ADR-006-eventdriven.md)** - Background services (OutboxProcessorService) implement graceful error handling to ensure event processing continues despite individual failures.

- **[ADR-019 - API Design Pattern](./ADR-019-api-design-pattern-controller-based-rest.md)** - Error handling patterns implemented in REST API controllers.

---

## References
- [ADR-015 - Application Insights Telemetry Strategy](./ADR-015-application-insights-telemetry-strategy.md) - Logging integration
- [ADR-017 - Service/Component Organization Pattern](./ADR-017-service-component-organization-pattern.md) - Code organization
- [ADR-006 - Event-Driven Architecture](./ADR-006-eventdriven.md) - Background service error handling
- [Microsoft Docs – Error Handling in ASP.NET Core](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/error-handling)
- [Microsoft Docs – Logging in .NET](https://learn.microsoft.com/en-us/dotnet/core/extensions/logging)
- [Microsoft Docs – Application Insights Logging](https://learn.microsoft.com/en-us/azure/azure-monitor/app/asp-net-core)

