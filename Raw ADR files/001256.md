# ADR-0004: Angular Async Testing Approach

## Status
Accepted

## Context
Our Angular unit tests for the AuthInterceptor were using `setTimeout` delays to coordinate asynchronous RxJS operations. This approach caused:
- Non-deterministic test behavior
- Different results between Windows (local) and Ubuntu (CI) environments
- Intermittent test failures requiring constant delay adjustments
- Tests that didn't actually validate event-driven behavior

Example of the problematic pattern:
```typescript
// Start first request
interceptor.intercept(request1, next1).subscribe();

// Wait arbitrary time for first request to process
setTimeout(() => {
  // Start second request
  interceptor.intercept(request2, next2).subscribe();
  
  // Wait for refresh to complete
  setTimeout(() => {
    refreshSubject.next(token);
    // More nested timeouts for assertions...
  }, 50);
}, 25);
```

## Decision
Use Angular's built-in `fakeAsync` and `tick()` testing utilities for all asynchronous test scenarios involving timers, promises, or observables.

## Rationale
1. **Deterministic execution**: `fakeAsync` creates a zone where we control time advancement
2. **No race conditions**: Tests execute the same way regardless of system performance
3. **Better test design**: Forces proper understanding of async flow rather than "wait and hope"
4. **Framework alignment**: Uses Angular's recommended testing patterns
5. **Maintainability**: No magic numbers or delay adjustments needed

## Implementation
Replace all `setTimeout` patterns with `fakeAsync`:

```typescript
it('should queue requests during token refresh', fakeAsync(() => {
  // Setup
  const refreshSubject = new Subject<TokenResponse>();
  authService.refreshToken.and.returnValue(refreshSubject.asObservable());
  
  // Start both requests
  interceptor.intercept(request1, next1).subscribe();
  tick(); // Advance microtasks
  
  interceptor.intercept(request2, next2).subscribe();
  tick(); // Process queuing
  
  // Complete refresh
  refreshSubject.next(token);
  refreshSubject.complete();
  flush(); // Process all pending async operations
  
  // Assertions
  expect(authService.refreshToken).toHaveBeenCalledTimes(1);
}));
```

## Consequences

### Positive
- Tests pass consistently across all environments
- Faster test execution (no real delays)
- Clearer test intent and flow
- Easier debugging of async issues
- Tests actually validate the event sequence

### Negative
- Requires understanding of Angular testing zones
- May need refactoring of existing delay-based tests
- Some complex RxJS scenarios might need `TestScheduler` instead

### Neutral
- Team needs training on `fakeAsync`/`tick`/`flush` concepts
- Test code looks different from production code

## Alternatives Considered

### 1. Increase setTimeout delays
- **Rejected**: Still non-deterministic, just fails less often

### 2. Use RxJS TestScheduler
- **Rejected**: More complex for simple timer scenarios
- **Note**: Still valid for complex observable marble testing

### 3. Use done() callbacks with real delays
- **Rejected**: Slow test execution, still environment-dependent

### 4. Mock all async operations
- **Rejected**: Doesn't test actual async behavior

## Related
- [Angular Testing Guide - Async Testing](https://angular.io/guide/testing-components-scenarios#async-test-with-fakeasync)
- [RxJS Testing Guide](https://rxjs.dev/guide/testing/marble-testing)
- Blocking Issue: BI-2025-09-09-002 (Test delay anti-pattern)

## Notes
This decision applies to all Angular unit tests, not just AuthInterceptor. Any test using `setTimeout`, `setInterval`, or testing promise/observable timing should use `fakeAsync`.

Exception: E2E tests use Playwright's own wait mechanisms and are not covered by this ADR.