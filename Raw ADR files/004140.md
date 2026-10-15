# ADR-0006: Agent-Based Service Patterns

**Status**: Accepted  
**Date**: 2025-11-26  
**Deciders**: Tony Moores  
**Technical Story**: Phase 0 - Foundation

## Context

TJMPaaS services must handle concurrent operations, maintain state safely, and communicate asynchronously. The choice of concurrency model significantly impacts system design, reliability, and maintainability.

### Problem Statement

Determine the concurrency and state management patterns for TJMPaaS services that:
- Handle concurrent requests safely
- Manage state without locks
- Support message-driven communication
- Enable reactive principles (ADR-0005)
- Integrate naturally with functional programming (ADR-0004)
- Scale horizontally across multiple instances

### Goals

- Safe concurrent state management
- Message-driven communication patterns
- Fault tolerance and supervision
- Location transparency (local or remote actors)
- Integration with Scala 3 and FP
- Support for digital commerce workloads
- Maintainable by solo developer initially

### Constraints

- Must work with Scala 3
- Must support functional programming paradigms
- Must align with Reactive Manifesto principles
- Must containerize well
- Must scale horizontally in Kubernetes
- Complexity must be manageable

## Decision

**Adopt agent-based patterns using the Actor Model** for concurrency and state management in TJMPaaS services.

Specifically:
1. Use Akka Typed, Pekko, or ZIO actors as primary implementation
2. Apply agent patterns for stateful services
3. Use actor supervision for fault tolerance
4. Leverage message-passing for all actor communication
5. Design agents as functional, immutable state machines
6. Use only open-source licensed frameworks (see PDR-0005)

## Rationale

### What is the Actor Model?

The Actor Model is a mathematical model of concurrent computation where "actors" are the fundamental units:

**Core Principles**:
- **Actors** are independent computational entities
- **Messages** are the only way actors communicate (no shared state)
- **Mailboxes** queue messages for processing
- **Behaviors** define how actors respond to messages
- **Location Transparency** - actors can be local or remote

**Actor Capabilities**:
When processing a message, an actor can:
1. Send messages to other actors
2. Create new actors
3. Designate the behavior for the next message

### Why Agent Patterns?

"Agent" in this context refers to actor-based entities with specific characteristics:

**Agent Characteristics**:
- **Autonomous**: Makes decisions based on its state and messages
- **Stateful**: Encapsulates mutable state safely
- **Message-Driven**: Communicates only via messages
- **Supervised**: Part of supervision hierarchy for fault tolerance
- **Single-Threaded Semantics**: Processes one message at a time (no locks!)

**Benefits for TJMPaaS**:
1. **Concurrency Safety**: No shared mutable state, no locks, no race conditions
2. **Fault Tolerance**: Supervision strategies handle failures
3. **Scalability**: Agents scale to millions per node
4. **Reactive**: Natural implementation of message-driven principle
5. **Commerce Fit**: Perfect for shopping carts, order processing, inventory

### Actor Model + Functional Programming

Excellent synergy:

**Immutable Messages**:
- Messages are immutable case classes
- Pattern matching for message handling
- Type-safe message protocols

**Functional State Machines**:
- State transitions as pure functions: `(State, Message) => (State, Effects)`
- Actor behavior as immutable data
- Effects separate from state computation

**Composition**:
- Actors compose via message protocols
- Supervision trees structure systems
- Higher-order patterns (routers, pools)

**Example Pattern**:
```scala
// Functional actor state machine
def apply(state: State): Behavior[Message] = 
  Behaviors.receiveMessage {
    case Update(data) =>
      val newState = updateState(state, data)  // pure function
      apply(newState)  // recursive behavior with new state
    
    case Query(replyTo) =>
      replyTo ! Response(state)  // no mutation
      Behaviors.same  // keep current behavior
  }
```

### Why Not Just FP Concurrency Primitives?

Alternatives like `Ref`, `Queue`, `Semaphore` from effect systems are powerful but:

