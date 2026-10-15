---
docid: ADR-064
title: ADR 026 Erp Startup Performance Optimization
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿# ADR-026: ERP Connector Startup Performance Optimization

**Status**: Proposed  
**Date**: 2026-01-03  
**Reviewers**: @Architect, @TechLead  
**Deciders**: @Architect, @TechLead, @Backend, @Enventa  
**DocID**: `ADR-026`

---

## Context

The ERP Connector service based on eGate patterns has **startup speed issues** caused by:
1. **Synchronous global object creation** during service startup
2. **Lock contention** in `CreateGlobal()` for enventa login (which is NOT thread-safe)
3. **Fire-and-forget Task.Run()** in `Initialize()` without proper completion tracking
4. **Blocking wait** when pool is exhausted

### Current Startup Sequence

```
ErpConnectorService.Start()
    │
    ├── EnventaGlobalFactory.Initialize(factory, poolSize)
    │       │
    │       └── (Nothing actually created here - lazy initialization)
    │
    ├── EnventaActorPool.Instance (singleton access - triggers lazy init)
    │       │
    │       └── EnventaActorPool() constructor
    │               └── Logger.Info("ERP Actor Pool initialized")
    │
    └── WebApp.Start<Startup>(baseAddress)  ← HTTP API ready
```

### Actual Pool Creation (Lazy - On First Request)

```
EnventaGlobalFactory.Get(identity)
    │
    ├── _globalPools.GetOrAdd(token, ...) 
    │       │
    │       └── new Lazy<EnventaGlobalPool>(() => CreateGlobalPool(identity))
    │               │
    │               └── CreateGlobalPool(identity)
    │                       │
    │                       ├── new EnventaGlobalPool(...)
    │                       │
    │                       └── pool.Initialize()  ← BLOCKING STARTUP ISSUE
    │                               │
    │                               └── for (int i = 0; i < _poolSize; i++)
    │                                       Task.Run(() => CreateGlobal())  ← Fire & forget!
```

### CreateGlobal() - The Bottleneck

```csharp
public void CreateGlobal()
{
    var globalId = Guid.NewGuid();
    var global = _globalObjectFactory.CreateGlobalObject(globalId);
    
    // ⚠️ PROBLEM: Login must be synchronized - enventa is NOT thread-safe
    lock (_lock)  // Static lock blocks ALL tenants!
    {
        _globalObjectFactory.Login(global, _identity);  // Slow network I/O
    }
    
    _globalObjectFactory.Validate(global);
    _globalObjectFactory.EnableCaching(global);
    
    _poolGlobals.Add(global);
    PutGlobal(global);
    global.CloseConnection();
}
```

---

## Identified Problems

### Problem 1: Fire-and-Forget Initialization
**Severity**: High  
**Impact**: First request may fail if pool not ready

```csharp
public void Initialize()
{
    for (int i = 0; i < _poolSize; i++)
    {
        Task.Run(() => CreateGlobal());  // No await, no tracking!
    }
}
```

**Issue**: Pool returns immediately but connections aren't ready. First `GetGlobal()` call may:
- Return successfully if at least one `CreateGlobal()` completed
- Block indefinitely waiting for `_globalWaitHandle`
- Timeout after 30 seconds per attempt

### Problem 2: Static Lock Contention
**Severity**: High  
**Impact**: All tenants blocked by single login operation

```csharp
private static readonly object _lock = new object();  // STATIC = ALL tenants share!

lock (_lock)
{
    _globalObjectFactory.Login(global, _identity);  // Blocks everyone
}
```

**Issue**: If TenantA is logging in, TenantB, TenantC, etc. all wait, even though they use different credentials.

### Problem 3: Synchronous Blocking on Pool Exhaustion
**Severity**: Medium  
**Impact**: Request threads block, reducing throughput

```csharp
public IFSGlobalObjects GetGlobal()
{
    if (!_availableGlobals.TryTake(out var global))
    {
        Task.Run(() => CreateGlobal());  // Fire-and-forget
        
        while (!_availableGlobals.TryTake(out global))
        {
            _globalWaitHandle.WaitOne(TimeSpan.FromSeconds(30));  // BLOCKING!
        }
    }
    return global;
}
```

**Issue**: Request threads block instead of yielding, reducing server throughput under load.

### Problem 4: No Warmup Strategy
**Severity**: Medium  
**Impact**: Cold start penalty on first requests

The current implementation creates connections lazily on first access. This means:
- First request for each tenant has high latency
- Multiple concurrent first requests may cause thundering herd

---

## Decision

Implement a **multi-phase startup optimization** strategy:

### Phase 1: Per-Tenant Lock (Quick Win)
Replace static lock with per-identity lock:

```csharp
// BEFORE: Static lock blocks ALL tenants
private static readonly object _lock = new object();

// AFTER: Per-identity lock allows parallel tenant logins
private readonly object _instanceLock = new object();

lock (_instanceLock)  // Only blocks same tenant
{
    _globalObjectFactory.Login(global, _identity);
}
```

**Rationale**: Different tenants use different credentials, so their logins are independent.

### Phase 2: Async Initialization with Completion Tracking
Replace fire-and-forget with tracked async initialization:

```csharp
public async Task InitializeAsync(CancellationToken ct = default)
{
    Log.Info("Initializing EnventaGlobalPool for {0} with pool size {1}", _identity, _poolSize);

    // Create minimum viable pool (1 connection) synchronously for immediate availability
    await CreateGlobalAsync(ct);
    
    // Warm up remaining connections in background with tracking
    _warmupTask = WarmupRemainingAsync(_poolSize - 1, ct);
}

private Task _warmupTask = Task.CompletedTask;

private async Task WarmupRemainingAsync(int count, CancellationToken ct)
{
    for (int i = 0; i < count; i++)
    {
        if (ct.IsCancellationRequested) break;
        await CreateGlobalAsync(ct);
        
        // Small delay to avoid overwhelming ERP server
        await Task.Delay(100, ct);
    }
}

public Task WaitForWarmupAsync() => _warmupTask;
```

