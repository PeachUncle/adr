## ADR 013: Realtime Messaging (Centrifugo) & JWT-Based Authentication

### Context
We needed **reliable realtime collaboration** (lightweight chat, presence, live notifications) without coupling long‑lived WebSocket state to our API servers. At the same time, our API surface grew and required **consistent, stateless authentication/authorization** across services and environments. Prior ad‑hoc polling and cookie sessions led to latency, scaling pain, and inconsistent security.

### Decision
Adopt **Centrifugo** as a dedicated WebSocket pub/sub server for realtime features, and standardize on **JWT-based stateless authentication** for API access.

- **Centrifugo** provides a managed pub/sub layer (channels, presence, history, server‑side broadcasts) over WebSockets/SSE, decoupling realtime fan‑out from the API.
- **JWT auth** protects all backend endpoints via a shared `get_current_user` dependency, enforcing verification and authorization checks per request.

### Status
**Accepted — Implemented**

### Rationale for Change
- **Scalability & Decoupling:** Offload fan‑out and connection management to Centrifugo; API instances remain stateless and horizontally scalable.
- **Lower Latency UX:** True realtime (WebSocket/SSE) replaces polling for chat, notifications, and board updates.
- **Security Consistency:** JWT verifies identity at the edge of every request; simpler zero‑trust posture for multi‑service topology.
- **Operational Clarity:** Clear separation of concerns—API for business logic, Centrifugo for delivery; easier to observe and tune independently.

### Consequences

**Positive**
1. **Realtime by default:** Channels for projects/boards/DMs; presence and typing indicators become straightforward.
2. **Stateless APIs:** Easier autoscaling; fewer sticky‑session constraints.
3. **Simpler integrations:** External services can publish into Centrifugo via signed server API or webhook bridge.
4. **Observability:** Pub/sub metrics + API auth logs (APM/traces) improve incident triage.

**Negative / Risks**
1. **New moving part:** Centrifugo adds another service to deploy, monitor, and secure.
2. **Token lifecycle:** JWT rotation/expiry must be handled correctly (clock skew, refresh flow).
3. **Vendor lock‑in (protocol):** While open, some Centrifugo features are specific (history/presence semantics).
4. **Permission drift:** Channel‑level ACLs must stay in sync with app roles to avoid over‑broad subscriptions.

### Implementation Notes
- **Centrifugo**
  - **Transport:** WebSocket (fallback SSE/HTTP‑streaming as needed).
  - **Channels:** `project:{id}`, `sprint:{id}`, `ticket:{id}`, `chat:{roomId}`, `user:{id}` for direct notifications.
  - **Auth:** Use **Centrifugo connection JWT** (short‑lived, signed by backend) and **channel subscribe tokens** where needed.
  - **Features:** Presence (optional), limited message history for chat, server‑side publish from backend on domain events.
  - **Ops:** Health checks, channel cardinality limits, message size caps, backpressure metrics.
- **JWT for API**
  - **Format:** Access tokens (short TTL) signed with server secret/keys; bearer in `Authorization` header.
  - **Enforcement:** `get_current_user` dependency validates signature, expiry, audience, and scopes/roles before handler logic.
  - **Authorization:** RBAC gates for Admin/Manager/Member across Projects, Sprints, Tickets, Marketing, Integrations.
  - **Rotation:** Support key rotation (KID headers + keystore); clock‑skew tolerant validation.
  - **Testing:** **All HTTP calls are mocked in tests**; no real external calls per policy.
- **Security**
  - **Secrets:** Managed via env/secret store; least privilege for publish keys; never expose server keys to clients.
  - **Webhooks/Publish:** HMAC signatures for inbound notifications; idempotency keys; retry with backoff.
  - **PII:** Mask sensitive fields in logs; redact tokens; apply rate limits on auth and publish endpoints.
- **Observability**
  - Distributed tracing spans for publish/subscribe and notification pipelines.
  - Metrics: connection count, publish latency, dropped messages, auth failures.
  - Log taxonomy ensures tags avoid restricted terms (e.g., replace any “pivotel” with “magento”).

### Alternatives Considered
- **Socket.IO on app servers + Redis Pub/Sub:** Simpler to start, but ties WebSockets to API lifecycle; harder to scale and operate.
- **Managed SaaS (Pusher/Ably):** Fast to ship, but introduces vendor cost/lock‑in and external data residency concerns.
- **AWS API Gateway WebSockets:** Works, but more operational glue for auth, multiplexing, and presence features.
- **Cookie sessions for API:** Heavier server state, stickiness at load balancer, and cross‑service auth complexity.

### Migration / Rollout
1. Deploy Centrifugo alongside API; expose internal publish API; restrict public ports via security groups.
2. Ship client SDK integration behind feature flags (chat/notifications first).
3. Generate short‑TTL connection tokens on login; renew silently before expiry.
4. Gradually replace polling endpoints with channel subscriptions; keep HTTP fallbacks.
5. Add dashboards/alerts; run load tests; document runbook and failure modes.

### Future Considerations
- **Refresh tokens / OIDC:** Optional long‑lived refresh with rotation and revoke lists.
- **End‑to‑end encryption for DMs:** Consider per‑room keys and client‑side crypto for private channels.
- **Federated events:** Bridge external systems (CI/CD, ticketing) via integration keys and scoped channels.
- **Presence/Typing:** Expand to include read receipts and ephemeral indicators.
- **Multi‑region:** Evaluate global presence with sharding or regional Centrifugo clusters.
