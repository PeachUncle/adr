# 004. Memory Pooling with Scope-Based Lifetime Management

**Status:** ✅ Accepted
**Date:** 2024-11-17

## Context

Float32Array allocations dominate memory usage in tensor operations. In training loops, thousands of temporary tensors are created per iteration, causing GC pressure.

Pure functional architecture creates challenge: tensors are immutable and could be referenced anywhere, so we can't know when to free buffers.

Options considered:
1. Reference counting (complex, error-prone)
2. Automatic GC hooks with FinalizationRegistry (unreliable timing)
3. Explicit manual release (error-prone, leaks if forgotten)
4. Scope-based lifetime management (explicit but safe)
5. No pooling (simple but wasteful)

## Decision

Implement **scope-based memory pooling** with `withScope()` API.

## Rationale

**Architecture compatibility**:
- Works with pure functional immutable tensors
- Explicit lifetime control without reference counting
- No reliance on GC timing

**Ergonomics**:
- Single `withScope(() => ...)` wrapper
- All buffers auto-released on scope exit
- No manual tracking required

**Safety**:
- Can't forget to release (automatic on scope exit)
- Can't double-free (pool manages state)
- Clear ownership semantics

**Performance**:
- Limits buffer creation to maxPoolSize per size
- Reuses buffers across iterations
- Reduces GC pressure in training loops

## Implementation

```typescript
// TensorPool tracks buffers by size
class TensorPool {
  pools: Map<number, PoolEntry[]>
  maxPoolSize = 100 // per size

  acquire(size): Float32Array {
    // Find available buffer or create new
    // Add to pool if under maxPoolSize
  }

  release(buffer): void {
    // Mark buffer as available for reuse
  }
}

// withScope releases all buffers on exit
function withScope<T>(fn: () => T): T {
  try {
    return fn()
  } finally {
    // Mark all buffers as available
    for (pool of pools) {
      for (entry of pool) {
        entry.inUse = false
      }
    }
  }
}
```

## Usage Pattern

```typescript
// Training loop with pooling
for (let epoch = 0; epoch < 100; epoch++) {
  withScope(() => {
    // All tensor operations reuse buffers
    const loss = forward(input)
    backward(loss)
    // Buffers released here
  })
}

// Without scope: buffers accumulate up to maxPoolSize
```

## Consequences

**Positive**:
- Reduces allocations from unlimited to maxPoolSize
- Zero memory leaks (scope enforces cleanup)
- Compatible with pure functional architecture
- Explicit control over buffer lifetime
- Small code addition (~100 LOC)

**Negative**:
- Requires explicit `withScope` wrapper (not automatic)
- Releases ALL buffers on scope exit (conservative)
- Small overhead for pool management
- Returned tensors share buffer references (safe but surprising)

**Performance Impact**:
- Without scope: creates 1000 buffers for 1000 matmuls
- With scope: creates 100 buffers (maxPoolSize), reuses across all operations
- Benchmark: 4.19 eps/sec (no regression vs pre-pooling)

## Alternatives Rejected

**Reference counting**: Complex to implement correctly, easy to create cycles

**FinalizationRegistry**: GC timing is non-deterministic, can't rely on for performance

**Manual release**: Error-prone, easy to leak buffers

**No pooling**: Simple but wastes memory in training loops

## References

<!-- VERIFY: packages/tensor/src/pool.ts -->
Implementation: `packages/tensor/src/pool.ts`

<!-- VERIFY: packages/tensor/src/ops.ts -->
Integration: All ops in `packages/tensor/src/ops.ts` use acquireBuffer
