# ADR-0002: E2E Database Performance Optimization

## Status

Accepted

## Date

2025-08-30

## Context

After implementing the test server optimization changes, E2E tests began experiencing severe performance degradation:

- Individual tests taking 30+ seconds instead of milliseconds
- API endpoints timing out after 20+ seconds
- Test suite completion time increased from minutes to hours
- All API calls in Testing environment were affected, not just database operations

Investigation revealed two critical performance issues introduced during the test optimization work:

1. **Expensive AnyAsync() Checks**: The `DatabaseTestService.ResetWithEfCoreAsync()` method included "optimization" checks that ran 4 separate `AnyAsync()` queries before each database reset to determine if cleanup was needed
2. **Database Path Issues**: Test setup used potentially inaccessible temp directory paths that could cause Entity Framework operations to hang

## Decision

We will optimize E2E test database operations by:

### 1. Remove Expensive Pre-Reset Checks

Remove the `AnyAsync()` checks from `DatabaseTestService.ResetWithEfCoreAsync()`:

```csharp
// REMOVED - Performance killer:
var hasData = await _context.People.AnyAsync() || 
             await _context.Roles.AnyAsync() || 
             await _context.Windows.AnyAsync() || 
             await _context.Walls.AnyAsync();

if (!hasData) {
    _logger.LogDebug("Database already clean for worker {WorkerIndex}", workerIndex);
    return;
}

// KEPT - Efficient bulk operations:
await _context.People.ExecuteDeleteAsync();
await _context.Roles.ExecuteDeleteAsync();  
await _context.Windows.ExecuteDeleteAsync();
await _context.Walls.ExecuteDeleteAsync();
```

**Rationale**: 
- The 4 `AnyAsync()` queries were more expensive than the `ExecuteDeleteAsync()` operations they were trying to avoid
- `ExecuteDeleteAsync()` is already optimized and handles empty tables efficiently
- The "optimization" was actually a pessimization causing 4 round-trips per reset

### 2. Fix Database Path Resolution

Change test database location from potentially inaccessible temp directory to reliable working directory:

```typescript
// OLD - Platform-specific hardcoded paths:
const tempDir = process.platform === 'win32' ? process.env.TEMP || 'C:\\temp' : '/tmp';
const databasePath = path.join(tempDir, `CrudTest_${timestamp}.db`);

// BETTER - Cross-platform temp directory:
const tempDir = process.env.TEMP || process.env.TMP || process.env.TMPDIR || os.tmpdir();
const databasePath = path.join(tempDir, `CrudTest_${timestamp}.db`);

// ALTERNATIVE - Project directory (if temp not available):
const databasePath = path.join(process.cwd(), '..', '..', `CrudTest_${timestamp}.db`);
```

## Consequences

### Positive

- **Massive Performance Improvement**: Tests run in seconds instead of 30+ seconds each
- **Reliable Database Access**: No more Entity Framework hanging due to path issues  
- **Simplified Code**: Removed unnecessary complexity from database reset logic
- **Better Test Experience**: Fast feedback loop restored for developers

### Negative

- **Slightly Less "Smart" Cleanup**: Database reset always runs DELETE operations even on empty tables (but this is negligible performance impact)
- **Database Files in Project Root**: Test databases created in project directory instead of temp (cleaned up automatically)

### Monitoring

- E2E test execution times should remain under 10 seconds per test
- API response times in Testing environment should be under 1 second
- No timeouts should occur during normal test operations

## Related

- ADR-0001: Serial E2E Testing (database isolation strategy)
- Original optimization spec: `specs/2025-08-29-test-server-optimization/tasks.md`

## Notes

This demonstrates the importance of:
1. **Performance testing** optimization changes, especially database operations
2. **Avoiding premature optimization** - the `AnyAsync()` checks were counterproductive  
3. **Path reliability** in cross-platform test environments
4. **Measuring before optimizing** - the original problem was startup time, not database reset time