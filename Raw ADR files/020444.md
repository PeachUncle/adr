# ADR-006: Elsa Workflows - Three Architecture Options

## Status

Proposed - Decision Pending

## Date

2026-01-06

## Context

We've decided to use Elsa Workflows as our orchestration engine. However, there are multiple valid ways to integrate Elsa into our architecture. This ADR proposes **three architectural approaches**, each with different complexity, control, and operational trade-offs.

---

## Comparison Summary

| Aspect             | **Architecture 1: Elsa-Native** | **Architecture 2: Hybrid Control** | **Architecture 3: Elsa-as-Engine** |
| ------------------ | ------------------------------- | ---------------------------------- | ---------------------------------- |
| **Complexity**     | Low                             | Medium                             | High                               |
| **Time to MVP**    | 4-6 weeks                       | 6-8 weeks                          | 8-12 weeks                         |
| **Control**        | Low (trust Elsa)                | Medium (shared)                    | High (full control)                |
| **Databases**      | 1 (PostgreSQL)                  | 2 (PG + MongoDB)                   | 3 (PG + Mongo + Elsa PG)           |
| **State Owner**    | Elsa                            | Hybrid (Elsa + Us)                 | Us (Elsa is executor)              |
| **Event Sourcing** | Elsa logs                       | Custom (MongoDB)                   | Custom (MongoDB)                   |
| **Multi-tenancy**  | Workflow variables              | Hybrid                             | Custom layer                       |
| **Best For**       | Fast MVP, trust Elsa            | Balanced approach                  | Maximum control                    |

---

## Architecture 1: Elsa-Native (Simplest)

### Philosophy

**"Let Elsa do everything it's designed to do. We build on top."**

Minimize custom code, maximize use of Elsa's built-in features. Our application is a thin GraphQL layer over Elsa.

### Architecture Diagram

```
┌──────────────────────────────────────────────────┐
│ Frontend (SvelteKit)                             │
└──────────────────────────────────────────────────┘
                    ↓ GraphQL
┌──────────────────────────────────────────────────┐
│ API Layer (ASP.NET Core + HotChocolate)         │
│  - GraphQL resolvers                             │
│  - Thin wrapper around Elsa API                  │
└──────────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────┐
│ Elsa Workflows (owns everything)                │
│  - Workflow execution                            │
│  - State storage (workflow variables)            │
│  - Event logs (ActivityExecutionLog)             │
│  - Bookmarks (pause/resume)                      │
│  - Multi-tenancy (via variables)                 │
└──────────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────┐
│ PostgreSQL (single database)                     │
│  ├── Application tables:                         │
│  │   ├── tenants                                 │
│  │   ├── users                                   │
│  │   └── workflow_templates                      │
│  └── Elsa tables:                                │
│      ├── Elsa.WorkflowDefinitions                │
│      ├── Elsa.WorkflowInstances                  │
│      ├── Elsa.ActivityExecutionRecords           │
│      └── Elsa.WorkflowExecutionLog               │
└──────────────────────────────────────────────────┘
```

### Key Decisions

#### 1. State Storage: Elsa Variables

```csharp
// All workflow state stored in Elsa's workflow variables
await _elsaRuntime.StartWorkflowAsync(
    "brp-onboarding",
    input: new
    {
        // Tenant context
        TenantId = tenantId,
        TenantName = "Engie Belgium",

        // Workflow data (stored in Elsa variables)
        CompanyInfo = new { /* form data */ },
        PortfolioData = new { /* form data */ },
        ApprovalStatus = "pending",

        // Metadata
        CreatedBy = userId,
        CreatedAt = DateTime.UtcNow
    }
);

// In activities, access/update variables
public class FormActivity : Activity
{
    protected override async ValueTask OnResumeAsync(ActivityExecutionContext context)
    {
        var formData = context.GetInput<object>("formData");

        // Store directly in Elsa variable
        context.SetVariable("CompanyInfo", formData);

        await context.CompleteActivityAsync();
    }
}
```

