# ADR-0014: Microservice Decomposition for Phase5 Services

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:**2025-12-30
- **Feature:** 002-phase-5-cloud-deploy
- **Context:**

Phase 5 introduces event-driven architecture with new functional requirements:
- Real-time task synchronization across multiple clients (US16)
- In-app notifications for reminders (US8)
- Auto-generation of recurring task occurrences (US9)
- Audit trail for all task operations (US10)
- Exact-time reminder scheduling via Dapr Jobs (US11)

The existing monolithic backend handles task CRUD, chat, and MCP server functionality. New requirements suggest separating concerns into focused services.

Key constraints from architecture:
- Single Responsibility Principle (SRP) should guide service boundaries
- Independent scaling based on load (each service has different usage patterns)
- Failure isolation needed (one service failure should not cascade)
- Event-driven communication via Dapr Pub/Sub already decided (ADR-0013)

Existing ADR-0009 (Three-Container Microservice Architecture) established microservice pattern for Phase 4.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Defines service boundaries for entire system
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Monolith vs Microservices vs Hybrid considered
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects deployment, scaling, monitoring of all services
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Create 4 new dedicated microservices for Phase 5 functionality:

**Service Decomposition:**
1. **WebSocket Service** (:8005) - Real-time multi-client synchronization
2. **Notification Service** (:8002) - In-app reminder notifications
3. **Recurring Task Service** (:8003) - Next occurrence auto-generation
4. **Audit Service** (:8004) - Event logging and history

**Existing Services Remain Monolithic:**
- Backend API (:8000) - Task CRUD, chat endpoints, MCP server, event publishing
- MCP Server (:8001) - AI agent tools (remains with backend)

**Communication Pattern:**
- All services communicate via Dapr Pub/Sub (no direct HTTP/RPC between microservices)
- Backend publishes events to `task-events`, `reminders`, `task-updates` topics
- Consumer services subscribe to topics and process events asynchronously

**Deployment Strategy:**
- Each service deployed as separate Kubernetes Deployment/ReplicaSet
- Independent HorizontalPodAutoscaler (HPA) per service
- Services share same Docker image base for consistency

<!-- For technology stacks, list all components:
     - Framework: Next.js 14 (App Router)
     - Styling: Tailwind CSS v3
     - Deployment: Vercel
     - State Management: React Context (start simple)
-->

## Consequences

### Positive

**Scalability:**
- WebSocket Service scales independently based on concurrent client connections
- Notification Service scales based on reminder volume (burst when reminders fire)
- Recurring Task Service scales based on task completion rate
- Audit Service scales based on audit log write rate
- Backend remains responsive even when microservices are under load

**Failure Isolation:**
- Notification Service failure doesn't prevent task CRUD
- WebSocket Service failure doesn't affect reminder delivery
- Audit Service failure doesn't impact user-facing features
- Recurring Task Service failure only affects next occurrence generation

**Development Velocity:**
- Services can be developed in parallel by different team members
- Clear service boundaries simplify testing (each service has defined inputs/outputs)
- Smaller codebases per service reduce cognitive load
- Independent deployment cycles per service

**Operational Clarity:**
- Each service has clear ownership and responsibility
- Metrics and monitoring per service (easier to identify issues)
- Independent deployment rollbacks per service
- Service-specific resource quotas and limits

**Team Organization:**
- Supports parallel team strategy (Team A: Backend, Team B: Services, Team C: DevOps)
- Clear boundaries for code review and pull requests
- Reduced merge conflicts (different codebases)

### Negative

**Operational Overhead:**
- 4 additional Kubernetes Deployments to manage
- 4 additional Dapr sidecars (resource overhead ~80MB total)
- More complex monitoring and alerting setup
- Increased configuration complexity (values files for each service)

**Development Overhead:**
- Need to manage service discovery (handled by Dapr, but still conceptual overhead)
- Distributed debugging requires tracing across services
- More complex local development (need to run all services)
- Shared libraries need separate packaging and versioning

**Inter-Service Latency:**
- Event-driven communication adds latency compared to in-process calls
- WebSocket sync requires extra hop (Backend → Kafka → WebSocket Service → Client)
- May impact user-perceived responsiveness for real-time features

**Testing Complexity:**
- Integration testing requires running all services
- Event ordering and timing tests needed
- Mock/stub infrastructure for each service
- E2E tests more fragile with multiple moving parts

**Deployment Complexity:**
- More deployment targets in CI/CD pipeline
- Helm chart templates for each service
- Coordinated deployments when services have interdependencies
- More surface area for deployment failures

## Alternatives Considered

**Alternative A: Monolith Extension (Add features to existing backend)**

**Rejected because:**
- No independent scaling (WebSocket connections scale with CPU/memory of entire backend)
- Failure cascades (notification failure affects all backend features)
- Team development velocity reduced (merge conflicts, larger codebase)
- Monolithic deployment (all-or-nothing release)

**Why rejected:** Microservices align with event-driven architecture pattern, enable independent scaling, and support parallel team development. Trade-off in operational complexity is acceptable for a hackathon context with time constraint.

**Alternative B: Hybrid Approach (Monolith + 1-2 microservices)**

**Rejected because:**
- Inconsistent architecture (some features monolith, some microservices)
- Undefined service boundaries (where to draw line?)
- Future refactoring complexity (moving between monolith and microservice)
- Mixed communication patterns (direct calls vs events)

**Why rejected:** Either fully microservices or fully monolith is clearer. With Dapr Pub/Sub already selected (ADR-0013), full microservices approach is more consistent.

**Alternative C: Service Mesh (Istio/Linkerd) instead of Dapr**

**Rejected because:**
- Higher complexity than Dapr (CRDs, sidecar injection, control plane)
- More resource overhead (Envoy sidecar vs Dapr sidecar)
- Steeper learning curve for hackathon timeline
- Constitution Principle XVIII explicitly mandates Dapr

**Why rejected:** Dapr provides needed abstraction and resilience patterns with lower complexity than full service mesh.

**Alternative D: Functions-as-a-Service (AWS Lambda, Cloud Functions)**

**Rejected because:**
- Target is DigitalOcean DOKS (Kubernetes), not serverless
- Different deployment model (no containers to manage)
- Cold start latency for infrequent operations
- Doesn't align with event-driven microservices pattern in spec

**Why rejected:** Project explicitly targets Kubernetes deployment. Serverless would require complete architecture change and doesn't fit DOKS target environment.

<!-- Group alternatives by cluster:
     Alternative Stack A: Remix + styled-components + Cloudflare
     Alternative Stack B: Vite + vanilla CSS + AWS Amplify
     Why rejected: Less integrated, more setup complexity
-->

## References

- Feature Spec: [specs/002-phase-5-cloud-deploy/spec.md](../../specs/002-phase-5-cloud-deploy/spec.md)
- Implementation Plan: [specs/002-phase-5-cloud-deploy/plan.md#architecture-decisions](../../specs/002-phase-5-cloud-deploy/plan.md#architecture-decisions)
- Constitution Phase 5: [constitution-prompt-phase-5.md](../../constitution-prompt-phase-5.md)
- Related ADRs: ADR-0009 (Three-Container Microservice Architecture), ADR-0013 (Dapr Abstraction Layer), ADR-0010 (Service Discovery and Networking)
- Evaluator Evidence: None (initial decision)