**When to use agents**:
- Complex stateful entities (shopping cart, order, session)
- Need supervision and fault tolerance
- Location transparency desired
- Natural entity model (aggregate roots in DDD)

**When to use FP primitives**:
- Simple coordination (locks, queues, flags)
- Functional streams and pipelines
- Concurrent algorithms
- No supervision needed

**Use both**: FP primitives within actors, actors for higher-level structure

## Alternatives Considered

### Alternative 1: Thread-Based Concurrency with Locks

**Description**: Traditional threads, synchronized blocks, locks

**Pros**:
- Familiar model
- Direct control
- Straightforward debugging

**Cons**:
- Race conditions common
- Deadlocks possible
- Doesn't scale (thread-per-entity is expensive)
- Hard to make correct
- No fault tolerance
- Blocking operations

**Reason for rejection**: Too error-prone; doesn't support reactive principles; doesn't scale

### Alternative 2: Software Transactional Memory (STM)

**Description**: Composable memory transactions (available in Scala via ZIO STM)

**Pros**:
- Composable
- No explicit locks
- Automatic retry
- Good for complex transactional logic

**Cons**:
- Performance overhead
- Retry storms under high contention
- Doesn't provide supervision
- No location transparency
- Conflicts can be expensive

**Reason for rejection**: Excellent for some use cases but doesn't provide the supervision, location transparency, and organizational structure of actors

### Alternative 3: Pure Effect System Concurrency (Fibers, Refs, Queues)

**Description**: Use ZIO/Cats Effect primitives exclusively

**Pros**:
- Functional purity
- Excellent performance
- Fine-grained control
- Good for reactive streams

**Cons**:
- No built-in supervision strategies
- No location transparency
- Manual error handling
- Less structure for large systems
- No natural entity model

**Reason for rejection**: Excellent primitives but lack the organizational patterns actors provide; better used *with* actors than instead of

### Alternative 4: Erlang-Style Processes

**Description**: Lightweight processes (not actors) with supervision

**Pros**:
- Proven in telecom
- Excellent fault tolerance
- Natural supervision

**Cons**:
- Requires Erlang/Elixir ecosystem
- Not JVM-native
- Loses Scala ecosystem benefits
- Different deployment model

**Reason for rejection**: Excellent model but wrong ecosystem; actor model provides similar benefits on JVM

### Alternative 5: No Formal Concurrency Model

**Description**: Ad-hoc concurrency patterns, different per service

**Pros**:
- Maximum flexibility
- Use best tool per job

**Cons**:
- Inconsistent codebase
- Hard to maintain
- Knowledge doesn't transfer
- Easy to get wrong
- No standards

**Reason for rejection**: Need consistent patterns across services for maintainability

## Consequences

### Positive

- **Safety**: No locks, no race conditions, no deadlocks
- **Scalability**: Millions of actors per node possible
- **Fault Tolerance**: Supervision trees handle failures
- **Reactive**: Natural message-driven implementation
- **Mental Model**: Actors map to domain entities (Cart, Order, Session)
- **Location Transparency**: Actors can move to different nodes
- **Testability**: Message protocols are testable
- **Maintainability**: Clear patterns, proven approach
- **Commerce Fit**: Perfect for stateful commerce entities

### Negative

- **Learning Curve**: Actor model requires different thinking
- **Debugging**: Async message flows harder to trace
- **Overhead**: Some memory overhead per actor
- **Complexity**: Supervision strategies require understanding
- **Tooling**: Debugging actors differs from sequential code

### Neutral

- **Library Choice**: Multiple options (Akka Typed, ZIO Actors)
- **Maturity**: Akka very mature; ZIO Actors newer but growing
- **Community**: Strong communities for both

## Implementation

### Technology Choices

**Actor System Options** (choose based on service needs, per PDR-0005):

**Primary: Pekko**
- Apache 2.0 licensed (free for all use)
- Community-driven fork of Akka
- Open governance model
- Compatible with Akka APIs
- Active development
- Recommended for new services