#### 2. Event Sourcing: Use Elsa's Execution Log

```csharp
// Elsa automatically logs all activity executions
// Query via Elsa API
public async Task<List<WorkflowEvent>> GetAuditTrailAsync(string workflowId)
{
    var executionLog = await _elsaWorkflowInstanceStore
        .FindByIdAsync(workflowId)
        .GetExecutionLogAsync();

    return executionLog.Select(log => new WorkflowEvent
    {
        EventType = log.ActivityType,
        OccurredAt = log.StartedAt,
        Data = log.Payload
    }).ToList();
}
```

#### 3. Multi-Tenancy: Workflow Variables + Filters

```csharp
// Pass tenant context via variables
await _elsaRuntime.StartWorkflowAsync("brp-onboarding", new
{
    TenantId = tenantId,
    // ... other data
});

// Query workflows by tenant
public async Task<List<WorkflowInstance>> GetWorkflowsForTenantAsync(Guid tenantId)
{
    // Filter Elsa workflows by TenantId variable
    var instances = await _elsaWorkflowInstanceStore
        .FindManyAsync(new WorkflowInstanceFilter
        {
            WorkflowDefinitionId = "brp-onboarding",
            // Elsa 3.x: Filter by variable
            Variables = new Dictionary<string, object>
            {
                { "TenantId", tenantId }
            }
        });

    return instances;
}
```

#### 4. Custom Activities: Minimal

```csharp
// Only create activities for domain-specific operations
[Activity("WorkflowManager", "Human Tasks")]
public class FormActivity : Activity
{
    [Input] public Input<FormSchema> FormSchema { get; set; }
    [Input] public Input<string> AssignedTo { get; set; }

    protected override async ValueTask ExecuteAsync(ActivityExecutionContext context)
    {
        // Create bookmark
        context.CreateBookmark($"Form_{context.ActivityId}", new
        {
            Schema = FormSchema.Get(context),
            AssignedTo = AssignedTo.Get(context)
        });
    }

    protected override async ValueTask OnResumeAsync(ActivityExecutionContext context)
    {
        var formData = context.GetInput<object>("formData");
        context.SetVariable($"{context.ActivityId}_Data", formData);
        await context.CompleteActivityAsync();
    }
}

// That's it! Elsa handles the rest.
```

#### 5. GraphQL Layer: Thin Wrapper

```csharp
[ExtendObjectType("Mutation")]
public class WorkflowMutations
{
    public async Task<WorkflowInstanceDto> CreateWorkflowAsync(
        CreateWorkflowInput input,
        [Service] IElsaWorkflowRuntime runtime,
        [Service] ITenantContext tenant)
    {
        // Directly call Elsa
        var instance = await runtime.StartWorkflowAsync(
            input.WorkflowDefinitionId,
            new { TenantId = tenant.TenantId, ...input.Data }
        );

        return new WorkflowInstanceDto
        {
            Id = Guid.Parse(instance.Id),
            Status = instance.Status.ToString(),
            // Map from Elsa instance
        };
    }

    public async Task<WorkflowInstanceDto> ExecuteStepAsync(
        ExecuteStepInput input,
        [Service] IElsaWorkflowRuntime runtime)
    {
        // Resume Elsa workflow
        await runtime.ResumeWorkflowAsync(
            input.WorkflowId,
            bookmarkId: input.StepId,
            input: new { formData = input.Data }
        );

        // Fetch updated instance
        var instance = await runtime.FindByIdAsync(input.WorkflowId);

        return MapToDto(instance);
    }
}
```

### Pros

1. **✅ Fastest to implement** (4-6 weeks to MVP)
2. **✅ Simplest architecture** (single database, trust Elsa)
3. **✅ Leverage Elsa fully** (use all built-in features)
4. **✅ Less custom code to maintain**
5. **✅ Elsa handles state persistence, retries, bookmarks**

### Cons

