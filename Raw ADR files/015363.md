# GraphQL Interface and Real-Time Subscriptions Architecture for Cart Service

* Status: proposed
* Deciders: platform-core + cart squad
* Date: 2025-12-05

## Context and Problem Statement

The cart-service requires a GraphQL interface to complement or replace its existing REST API. The most complex aspect is real-time subscriptions: clients need to receive cart updates as they happen (products added, discounts applied, totals recalculated). This raises several interconnected decisions:

1. **GraphQL Implementation**: How to add GraphQL to the reactive WebFlux cart-service
2. **Subscription Transport**: How to deliver real-time updates to subscribers (WebSocket, SSE)
3. **Event Distribution**: How events reach subscribers across horizontally-scaled cart-service instances
4. **Service Responsibility**: Whether cart-service owns subscriptions or delegates to a dedicated events service
5. **Persistence for Subscriptions**: What backing store enables subscription fan-out across instances

Currently, cart-service uses PostgreSQL (R2DBC) for durable cart storage (ADR 002) and publishes audit events to Redis Streams (ADR 003). There is no real-time push mechanism; clients must poll for updates. The platform already has Redis infrastructure and a pattern for Redis Streams pub/sub via the audit system.

## Decision Drivers

1. **Real-time UX**: Subscribers must receive cart changes within seconds, not through polling
2. **Horizontal Scalability**: Subscriptions must work across multiple cart-service instances without sticky sessions
3. **Operational Simplicity**: Minimize new infrastructure; prefer Redis (already deployed) over Kafka/RabbitMQ
4. **Reactive Consistency**: Solution must integrate with existing WebFlux/Reactor patterns without blocking
5. **Separation of Concerns**: Avoid coupling GraphQL subscription delivery with core cart domain logic
6. **Failure Isolation**: Subscription delivery failures must not impact cart mutations or REST API availability
7. **Existing Patterns**: Leverage platform-audit's Redis Streams pattern where applicable

## Considered Options

### GraphQL Implementation
1. Spring for GraphQL with WebFlux (chosen)
2. Netflix DGS Framework
3. GraphQL Java with custom WebFlux integration

### Subscription Transport
1. Server-Sent Events (SSE) (chosen)
2. WebSocket

### Subscription Event Store / Fan-Out Mechanism
1. Redis Pub/Sub for ephemeral fan-out (chosen)
2. Redis Streams (persistent, consumer-group based)
3. Kafka for durable event streaming
4. In-memory (per-instance only, no cross-instance support)

### Service Responsibility for Subscriptions
1. Cart-service owns subscriptions with Redis Pub/Sub fan-out (chosen)
2. Dedicated events-service mediates all subscriptions
3. API Gateway handles subscription multiplexing

## Decision Outcome

### Prerequisite: Upgrade to Spring Boot 4.0

**This ADR requires upgrading to Spring Boot 4.0 and Spring GraphQL 2.0** (released November 2025).

Spring GraphQL 2.0 added critical SSE support features:
- Native SSE transport for subscriptions (no extra configuration)
- **Keep-Alive for SSE subscriptions** - prevents load balancers/proxies from closing idle connections
- JSpecify nullability annotations for better IDE support
- GraphQL Java 25 baseline with improved request cancellation

Without this upgrade, SSE subscriptions would lack keep-alive support, making them unreliable in production environments with proxies or load balancers.

### GraphQL: Spring for GraphQL 2.0 with WebFlux

Chosen option: **Spring for GraphQL 2.0** integrated with the existing WebFlux stack.

Spring for GraphQL provides first-class reactive support via `Flux<T>` return types for subscriptions, integrates seamlessly with Spring Security OAuth2, and aligns with the existing Spring Boot ecosystem. Version 2.0 supports both SSE and WebSocket transports natively.

### Subscription Transport: Server-Sent Events (SSE)

Chosen option: **SSE** for subscription delivery to clients.

SSE is the recommended transport for cart subscriptions because:
- **Zero configuration**: Uses the standard `/graphql` endpoint with `text/event-stream` media type
- **HTTP/2 compatible**: Multiplexes over existing connections; WebSocket requires separate TCP
- **Firewall friendly**: Works through proxies and firewalls that may block WebSocket upgrades
- **Simpler client implementation**: Native browser `EventSource` API; no WebSocket library needed
- **Sufficient for cart updates**: Server-to-client only; cart subscriptions don't need bidirectional communication
- **Keep-Alive supported**: Spring GraphQL 2.0 added SSE keep-alive to prevent connection timeouts

WebSocket remains a valid alternative if:
- Bidirectional communication is needed in the future (e.g., typing indicators, collaborative editing)
- Clients have specific WebSocket requirements