**Alternative: Akka Typed 2.6.x**
- Last Apache 2.0 version of Akka (pre-BSL)
- Most mature JVM actor implementation
- Excellent documentation
- Battle-tested in production
- Strong ecosystem (Akka HTTP, Akka Streams, Akka Cluster)
- **Note**: Akka 2.7+ uses Business Source License (BSL) requiring paid license above revenue threshold
- Use 2.6.x for zero cost, or Pekko for ongoing updates

**Alternative: ZIO Actors**
- Apache 2.0 licensed
- Tighter ZIO integration
- More functional style
- Growing ecosystem
- Good for ZIO-first architectures
- Lighter weight than Akka/Pekko

**Decision**: 
- **Prefer Pekko** for new services (open-source, actively maintained)
- **Akka Typed 2.6.x** acceptable if already familiar or specific ecosystem needs
- **ZIO Actors** for ZIO-centric services
- See [PDR-0005: Framework Selection Policy](../PDRs/PDR-0005-framework-selection-policy.md) for framework selection guidelines

### Actor Model Architecture

The following diagrams illustrate actor model patterns in TJMPaaS:

#### Actor Hierarchy and Message Flow

```mermaid
graph TB
    subgraph "Supervisor Layer"
        Root[Root Guardian<br/>System-Level Supervisor]
        CartSup[CartService Supervisor<br/>Manages Cart Actors]
        SessionSup[Session Supervisor<br/>Manages Session Actors]
    end
    
    subgraph "Entity Actors"
        Cart1[Cart Actor<br/>cart-123]
        Cart2[Cart Actor<br/>cart-456]
        Cart3[Cart Actor<br/>cart-789]
        Session1[Session Actor<br/>session-abc]
        Session2[Session Actor<br/>session-def]
    end
    
    subgraph "Message Flow"
        Client[Client/API] -->|AddItem| Cart1
        Cart1 -->|ItemAdded Event| EventStore[(Event Store)]
        Cart1 -->|Publish| Kafka[Kafka]
        Cart1 -->|Response| Client
    end
    
    Root --> CartSup
    Root --> SessionSup
    CartSup -->|Creates/Supervises| Cart1
    CartSup -->|Creates/Supervises| Cart2
    CartSup -->|Creates/Supervises| Cart3
    SessionSup -->|Creates/Supervises| Session1
    SessionSup -->|Creates/Supervises| Session2
    
    Cart1 -.->|Failure| CartSup
    CartSup -.->|Restart Strategy| Cart1
    
    style Root fill:#f99,stroke:#333,stroke-width:3px
    style CartSup fill:#fb9,stroke:#333,stroke-width:2px
    style SessionSup fill:#fb9,stroke:#333,stroke-width:2px
    style Cart1 fill:#bfb,stroke:#333,stroke-width:2px
    style Cart2 fill:#bfb,stroke:#333,stroke-width:2px
    style Cart3 fill:#bfb,stroke:#333,stroke-width:2px
```

#### Supervision Strategies

```mermaid
graph TB
    subgraph "OneForOne Strategy"
        S1[Supervisor] --> C1[Child 1]
        S1 --> C2[Child 2]
        S1 --> C3[Child 3]
        C2 -.->|Fails| S1
        S1 -.->|Restart Only Child 2| C2
        Note1[Use: Independent entities<br/>Example: Cart actors]
    end
    
    subgraph "AllForOne Strategy"
        S2[Supervisor] --> G1[Child A]
        S2 --> G2[Child B]
        S2 --> G3[Child C]
        G2 -.->|Fails| S2
        S2 -.->|Restart All Children| G1
        S2 -.->|Restart All Children| G2
        S2 -.->|Restart All Children| G3
        Note2[Use: Tightly coupled<br/>Example: Service components]
    end
    
    subgraph "Escalate Strategy"
        S3[Supervisor] --> E1[Child X]
        E1 -.->|Critical Failure| S3
        S3 -.->|Escalate to Parent| Root[Parent Supervisor]
        Root -.->|Decide Strategy| S3
        Note3[Use: Parent decides<br/>Example: Unrecoverable errors]
    end
    
    style S1 fill:#fb9,stroke:#333,stroke-width:2px
    style S2 fill:#fb9,stroke:#333,stroke-width:2px
    style S3 fill:#fb9,stroke:#333,stroke-width:2px
    style C2 fill:#f99,stroke:#333,stroke-width:2px
    style G2 fill:#f99,stroke:#333,stroke-width:2px
    style E1 fill:#f99,stroke:#333,stroke-width:2px
```

