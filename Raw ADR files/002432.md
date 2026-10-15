# ADR-007: Observability and Monitoring Strategy

## Status
Accepted

## Context
Lead Tracker needs comprehensive observability for:
- Application performance monitoring and debugging
- Multi-tenant request tracing with organization correlation
- Error tracking and alerting for production issues
- User activity auditing for security and compliance
- Business metrics monitoring (leads, conversions, revenue)
- Infrastructure monitoring (database, memory, CPU usage)

## Decision
We will implement a **structured logging and monitoring stack** with Serilog and Application Insights:

### Architecture Components:
1. **Serilog** for structured logging with enrichers
2. **Application Insights** for APM and telemetry
3. **Custom Middleware** for request correlation and tenant context
4. **Health Checks** for service monitoring
5. **Business Metrics** tracking for KPIs
6. **Alert Rules** for proactive issue detection

### Logging Implementation:

#### 1. Serilog Configuration
```csharp
// Program.cs
public static void Main(string[] args)
{
    Log.Logger = new LoggerConfiguration()
        .MinimumLevel.Information()
        .MinimumLevel.Override("Microsoft", LogEventLevel.Warning)
        .MinimumLevel.Override("System", LogEventLevel.Warning)
        .Enrich.FromLogContext()
        .Enrich.WithProperty("Application", "LeadTracker.Api")
        .Enrich.WithProperty("Environment", Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT"))
        .Enrich.WithMachineName()
        .Enrich.WithThreadId()
        .WriteTo.Console(new JsonFormatter())
        .WriteTo.ApplicationInsights(TelemetryConfiguration.CreateDefault(), TelemetryConverter.Traces)
        .CreateLogger();

    try
    {
        Log.Information("Starting Lead Tracker API");
        CreateHostBuilder(args).Build().Run();
    }
    catch (Exception ex)
    {
        Log.Fatal(ex, "Application start-up failed");
    }
    finally
    {
        Log.CloseAndFlush();
    }
}

// Startup.cs
public void ConfigureServices(IServiceCollection services)
{
    services.AddSerilog();
    services.AddApplicationInsightsTelemetry();
    
    // Custom enrichers
    services.AddScoped<ILogEventEnricher, TenantEnricher>();
    services.AddScoped<ILogEventEnricher, UserEnricher>();
}
```

#### 2. Custom Enrichers for Multi-tenant Context
```csharp
public class TenantEnricher : ILogEventEnricher
{
    private readonly IHttpContextAccessor _contextAccessor;
    private readonly ITenantContext _tenantContext;

    public TenantEnricher(IHttpContextAccessor contextAccessor, ITenantContext tenantContext)
    {
        _contextAccessor = contextAccessor;
        _tenantContext = tenantContext;
    }

    public void Enrich(LogEvent logEvent, ILogEventPropertyFactory propertyFactory)
    {
        if (_tenantContext.OrganizationId.HasValue)
        {
            logEvent.AddPropertyIfAbsent(propertyFactory.CreateProperty("OrganizationId", _tenantContext.OrganizationId.Value));
            logEvent.AddPropertyIfAbsent(propertyFactory.CreateProperty("OrganizationName", _tenantContext.OrganizationName));
        }

        if (_tenantContext.UserId.HasValue)
        {
            logEvent.AddPropertyIfAbsent(propertyFactory.CreateProperty("UserId", _tenantContext.UserId.Value));
            logEvent.AddPropertyIfAbsent(propertyFactory.CreateProperty("UserEmail", _tenantContext.UserEmail));
        }

        var httpContext = _contextAccessor.HttpContext;
        if (httpContext != null)
        {
            logEvent.AddPropertyIfAbsent(propertyFactory.CreateProperty("RequestId", httpContext.TraceIdentifier));
            logEvent.AddPropertyIfAbsent(propertyFactory.CreateProperty("RequestPath", httpContext.Request.Path));
            logEvent.AddPropertyIfAbsent(propertyFactory.CreateProperty("UserAgent", httpContext.Request.Headers["User-Agent"].FirstOrDefault()));
            logEvent.AddPropertyIfAbsent(propertyFactory.CreateProperty("RemoteIP", httpContext.Connection.RemoteIpAddress?.ToString()));
        }
    }
}
```

