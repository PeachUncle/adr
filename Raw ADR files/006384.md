# ADR-002: GraphQL Federation v2 for Microservices Integration

**Status:** Accepted
**Date:** 2025-11-07
**Decision Makers:** Arman Platform Team
**Related:** P0-2

## Context

The Arman platform consists of 32+ microservices that need to expose a unified GraphQL API to clients. Previously, we had:
- A basic gateway with only 3 subgraphs (activity, social, physio)
- No entity resolution across services
- Limited Federation capabilities
- Missing critical services from the gateway (users, auth, coaches, nutrition, content)

Clients (web, mobile) need to:
- Query data from multiple services in a single GraphQL operation
- Navigate relationships across service boundaries
- Have a consistent, type-safe API

## Decision

We will implement **Apollo Federation v2** as our GraphQL composition strategy with the following architecture:

### Gateway Configuration
- **Apollo Gateway** with `IntrospectAndCompose` for development
- 8 core subgraphs registered:
  - activity-subgraph (app/)
  - social-subgraph (app/)
  - physio-subgraph (app/)
  - live-subgraph (app/)
  - users-service (services/)
  - coaches-service (services/)
  - nutrition-service (services/)
  - content-service (services/)

### Entity Pattern
- **User** as the primary shared entity with `@key(fields: "id")`
- Each subgraph can extend User with domain-specific fields
- Reference resolvers (`__resolveReference`) enable cross-service queries

Example:
```graphql
# In users-service
type User @key(fields: "id") {
  id: ID!
  email: String!
  name: String!
}

# In activity-subgraph
type User @key(fields: "id") {
  id: ID!
  activityRings(date: String): ActivityRings
  loadSummary: LoadSummary
  awards: [Award!]!
}
```

### Security
- JWT propagation via `RemoteGraphQLDataSource`
- Authorization headers forwarded to all subgraphs
- Rate limiting at gateway level
- CSP with nonce mode

### Infrastructure
- Multi-stage Docker build with non-root user
- Kubernetes deployment with HPA (2-10 replicas)
- Readiness probes checking gateway initialization
- Prometheus metrics exposed

## Consequences

### Positive
✅ **Unified API Surface:** Single GraphQL endpoint for all clients
✅ **Type Safety:** Strong typing across service boundaries
✅ **Flexible Querying:** Clients can request exactly what they need
✅ **Independent Deployment:** Subgraphs can deploy independently
✅ **Discoverability:** Schema introspection for all services

### Negative
❌ **Single Point of Failure:** Gateway outage affects all GraphQL operations
❌ **Complexity:** Requires understanding Federation directives
❌ **N+1 Queries:** Potential performance issues without DataLoader
❌ **Schema Coordination:** Breaking changes require careful coordination

### Mitigations
- High availability with multiple replicas and HPA
- Comprehensive monitoring and alerting
- DataLoader implementation in subgraphs
- Schema versioning and deprecation policies
- Managed Federation for production (Rover/Apollo Studio)

## Alternatives Considered

### 1. Schema Stitching
**Rejected:** Deprecated by Apollo, less type-safe, manual merging

### 2. REST API Gateway
**Rejected:** Lose GraphQL benefits, no unified schema, more client complexity

### 3. Monolithic GraphQL Server
**Rejected:** Against microservices architecture, single deployment unit

## Implementation Notes

### Subgraph Requirements
Each subgraph must:
1. Use `@apollo/subgraph` package
2. Import Federation directives: `@key`, `@shareable`, `@external`
3. Implement `__resolveReference` for entities
4. Expose GraphQL at `/graphql`
5. Support health checks

### Gateway Environment Variables
```bash
ACTIVITY_URL=http://activity-subgraph:4005/graphql
SOCIAL_URL=http://social-subgraph:4006/graphql
PHYSIO_URL=http://physio-subgraph:4016/graphql
LIVE_URL=http://live-subgraph:4017/graphql
USERS_URL=http://users-service:4001/graphql
COACHES_URL=http://coaches-service:4008/graphql
NUTRITION_URL=http://nutrition-service:4013/graphql
CONTENT_URL=http://content-service:4014/graphql
```

### Deployment
```bash
# Install Helm chart
helm install graphql-gateway ./helm/graphql-gateway \
  --namespace arman \
  --create-namespace \
  --values ./helm/graphql-gateway/values.yaml

# Verify deployment
kubectl -n arman get pods -l app.kubernetes.io/name=graphql-gateway
kubectl -n arman logs -l app.kubernetes.io/name=graphql-gateway
```

## Future Enhancements
- [ ] Managed Federation with Apollo Studio/Rover
- [ ] Persisted queries for performance
- [ ] GraphQL subscriptions for real-time features
- [ ] Rate limiting per-operation
- [ ] Query complexity analysis
- [ ] Automatic schema validation in CI/CD

## References
- [Apollo Federation Docs](https://www.apollographql.com/docs/federation/)
- [Federation v2 Spec](https://specs.apollo.dev/federation/v2.3)
- COMPREHENSIVE_AUDIT_REPORT_45_PHASES.md (P0-2)