### Subscription Fan-Out: Redis Pub/Sub

Chosen option: **Redis Pub/Sub** for ephemeral subscription fan-out across instances.

Redis Pub/Sub is the right tool for this use case because:
- **Ephemeral by design**: Subscriptions are transient; if a subscriber disconnects, missed messages don't need replay (client re-fetches current state)
- **Low latency**: Pub/Sub delivers messages in ~1ms vs. Streams' consumer-group overhead
- **Simple fan-out**: All cart-service instances subscribe to cart change channels; each routes to its connected WebSocket clients
- **Already deployed**: Redis is running for cache and audit streams; no new infrastructure

Redis Streams (used for audit) is inappropriate here because:
- Audit needs durability and exactly-once processing; subscriptions do not
- Consumer groups add complexity for fire-and-forget notification patterns
- Streams retain messages until acknowledged; subscriptions want immediate discard

### Service Responsibility: Cart-Service Owns Subscriptions

Chosen option: **Cart-service directly handles GraphQL subscriptions** with Redis Pub/Sub for cross-instance coordination.

Rationale:
- **Domain cohesion**: Cart mutations and cart subscriptions share the same domain model and authorization rules
- **Reduced latency**: No extra network hop to an events-service
- **Simpler deployment**: One service to scale, monitor, and debug
- **Proven pattern**: The mutation → publish → subscribe loop stays within one bounded context

A dedicated events-service would be warranted if:
- Multiple domains (carts, orders, inventory) needed unified subscription aggregation
- Complex event routing/filtering required a separate orchestration layer
- Cart-service couldn't handle the WebSocket connection load (unlikely at current scale)

### Positive Consequences

- **Low latency**: Cart changes reach subscribers in milliseconds via Redis Pub/Sub
- **Horizontal scaling**: Any cart-service instance can serve any subscription; Redis fans out events
- **Operational simplicity**: No new infrastructure; reuses existing Redis deployment
- **Consistent stack**: Spring for GraphQL integrates with existing WebFlux, Security, and observability
- **Domain cohesion**: Cart mutations and subscriptions share authentication, authorization, and domain logic
- **Zero transport configuration**: SSE works on the standard `/graphql` endpoint; no additional WebSocket config needed
- **HTTP/2 benefits**: SSE multiplexes over existing HTTP/2 connections; better resource utilization

### Negative Consequences

- **No message replay**: If a client disconnects and reconnects, it must re-fetch current cart state (acceptable for UX; cart state is small)
- **Redis single point of failure for subscriptions**: Redis outage breaks subscriptions (but not REST API or mutations)
- **SSE connection management**: Cart-service must handle long-lived SSE connections and keep-alive
- **Schema surface area**: GraphQL adds API surface to maintain alongside REST (or REST is deprecated over time)
- **Upgrade required**: Requires Spring Boot 4.0 / Spring GraphQL 2.0 for production-ready SSE support

## Pros and Cons of the Options

### GraphQL Implementation

#### 1. Spring for GraphQL (chosen)

**Good**
- Native reactive support with `Flux<T>` subscriptions
- Integrates with Spring Security, WebFlux, and existing auto-configuration
- Active maintenance and Spring Boot alignment
- Built-in WebSocket transport and subscription support

**Bad**
- Newer than DGS; smaller community and fewer advanced features
- Less flexible for complex federation scenarios

#### 2. Netflix DGS Framework

**Good**
- Battle-tested at Netflix scale
- Rich codegen, testing utilities, and federation support
- Large community and extensive documentation

**Bad**
- Heavier dependency footprint
- Some features assume servlet stack; WebFlux support is secondary
- Additional abstraction layer over GraphQL Java

#### 3. GraphQL Java with Custom Integration

**Good**
- Maximum flexibility; no framework opinions
- Minimal dependencies

**Bad**
- Significant boilerplate for WebFlux, SSE/WebSocket, and subscription wiring
- Must build security, context propagation, and error handling from scratch

### Subscription Transport

#### 1. Server-Sent Events (SSE) (chosen)

**Good**
- Zero configuration; uses standard `/graphql` endpoint with `text/event-stream` media type
- HTTP/2 compatible; multiplexes over existing connections
- Better firewall/proxy compatibility than WebSocket
- Simpler client implementation via native `EventSource` API
- Keep-Alive supported in Spring GraphQL 2.0
- Sufficient for server-to-client cart update notifications

**Bad**
- Unidirectional (server → client only); cannot support client-to-server messages
- Requires Spring GraphQL 2.0 for production-ready keep-alive support
- Less established than WebSocket for GraphQL subscriptions (historically)

