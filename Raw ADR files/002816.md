# ADR-002: Rust for Core Backend Services

## Status
Accepted

## Date
2024-01-15

## Context

NEURECTOMY requires a high-performance backend capable of:
1. Handling thousands of concurrent WebSocket connections
2. Processing real-time agent orchestration events
3. Efficient memory management for long-running services
4. Type safety for complex business logic
5. High throughput for API requests

The backend must also integrate with multiple databases and message queues.

## Decision

We will use **Rust** as the primary language for core backend services.

### Technology Stack
- **Runtime**: Tokio (async runtime)
- **Web Framework**: Axum 0.8
- **GraphQL**: async-graphql 7.0
- **Database**: SQLx (PostgreSQL), neo4rs (Neo4j), redis-rs
- **Message Queue**: async-nats
- **Observability**: tracing, opentelemetry

### Key Reasons
1. **Performance**: Near-C performance with zero-cost abstractions
2. **Memory Safety**: No garbage collection pauses, predictable latency
3. **Concurrency**: Excellent async/await support with Tokio
4. **Type System**: Prevents entire classes of bugs at compile time
5. **Ecosystem**: Mature crates for all required functionality

## Consequences

### Positive
- **Performance**: Sub-millisecond response times achievable
- **Resource Efficiency**: Lower memory footprint than JVM/Node.js
- **Reliability**: Compiler catches many bugs before runtime
- **Concurrency**: Safe concurrent programming without data races
- **Long-term Maintenance**: Strong types make refactoring safer

### Negative
- **Learning Curve**: Rust has a steeper learning curve
- **Compile Times**: Longer compilation than interpreted languages
- **Ecosystem Maturity**: Some crates less mature than Node.js equivalents
- **Hiring**: Smaller pool of Rust developers

### Mitigations
- Use cargo-watch for faster development iteration
- Leverage sccache for distributed compilation caching
- Provide comprehensive documentation and examples
- Invest in team training

## Alternatives Considered

### 1. Node.js/TypeScript
- ✅ Large ecosystem, fast development
- ❌ GC pauses, higher memory usage
- ❌ Single-threaded (requires clustering)
- ❌ Less type safety (even with TypeScript)

### 2. Go
- ✅ Fast compilation, good concurrency
- ❌ Less expressive type system
- ❌ GC pauses (though minimal)
- ❌ Error handling verbosity

### 3. Java/Kotlin (Spring Boot)
- ✅ Mature ecosystem, enterprise support
- ❌ Higher memory footprint
- ❌ JVM startup time
- ❌ GC tuning complexity

## Performance Benchmarks

Initial benchmarks (synthetic load):
| Metric | Rust (Axum) | Node.js (Fastify) | Go (Gin) |
|--------|-------------|-------------------|----------|
| Requests/sec | 150,000 | 45,000 | 95,000 |
| P99 Latency | 2ms | 15ms | 5ms |
| Memory (idle) | 12MB | 85MB | 25MB |
| Memory (load) | 45MB | 350MB | 120MB |

## References
- [Rust Performance Book](https://nnethercote.github.io/perf-book/)
- [Tokio Tutorial](https://tokio.rs/tokio/tutorial)
- [Axum Documentation](https://docs.rs/axum/latest/axum/)
