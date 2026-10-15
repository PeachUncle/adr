# ADR-0010: Service Discovery and Networking Strategy

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-24
- **Feature:** 001-k8s-local-deploy
- **Context:** Phase 4 requires defining how services communicate within Minikube and how users access the application. The three services (frontend, backend, MCP server) need internal communication patterns for API calls and tool invocations. External users need browser access to the frontend. Constitution Principle V mandates using Kubernetes internal DNS for service discovery.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Defines inter-service and external access patterns
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - LoadBalancer, port-forward only evaluated
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects Service types, Ingress, and DNS resolution
-->

## Decision

We will adopt a hybrid networking strategy using three Kubernetes service types and NGINX Ingress:

**Internal Communication (ClusterIP Services):**
- Backend Service: `backend.todo-app.svc.cluster.local` or `backend:8000` (ClusterIP)
- MCP Server Service: `mcp-server.todo-app.svc.cluster.local` or `mcp-server:8001` (ClusterIP)
- Frontend uses `http://backend:8000` for API calls
- Backend uses `http://mcp-server:8001` for tool invocations

**External Access (NodePort + Ingress):**
- Frontend Service: NodePort type exposing on port 80 (mapped to node port 30080)
- Minikube access: `minikube service frontend -n todo-app` or `http://<minikube-ip>:30080`
- Ingress Resource: NGINX ingress controller with `todo.local` hostname
- DNS: `/etc/hosts` entry for local testing (`<minikube-ip> todo.local`)

**Service Discovery Pattern:**
- Frontend: `NEXT_PUBLIC_API_URL=http://backend:8000`
- Backend: `MCP_SERVER_URL=http://mcp-server:8001`
- No hardcoded IPs; Kubernetes DNS resolves service names to cluster IPs

### Networking Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                       Minikube Cluster                      │
│                                                           │
│  External Access                                           │
│  ┌────────────────────────────────────────────────────┐      │
│  │  Browser → todo.local:80                          │      │
│  │                  ↓                                   │      │
│  │          NGINX Ingress (Cluster Addon)              │      │
│  │                  ↓                                   │      │
│  │  frontend Service (NodePort:80 → Pod:3000)          │      │
│  └────────────────────────────────────────────────────┘      │
│                      ↓                                     │
│  ┌──────────────┐    ┌──────────────┐                 │
│  │   Frontend   │───▶│   Backend    │                 │
│  │  Pod: 3000   │    │ Pod: 8000   │                 │
│  └──────────────┘    └──────┬───────┘                 │
│                            │ DNS: backend              │
│                            ↓                          │
│                      ┌──────────────┐                 │
│                      │  MCP Server  │                 │
│                      │ Pod: 8001   │                 │
│                      └──────────────┘                 │
│                        DNS: mcp-server             │
└─────────────────────────────────────────────────────────────┘
```

### Rationale

ClusterIP for internal services provides secure, low-latency communication within the cluster using Kubernetes DNS. NodePort for frontend allows easy Minikube access without requiring `minikube tunnel`. Ingress provides production-like URL routing (todo.local) that can transition to LoadBalancer in Phase 5. This hybrid approach balances development convenience with production readiness.

## Consequences

### Positive

- **Production-Ready Pattern:** Ingress with host-based routing mirrors Phase 5 cloud deployment patterns
- **Constitution Alignment:** Satisfies Principle V (Service Discovery) using Kubernetes internal DNS
- **Secure Internal Traffic:** ClusterIP services are not exposed outside cluster, reducing attack surface
- **Easy Minikube Access:** NodePort works with `minikube service` command without tunnel
- **Service Discovery:** No hardcoded IPs; Kubernetes DNS automatically handles pod restarts and scaling
- **Future-Proof:** Ingress configuration directly migrates to LoadBalancer in Phase 5
- **Development Convenience:** `todo.local` hostname provides clean local testing experience

### Negative

- **Manual Hosts File:** Requires editing `/etc/hosts` for `todo.local` access
  - *Mitigation:* Document setup in quickstart.md; provide `minikube service` as alternative
- **Minikube IP Changes:** Minikube IP may change on restart, requiring hosts file update
  - *Mitigation:* Use `minikube service frontend -n todo-app --url` which is stable
- **NodePort Limits:** NodePort range is 30000-32767, high port number may confuse users
  - *Mitigation:* Ingress provides standard port 80 access; NodePort is fallback
- **Minikube-Specific:** LoadBalancer would be simpler but requires `minikube tunnel`
  - *Mitigation:* Document both access methods; use Ingress as primary

## Alternatives Considered

### Alternative A: LoadBalancer for Frontend
- **Pros:** External IP, standard port 80, no hosts file editing, cloud-native
- **Cons:** Requires `minikube tunnel` which is unstable, creates background process
- **Why Rejected:** LoadBalancer in Minikube requires running `minikube tunnel` command in background. This process often disconnects and requires restart. NodePort provides more stable Minikube experience.

### Alternative B: All Services with LoadBalancer
- **Pros:** Consistent service type, all services accessible externally
- **Cons:** Backend and MCP server should NOT be externally accessible (security risk)
- **Why Rejected:** Exposing backend API and MCP tools to the internet creates a significant security vulnerability. Only frontend should have external access.

### Alternative C: Port-Forward Only (No Service Types)
- **Pros:** Simplest setup, no Ingress/Service resources
- **Cons:** Manual command required for each access session, not production-like
- **Why Rejected:** Port-forwarding (`kubectl port-forward`) is useful for debugging but not a production deployment pattern. We want development to mirror production as closely as possible.

### Alternative D: Traefik Ingress Controller
- **Pros:** More features than NGINX, better auto-discovery, Let's Encrypt built-in
- **Cons:** Less common than NGINX, more complex setup, overkill for Phase 4
- **Why Rejected:** NGINX is the default Minikube ingress addon, well-documented, and sufficient for our needs. Traefik adds complexity without proportional benefit.

## References

- Feature Spec: [specs/001-k8s-local-deploy/spec.md](../../specs/001-k8s-local-deploy/spec.md)
- Implementation Plan: [specs/001-k8s-local-deploy/plan.md](../../specs/001-k8s-local-deploy/plan.md) AD-02
- Research Notes: [specs/001-k8s-local-deploy/research.md](../../specs/001-k8s-local-deploy/research.md) §2, §9
- Data Model: [specs/001-k8s-local-deploy/data-model.md](../../specs/001-k8s-local-deploy/data-model.md) §7-10
- Related ADRs: ADR-0009 (Three-Container Architecture)
- Constitution Phase 4: [constitution-prompt-phase-4.md](../../constitution-prompt-phase-4.md) Principle V
- Kubernetes Service Types: https://kubernetes.io/docs/concepts/services-networking/service/