#### 2. WebSocket

**Good**
- Bidirectional communication; supports future interactive features
- Well-established protocol for GraphQL subscriptions
- Built-in ping/pong keep-alive mechanism

**Bad**
- Requires explicit configuration (`spring.graphql.websocket.path`)
- Separate TCP connection; doesn't benefit from HTTP/2 multiplexing
- May be blocked by some firewalls and proxies
- More complex client implementation than SSE

### Subscription Event Store / Fan-Out

#### 1. Redis Pub/Sub (chosen)

**Good**
- Fire-and-forget semantics match subscription ephemeral needs
- Sub-millisecond fan-out latency
- Simple channel-per-cart pattern: `cart:{cartId}:events`
- No message retention overhead

**Bad**
- No durability; missed messages are lost (acceptable for subscriptions)
- No built-in replay or consumer tracking

#### 2. Redis Streams

**Good**
- Durable message retention with consumer groups
- Supports replay from last-read position
- Already used for audit events

**Bad**
- Overhead of acknowledgments and consumer groups for ephemeral notifications
- Higher latency than Pub/Sub for fire-and-forget patterns
- Streams retain messages until acknowledged; requires TTL/trimming for subscriptions

#### 3. Kafka

**Good**
- Enterprise-grade durability, ordering, and replay
- Scales to massive throughput
- Rich ecosystem for stream processing

**Bad**
- Significant operational overhead; new infrastructure to deploy and manage
- Overkill for ephemeral subscription notifications
- Higher latency than Redis for this use case

#### 4. In-Memory (Per-Instance)

**Good**
- Simplest implementation; no external dependencies
- Fastest for single-instance deployments

**Bad**
- No cross-instance fan-out; requires sticky sessions or breaks with horizontal scaling
- Not viable for production multi-pod deployments

### Service Responsibility

#### 1. Cart-Service Owns Subscriptions (chosen)

**Good**
- Domain cohesion: mutations and subscriptions share domain logic
- Single deployment unit; simpler operations
- Lower latency; no inter-service hop

**Bad**
- Cart-service must manage WebSocket connections and lifecycle
- Coupling between API concerns and real-time delivery

#### 2. Dedicated Events-Service

**Good**
- Clean separation: cart-service focuses on domain, events-service on delivery
- Single place for cross-domain subscription aggregation
- Potentially easier to scale WebSocket connections independently

**Bad**
- Additional service to deploy, monitor, and maintain
- Extra network hop adds latency
- Must synchronize authorization rules between services
- Over-engineering for single-domain subscriptions

#### 3. API Gateway Handles Subscriptions

**Good**
- Centralized WebSocket termination and connection management
- Cart-service remains stateless REST-only

**Bad**
- Gateway becomes complex; must understand GraphQL subscription semantics
- Tight coupling between gateway and domain events
- Most API gateways have limited GraphQL subscription support

## Implementation Notes and Next Steps

### Phase 0: Spring Boot 4.0 Upgrade (Prerequisite)
1. Upgrade `spring-boot-starter-parent` from 3.x to 4.0.x in `build.gradle.kts`
2. Update Spring GraphQL to 2.0.x (comes with Spring Boot 4.0)
3. Review and address any breaking changes from Spring Framework 7.0 / Spring Security 7.0
4. Verify existing tests pass after upgrade
5. Update platform-bom to align all dependency versions

### Phase 1: GraphQL Foundation
1. Add `spring-boot-starter-graphql` dependency to cart-service (no WebSocket starter needed for SSE)
2. Define GraphQL schema (`schema.graphqls`) mirroring existing REST resources: `Cart`, `CartProduct`, `Discount`, `Fulfillment`, `CartTotals`
3. Implement `@QueryMapping` and `@MutationMapping` controllers wrapping existing `CartService` methods
4. Configure Spring Security OAuth2 for GraphQL endpoint authentication

### Phase 2: Subscription Infrastructure
1. Add `ReactiveRedisTemplate` for Pub/Sub (already available via platform-cache)
2. Create `CartEventPublisher` that publishes to Redis Pub/Sub channel `cart:{cartId}:events` on mutations
3. Create `CartSubscriptionResolver` with `@SubscriptionMapping` returning `Flux<CartEvent>` from Redis Pub/Sub
4. SSE transport works automatically on `/graphql` endpoint with `Accept: text/event-stream` header

### Phase 3: Integration and Observability
1. Add subscription metrics: active SSE connections, message throughput, latency histograms
2. Configure SSE keep-alive interval to prevent proxy/load balancer timeouts
3. Add tracing correlation between mutations and subscription deliveries
4. Document SSE subscription protocol and client integration patterns