#### Actor Message Protocol

```mermaid
sequenceDiagram
    participant Client
    participant Supervisor
    participant CartActor
    participant EventStore
    
    Note over Client,EventStore: Normal Message Flow
    
    Client->>CartActor: AddItem(item, replyTo)
    Note over CartActor: Process in mailbox<br/>One message at a time
    CartActor->>CartActor: Validate business rules
    CartActor->>EventStore: Persist(ItemAdded)
    EventStore-->>CartActor: Success
    CartActor->>CartActor: Apply event to state
    CartActor-->>Client: ItemAdded(itemId)
    
    Note over Client,EventStore: Failure and Recovery
    
    Client->>CartActor: RemoveItem(badId, replyTo)
    CartActor->>CartActor: Validation fails
    CartActor->>CartActor: Exception thrown
    CartActor->>Supervisor: Failure signal
    
    Note over Supervisor: Apply supervision strategy<br/>Decision: Restart
    
    Supervisor->>CartActor: Restart actor
    CartActor->>EventStore: Replay events
    EventStore-->>CartActor: Event history
    CartActor->>CartActor: Rebuild state
    
    Note over CartActor: Actor recovered<br/>Ready for new messages
    
    Client->>CartActor: GetCart(replyTo)
    CartActor-->>Client: Cart(items)
```

#### Actor Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Creating: Supervisor creates actor
    Creating --> Started: Actor initialized
    
    Started --> Idle: No messages
    Idle --> Processing: Message received
    Processing --> Idle: Message processed
    
    Processing --> Failed: Exception thrown
    Failed --> Restarting: Supervisor: Restart
    Failed --> Stopped: Supervisor: Stop
    Failed --> Escalated: Supervisor: Escalate
    
    Restarting --> Recovering: Replay events
    Recovering --> Started: State restored
    
    Stopped --> [*]
    
    Idle --> Passivated: Idle timeout
    Passivated --> Started: New message arrives
    
    Processing --> Terminated: Poison Pill
    Terminated --> [*]
    
    note right of Failed
        Supervision Strategy:
        - Restart (recoverable)
        - Stop (unrecoverable)
        - Escalate (parent decides)
    end note
```

#### Mailbox and Backpressure

```mermaid
graph LR
    subgraph "Message Producers"
        C1[Client 1] -->|AddItem| Q
        C2[Client 2] -->|RemoveItem| Q
        C3[Client 3] -->|GetCart| Q
    end
    
    subgraph "Actor Mailbox"
        Q[Message Queue<br/>Bounded Size: 1000]
        Q -->|FIFO| Process
    end
    
    subgraph "Actor Processing"
        Process[Cart Actor<br/>Processes 1 at a time]
        Process -->|Update State| State[(In-Memory<br/>State)]
        Process -->|Persist Events| ES[(Event Store)]
    end
    
    Q -.->|Mailbox Full| BP[Backpressure Signal]
    BP -.->|Slow Down| C1
    BP -.->|Slow Down| C2
    BP -.->|Slow Down| C3
    
    style Q fill:#ffb,stroke:#333,stroke-width:2px
    style Process fill:#bfb,stroke:#333,stroke-width:2px
    style BP fill:#f99,stroke:#333,stroke-width:2px
```

### Actor Design Patterns for TJMPaaS

**Entity Actors**:
```scala
// Shopping cart as actor
object ShoppingCart {
  sealed trait Command
  case class AddItem(item: Item, replyTo: ActorRef[Response]) extends Command
  case class RemoveItem(itemId: Id, replyTo: ActorRef[Response]) extends Command
  case class Checkout(replyTo: ActorRef[Response]) extends Command
  
