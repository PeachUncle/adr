# ADR-002: Caddy Reverse Proxy

## Status

Accepted

## Context

The CID Stack standard specifies NGINX as the reverse proxy. However, OneShot is designed for single-tenant self-hosted deployments where ease of setup is prioritized over advanced configuration options.

NGINX requires:
- Manual TLS certificate management or separate certbot setup
- Complex configuration syntax for common tasks
- Additional container for certificate renewal

Caddy provides:
- Automatic HTTPS with Let's Encrypt
- Simple Caddyfile syntax
- Built-in certificate management
- No additional containers needed

## Decision

OneShot will use Caddy as the default reverse proxy for deployments requiring TLS. NGINX remains an option for users with existing NGINX infrastructure.

## Evaluation Against CID Stack Criteria

### Required Criteria (All Pass)

| Criterion | Status | Notes |
|-----------|--------|-------|
| Open source license | ✅ | Apache 2.0 |
| Active maintenance | ✅ | Weekly releases |
| No unpatched critical CVEs | ✅ | Clean security record |
| Proven scale | ✅ | Used by Cloudflare, DigitalOcean |
| TypeScript support | N/A | Infrastructure, not code |
| Complete documentation | ✅ | Excellent docs at caddyserver.com |

### Weighted Criteria

| Criterion | Weight | Score | Notes |
|-----------|--------|-------|-------|
| Integration | High | 5 | Drop-in replacement for NGINX |
| Simplicity | High | 5 | Automatic HTTPS, simple config |
| Community | Medium | 4 | Active community, responsive maintainers |
| Longevity | Medium | 4 | V2 stable since 2020 |
| Performance | Medium | 4 | Comparable to NGINX for our scale |

**Total Score: 22/25**

## Rationale

For OneShot's target use case (single-tenant, self-hosted, under 30-minute installation), Caddy's automatic HTTPS and simple configuration outweigh NGINX's advanced features.

Key benefits:
1. **Zero-touch HTTPS**: Automatic certificate provisioning and renewal
2. **Simpler configuration**: 5-line Caddyfile vs 50+ line nginx.conf
3. **Faster setup**: No certbot container, no cron jobs
4. **Lower maintenance**: Certificates renew automatically

## Consequences

**Positive:**
- Faster installation (under 30 minutes, meeting persona requirement)
- Lower maintenance burden
- Automatic HTTPS without configuration
- Simpler troubleshooting

**Negative:**
- Deviates from CID Stack standard
- Less familiar to some operators
- Fewer advanced features than NGINX

**Mitigation:**
- NGINX configuration can be documented as alternative
- Docker Compose supports profile switching

## Alternatives Considered

### NGINX with Certbot
Standard CID Stack approach. Rejected for complexity in self-hosted scenario.

### Traefik
Powerful, but more complex than needed for single-tenant. Overkill for v1.

### No Reverse Proxy
Direct exposure of Node.js. Rejected for security and TLS requirements.

## Task Classification (CID)

- **Decision Type**: Human-Sovereign (infrastructure choice)
- **Novelty**: 2 - Caddy is well-established
- **Risk**: 1 - Low risk, easy to swap if needed
- **Future AI Delegation**: N/A for infrastructure decisions

---

*Decision Date: 2026-01-05*
*Decision Maker: Thomas (Product Owner)*