### Phase 3: Async GetGlobal with Timeout
Replace blocking wait with async/await:

```csharp
public async ValueTask<IFSGlobalObjects> GetGlobalAsync(CancellationToken ct = default)
{
    if (_disposed)
        throw new ObjectDisposedException(nameof(EnventaGlobalPool));

    // Try to get from pool
    if (_availableGlobals.TryTake(out var global))
    {
        Log.Trace("Got global object from pool for {0}", _identity);
        return global;
    }

    // Pool exhausted - create new one (not fire-and-forget)
    using var timeoutCts = CancellationTokenSource.CreateLinkedTokenSource(ct);
    timeoutCts.CancelAfter(TimeSpan.FromSeconds(30));
    
    try
    {
        return await CreateGlobalAsync(timeoutCts.Token);
    }
    catch (OperationCanceledException) when (!ct.IsCancellationRequested)
    {
        throw new TimeoutException($"Failed to create ERP connection for {_identity} within 30 seconds");
    }
}
```

### Phase 4: Background Warmup Service
Add optional background warmup for configured tenants:

```csharp
// In Startup.cs or service configuration
public class ErpWarmupHostedService : IHostedService
{
    public async Task StartAsync(CancellationToken ct)
    {
        // Read configured tenants from appsettings
        var tenantsToWarm = _config.GetSection("Erp:WarmupTenants").Get<string[]>() ?? [];
        
        foreach (var tenant in tenantsToWarm)
        {
            var identity = await GetTenantIdentityAsync(tenant, ct);
            var pool = EnventaGlobalFactory.GetOrCreatePool(identity);
            await pool.InitializeAsync(ct);
            
            _logger.Info("Pre-warmed ERP pool for tenant {Tenant}", tenant);
        }
    }
}
```

### Phase 5: Health Check Integration
Add pool health to service health endpoint:

```csharp
[Route("api/health")]
public async Task<IHttpActionResult> GetHealth()
{
    var poolStats = EnventaGlobalFactory.GetAllStatistics();
    
    return Ok(new
    {
        status = "healthy",
        timestamp = DateTime.UtcNow,
        pools = poolStats.Select(p => new
        {
            tenant = p.TenantId,
            available = p.AvailableConnections,
            total = p.TotalConnections,
            warmupComplete = p.WarmupComplete
        })
    });
}
```

---

## Comparison: Current vs. Proposed

| Aspect | Current | Proposed |
|--------|---------|----------|
| **First Request Latency** | High (cold start) | Low (warmup) |
| **Lock Contention** | All tenants blocked | Per-tenant isolation |
| **Initialization Tracking** | None (fire-and-forget) | Task completion |
| **Error Handling** | Swallowed in Task.Run | Propagated to caller |
| **Pool Exhaustion** | Blocking wait | Async with timeout |
| **Observability** | Logs only | Metrics + health |

---

## Implementation Priority

### P0 - Critical (Week 1)
1. **Per-tenant lock** - Simple change, immediate benefit
2. **Async CreateGlobalAsync** - Foundation for other improvements

### P1 - High (Week 2)
3. **Tracked initialization** - Remove fire-and-forget
4. **Async GetGlobalAsync** - Non-blocking pool access

### P2 - Medium (Week 3-4)
5. **Background warmup service** - Optional pre-warming
6. **Health check integration** - Observability

---

## Metrics to Track

| Metric | Current | Target |
|--------|---------|--------|
| Service startup time | Unknown | < 5s |
| First request latency | High (cold start) | < 500ms (warmed) |
| Pool exhaustion events | Unknown | < 1/hour |
| Login lock wait time | Unknown | < 100ms avg |

---

## Risks & Mitigations

### Risk 1: Breaking Changes to API
**Mitigation**: Keep sync methods as wrappers around async versions:
```csharp
public IFSGlobalObjects GetGlobal() => GetGlobalAsync().GetAwaiter().GetResult();
```

### Risk 2: enventa Thread Safety Violations
**Mitigation**: Keep per-tenant locks, never share connections across threads.

### Risk 3: Increased Complexity
**Mitigation**: Phase implementation, comprehensive tests.

---

## Testing Strategy

1. **Unit Tests**: Mock factory, verify initialization behavior
2. **Integration Tests**: Verify pool behavior under load
3. **Load Tests**: Measure startup time, throughput, latency
4. **Chaos Tests**: Pool exhaustion, login failures, timeouts

---

## References

- [EnventaGlobalPool.cs](../../erp-connector/src/B2X.ErpConnector/Infrastructure/Erp/EnventaGlobalPool.cs)
- [EnventaGlobalFactory.cs](../../erp-connector/src/B2X.ErpConnector/Infrastructure/Erp/EnventaGlobalFactory.cs)
- [ErpConnectorService.cs](../../erp-connector/src/B2X.ErpConnector/ErpConnectorService.cs)
- [ADR-023] ERP Plugin Architecture
- [KB-021] enventa Trade ERP
- eGate Reference: FSGlobalPool, FSGlobalFactory patterns

---

## Decision Outcome

**Pending Review**: @Architect and @TechLead to approve.

---

**Agents**: @Architect, @TechLead, @Enventa | **Owner**: @Architect
