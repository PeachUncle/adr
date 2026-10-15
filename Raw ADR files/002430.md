# ADR-004: Background Jobs Strategy

## Status
Accepted

## Context
Lead Tracker requires reliable background job processing for:
- Daily email summaries at 7:00 AM per user timezone
- Email notifications for task reminders
- CSV import/export processing for large datasets
- Data cleanup and archiving tasks
- Pipeline metrics calculation and caching

## Decision
We will use **Hangfire** with PostgreSQL storage for background job processing:

### Architecture Components:
1. **Hangfire Server** integrated in API application
2. **PostgreSQL storage** for job persistence and reliability
3. **Recurring jobs** for scheduled tasks (daily summaries)
4. **Fire-and-forget jobs** for immediate processing (notifications)
5. **Batch jobs** for bulk operations (CSV processing)

### Job Types:

#### 1. Recurring Jobs (Scheduled)
```csharp
// Daily summary emails at 7:00 AM user timezone
RecurringJob.AddOrUpdate<EmailService>(
    "daily-summary", 
    x => x.SendDailySummaryEmails(),
    "0 7 * * *", // 7:00 AM daily
    TimeZoneInfo.FindSystemTimeZoneById("UTC")
);

// Weekly pipeline metrics calculation
RecurringJob.AddOrUpdate<MetricsService>(
    "weekly-metrics",
    x => x.CalculatePipelineMetrics(),
    "0 2 * * 1" // 2:00 AM every Monday
);
```

#### 2. Fire-and-Forget Jobs (Immediate)
```csharp
// Task reminder notifications
BackgroundJob.Enqueue<NotificationService>(
    x => x.SendTaskReminder(taskId, userId)
);

// Welcome email after registration
BackgroundJob.Enqueue<EmailService>(
    x => x.SendWelcomeEmail(userId)
);
```

#### 3. Delayed Jobs (Scheduled Future)
```csharp
// Send reminder 1 hour before task due date
BackgroundJob.Schedule<NotificationService>(
    x => x.SendTaskReminder(taskId, userId),
    task.DueDate.AddHours(-1)
);
```

#### 4. Batch Jobs (Bulk Processing)
```csharp
// CSV import processing
var batchId = BatchJob.StartNew(x =>
{
    x.Enqueue<ImportService>(s => s.ValidateImportData(importId));
    x.Enqueue<ImportService>(s => s.ProcessImportBatch(importId, 1));
    x.Enqueue<ImportService>(s => s.ProcessImportBatch(importId, 2));
    // ... more batches
});

BatchJob.ContinueWith(batchId, x =>
    x.Enqueue<ImportService>(s => s.FinalizeImport(importId))
);
```

### Configuration:
```csharp
// Startup.cs
services.AddHangfire(config => config
    .SetDataCompatibilityLevel(CompatibilityLevel.Version_170)
    .UseSimpleAssemblyNameTypeSerializer()
    .UseRecommendedSerializerSettings()
    .UsePostgreSqlStorage(connectionString, new PostgreSqlStorageOptions
    {
        QueuePollInterval = TimeSpan.FromSeconds(15),
        JobExpirationCheckInterval = TimeSpan.FromHours(1),
        CountersAggregateInterval = TimeSpan.FromMinutes(5),
        PrepareSchemaIfNecessary = true,
        DashboardJobListLimit = 50000,
        TransactionSynchronisationTimeout = TimeSpan.FromMinutes(5)
    }));

services.AddHangfireServer(options =>
{
    options.WorkerCount = Environment.ProcessorCount * 2;
    options.Queues = new[] { "critical", "default", "low" };
    options.ServerTimeout = TimeSpan.FromMinutes(5);
    options.SchedulePollingInterval = TimeSpan.FromSeconds(15);
});
```

## Job Implementation Patterns

### 1. Email Service Jobs
```csharp
public class EmailService
{
    [Queue("critical")]
    public async Task SendDailySummaryEmails()
    {
        var users = await GetUsersWithPendingTasks();
        
        foreach (var user in users)
        {
            // Enqueue individual email jobs for better error handling
            BackgroundJob.Enqueue<EmailService>(
                x => x.SendUserDailySummary(user.Id)
            );
        }
    }
    
    [AutomaticRetry(Attempts = 3, DelaysInSeconds = new[] { 60, 300, 900 })]
    public async Task SendUserDailySummary(Guid userId)
    {
        // Send individual user summary
        // Automatic retry on failure with exponential backoff
    }
}
```

### 2. Import/Export Jobs
```csharp
public class ImportService
{
    [Queue("low")]
    [DisableConcurrentExecution(timeoutInSeconds: 10 * 60)]
    public async Task ProcessCsvImport(Guid importId)
    {
        // Process large CSV imports
        // Prevent concurrent execution of same import
        // 10-minute timeout for processing
    }
}
```

### 3. Cleanup Jobs
```csharp
public class MaintenanceService
{
    [Queue("low")]
    public async Task ArchiveOldActivities()
    {
        // Archive activities older than 2 years
        // Run during off-peak hours
    }
}
```

## Monitoring and Reliability

### 1. Dashboard Access
- Hangfire dashboard at `/hangfire` (admin-only)
- Real-time job monitoring and statistics
- Failed job inspection and retry capabilities

### 2. Error Handling
```csharp
[AutomaticRetry(Attempts = 3, DelaysInSeconds = new[] { 30, 60, 120 })]
public class ResilientJob
{
    public async Task Execute()
    {
        try
        {
            // Job logic
        }
        catch (TransientException ex)
        {
            // Will be retried automatically
            throw;
        }
        catch (PermanentException ex)
        {
            // Log and mark as failed
            _logger.LogError(ex, "Permanent failure in job");
            throw new JobFailedException("Job failed permanently", ex);
        }
    }
}
```

### 3. Logging Integration
```csharp
public class LoggedJob
{
    private readonly ILogger<LoggedJob> _logger;
    
    [JobDisplayName("Process Import #{0}")]
    public async Task ProcessImport(Guid importId)
    {
        using var scope = _logger.BeginScope(new { ImportId = importId });
        _logger.LogInformation("Starting import processing");
        
        // Job logic with structured logging
    }
}
```

## Alternatives Considered

### 1. Azure Service Bus
**Rejected** - Vendor lock-in, additional infrastructure cost

### 2. RabbitMQ + MassTransit
**Rejected** - Additional infrastructure complexity for MVP

### 3. Quartz.NET
**Rejected** - More complex setup, less monitoring capabilities

## Consequences

### Positive:
- **Reliable**: PostgreSQL persistence prevents job loss
- **Scalable**: Can add more worker processes/servers
- **Monitorable**: Built-in dashboard and metrics
- **Flexible**: Multiple job types and scheduling options
- **Integrated**: Shares same database as application

### Negative:
- **Single Point of Failure**: If API goes down, jobs stop
- **Resource Usage**: Background processing uses API server resources
- **Database Load**: Additional tables and connections

### Production Considerations:
- **Dedicated Workers**: Consider separate Hangfire server for production
- **Queue Separation**: Use different queues for different priorities
- **Resource Limits**: Monitor memory usage during bulk operations
- **Backup Strategy**: Include Hangfire tables in database backups

## Implementation Checklist:
- [ ] Configure Hangfire with PostgreSQL storage
- [ ] Implement email service with daily summaries
- [ ] Create import/export background jobs
- [ ] Set up monitoring and alerting
- [ ] Configure job queues by priority
- [ ] Implement error handling and retries
- [ ] Add structured logging for job tracking
- [ ] Create admin dashboard access controls