#### 3. Request Correlation Middleware
```csharp
public class RequestCorrelationMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<RequestCorrelationMiddleware> _logger;

    public RequestCorrelationMiddleware(RequestDelegate next, ILogger<RequestCorrelationMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        var correlationId = context.Request.Headers["X-Correlation-ID"].FirstOrDefault() ?? Guid.NewGuid().ToString();
        context.Items["CorrelationId"] = correlationId;
        context.Response.Headers.Add("X-Correlation-ID", correlationId);

        using (LogContext.PushProperty("CorrelationId", correlationId))
        {
            var stopwatch = Stopwatch.StartNew();
            
            _logger.LogInformation("Request started: {Method} {Path}", 
                context.Request.Method, context.Request.Path);

            try
            {
                await _next(context);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Request failed: {Method} {Path}", 
                    context.Request.Method, context.Request.Path);
                throw;
            }
            finally
            {
                stopwatch.Stop();
                _logger.LogInformation("Request completed: {Method} {Path} in {ElapsedMs}ms with status {StatusCode}",
                    context.Request.Method, context.Request.Path, stopwatch.ElapsedMilliseconds, context.Response.StatusCode);
            }
        }
    }
}
```

### Application Performance Monitoring:

#### 1. Custom Telemetry Tracking
```csharp
public class TelemetryService
{
    private readonly TelemetryClient _telemetryClient;
    private readonly ITenantContext _tenantContext;

    public TelemetryService(TelemetryClient telemetryClient, ITenantContext tenantContext)
    {
        _telemetryClient = telemetryClient;
        _tenantContext = tenantContext;
    }

    public void TrackBusinessEvent(string eventName, Dictionary<string, string> properties = null, Dictionary<string, double> metrics = null)
    {
        var enrichedProperties = new Dictionary<string, string>(properties ?? new Dictionary<string, string>());
        
        if (_tenantContext.OrganizationId.HasValue)
        {
            enrichedProperties["OrganizationId"] = _tenantContext.OrganizationId.Value.ToString();
            enrichedProperties["OrganizationName"] = _tenantContext.OrganizationName;
        }

        if (_tenantContext.UserId.HasValue)
        {
            enrichedProperties["UserId"] = _tenantContext.UserId.Value.ToString();
        }

        _telemetryClient.TrackEvent(eventName, enrichedProperties, metrics);
    }

    public void TrackLeadCreated(Lead lead)
    {
        TrackBusinessEvent("Lead.Created", new Dictionary<string, string>
        {
            ["LeadId"] = lead.Id.ToString(),
            ["Source"] = lead.Source.ToString(),
            ["StageId"] = lead.StageId.ToString()
        }, new Dictionary<string, double>
        {
            ["Value"] = (double)(lead.Value ?? 0)
        });
    }

    public void TrackLeadConverted(Lead lead, Stage fromStage, Stage toStage)
    {
        TrackBusinessEvent("Lead.Converted", new Dictionary<string, string>
        {
            ["LeadId"] = lead.Id.ToString(),
            ["FromStage"] = fromStage.Name,
            ["ToStage"] = toStage.Name
        }, new Dictionary<string, double>
        {
            ["Value"] = (double)(lead.Value ?? 0),
            ["DaysInStage"] = (DateTime.UtcNow - lead.UpdatedAt).TotalDays
        });
    }
}
```

