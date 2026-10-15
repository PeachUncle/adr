# Architecture Decision Record (ADR) Template

## ADR-000: Two-Phase Modular Monolith to Microservices Architecture

**Status:** Accepted  
**Decision Date:** November 2025  
**Phase:** Phase 1 (MVP) and Phase 2 (Microservices)

---

## Context

CrudCloud is a cloud database provisioning platform that will eventually scale to multiple independent microservices. However, to reduce MVP complexity and de-risk the project, we are adopting a **modular monolith** approach for Phase 1 that naturally transitions to microservices in Phase 2.

---

## Decision

The application will be organized into **vertical, domain-driven modules** with clear boundaries:

1. **Auth Module** - User authentication, registration, organization management
2. **Instance Module** - Database instance provisioning and lifecycle management
3. **Payment Module** - Transaction processing and payment integration
4. **Plan Module** - Subscription tier management and limits
5. **Catalog Module** - Database engine catalog and specifications
6. **Core Module** - Shared infrastructure (database, config, events, exceptions)

**Phase 1 Deployment:** Single monolithic JAR with all modules  
**Phase 2 Deployment:** Separate microservices with API Gateway

---

## Rationale

### Why Modular Monolith (Phase 1)?

| Factor | Monolith | Microservices |
|--------|----------|--------------|
| **MVP Time to Market** | 6-8 weeks | 12-14 weeks |
| **Operational Complexity** | Low (1 deployment) | High (6+ deployments) |
| **Debugging** | Simple (single JVM) | Complex (distributed) |
| **Transactions** | ACID (automatic) | Eventual (manual saga) |
| **Learning Curve** | Lower | Steeper |
| **Cost (Dev)** | Lower | Higher |

**Benefit:** Ship MVP faster, validate with real users before microservices complexity

### Why Modular Design?

| Benefit | Implementation |
|---------|-----------------|
| **Clear Ownership** | One team = one module (scalable to multiple teams in Phase 2) |
| **Easy Testing** | Module-level unit and integration tests |
| **Reduced Coupling** | APIs and events instead of direct imports |
| **Future Extraction** | Modules become services with minimal refactoring |
| **Scalability** | Phase 2 only changes deployment topology, not code |

---

## Module Communication Strategy

### Cross-Module Communication Methods

#### ✅ **Preferred: Event-Driven (for notifications/reactions)**
- Instance Created → Publish `InstanceCreatedEvent` 
- Payment Module listens and logs for billing
- Auth Module listens and updates user activity
- No immediate coupling, allows async reactions
- Easily becomes message queue in Phase 2

#### ✅ **Allowed: Module API (for queries/validation)**
- Instance Module queries Payment Module via `PaymentModuleApi` interface
- Depends on interface, not implementation
- Easily becomes HTTP client in Phase 2
- Clear contract definition

#### ❌ **Forbidden: Direct Service Injection**
```java
// ❌ Never do this
@Service
public class InstanceService {
    @Autowired
    private PaymentService paymentService;  // Violates boundary!
}
```

---

## Implementation Commitments

### Phase 1 (Monolith with Module Structure)

1. **Module Isolation**
   - Services ONLY autowired within their module
   - Public contracts via `*ModuleApi` interfaces
   - Cross-module calls via events or APIs only

2. **API Gateway Concept**
   - Each module under distinct `/api/v1/{module}/*` prefix
   - Controllers don't cross boundaries
   - Routes document module ownership

3. **Database Strategy**
   - Single PostgreSQL instance (monolith)
   - Tables logically owned by modules
   - Schema designed for independent DB per module (Phase 2)

4. **Configuration**
   - Externalized config via `application.properties`
   - Module-specific configs in module packages
   - Environment profiles (dev, staging, prod)

### Phase 2 (Microservices with Minimal Refactoring)

1. **Service Extraction**
   - Extract each module to separate repository
   - Each service gets own database (schema migration)
   - Deploy independently with versioning

2. **Communication Migration**
   - Replace event publishing with message broker (RabbitMQ/Kafka)
   - Replace `@Autowired` APIs with HTTP clients (Feign/RestTemplate)
   - Implement service discovery (Eureka/Consul)

3. **API Gateway**
   - Spring Cloud Gateway routes `/api/v1/{module}/*` to services
   - Centralized authentication/authorization
   - Rate limiting and circuit breaking

4. **Operational Changes**
   - Independent CI/CD pipelines per service
   - Service-specific monitoring and alerting
   - Distributed tracing (Jaeger/Zipkin)
   - Saga pattern for distributed transactions

---

## Constraints & Trade-offs

### Constraints

1. **No Service-to-Service Transactions in Phase 1**
   - Use event-driven patterns for workflows
   - Example: Upgrade → UserUpgradedEvent → listeners react

2. **No Service Discovery in Phase 1**
   - Services found via Spring autowiring
   - Phase 2 adds Eureka/Consul

3. **Single Database Instance**
   - Data isolation only at application layer
   - Phase 2 introduces database per service

4. **No API Gateway Proxy**
   - Direct controller routing
   - Phase 2 adds Spring Cloud Gateway

### Trade-offs

| Trade-off | Phase 1 | Phase 2 |
|-----------|---------|---------|
| **Deployment Complexity** | ✅ Low | ⚠️ Higher |
| **Code Organization** | ⚠️ Monolith | ✅ Microservices |
| **Scaling** | ⚠️ Vertical | ✅ Horizontal |
| **Development Speed** | ✅ Fast | ⚠️ Slower per change |
| **Testing** | ✅ Simpler | ⚠️ More complex |

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| **Module coupling** | HIGH | HIGH | Code reviews enforce APIs, strict import rules |
| **Migration complexity** | MEDIUM | MEDIUM | Contract tests now, CDC tests in Phase 2 |
| **Performance bottleneck** | LOW | MEDIUM | Single database fine for MVP, Phase 2 adds sharding |
| **Distributed transactions** | LOW (Phase 1) | HIGH (Phase 2) | Event-driven design now, saga pattern ready |

---

## Success Metrics

### Phase 1 (MVP)
- [ ] Modular structure with zero direct service imports across modules
- [ ] All cross-module communication via events or APIs
- [ ] 70%+ unit test coverage
- [ ] Contract tests define module boundaries
- [ ] Single JAR deployment working
- [ ] API documentation complete

### Phase 2 Readiness
- [ ] Modules extractable to separate repositories with <10 hours refactoring
- [ ] No data joins across module boundaries
- [ ] Event-driven patterns in place for workflows
- [ ] Module APIs translateable to HTTP clients

---

## Related ADRs (Create as needed)

- ADR-001: Event-Driven Communication Strategy
- ADR-002: Database Schema Ownership Model
- ADR-003: Exception Handling Hierarchy
- ADR-004: DTO Design and Validation Strategy
- ADR-005: Module API Contract Definition

---

## References

- **Modular Monoliths:** Sam Newman - "Building Microservices" (2nd Ed)
- **Domain-Driven Design:** Eric Evans - "Domain-Driven Design"
- **Consumer-Driven Contracts:** Pact Framework
- **Distributed Transactions:** Chris Richardson - "Saga Pattern"
