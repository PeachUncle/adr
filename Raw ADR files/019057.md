# ADR-0016: Real-time Communication Protocol

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-30
- **Feature:** 002-phase-5-cloud-deploy
- **Context:**

Phase 5 requires real-time task synchronization across multiple connected clients (US16). When a user creates, updates, or completes a task on one device, all other connected devices should see the change within 1 second.

Key requirements:
- Bi-directional communication support (future extension to user presence, typing indicators)
- Fan-out pattern to multiple clients (same user, different devices)
- Connection management (reconnect on network interruption)
- User isolation (user A's updates go to user A's clients only)
- Integration with event-driven architecture (consume from task-updates topic)
- WebSocket Service must be separate from main backend (already decided in ADR-0014)

NFR-EDA-012 requires: "System MUST deliver task updates to all connected clients within 1 second"

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Defines real-time sync pattern for all clients
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - WebSocket vs SSE vs Polling considered
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects frontend, WebSocket Service, all client devices
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Use WebSocket with dedicated WebSocket Service consuming task-updates topic via Dapr Pub/Sub.

**Real-time Stack:**
- **Protocol**: WebSocket (RFC 6455)
- **Service**: WebSocket Service (:8005) - dedicated microservice
- **Frontend Client**: WebSocket connection with reconnection logic
- **Event Source**: task-updates Kafka topic (consumed via Dapr)
- **Fan-out Pattern**: In-memory connection manager per user, broadcast to all user's connections
- **Reconnection Strategy**: Exponential backoff, state resync on reconnect
- **User Isolation**: Connection tracking by user_id, broadcast only to user's connections

**Message Flow:**
```
User Action → Backend API → Dapr Pub/Sub → task-updates topic
                                                          ↓
                                        Dapr Consumer
                                                          ↓
                                             WebSocket Service
                                                          ↓
                                       Fan-out to user's connections
                                                          ↓
                                              All Client Devices
```

<!-- For technology stacks, list all components:
     - Framework: Next.js 14 (App Router)
     - Styling: Tailwind CSS v3
     - Deployment: Vercel
     - State Management: React Context (start simple)
-->

## Consequences

### Positive

**Bi-directional Communication:**
- Future support for user presence (online/offline indicators)
- Future support for typing indicators, collaborative features
- Server can push unsolicited updates (e.g., admin notifications)

**Connection Management:**
- Persistent connections reduce overhead compared to polling
- Automatic reconnection handling (exponential backoff)
- Connection state visibility (connected, connecting, disconnected)
- Efficient bandwidth utilization (no repeated polling)

**Fan-out Scalability:**
- In-memory connection manager (O(1) broadcast per user)
- WebSocket Service scales independently based on connection count
- No impact on main backend performance
- Scales to thousands of concurrent connections

**Event-Driven Integration:**
- Clean separation from Backend API (via Kafka topic)
- Existing services can publish to task-updates without knowledge of WebSocket
- Consistent with ADR-0013 (Dapr Abstraction Layer)
- Consumer pattern matches other microservices (Notification, Recurring, Audit)

**User Experience:**
- Sub-1 second sync as required (NFR-EDA-012)
- Real-time feedback (immediate UI updates)
- Offline queueing (client-side cache, sync on reconnect)

### Negative

**Complexity:**
- Additional WebSocket Service to develop and deploy
- Frontend WebSocket client with state management (reconnection, queueing)
- Connection management complexity (handle disconnects, network changes, mobile sleep)

**Resource Consumption:**
- WebSocket connections hold TCP connection per client (more server resources)
- In-memory connection state scales with concurrent users
- Load balancer needs WebSocket support (sticky sessions)

**Debugging:**
- Distributed system (Backend → Kafka → WebSocket Service → Client)
- Harder to trace message flow across services
- Connection state debugging requires WebSocket inspection tools

**Browser Limitations:**
- Mobile browsers may close WebSocket on background/sleep
- Proxy servers may block WebSocket connections
- Requires fallback for WebSocket-unavailable environments

**Operational Overhead:**
- WebSocket Service monitoring (connection counts, error rates)
- More deployment targets in CI/CD pipeline
- Connection health checks and alerting

## Alternatives Considered

**Alternative A: Server-Sent Events (SSE) from Backend API**

**Rejected because:**
- Unidirectional (server to client only) - no bi-directional future support
- Limited connection management (standard HTTP with streaming response)
- Client must implement reconnection (no standard browser API)
- Falls back to long-polling when SSE unsupported
- Doesn't support fan-out pattern without additional complexity

**Why rejected:** WebSocket provides superior connection management and bi-directional capabilities. SSE would require additional infrastructure for connection pooling and doesn't support future collaborative features.

**Alternative B: Long-Polling from Frontend**

**Rejected because:**
- High latency (poll interval required, minimum 1-5 seconds)
- High server load (many requests with 200 OK responses)
- Inefficient bandwidth (repeated HTTP headers)
- Poor battery/charging impact on mobile devices
- No real-time feel

**Why rejected:** Violates NFR-EDA-012 (<1 second sync). Polling latency and inefficiency don't meet real-time requirements.

**Alternative C: WebRTC for P2P Sync**

**Rejected because:**
- Over-engineered for client-server sync (designed for peer-to-peer)
- Requires STUN/TURN signaling server
- Higher complexity and resource consumption
- Unnecessary for simple fan-out pattern
- Browser support inconsistent (especially on mobile)

**Why rejected:** WebSocket Service provides simpler fan-out without peer-to-peer complexity. WebRTC doesn't align with use case.

**Alternative D: Push Notifications (FCM/APNs)**

**Rejected because:**
- Out-of-band (not in-app, requires user permission)
- Limited message size and rate limiting
- Platform-specific (different implementation per platform)
- No guarantee of delivery (platform may batch/delay)
- Doesn't support real-time collaborative features

**Why rejected:** Spec requires in-app real-time notifications (US8), not external push. WebSocket provides in-app sync with guaranteed delivery for connected clients.

**Alternative E: WebSocket from Main Backend (no separate service)**

**Rejected because:**
- Ties real-time scaling to main backend (can't scale independently)
- Backend already handles chat, MCP, task CRUD - adding WebSocket increases complexity
- Violates single responsibility (Backend becomes both API and sync service)
- Harder to test (WebSocket testing mixed with API testing)
- No separation of concerns

**Why rejected:** Separate WebSocket Service (ADR-0014) allows independent scaling and clearer boundaries. ADR-0014 established microservice pattern, consistent to keep WebSocket separate.

<!-- Group alternatives by cluster:
     Alternative Stack A: Remix + styled-components + Cloudflare
     Alternative Stack B: Vite + vanilla CSS + AWS Amplify
     Why rejected: Less integrated, more setup complexity
-->

## References

- Feature Spec: [specs/002-phase-5-cloud-deploy/spec.md](../../specs/002-phase-5-cloud-deploy/spec.md)
- Implementation Plan: [specs/002-phase-5-cloud-deploy/plan.md#architecture-decisions](../../specs/002-phase-5-cloud-deploy/plan.md#architecture-decisions)
- WebSocket RFC: https://datatracker.ietf.org/doc/html/rfc6455/
- Related ADRs: ADR-0013 (Dapr Abstraction Layer), ADR-0014 (Microservice Decomposition)
- Evaluator Evidence: None (initial decision)
