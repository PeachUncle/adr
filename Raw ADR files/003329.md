# ADR 0005: Incremental Migration from Synchronous to Asynchronous Application Logic

## Status
Accepted

## Context

The existing internal library (Domain, ApplicationLogic, Infrastructure) was designed as a synchronous API.

This decision was historically justified because:
- The primary (and only) client was a WinForms application
- UI logic was event-driven and synchronous
- No external clients or network boundaries existed
- Database access patterns were synchronous at the time

With the introduction of an API layer, new constraints apply:
- API controllers require non-blocking, asynchronous execution
- Network I/O and scalability require async-first patterns
- Wrapping synchronous logic using Task.Run is not acceptable as a long-term solution

At the same time, the system must be modernized incrementally:
- No full rewrite
- No breaking changes to the existing WinForms UI
- Business continuity must be preserved

## Decision

We will introduce an incremental async migration strategy for ApplicationLogic.

### Principles

1. Synchronous ApplicationLogic APIs remain valid
- Existing synchronous methods are not removed
- WinForms continues to call synchronous methods during the transition

2. Asynchronous APIs are introduced alongside synchronous ones
- New async methods are added using the Async suffix
- Async methods delegate to Infrastructure async operations where possible

3. API layer must use asynchronous ApplicationLogic APIs
- API controllers must NOT call synchronous methods
- Task.Run, .Result, and .Wait() are explicitly forbidden in the API layer

4. No business logic duplication
- Async methods must reuse existing business rules
- Logic may be refactored internally to shared private methods if needed

5. Migration is use-case driven
- Async migration is performed per use case, not per layer
- Only functionality exposed through the API must be async initially

## Example Pattern

### Before (synchronous only)

```csharp
public class OrderService
{
    public Order Get(Guid id)
    {
        return _repository.Get(id);
    }
}

```

### After (incremental async)


```csharp
public class OrderService
{
    public Order Get(Guid id)
    {
        return GetInternal(id);
    }

    public async Task<Order> GetAsync(Guid id, CancellationToken ct = default)
    {
        return await GetInternalAsync(id, ct);
    }

    private Order GetInternal(Guid id)
    {
        return _repository.Get(id);
    }

    private async Task<Order> GetInternalAsync(Guid id, CancellationToken ct)
    {
        return await _repository.GetAsync(id, ct);
    }
}
```

### API usage (mandatory async)

```csharp
[HttpGet("{id}")]
public async Task<ActionResult<OrderDto>> GetOrder(Guid id, CancellationToken ct)
{
    var order = await _orderService.GetAsync(id, ct);
    if (order == null)
        return NotFound();

    return Ok(order);
}

```

### WinForms usage (unchanged)

```csharp
var order = _orderService.Get(orderId);
```

## Consequences

### Positive

- No breaking changes to existing UI
- API layer remains scalable and non-blocking
- Async migration can be planned and controlled
- Avoids Task.Run anti-patterns
- Clear contract for future contributors and tooling

### Negative

- Temporary duplication of sync and async APIs
- Slightly increased maintenance cost during migration
- Requires discipline to avoid regressions

### Notes

- Once all UI clients are async-capable, synchronous APIs may be deprecated
- Removal of synchronous APIs requires a separate ADR
- Any deviation from this strategy requires explicit architectural approval