  def apply(cartId: CartId): Behavior[Command] = ...
}
```

**Service Actors**:
- Handle requests
- Coordinate with entity actors
- Manage external integrations

**Supervisor Actors**:
- Manage lifecycle of child actors
- Handle failures
- Implement restart strategies

### Supervision Strategies

**OneForOne**: Failed child restarted individually
- Use for independent entities (shopping carts, user sessions)

**AllForOne**: All children restarted together
- Use for tightly coupled components

**Restart**: Actor restarts with fresh state
- Use for recoverable failures

**Stop**: Actor stops permanently
- Use for unrecoverable failures

**Escalate**: Failure passed to parent
- Use when parent should decide

### Message Design Principles

**Immutable**:
```scala
final case class AddItem(item: Item, replyTo: ActorRef[Response])
```

**Type-Safe**:
```scala
sealed trait CartCommand
sealed trait CartResponse
```

**Request-Response**:
```scala
case class Query(replyTo: ActorRef[Response])
```

**Fire-and-Forget** (use sparingly):
```scala
case class NotifyEvent(event: Event)
```

### Integration with Effect Systems

Actors work well with ZIO/Cats Effect:

```scala
// Call actor from effect
for {
  actor <- getActor
  response <- ZIO.fromFuture(_ => actor ? Query)
  _ <- ZIO.log(s"Got response: $response")
} yield response
```

### Testing Actors

**ActorTestKit** (Akka):
```scala
val testKit = ActorTestKit()
val probe = testKit.createTestProbe[Response]()
val actor = testKit.spawn(ShoppingCart(cartId))
actor ! AddItem(item, probe.ref)
probe.expectMessage(ItemAdded(item))
```

**Benefits**:
- Synchronous testing of async actors
- Test probes for responses
- Time control for testing timeouts

### Deployment Considerations

**Containerization**:
- Actors run fine in containers
- Consider Akka Cluster for multi-pod coordination
- Use Kubernetes for orchestration

**Scaling**:
- Horizontal: Add more pods
- Vertical: More actors per pod
- Cluster sharding for distributed state

**Monitoring**:
- Actor mailbox sizes
- Message processing times
- Actor lifecycle events
- Supervision events

### Guidelines

**When to Use Actors**:
- Stateful entities (cart, order, session, user)
- Long-lived state
- Need supervision
- Need location transparency
- Natural entity boundaries

**When Not to Use Actors**:
- Stateless request handling (use effect systems)
- Simple concurrent data structures (use Ref, etc.)
- CPU-bound algorithms (use parallel collections)
- Very high-frequency updates (consider different state management)

**Actor Granularity**:
- One actor per cart, order, session (fine-grained)
- Not one actor for all carts (too coarse)
- Consider sharding for distribution

## Validation

Success criteria:

- Actor-based services handle concurrent loads safely
- No race conditions in production
- Supervision recovers from failures automatically
- Performance meets requirements (< 10ms message processing p95)
- Developer productivity remains high
- Code maintainability improves with clear patterns

Metrics:
- Messages per second per actor
- Mailbox sizes (< 100 typical, < 1000 max)
- Actor lifecycle events (restarts, stops)
- Message processing latency (< 10ms p95)
- Actor count and distribution

## Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Learning curve | Medium | Good documentation; start simple; training materials; pair programming when team grows |
| Debugging complexity | Medium | Logging; distributed tracing; Akka observability tools; test thoroughly |
| Overhead | Low | Profile; optimize hot paths; actors are quite lightweight |
| Library lock-in (Akka) | Low | Actor model is portable; could migrate to ZIO Actors if needed |
| Over-use of actors | Medium | Clear guidelines on when/when not to use; code reviews |
| Message protocol evolution | Medium | Versioned messages; backward compatibility strategies |

## Related Decisions

- [ADR-0005: Reactive Manifesto Alignment](./ADR-0005-reactive-manifesto-alignment.md) - Actors implement message-driven principle
- [ADR-0004: Scala 3 Technology Stack](./ADR-0004-scala3-technology-stack.md) - Scala 3 provides excellent actor support
- [ADR-0003: Containerization Strategy](./ADR-0003-containerization-strategy.md) - Actors containerize well
- [ADR-0007: CQRS and Event-Driven Architecture](./ADR-0007-cqrs-event-driven-architecture.md) - Actors as event-sourced aggregates
- [PDR-0005: Framework Selection Policy](../PDRs/PDR-0005-framework-selection-policy.md) - Guidelines for choosing actor frameworks
- [SECURITY-JWT-PERMISSIONS.md](../../technical/standards/SECURITY-JWT-PERMISSIONS.md) - JWT validation in actor-based services
- Future ADR: Event sourcing with actors
- Future ADR: CQRS patterns with actors
- Future ADR: Akka/Pekko Cluster vs single-node actors

## Related Best Practices

This decision is validated by comprehensive industry research:

- **[Actor Patterns and Frameworks Best Practices](../../technical/best-practices/architecture/actor-patterns.md)**: LinkedIn runs 15,000+ Akka actors handling 100M+ requests/day with 99.99% uptime; PayPal achieves 99.999% uptime with actor-based architecture processing billions of transactions annually; ING Bank rebuilt core banking on actors achieving 10x throughput improvement. Research shows actors deliver 50M+ messages/second throughput, near-linear scaling, and concurrency safety without locks.

**Framework Comparison**: Industry evidence strongly supports **Pekko (Apache 2.0)** as recommended choice for new TJMPaaS services over Akka 2.7+ (Business Source License). Pekko maintains full Akka compatibility while preserving open-source licensing. Akka Typed 2.6.x (last Apache 2.0 version) remains acceptable for teams already invested. ZIO Actors provides lightweight alternative for ZIO-first architectures.

**Key Validation**: Actor model enables 99.999% uptime and 50M+ msg/sec throughput in production at companies processing billions of transactions. Pekko recommended for licensing freedom while maintaining production-proven capabilities.

## Related Features

**Features That Validate This Decision**:

**Entity Management Service** demonstrates actor model patterns:

1. **Tenant Provisioning** (EMS-F001):
   - TenantActor manages tenant lifecycle
   - Commands: CreateTenant, UpdateSubscription
   - Events: TenantProvisioned, SubscriptionChanged
   - Supervision: Restart on transient failures

2. **Organization Hierarchy** (EMS-F002):
   - OrganizationActor per organization
   - Hierarchy validation (acyclic graph enforcement)
   - Commands: CreateOrganization, MoveOrganization, DeleteOrganization
   - Events: OrganizationCreated, OrganizationMoved, OrganizationDeleted

3. **User Management** (EMS-F003):
   - UserActor per user
   - Commands: CreateUser, UpdateUserRole, DeactivateUser
   - Events: UserCreated, UserRoleChanged, UserDeactivated
   - Role-based state transitions

4. **Role-Based Permissions** (EMS-F004):
   - RoleActor per custom role
   - Permission cache (5-minute TTL) for < 1ms checks
   - Commands: CreateRole, UpdatePermissions
   - Events: RoleCreated, RolePermissionsUpdated

5. **Audit Trail** (EMS-F005):
   - KafkaAuditLogger (async actor)
   - AuditEventConsumer (processes audit events)
   - Immutable append-only logging
   - 7-year retention with tiered storage

**Architecture Reference**: See [Entity Management Service Architecture](../../services/entity-management/SERVICE-ARCHITECTURE.md) for complete actor design including supervision strategies, message protocols, and state machines.

**Multi-Tenant Integration**: All actors include tenant_id scoping, cross-tenant isolation enforced at actor boundaries per [MULTI-TENANT-SEAM-ARCHITECTURE.md](../../standards/MULTI-TENANT-SEAM-ARCHITECTURE.md).

## References

- [Akka Documentation](https://doc.akka.io/)
- [Akka Typed Guide](https://doc.akka.io/docs/akka/current/typed/guide/index.html)
- [Pekko Documentation](https://pekko.apache.org/docs/pekko/current/)
- [Pekko Typed Guide](https://pekko.apache.org/docs/pekko/current/typed/guide/index.html)
- [ZIO Actors](https://zio.dev/ecosystem/officials/zio-actors)
- [Reactive Messaging Patterns with the Actor Model](https://www.lightbend.com/ebooks/reactive-messaging-patterns-with-the-actor-model)
- [Actor Model - Wikipedia](https://en.wikipedia.org/wiki/Actor_model)
- Carl Hewitt's original Actor Model papers
- Erlang/OTP Design Principles (inspiration)
- [Akka License FAQ](https://www.lightbend.com/akka/license-faq) - BSL licensing for Akka 2.7+
- [Pekko License](https://pekko.apache.org/docs/pekko/current/project/licenses.html) - Apache 2.0

## Notes

**Why "Agent" vs "Actor"?**

Using "agent patterns" emphasizes:
- **Autonomy**: Agents make decisions based on their state
- **Purpose**: Agents have clear responsibilities
- **Business Alignment**: "Shopping cart agent" vs "shopping cart actor"

Both terms refer to the Actor Model; "agent" emphasizes the business entity aspect.

**Digital Commerce Use Cases**:

Excellent agent/actor applications:
1. **Shopping Cart**: Each cart is an actor managing its state
2. **User Session**: Session state managed by session actor
3. **Order Processing**: Order workflow managed by order actor
4. **Inventory Item**: Each SKU managed by inventory actor
5. **Payment Transaction**: Transaction state managed by payment actor
6. **Price Calculator**: Pricing rules and calculations
7. **Promotion Engine**: Active promotions as actors
8. **Customer Profile**: Customer state and preferences

**Functional Actors in Scala 3**:

Modern Akka Typed with Scala 3 is very functional:
- Immutable behaviors
- Pure state transitions
- Type-safe message protocols
- Functional effect integration
- No mutable variables needed

Example:
```scala
def cartBehavior(items: Map[ItemId, Item]): Behavior[Command] =
  Behaviors.receiveMessage {
    case AddItem(item, replyTo) =>
      val newItems = items + (item.id -> item)  // immutable update
      replyTo ! ItemAdded(item)
      cartBehavior(newItems)  // new behavior with new state
      
    case GetItems(replyTo) =>
      replyTo ! Items(items.values.toSeq)
      Behaviors.same  // no state change
  }