#### 2. Performance Monitoring Attributes
```csharp
public class PerformanceMonitoringAttribute : ActionFilterAttribute
{
    private readonly ILogger<PerformanceMonitoringAttribute> _logger;
    private readonly TelemetryClient _telemetryClient;

    public override async Task OnActionExecutionAsync(ActionExecutingContext context, ActionExecutionDelegate next)
    {
        var stopwatch = Stopwatch.StartNew();
        var actionName = $"{context.Controller.GetType().Name}.{context.ActionDescriptor.DisplayName}";

        try
        {
            var result = await next();
            stopwatch.Stop();

            _logger.LogInformation("Action {ActionName} completed in {ElapsedMs}ms", 
                actionName, stopwatch.ElapsedMilliseconds);

            _telemetryClient.TrackDependency("Action", actionName, DateTime.UtcNow.Subtract(stopwatch.Elapsed), 
                stopwatch.Elapsed, result.Exception == null);

            if (stopwatch.ElapsedMilliseconds > 5000) // Log slow operations
            {
                _logger.LogWarning("Slow action detected: {ActionName} took {ElapsedMs}ms", 
                    actionName, stopwatch.ElapsedMilliseconds);
            }
        }
        catch (Exception ex)
        {
            stopwatch.Stop();
            _logger.LogError(ex, "Action {ActionName} failed after {ElapsedMs}ms", 
                actionName, stopwatch.ElapsedMilliseconds);
            throw;
        }
    }
}
```

### Health Checks Implementation:

#### 1. Comprehensive Health Checks
```csharp
// Startup.cs
public void ConfigureServices(IServiceCollection services)
{
    services.AddHealthChecks()
        .AddCheck<DatabaseHealthCheck>("database")
        .AddCheck<HangfireHealthCheck>("hangfire")
        .AddCheck<EmailServiceHealthCheck>("email")
        .AddCheck<FileStorageHealthCheck>("storage")
        .AddApplicationInsightsPublisher();
}

public class DatabaseHealthCheck : IHealthCheck
{
    private readonly LeadTrackerDbContext _context;

    public DatabaseHealthCheck(LeadTrackerDbContext context)
    {
        _context = context;
    }

    public async Task<HealthCheckResult> CheckHealthAsync(HealthCheckContext context, CancellationToken cancellationToken = default)
    {
        try
        {
            // Simple connectivity test
            await _context.Database.ExecuteSqlRawAsync("SELECT 1", cancellationToken);
            
            // Check for recent activity
            var recentLeadsCount = await _context.Leads
                .Where(l => l.CreatedAt > DateTime.UtcNow.AddHours(-1))
                .CountAsync(cancellationToken);

            var data = new Dictionary<string, object>
            {
                ["recent_leads"] = recentLeadsCount,
                ["connection_string"] = _context.Database.GetConnectionString()?.Substring(0, 50) + "..."
            };

            return HealthCheckResult.Healthy("Database is responsive", data);
        }
        catch (Exception ex)
        {
            return HealthCheckResult.Unhealthy("Database connection failed", ex);
        }
    }
}
```