1. **❌ Less control** over state structure
2. **❌ Harder to query** workflow data (Elsa's schema, not ours)
3. **❌ Audit trail** is Elsa's format (not custom event sourcing)
4. **❌ Coupled to Elsa** (harder to migrate away later)
5. **❌ Multi-tenancy** via variable filtering (not database RLS)

### When to Choose

- ✅ **Fast MVP needed** (2-3 months to production)
- ✅ **Small team** (1-2 devs)
- ✅ **Trust Elsa's design** decisions
- ✅ **Simple reporting** (basic dashboards, not complex analytics)
- ❌ **Don't choose if**: Need complex queries, strict compliance requirements

---

## Architecture 2: Hybrid Control (Balanced)

### Philosophy

**"Use Elsa for orchestration, own the business state."**

Elsa manages execution flow, we manage business data. Separate concerns: Elsa knows "what step am I on?", we know "what's the portfolio data?".

### Architecture Diagram

```
┌──────────────────────────────────────────────────┐
│ Frontend (SvelteKit)                             │
└──────────────────────────────────────────────────┘
                    ↓ GraphQL
┌──────────────────────────────────────────────────┐
│ API Layer (ASP.NET Core + HotChocolate)         │
│  - GraphQL resolvers                             │
│  - WorkflowService (orchestrates both)           │
└──────────────────────────────────────────────────┘
         ↓                              ↓
┌────────────────────┐      ┌──────────────────────┐
│ Elsa Workflows     │      │ Application Services │
│ (execution flow)   │      │ (business logic)     │
└────────────────────┘      └──────────────────────┘
         ↓                              ↓
┌────────────────────┐      ┌──────────────────────┐
│ PostgreSQL (Elsa)  │      │ PostgreSQL + MongoDB │
│ - Workflow state   │      │ - Tenants            │
│ - Bookmarks        │      │ - Users              │
│ - Execution log    │      │ - Workflow data      │
└────────────────────┘      │ - Events (audit)     │
                            └──────────────────────┘
```

### Key Decisions

#### 1. State Storage: Split Ownership

```csharp
// Elsa stores: execution state
await _elsaRuntime.StartWorkflowAsync("brp-onboarding", new
{
    TenantId = tenantId,           // Context only
    WorkflowInstanceId = instanceId,  // Our ID for correlation
    CurrentStepId = "company-info"    // Minimal tracking
});

// We store: business data in MongoDB
var instance = new WorkflowInstance
{
    Id = instanceId,
    TenantId = tenantId,
    ElsaInstanceId = elsaInstance.Id, // Correlation
    State = new WorkflowState
    {
        CurrentStepId = "company-info",
        StepStates = new Dictionary<string, StepState>
        {
            ["company-info"] = new StepState
            {
                Status = "pending",
                Data = null,  // Will be filled when user submits
                StartedAt = DateTime.UtcNow
            }
        },
        Metadata = new { /* rich metadata */ }
    },
    CreatedAt = DateTime.UtcNow
};

await _instanceRepository.InsertAsync(instance);
```

#### 2. Activity Pattern: Write to Both

```csharp
public class FormActivity : Activity
{
    [Inject] private IWorkflowService WorkflowService { get; set; }

    protected override async ValueTask OnResumeAsync(ActivityExecutionContext context)
    {
        var formData = context.GetInput<object>("formData");
        var workflowId = Guid.Parse(context.GetVariable<string>("WorkflowInstanceId"));

        // 1. Save to OUR database (MongoDB)
        await WorkflowService.SaveStepDataAsync(
            workflowId,
            context.ActivityId,
            formData
        );

        // 2. Store minimal reference in Elsa
        context.SetVariable($"{context.ActivityId}_Completed", true);

        await context.CompleteActivityAsync();
    }
}

// WorkflowService implementation
public async Task SaveStepDataAsync(Guid workflowId, string stepId, object data)
{
    var instance = await _instanceRepository.GetByIdAsync(workflowId);

    // Update MongoDB
    instance.State.StepStates[stepId] = new StepState
    {
        Status = "completed",
        Data = data,
        CompletedAt = DateTime.UtcNow
    };

    await _instanceRepository.UpdateAsync(instance);

    // Update PostgreSQL index (for fast queries)
    await _indexRepository.UpdateStepAsync(workflowId, stepId, "completed");

    // Record event (MongoDB)
    await _eventStore.AppendAsync(new WorkflowEvent
    {
        WorkflowInstanceId = workflowId,
        EventType = "STEP_COMPLETED",
        StepId = stepId,
        EventData = new { Data = data }
    });
}
```

#### 3. Event Sourcing: Custom (MongoDB)

```csharp
// Middleware intercepts all activity execution
public class EventSourcingMiddleware : IActivityExecutionMiddleware
{
    private readonly IEventStore _eventStore;

    public async ValueTask ExecuteAsync(
        ActivityExecutionContext context,
        ActivityExecutionDelegate next)
    {
        var workflowId = Guid.Parse(context.GetVariable<string>("WorkflowInstanceId"));

        // Before
        await _eventStore.AppendAsync(new WorkflowEvent
        {
            WorkflowInstanceId = workflowId,
            EventType = $"{context.Activity.Type}_STARTED",
            OccurredAt = DateTime.UtcNow
        });

        try
        {
            // Execute
            await next(context);

            // After (success)
            await _eventStore.AppendAsync(new WorkflowEvent
            {
                WorkflowInstanceId = workflowId,
                EventType = $"{context.Activity.Type}_COMPLETED",
                OccurredAt = DateTime.UtcNow
            });
        }
        catch (Exception ex)
        {
            // After (failure)
            await _eventStore.AppendAsync(new WorkflowEvent
            {
                WorkflowInstanceId = workflowId,
                EventType = $"{context.Activity.Type}_FAILED",
                EventData = new { Error = ex.Message },
                OccurredAt = DateTime.UtcNow
            });
            throw;
        }
    }
}
```

#### 4. Multi-Tenancy: PostgreSQL RLS + Elsa Variables

```csharp
// PostgreSQL RLS enforces tenant isolation for queries
public async Task<List<WorkflowInstanceDto>> GetWorkflowsAsync()
{
    // This query automatically filtered by RLS
    var index = await _dbContext.WorkflowInstancesIndex
        .Where(w => w.Status == "in_progress")
        .ToListAsync();

    // Fetch full data from MongoDB
    var instances = await _mongoDb.GetCollection<WorkflowInstance>("workflow_instances")
        .Find(w => index.Select(i => i.Id).Contains(w.Id))
        .ToListAsync();

    return instances.Select(MapToDto).ToList();
}

// Elsa workflows carry tenant context
await _elsaRuntime.StartWorkflowAsync("brp-onboarding", new
{
    TenantId = tenantContext.TenantId,
    // Activities can access this
});
```

#### 5. GraphQL Layer: Orchestration Service

```csharp
// WorkflowService orchestrates Elsa + our databases
public class WorkflowService
{
    private readonly IElsaWorkflowRuntime _elsaRuntime;
    private readonly IWorkflowInstanceRepository _instanceRepo;
    private readonly IWorkflowIndexRepository _indexRepo;
    private readonly IEventStore _eventStore;

    public async Task<WorkflowInstanceDto> CreateWorkflowAsync(CreateWorkflowCommand cmd)
    {
        // 1. Start Elsa workflow
        var elsaInstance = await _elsaRuntime.StartWorkflowAsync(
            cmd.TemplateId,
            new { TenantId = cmd.TenantId, WorkflowInstanceId = cmd.Id }
        );

        // 2. Create our instance (MongoDB)
        var instance = new WorkflowInstance
        {
            Id = cmd.Id,
            TenantId = cmd.TenantId,
            ElsaInstanceId = elsaInstance.Id,
            State = CreateInitialState(),
            CreatedAt = DateTime.UtcNow
        };
        await _instanceRepo.InsertAsync(instance);

        // 3. Create index (PostgreSQL)
        await _indexRepo.InsertAsync(new WorkflowInstanceIndex
        {
            Id = instance.Id,
            TenantId = instance.TenantId,
            ElsaInstanceId = elsaInstance.Id,
            Status = "in_progress"
        });

        // 4. Record event (MongoDB)
        await _eventStore.AppendAsync(new WorkflowEvent
        {
            WorkflowInstanceId = instance.Id,
            EventType = "WORKFLOW_CREATED"
        });

        return MapToDto(instance);
    }

    public async Task<WorkflowInstanceDto> ExecuteStepAsync(ExecuteStepCommand cmd)
    {
        // 1. Resume Elsa
        await _elsaRuntime.ResumeWorkflowAsync(
            cmd.ElsaInstanceId,
            cmd.StepId,
            new { formData = cmd.Data }
        );

        // 2. Activity middleware already saved to MongoDB
        // 3. Fetch updated state
        var instance = await _instanceRepo.GetByIdAsync(cmd.WorkflowId);

        return MapToDto(instance);
    }
}
```

### Pros

1. **✅ Balanced control** (Elsa handles flow, we handle data)
2. **✅ Rich queries** (PostgreSQL index for fast filtering)
3. **✅ Custom event sourcing** (full audit trail ownership)
4. **✅ Multi-tenant RLS** (database-level isolation)
5. **✅ Easier to migrate** away from Elsa (own business state)

### Cons

1. **❌ More complexity** (two storage systems to sync)
2. **❌ Longer implementation** (6-8 weeks)
3. **❌ Potential sync issues** (Elsa state vs our state)
4. **❌ More operational overhead** (2+ databases)

### When to Choose

- ✅ **Production-grade requirements** (compliance, reporting)
- ✅ **Need complex queries** (dashboards, analytics)
- ✅ **Want migration flexibility** (might replace Elsa later)
- ✅ **Medium team** (2-3 devs)
- ❌ **Don't choose if**: Simple use case, MVP speed critical

---

## Architecture 3: Elsa-as-Engine (Maximum Control)

### Philosophy

**"Elsa is just an execution engine. We own everything else."**

Elsa is a low-level runtime. We build our own workflow abstraction layer on top. Maximum control, maximum complexity.

### Architecture Diagram

```
┌──────────────────────────────────────────────────┐
│ Frontend (SvelteKit)                             │
└──────────────────────────────────────────────────┘
                    ↓ GraphQL
┌──────────────────────────────────────────────────┐
│ API Layer (ASP.NET Core + HotChocolate)         │
└──────────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────┐
│ Custom Workflow Abstraction Layer               │
│  ┌────────────────┐  ┌─────────────────────┐    │
│  │ Workflow       │  │ State Machine       │    │
│  │ Orchestrator   │  │ (our logic)         │    │
│  └────────────────┘  └─────────────────────┘    │
│  ┌────────────────┐  ┌─────────────────────┐    │
│  │ Step Executor  │  │ Compensation        │    │
│  │ (delegates)    │  │ Coordinator         │    │
│  └────────────────┘  └─────────────────────┘    │
└──────────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────┐
│ Elsa Runtime (execution engine only)             │
│  - Activity execution                            │
│  - Bookmark management                           │
│  - Persistence (minimal)                         │
└──────────────────────────────────────────────────┘
         ↓                              ↓
┌────────────────────┐      ┌──────────────────────┐
│ PostgreSQL (Elsa)  │      │ PostgreSQL + MongoDB │
│ - Execution state  │      │ - OUR workflow state │
│ (throwaway)        │      │ - OUR events         │
└────────────────────┘      │ - OUR templates      │
                            │ - EVERYTHING         │
                            └──────────────────────┘
```

### Key Decisions

#### 1. State Storage: We Own Everything

```csharp
// Elsa only stores: "which activity is running right now"
// Minimal, transient execution state

// We store: EVERYTHING in MongoDB
var instance = new WorkflowInstance
{
    Id = instanceId,
    TenantId = tenantId,
    TemplateId = templateId,
    ElsaInstanceId = elsaInstanceId,  // Just for correlation

    // OUR state machine
    State = new WorkflowState
    {
        CurrentStepId = "company-info",
        Status = WorkflowStatus.InProgress,

        // Complete step history
        StepStates = new Dictionary<string, StepState>(),

        // Our transition rules
        ValidTransitions = template.Definition.Transitions,

        // Our validation rules
        ValidationRules = template.Definition.ValidationRules,

        // Rich metadata
        Metadata = new WorkflowMetadata
        {
            StartedAt = DateTime.UtcNow,
            PausedDuration = TimeSpan.Zero,
            TotalSteps = template.Definition.Steps.Count,
            CompletedSteps = 0,
            Priority = "high",
            SLA = DateTime.UtcNow.AddDays(7),
            Tags = new[] { "brp", "onboarding", "q1-2026" }
        }
    },

    CreatedAt = DateTime.UtcNow,
    CreatedBy = userId
};
```

#### 2. Custom Orchestrator: We Decide Flow

```csharp
// Our orchestrator calls Elsa for step execution
public class WorkflowOrchestrator
{
    public async Task<WorkflowInstance> ExecuteStepAsync(
        Guid workflowId,
        string stepId,
        object data,
        ExecutionContext context)
    {
        var instance = await _instanceRepo.GetByIdAsync(workflowId);
        var template = await _templateRepo.GetByIdAsync(instance.TemplateId);

        // 1. OUR validation (before Elsa)
        var isValidTransition = ValidateTransition(
            instance.State.CurrentStepId,
            stepId,
            template.Definition.Transitions
        );

        if (!isValidTransition)
        {
            throw new InvalidTransitionException(
                $"Cannot transition from {instance.State.CurrentStepId} to {stepId}"
            );
        }

        // 2. OUR state update (before Elsa)
        instance.State.CurrentStepId = stepId;
        instance.State.StepStates[stepId] = new StepState
        {
            Status = "in_progress",
            Data = data,
            StartedAt = DateTime.UtcNow
        };

        await _instanceRepo.UpdateAsync(instance);

        // 3. Call Elsa to execute activity (Elsa is just executor)
        try
        {
            await _elsaRuntime.ResumeWorkflowAsync(
                instance.ElsaInstanceId,
                stepId,
                new { data }
            );

            // 4. OUR state update (after Elsa success)
            instance.State.StepStates[stepId].Status = "completed";
            instance.State.StepStates[stepId].CompletedAt = DateTime.UtcNow;
            instance.State.Metadata.CompletedSteps++;

            await _instanceRepo.UpdateAsync(instance);
        }
        catch (Exception ex)
        {
            // 5. OUR error handling
            instance.State.StepStates[stepId].Status = "failed";
            instance.State.StepStates[stepId].Error = ex.Message;

            await _instanceRepo.UpdateAsync(instance);

            throw;
        }

        // 6. OUR event recording
        await _eventStore.AppendAsync(new WorkflowEvent
        {
            WorkflowInstanceId = workflowId,
            EventType = "STEP_COMPLETED",
            StepId = stepId,
            EventData = new
            {
                Data = data,
                PreviousState = /* snapshot */,
                NewState = instance.State
            }
        });

        return instance;
    }
}
```

#### 3. Activities: Thin Delegates

```csharp
// Activities just execute logic, don't manage state
public class FormActivity : Activity
{
    // No state management in activity!
    // Orchestrator already updated state before calling us

    protected override async ValueTask OnResumeAsync(ActivityExecutionContext context)
    {
        var data = context.GetInput<object>("data");

        // Just validate
        var validator = context.GetRequiredService<IFormValidator>();
        await validator.ValidateAsync(data);

        // That's it! Orchestrator handles the rest.
        await context.CompleteActivityAsync();
    }
}
```

#### 4. Custom State Machine

```csharp
// We implement our own state machine logic
public class WorkflowStateMachine
{
    public bool CanTransition(
        string fromStepId,
        string toStepId,
        WorkflowTemplate template)
    {
        var step = template.Definition.Steps
            .First(s => s.Id == fromStepId);

        return step.AllowedTransitions.Contains(toStepId);
    }

    public async Task<ValidationResult> ValidateStateAsync(
        WorkflowInstance instance,
        WorkflowTemplate template)
    {
        var errors = new List<ValidationError>();

        // Check all required steps completed
        var requiredSteps = template.Definition.Steps
            .Where(s => s.Required);

        foreach (var step in requiredSteps)
        {
            if (!instance.State.StepStates.ContainsKey(step.Id) ||
                instance.State.StepStates[step.Id].Status != "completed")
            {
                errors.Add(new ValidationError
                {
                    StepId = step.Id,
                    Message = $"Required step '{step.Name}' not completed"
                });
            }
        }

        // Custom validation rules
        foreach (var rule in template.Definition.ValidationRules)
        {
            var result = await rule.ValidateAsync(instance.State);
            if (!result.IsValid)
            {
                errors.AddRange(result.Errors);
            }
        }

        return new ValidationResult { IsValid = !errors.Any(), Errors = errors };
    }

    public async Task RollbackAsync(
        WorkflowInstance instance,
        string toStepId,
        ICompensationCoordinator compensator)
    {
        var stepsToCompensate = GetStepsBetween(
            instance.State.CurrentStepId,
            toStepId,
            instance.State.StepStates.Keys
        ).Reverse();

        foreach (var stepId in stepsToCompensate)
        {
            await compensator.CompensateStepAsync(
                instance.Id,
                stepId,
                instance.State.StepStates[stepId].Data
            );

            instance.State.StepStates.Remove(stepId);
        }

        instance.State.CurrentStepId = toStepId;
        instance.Status = WorkflowStatus.InProgress;

        await _instanceRepo.UpdateAsync(instance);
    }
}
```

#### 5. Event Sourcing: Complete Ownership

```csharp
// Every state change is an event
public class EventStore
{
    public async Task AppendAsync(WorkflowEvent @event)
    {
        @event.EventId = Guid.NewGuid();
        @event.OccurredAt = DateTime.UtcNow;

        await _mongoDb
            .GetCollection<WorkflowEvent>("workflow_events")
            .InsertOneAsync(@event);
    }

    public async Task<WorkflowState> ReplayEventsAsync(
        Guid workflowId,
        DateTime? untilTimestamp = null)
    {
        var query = _mongoDb
            .GetCollection<WorkflowEvent>("workflow_events")
            .Find(e => e.WorkflowInstanceId == workflowId);

        if (untilTimestamp.HasValue)
        {
            query = query.Where(e => e.OccurredAt <= untilTimestamp.Value);
        }

        var events = await query
            .SortBy(e => e.OccurredAt)
            .ToListAsync();

        var state = new WorkflowState();

        foreach (var @event in events)
        {
            state = ApplyEvent(state, @event);
        }

        return state;
    }

    private WorkflowState ApplyEvent(WorkflowState state, WorkflowEvent @event)
    {
        return @event.EventType switch
        {
            "WORKFLOW_CREATED" => /* ... */,
            "STEP_STARTED" => /* ... */,
            "STEP_COMPLETED" => /* ... */,
            "WORKFLOW_PAUSED" => /* ... */,
            // ... handle all event types
            _ => state
        };
    }
}
```

### Pros

1. **✅ Maximum control** over every aspect
2. **✅ Fully custom state machine** (exact requirements)
3. **✅ Own event sourcing** (regulatory compliance)
4. **✅ Easy to replace Elsa** (it's just an executor)
5. **✅ Custom validation, rollback, compensation** logic
6. **✅ No Elsa coupling** in business logic

### Cons

1. **❌ Most complexity** (essentially building a workflow engine)
2. **❌ Longest timeline** (8-12 weeks to MVP)
3. **❌ Most code to maintain**
4. **❌ Reinventing Elsa features** (state management, bookmarks)
5. **❌ Requires experienced team**

### When to Choose

- ✅ **Strict compliance requirements** (full audit control)
- ✅ **Complex business rules** (custom state machine)
- ✅ **Long-term investment** (willing to build custom)
- ✅ **Experienced team** (3+ senior devs)
- ❌ **Don't choose if**: Fast MVP needed, small team, trust Elsa

---

## Decision Matrix

### By Use Case

| Use Case                  | Architecture 1 | Architecture 2 | Architecture 3 |
| ------------------------- | -------------- | -------------- | -------------- |
| **MVP in 8 weeks**        | ⭐⭐⭐         | ⭐⭐           | ❌             |
| **Complex reporting**     | ⭐             | ⭐⭐⭐         | ⭐⭐⭐         |
| **Strict compliance**     | ⭐             | ⭐⭐           | ⭐⭐⭐         |
| **Custom business rules** | ⭐             | ⭐⭐           | ⭐⭐⭐         |
| **Easy maintenance**      | ⭐⭐⭐         | ⭐⭐           | ⭐             |
| **Migration flexibility** | ⭐             | ⭐⭐           | ⭐⭐⭐         |
| **Small team (1-2)**      | ⭐⭐⭐         | ⭐⭐           | ❌             |
| **Large team (3+)**       | ⭐⭐           | ⭐⭐⭐         | ⭐⭐⭐         |

### By Team Expertise

| Team Profile          | Recommended Architecture      |
| --------------------- | ----------------------------- |
| **Junior .NET team**  | Architecture 1 (learn Elsa)   |
| **Mixed experience**  | Architecture 2 (balanced)     |
| **Senior architects** | Architecture 3 (full control) |
| **Solo developer**    | Architecture 1 (simplest)     |
| **Startup speed**     | Architecture 1 (fastest)      |
| **Enterprise grade**  | Architecture 2 or 3           |

### By Timeline

| Timeline       | Feasible Architectures |
| -------------- | ---------------------- |
| **< 2 months** | Architecture 1 only    |
| **2-3 months** | Architecture 1 or 2    |
| **3-4 months** | Architecture 2 (solid) |
| **4+ months**  | All architectures      |

---

## Recommendation

### For Your Context (Elia Workflow Manager)

Based on:

- **Team**: 3 developers (1 TS expert, 2 .NET experts)
- **Timeline**: Production in 3-4 months
- **Requirements**: Compliance, audit, reporting
- **Complexity**: Medium (7 market roles, multi-tenant)

**Recommended: Architecture 2 (Hybrid Control)**

#### Why?

1. **✅ Balanced approach** for your team size and timeline
2. **✅ Meets compliance** requirements (custom event sourcing)
3. **✅ Enables rich reporting** (PostgreSQL index + MongoDB)
4. **✅ Multi-tenant RLS** (security requirement)
5. **✅ Reasonable timeline** (6-8 weeks implementation)
6. **✅ Migration path** (can simplify to Arch 1 or expand to Arch 3)

#### Alternative Paths

**If speed is critical** (need MVP in 6 weeks):
→ Start with **Architecture 1**, migrate to 2 later

**If full control is non-negotiable** (regulatory reasons):
→ Choose **Architecture 3**, accept longer timeline

---

## Next Steps

1. **Choose architecture** based on priorities (speed vs control)
2. **Create POC** (2 weeks)
   - Implement simple BRP workflow
   - Test pause/resume/rollback
   - Validate approach
3. **Review POC results**
4. **Commit to architecture**
5. **Full implementation**

---

## Questions to Answer

Before deciding, answer:

1. **Timeline**: Do we need MVP in < 8 weeks? (→ Arch 1)
2. **Control**: How important is full state ownership? (→ Arch 3)
3. **Queries**: Need complex reporting/analytics? (→ Arch 2 or 3)
4. **Team**: Comfortable with complexity? (→ Arch 2 or 3)
5. **Budget**: Can maintain 3 databases? (→ Arch 3 needs most infra)

---

What would you like to explore deeper? Or shall we decide and move forward with implementation?
