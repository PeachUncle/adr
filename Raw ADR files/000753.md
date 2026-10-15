# ADR-001: Actor-Based Concurrency for Thread Safety

## Status

Accepted

**Date:** 2025-11-20

## Context

The Trading Cockpit application handles concurrent operations from multiple sources:

- Real-time market data streaming via WebSocket
- User-initiated trading operations
- Background portfolio synchronization
- 3D visualization updates

These concurrent operations access shared mutable state (positions, quotes, orders), creating potential race conditions and data corruption. We need a concurrency model that:

1. Guarantees thread safety without explicit locks
2. Prevents data races at compile time
3. Maintains good performance for real-time updates
4. Integrates well with Swift's async/await

## Decision

We will use Swift's **Actor model** for managing shared mutable state.

Key components will be implemented as actors:
- `MarketDataHub` - Manages quote cache and WebSocket connections
- `PortfolioManager` - Manages positions and order state
- `DatabaseManager` - Handles SQLite persistence

Services that don't need isolation will use `@Observable` classes:
- `TradingService` - Coordinates trading operations
- `WatchlistService` - Manages watchlists
- `AuthenticationService` - Handles authentication

## Consequences

### Positive

- **Compile-time safety**: Data races prevented by the compiler
- **No explicit locking**: Actors handle synchronization automatically
- **Async/await integration**: Natural fit with modern Swift concurrency
- **Easier reasoning**: Clear isolation boundaries
- **Performance**: Efficient execution without lock contention

### Negative

- **Learning curve**: Team needs to understand actor semantics
- **Async overhead**: All actor access requires `await`
- **Cannot use synchronous APIs**: Must migrate to async/await
- **Debugging complexity**: Concurrent issues harder to debug

### Neutral

- **visionOS requirement**: Requires Swift 5.5+ (already required for visionOS)
- **Migration effort**: Existing code needs actor annotations

## Implementation Notes

### Actor Usage Example

```swift
actor MarketDataHub {
    private var quoteCache: [String: Quote] = [:]
    private var subscribers: [String: [AsyncStream<Quote>.Continuation]] = [:]

    func updateQuote(_ quote: Quote) {
        quoteCache[quote.symbol] = quote
        notifySubscribers(quote)
    }

    func getQuote(symbol: String) -> Quote? {
        return quoteCache[symbol]
    }
}

// Usage
let hub = MarketDataHub()
let quote = await hub.getQuote(symbol: "AAPL")
```

### Performance Considerations

- Actor reentrancy: Be aware of suspension points
- Minimize actor crossings: Batch operations when possible
- Use `@MainActor` for UI updates

### Testing Strategy

- Use `XCTestExpectation` for async actor tests
- Test concurrent access with multiple tasks
- Verify no data races with Thread Sanitizer

## Alternatives Considered

### 1. Traditional Locks (NSLock, os_unfair_lock)

**Pros:**
- Familiar to experienced developers
- Synchronous access (no async/await needed)
- Fine-grained control

**Cons:**
- No compile-time safety
- Easy to introduce deadlocks
- Manual lock management error-prone
- Doesn't leverage Swift's modern concurrency

**Decision:** Rejected - Too error-prone for critical financial data

### 2. Serial Dispatch Queues

**Pros:**
- Well-understood GCD pattern
- Good for background work
- Compatible with existing code

**Cons:**
- No compile-time checking
- Easy to deadlock
- Harder to reason about
- Not the "Swift way"

**Decision:** Rejected - Actors provide better safety guarantees

### 3. Combine Publishers

**Pros:**
- Reactive programming model
- Good for data streams
- Apple framework

**Cons:**
- Complex for state management
- Steep learning curve
- Doesn't solve thread safety directly
- Being deprecated in favor of async/await

**Decision:** Rejected - Async/await is the future

## Related ADRs

- [ADR-002: Observable Macro for State Management](002-observable-macro-state-management.md)
- [ADR-003: AsyncStream for Market Data Distribution](003-asyncstream-for-market-data.md)

## References

- [Swift Concurrency: Actors](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html#ID645)
- [SE-0306: Actors](https://github.com/apple/swift-evolution/blob/main/proposals/0306-actors.md)
- [WWDC 2021: Protect mutable state with Swift actors](https://developer.apple.com/videos/play/wwdc2021/10133/)
- [Thread Sanitizer Documentation](https://developer.apple.com/documentation/xcode/diagnosing-memory-thread-and-crash-issues-early)

## Review History

- **2025-11-20**: Proposed by development team
- **2025-11-20**: Accepted after architecture review
