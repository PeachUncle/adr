# Ingress Gateway for Multi-UI Hosting and API Abstraction

* Status: proposed
* Deciders: Platform Team, Frontend Team
* Date: 2025-12-13

## Context and Problem Statement

Today, each UI application is served on its own host port (e.g. `ecommerce-web` and `merchant-portal`) and each UI container owns its own reverse-proxy rules to backend services (Nginx configs under `docker/`).

As we add more UI applications (admin, kiosk, POS, etc.), we want:

1. **One browser origin** for all UIs (same host, path-based routing) to simplify cookies and eliminate CORS.
2. **Same-origin API access** so UIs can call `/api/...` without environment-specific host config.
3. **A single “front door”** where we can apply cross-cutting concerns (TLS, redirects, security headers, observability).

We need to decide which technology to use for an ingress gateway pattern that can serve multiple UIs on one host via path-based routing, while abstracting internal API hosts.

## Decision Drivers

1. **Path-based multi-app routing** - `/`, `/merchant/`, `/pos/`, etc. on the same host.
2. **Same-origin APIs** - UIs use relative URLs (e.g. `/api/cart/graphql`), not service hostnames.
3. **Subpath-safe SPAs** - No fragile HTML rewriting; apps must be buildable to run under a prefix.
4. **Operational simplicity** - Easy local Docker usage; minimal duplicated config across UIs.
5. **Production alignment** - A solution that maps cleanly to an eventual Kubernetes ingress/controller setup.
6. **Observability** - Access logs + metrics, and clean propagation of trace headers.

## Considered Options

1. **Traefik as the edge ingress gateway** (chosen)
2. **Nginx as a single edge reverse proxy** (viable, simpler but more static)
3. **Envoy as an edge proxy** (powerful, higher operational/config complexity)
4. **Spring Cloud Gateway as ingress** (better fit for API concerns than static UI delivery)
5. **Two-tier: edge ingress + API gateway** (future option if API policy needs grow)

## Decision Outcome

Chosen option: **Traefik as the edge ingress gateway**.

Traefik is a strong fit for a “single front door” in both Docker Compose and Kubernetes because:

- It supports **path-prefix routing** and middleware (strip-prefix, redirects, headers) without bespoke code.
- It integrates well with **Docker service discovery** (labels) and has a clean migration path to **Kubernetes Ingress / Gateway API**.
- It keeps the “gateway” as infrastructure, avoiding a new JVM service just to route traffic.

### Routing Contract (External)

The gateway provides a stable, same-origin contract for browsers:

- **UI apps**
  - `/` → default customer UI (e.g. `ecommerce-web`)
  - `/merchant/` → merchant portal
  - Future apps use stable prefixes (e.g. `/admin/`, `/kiosk/`, `/pos/`)
- **APIs**
  - `/api/...` → routed to internal services by prefix (e.g. `/api/merchandise/*`, `/api/cart/graphql`)
- **Auth and identity**
  - `/auth/*`, `/oauth2/*`, `/.well-known/*` → routed to `user-service` (or future identity edge)

### Best-Practice Requirements (Non-Negotiable)

To make path-based routing reliable:

1. **UIs must be subpath-safe**
   - Build assets must respect a configurable base path (e.g. Vite `base`).
   - Client routing must support a configurable base path (e.g. TanStack Router `basepath`).
   - OAuth redirect URIs must incorporate the base path (e.g. `/merchant/callback`).
2. **UIs must call APIs using relative, same-origin URLs**
   - Prefer `/api/...` and avoid embedding per-environment service hostnames in frontend code.
3. **Avoid HTML response rewriting**
   - Rewrite-based approaches are brittle (break CSP/SRI, caching, and future framework changes).
4. **Standardize forwarded headers**
   - Gateway sets `X-Forwarded-Proto`, `X-Forwarded-For`, `X-Forwarded-Host` and (when applicable) `X-Forwarded-Prefix`.
   - Preserve W3C trace context headers (`traceparent`, `tracestate`, `baggage`).
5. **Cache correctly**
   - Cache immutable hashed assets aggressively; avoid caching `index.html` (or equivalent entry HTML).

## Consequences

### Positive Consequences

- **Single origin** for all UIs (cookies and auth flows become simpler; no CORS).
- **Centralized routing** and reduced duplication of API proxy rules across UI containers.
- **Easier app onboarding**: adding a new UI becomes “choose a prefix + add routing”.
- **Clean path to Kubernetes** if/when we move from Docker Compose to an ingress controller.

### Negative Consequences

- **UI changes required** to support running under a base path (routing, asset URLs, auth callbacks).
- **One more runtime component** (Traefik) to operate and debug locally and in environments.
- **Prefix-routing complexity** (redirects, strip-prefix behavior) must be standardized to avoid drift.

## Implementation Notes and Next Steps

1. **Define canonical prefixes**
   - Decide prefix mapping (`/merchant/`, `/admin/`, etc.) and reserve `/api/`, `/oauth2/`, `/.well-known/`.
2. **Make each UI subpath-safe**
   - Introduce a single environment variable per UI (e.g. `VITE_BASE_PATH`) used for Vite `base`, router `basepath`, and auth redirect URIs.
3. **Introduce an edge gateway service (Docker)**
   - Add a Traefik service to `docker/docker-compose.yml` and route to existing UI containers and backend services via path prefixes.
4. **Consolidate API routing**
   - Move towards a single stable `/api/*` contract and migrate any non-`/api` UI calls (e.g. `/products`) to `/api/...` for consistency.
5. **Decide if/when an API gateway is needed**
   - If we need API-specific concerns (rate limits per client, JWT validation, quotas, schema routing), revisit option #5 (two-tier).

## References

- `docker/nginx-frontend.conf` and `docker/nginx-merchant-portal.conf` (current per-UI reverse-proxy rules)
- ADR-011: `docs/ADRs/011_spring_authorization_server.md`
- ADR-006: `docs/ADRs/006_frontend_monorepo_strategy.md`