#### 2. Custom Metrics Collection
```csharp
public class BusinessMetricsCollector : BackgroundService
{
    private readonly IServiceProvider _serviceProvider;
    private readonly TelemetryClient _telemetryClient;
    private readonly ILogger<BusinessMetricsCollector> _logger;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                await CollectMetrics();
                await Task.Delay(TimeSpan.FromMinutes(5), stoppingToken); // Collect every 5 minutes
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error collecting business metrics");
                await Task.Delay(TimeSpan.FromMinutes(1), stoppingToken); // Retry in 1 minute on error
            }
        }
    }

    private async Task CollectMetrics()
    {
        using var scope = _serviceProvider.CreateScope();
        var context = scope.ServiceProvider.GetRequiredService<LeadTrackerDbContext>();

        // Collect system-wide metrics
        var totalOrganizations = await context.Organizations.CountAsync(o => o.IsActive);
        var totalUsers = await context.Users.CountAsync(u => u.IsActive);
        var totalLeads = await context.Leads.CountAsync();
        var leadsToday = await context.Leads.CountAsync(l => l.CreatedAt.Date == DateTime.UtcNow.Date);

        _telemetryClient.TrackMetric("Organizations.Total", totalOrganizations);
        _telemetryClient.TrackMetric("Users.Total", totalUsers);
        _telemetryClient.TrackMetric("Leads.Total", totalLeads);
        _telemetryClient.TrackMetric("Leads.Today", leadsToday);

        // Collect per-organization metrics
        var orgMetrics = await context.Organizations
            .Where(o => o.IsActive)
            .Select(o => new
            {
                o.Id,
                o.Name,
                LeadCount = o.Leads.Count(),
                ActiveLeadCount = o.Leads.Count(l => l.Status != LeadStatus.Lost && l.Status != LeadStatus.Won),
                TotalValue = o.Leads.Where(l => l.Status == LeadStatus.Won).Sum(l => l.Value ?? 0)
            })
            .ToListAsync();

        foreach (var org in orgMetrics)
        {
            var properties = new Dictionary<string, string>
            {
                ["OrganizationId"] = org.Id.ToString(),
                ["OrganizationName"] = org.Name
            };

            _telemetryClient.TrackMetric("Leads.Count", org.LeadCount, properties);
            _telemetryClient.TrackMetric("Leads.Active", org.ActiveLeadCount, properties);
            _telemetryClient.TrackMetric("Revenue.Total", (double)org.TotalValue, properties);
        }
    }
}
```

### Error Handling and Alerting:

#### 1. Global Exception Handler
```csharp
public class GlobalExceptionMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<GlobalExceptionMiddleware> _logger;
    private readonly TelemetryClient _telemetryClient;

    public async Task InvokeAsync(HttpContext context)
    {
        try
        {
            await _next(context);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unhandled exception occurred");
            
            // Track exception in Application Insights
            var properties = new Dictionary<string, string>
            {
                ["RequestPath"] = context.Request.Path,
                ["RequestMethod"] = context.Request.Method,
                ["UserId"] = context.User?.FindFirst(ClaimTypes.NameIdentifier)?.Value,
                ["OrganizationId"] = context.User?.FindFirst("org_id")?.Value
            };

            _telemetryClient.TrackException(ex, properties);

            await HandleExceptionAsync(context, ex);
        }
    }

    private static async Task HandleExceptionAsync(HttpContext context, Exception exception)
    {
        context.Response.ContentType = "application/json";
        context.Response.StatusCode = exception switch
        {
            ValidationException => 400,
            UnauthorizedAccessException => 401,
            ForbiddenException => 403,
            NotFoundException => 404,
            _ => 500
        };

        var response = new
        {
            error = new
            {
                message = exception.Message,
                details = context.Response.StatusCode == 500 ? "Internal server error" : exception.Message,
                traceId = context.TraceIdentifier
            }
        };

        await context.Response.WriteAsync(JsonSerializer.Serialize(response));
    }
}
```

#### 2. Alert Rules Configuration
```csharp
// Application Insights Alert Rules (configured via ARM template or Portal)
public class AlertingConfiguration
{
    public static readonly AlertRule[] AlertRules = new[]
    {
        new AlertRule
        {
            Name = "High Error Rate",
            Description = "Alert when error rate exceeds 5% over 5 minutes",
            Query = "requests | where success == false | summarize ErrorRate = (count() * 100.0) / toscalar(requests | count()) by bin(timestamp, 5m)",
            Threshold = 5.0,
            Severity = AlertSeverity.High
        },
        new AlertRule
        {
            Name = "Slow Response Time",
            Description = "Alert when average response time exceeds 2 seconds",
            Query = "requests | summarize AvgDuration = avg(duration) by bin(timestamp, 5m)",
            Threshold = 2000.0,
            Severity = AlertSeverity.Medium
        },
        new AlertRule
        {
            Name = "Database Connection Failures",
            Description = "Alert on database connectivity issues",
            Query = "dependencies | where type == 'SQL' and success == false | count",
            Threshold = 5.0,
            Severity = AlertSeverity.High
        }
    };
}
```

### Audit Logging:

