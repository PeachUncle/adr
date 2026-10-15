# ADR-003: GraphQL as Primary API

## Status
Accepted

## Date
2024-01-16

## Context

NEURECTOMY needs an API layer that:
1. Supports complex, nested data queries for agent hierarchies
2. Enables real-time updates via subscriptions
3. Provides strong typing for frontend integration
4. Allows efficient data fetching (avoid over/under-fetching)
5. Supports introspection for tooling and documentation

## Decision

We will use **GraphQL** as the primary API protocol, implemented with **async-graphql**.

### Schema Design Principles
1. **Domain-Driven**: Types mirror domain concepts (Agent, Workflow, Container)
2. **Relay Specification**: Follow Relay connection spec for pagination
3. **Input Validation**: Use input types with validation
4. **Error Handling**: Structured errors with error codes

### Implementation
```graphql
type Query {
  agent(id: UUID!): Agent
  agents(first: Int, after: String): AgentConnection!
  me: User!
}

type Mutation {
  createAgent(input: CreateAgentInput!): AgentPayload!
  updateAgent(id: UUID!, input: UpdateAgentInput!): AgentPayload!
  deleteAgent(id: UUID!): DeletePayload!
}

type Subscription {
  agentUpdates(agentId: UUID!): AgentUpdate!
  systemEvents: SystemEvent!
}
```

### Authentication
- JWT tokens passed in `Authorization` header
- Extracted and validated in middleware
- User context available in all resolvers

## Consequences

### Positive
- **Flexible Queries**: Clients request exactly what they need
- **Strong Typing**: Schema serves as contract and documentation
- **Real-time**: Native subscription support for WebSocket
- **Tooling**: GraphiQL/Playground for exploration
- **Introspection**: Auto-generated documentation
- **Batching**: DataLoader pattern prevents N+1 queries

### Negative
- **Complexity**: More complex than simple REST for simple cases
- **Caching**: HTTP caching more difficult (all POST requests)
- **Learning Curve**: Team needs GraphQL expertise
- **Security**: Must prevent expensive queries (depth/complexity limits)

### Security Mitigations
- Query depth limiting (max 10 levels)
- Query complexity analysis
- Rate limiting per user
- Field-level authorization

## Alternatives Considered

### 1. REST API
- ✅ Simpler, well-understood
- ✅ Better HTTP caching
- ❌ Over-fetching/under-fetching
- ❌ Multiple requests for related data
- ❌ No native subscriptions

### 2. gRPC
- ✅ Excellent performance
- ✅ Strong typing with Protobuf
- ❌ Not browser-friendly without proxy
- ❌ Less developer-friendly for exploration
- ❌ More complex subscription handling

### 3. REST + WebSocket (separate)
- ✅ Simpler individual components
- ❌ Two protocols to maintain
- ❌ No unified schema
- ❌ More client complexity

## Query Examples

### Fetch Agent with Nested Data
```graphql
query GetAgentDetails($id: UUID!) {
  agent(id: $id) {
    id
    name
    status
    config
    conversations(first: 10) {
      edges {
        node {
          id
          messageCount
          lastActivity
        }
      }
    }
    metrics {
      totalRequests
      averageLatency
    }
  }
}
```

### Subscribe to Updates
```graphql
subscription WatchAgent($agentId: UUID!) {
  agentUpdates(agentId: $agentId) {
    id
    status
    lastActivity
    metrics {
      requestsPerMinute
      errorRate
    }
  }
}
```

## References
- [GraphQL Specification](https://spec.graphql.org/)
- [async-graphql Book](https://async-graphql.github.io/async-graphql/en/index.html)
- [Relay Cursor Connections](https://relay.dev/graphql/connections.htm)
