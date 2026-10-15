# ADR-0001: Subdomain Routing for Interactive Demos

- Status: Proposed
- Date: 2025-11-22
- Related: Spike in `ai/anchors.json` (technicalSpikes), `docs/phase-1-initiation-&-planning/1.2.txt`
- Anchors: `ai/anchors.json`
- Persona/KPI focus: manager (architecture clarity), client (fast credibility); KPI: LCP < 1500ms, demo_error_rate < 1%

## Context

Interactive demos (e.g., CLI-style terminals) must be hosted on isolated subdomains (e.g., `demo-foo.russellbomer.com`) for clarity and failure containment. MVP deploys on a DigitalOcean VPS and should remain portable to a future Hetzner migration. High availability and auto-scaling are not required for MVP.

## Options Considered

1. Nginx reverse proxy + wildcard DNS (\*.russellbomer.com)
   - Pros: Familiar, efficient, fine-grained routing, TLS via certbot.
   - Cons: Extra config management; manual reloads; less dynamic if routing changes often.
2. Traefik or Caddy as dynamic reverse proxy
   - Pros: Auto TLS, dynamic config via labels; easier local-to-prod parity.
   - Cons: New dependency; learning curve; container-first workflows.
3. Next.js middleware with host-based routing only
   - Pros: Minimal moving parts; code-centric.
   - Cons: Still requires wildcard DNS/TLS termination at the edge; less flexibility for non-Next services.
4. Managed DNS + light Nginx + per-demo ports
   - Pros: Simple and explicit mapping per demo.
   - Cons: Port management overhead; scale pain; brittle.

## Decision (Proposed)

Adopt Nginx reverse proxy with wildcard DNS and per-subdomain routing to the Next.js app (or future demo services) behind it. Terminate TLS at Nginx (Let’s Encrypt certbot). Use host headers to route to a single Next.js instance for MVP.

Rationale:

- Low operational overhead for MVP on a single VPS.
- Clear portability to Hetzner by reapplying Nginx + certbot.
- Keeps Next.js app simple while enabling future split of demo services.

## Consequences

- Nginx configuration and cert management scripts are required.
- Subdomain demo routing is centralized; changes require Nginx reload.
- If future demos require separate processes, we can extend upstreams.

## Spike Exit Criteria

- Wildcard DNS (e.g., `*.russellbomer.com`) resolves to VPS.
- Nginx serves valid TLS certificates for wildcard domain.
- Request to `demo-foo.russellbomer.com` reaches Next.js app and renders a demo page.
- Basic error boundary confirmed; demo error does not crash overall site.
- Metrics collected for LCP and demo_error_rate via Web Vitals stub.

## Implementation Notes

- Provision Nginx and certbot on DO VPS.
- Add host-based server block with upstream to Next.js (`localhost:3000`).
- Add demo route detection in Next.js (read `Host` header, map to demo content).
- Maintain routing portability: config files and scripts stored under `deploy/`.
- Document Nginx config and renewal steps in `README.md` at deployment time.