#### 1. Activity Tracking Service
```csharp
public class ActivityTrackingService
{
    private readonly LeadTrackerDbContext _context;
    private readonly ITenantContext _tenantContext;
    private readonly ILogger<ActivityTrackingService> _logger;

    public async Task TrackActivityAsync(string action, string entityType, Guid entityId, object oldValues = null, object newValues = null)
    {
        try
        {
            var activity = new Activity
            {
                Id = Guid.NewGuid(),
                OrganizationId = _tenantContext.OrganizationId.Value,
                UserId = _tenantContext.UserId.Value,
                Action = action,
                EntityType = entityType,
                EntityId = entityId,
                OldValues = oldValues != null ? JsonSerializer.Serialize(oldValues) : null,
                NewValues = newValues != null ? JsonSerializer.Serialize(newValues) : null,
                CreatedAt = DateTime.UtcNow,
                IpAddress = _httpContextAccessor.HttpContext?.Connection.RemoteIpAddress?.ToString(),
                UserAgent = _httpContextAccessor.HttpContext?.Request.Headers["User-Agent"].FirstOrDefault()
            };

            _context.Activities.Add(activity);
            await _context.SaveChangesAsync();

            _logger.LogInformation("Activity tracked: {Action} on {EntityType} {EntityId} by user {UserId}",
                action, entityType, entityId, _tenantContext.UserId);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to track activity: {Action} on {EntityType} {EntityId}",
                action, entityType, entityId);
        }
    }
}

// Usage in controllers
[HttpPut("{id}")]
public async Task<IActionResult> UpdateLead(Guid id, UpdateLeadRequest request)
{
    var existingLead = await _leadService.GetByIdAsync(id);
    var updatedLead = await _leadService.UpdateAsync(id, request);
    
    await _activityTracker.TrackActivityAsync("Updated", "Lead", id, existingLead, updatedLead);
    
    return Ok(updatedLead);
}
```

## Dashboard and Monitoring:

#### 1. Application Insights Workbooks
```json
{
  "workbook": {
    "name": "Lead Tracker Monitoring Dashboard",
    "sections": [
      {
        "name": "System Health",
        "queries": [
          {
            "title": "Request Success Rate",
            "query": "requests | summarize SuccessRate = (countif(success == true) * 100.0) / count() by bin(timestamp, 5m) | render timechart"
          },
          {
            "title": "Response Time Percentiles",
            "query": "requests | summarize P50 = percentile(duration, 50), P95 = percentile(duration, 95), P99 = percentile(duration, 99) by bin(timestamp, 5m) | render timechart"
          }
        ]
      },
      {
        "name": "Business Metrics",
        "queries": [
          {
            "title": "Daily Lead Creation",
            "query": "customEvents | where name == 'Lead.Created' | summarize count() by bin(timestamp, 1d) | render columnchart"
          },
          {
            "title": "Conversion Funnel",
            "query": "customEvents | where name == 'Lead.Converted' | summarize count() by tostring(customDimensions.ToStage) | render piechart"
          }
        ]
      }
    ]
  }
}
```

## Consequences

### Positive:
- **Comprehensive Visibility**: Full request tracing with tenant context
- **Proactive Monitoring**: Automated alerts for issues
- **Business Insights**: KPI tracking and trend analysis
- **Security Auditing**: Complete activity trail for compliance
- **Performance Optimization**: Detailed APM data for tuning

### Negative:
- **Storage Costs**: Telemetry data can be expensive at scale
- **Performance Impact**: Logging overhead on high-traffic endpoints
- **Complexity**: Multiple monitoring tools and configurations

### Implementation Checklist:
- [ ] Configure Serilog with structured logging
- [ ] Implement tenant-aware enrichers
- [ ] Set up Application Insights telemetry
- [ ] Create custom health checks
- [ ] Build business metrics collection
- [ ] Implement activity tracking service
- [ ] Configure alert rules and notifications
- [ ] Create monitoring dashboards
- [ ] Set up log aggregation and analysis
- [ ] Implement error tracking and reporting