### Schema Design Considerations
```graphql
type Subscription {
  cartUpdated(cartId: ID!): CartEvent!
}

type CartEvent {
  eventType: CartEventType!
  cart: Cart!
  timestamp: DateTime!
}

enum CartEventType {
  PRODUCT_ADDED
  PRODUCT_REMOVED
  PRODUCT_UPDATED
  DISCOUNT_APPLIED
  DISCOUNT_REMOVED
  FULFILLMENT_ADDED
  FULFILLMENT_UPDATED
  FULFILLMENT_REMOVED
  CUSTOMER_SET
  TOTALS_RECALCULATED
}
```

### Redis Pub/Sub Channel Pattern
- Channel: `cart:{cartId}:events`
- Message: JSON-serialized `CartEvent` with eventType, cartId, and full cart state
- Fan-out: All cart-service instances subscribe to channels for their connected clients

### SSE Connection Management
- Max connections per instance: Configure via Netty settings (`reactor.netty.http.server.maxKeepAliveRequests`)
- Keep-alive: Spring GraphQL 2.0 sends periodic SSE comments to maintain connection liveness
- Idle timeout: Configure via `spring.graphql.sse.timeout` or equivalent property
- Client reconnection: Browsers' `EventSource` API automatically reconnects on connection loss

### Client Integration Example
```javascript
// Browser client using EventSource
const eventSource = new EventSource('/graphql?query=subscription{cartUpdated(cartId:"123"){eventType,cart{id,totals{grandTotal}}}}', {
  headers: { 'Authorization': 'Bearer <token>' }
});

eventSource.onmessage = (event) => {
  const cartEvent = JSON.parse(event.data);
  console.log('Cart updated:', cartEvent);
};

eventSource.onerror = (error) => {
  console.error('SSE error:', error);
  // EventSource automatically attempts reconnection
};
```

## Other Architectural Considerations Addressed

### Why SSE Over WebSocket?
- **Simpler**: Zero configuration; uses existing `/graphql` endpoint
- **HTTP/2 friendly**: Multiplexes over existing connections; better resource utilization
- **Firewall compatible**: Standard HTTP; no upgrade handshake that proxies might block
- **Sufficient**: Cart subscriptions are server-to-client only; bidirectionality not needed
- **Native browser support**: `EventSource` API with automatic reconnection

WebSocket would be preferred if bidirectional communication becomes necessary (e.g., collaborative cart editing, typing indicators).

### Why Not Persist Subscription State?
- Subscriptions are transient; state is the SSE connection itself
- On reconnect, client re-subscribes and fetches current cart state
- No need for subscription recovery or replay

### REST API Deprecation Path
- GraphQL can coexist with REST initially
- Recommend GraphQL for new clients; REST remains for backward compatibility
- Consider REST deprecation once GraphQL adoption reaches critical mass

### Federation Considerations (Future)
- If product-service or other domains add GraphQL, consider Apollo Federation or schema stitching
- Current single-domain scope doesn't require federation yet

## References

### Codebase
- `apps/cart-service/src/main/java/org/example/cart/service/CartService.java` - Cart mutation logic (publish points)
- `apps/cart-service/src/main/java/org/example/cart/controller/CartController.java:49-149` - Existing REST endpoints to mirror
- `libs/platform/platform-audit/src/main/java/org/example/platform/audit/RedisStreamAuditPublisher.java` - Redis Streams pattern (different use case)
- `libs/platform/platform-cache/src/main/java/org/example/platform/cache/RedisCacheService.java` - Existing ReactiveRedisTemplate usage
- `docs/ADRs/002_write_data_store.md` - Cart persistence decision (PostgreSQL)
- `docs/ADRs/003_audit_data_store.md` - Audit event streaming decision (Redis Streams + Cassandra)

### Spring Boot 4.0 / Spring GraphQL 2.0 (Required Upgrade)
- [Spring Boot 4.0.0 Release Announcement](https://spring.io/blog/2025/11/20/spring-boot-4-0-0-available-now/)
- [Spring Boot 4.0 Release Notes](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Release-Notes)
- [Spring for GraphQL 2.0.0 GA Announcement](https://spring.io/blog/2025/11/18/spring-for-graphql-2-0-0-goes-ga/)
- [Spring for GraphQL Documentation](https://docs.spring.io/spring-graphql/reference/)

### GraphQL Subscriptions
- [GraphQL over SSE Specification](https://github.com/graphql/graphql-over-http/blob/main/rfcs/GraphQLOverSSE.md)
- [WunderGraph: Why SSE over WebSockets](https://wundergraph.com/blog/deprecate_graphql_subscriptions_over_websockets)