```

**Actors + Event Sourcing**:

Actors work beautifully with event sourcing:
- Events persist state changes
- State recovered by replaying events
- Commands become events
- Natural fit for CQRS

Future ADR will detail this pattern (see ADR-0007).

**Pekko vs Akka vs ZIO Actors**:

**When to choose Pekko**:
- New services (default recommendation)
- Want Apache 2.0 license
- Community-driven development preferred
- Akka compatibility desired

**When to choose Akka Typed 2.6.x**:
- Already familiar with Akka
- Need specific Akka ecosystem libraries
- Comfortable staying on 2.6.x (no BSL)
- Legacy compatibility

**When to choose ZIO Actors**:
- ZIO-first architecture
- Want lightweight actor system
- Tight ZIO integration critical
- Simpler use cases

All three are valid choices per [PDR-0005: Framework Selection Policy](../PDRs/PDR-0005-framework-selection-policy.md).

**Licensing Note**:

Akka licensing changed in 2022:
- **Akka 2.6.x and earlier**: Apache 2.0 (free for all use)
- **Akka 2.7+**: Business Source License (BSL)
  - Free for evaluation and development
  - Free for production below $25M annual revenue
  - Paid license required above threshold
- **Pekko**: Apache 2.0 fork of Akka, fully open-source
- **ZIO Actors**: Apache 2.0, fully open-source

TJMPaaS policy: Use only open-source frameworks with permissive licenses (see PDR-0005).

## Revision History

| Date | Change | Author |
|------|--------|--------|
| 2025-11-26 | Initial draft and acceptance | Tony Moores |
