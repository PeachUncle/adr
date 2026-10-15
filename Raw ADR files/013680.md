# ADR-0002: nginx Reverse Proxy

**Status:** Accepted  
**Date:** 2026-01-XX  
**Context:** Backend POC-3 - Infrastructure Reverse Proxy Selection  
**Decision Makers:** Backend Team

---

## Context

We need to choose a reverse proxy for POC-3 to handle load balancing, SSL/TLS termination, request routing, and infrastructure-level security. The reverse proxy will sit in front of the API Gateway and handle all incoming requests. This decision affects performance, security, operational complexity, and scalability.

**Requirements:**

- Reverse proxy functionality
- Load balancing across service instances
- SSL/TLS termination
- Rate limiting at infrastructure level
- Request routing and path rewriting
- High performance
- Production-ready
- Flexible configuration
- Active maintenance

---

## Decision

We will use **nginx** as the reverse proxy for POC-3.

**Rationale:**

- **Industry Standard** - Most popular reverse proxy, used by major companies
- **High Performance** - Handles high traffic loads efficiently
- **Excellent SSL/TLS Support** - Comprehensive SSL/TLS features
- **Load Balancing** - Multiple algorithms (round-robin, least-conn, ip-hash)
- **Flexible Configuration** - Powerful configuration language
- **Production-Ready** - Battle-tested, used in production at scale
- **Feature-Rich** - Compression, caching, rate limiting, security headers
- **Active Maintenance** - Regularly updated, active development

---

## Alternatives Considered

### 1. Traefik

**Pros:**
- Modern, cloud-native
- Automatic SSL certificate management (Let's Encrypt)
- Service discovery integration
- Docker/Kubernetes native
- Good documentation

**Cons:**
- Less mature than nginx
- Smaller ecosystem
- Less control over configuration
- May be overkill for POC-3 needs

**Decision:** Not chosen - nginx's maturity and ecosystem outweigh Traefik's modern features for POC-3.

---

### 2. HAProxy

**Pros:**
- High performance
- Excellent load balancing
- Production-ready
- Good for TCP/HTTP load balancing

**Cons:**
- Less feature-rich than nginx
- More complex configuration
- Less commonly used for reverse proxy
- Smaller ecosystem

**Decision:** Not chosen - nginx provides better feature set and ecosystem.

---

### 3. AWS Application Load Balancer (ALB)

**Pros:**
- Managed service (no infrastructure to manage)
- Automatic scaling
- Integrated with AWS services
- Pay-as-you-go

**Cons:**
- Vendor lock-in (AWS only)
- Additional cost
- Less control over configuration
- May not be suitable for on-premise deployment

**Decision:** Not chosen - Vendor lock-in and cost concerns. nginx provides more control and flexibility.

---

### 4. nginx (Chosen)

**Pros:**
- Industry standard
- High performance
- Excellent SSL/TLS support
- Load balancing
- Flexible configuration
- Production-ready
- Feature-rich
- Large ecosystem

**Cons:**
- Configuration can be complex
- Requires manual SSL certificate management (in POC-3)

**Decision:** Chosen - Best balance of features, performance, and production-readiness for POC-3.

---

## Trade-offs

### Pros

- ✅ **Industry Standard** - Most popular, large ecosystem
- ✅ **High Performance** - Handles high traffic loads
- ✅ **Excellent SSL/TLS** - Comprehensive SSL/TLS features
- ✅ **Load Balancing** - Multiple algorithms
- ✅ **Feature-Rich** - Compression, caching, rate limiting
- ✅ **Production-Ready** - Battle-tested at scale
- ✅ **Flexible Configuration** - Powerful configuration language

### Cons

- ⚠️ **Configuration Complexity** - Configuration can be complex
- ⚠️ **Manual SSL Management** - Need to manage SSL certificates (in POC-3)

---

## Consequences

### Positive

- ✅ **Performance** - High performance, handles high traffic
- ✅ **Reliability** - Battle-tested, production-ready
- ✅ **Flexibility** - Powerful configuration options
- ✅ **Security** - Infrastructure-level security (rate limiting, SSL/TLS)
- ✅ **Scalability** - Load balancing across service instances

### Negative

- ⚠️ **Configuration Complexity** - Need to learn nginx configuration
- ⚠️ **Operational Overhead** - Need to manage nginx configuration

### Neutral

- 🔄 **SSL Certificate Management** - Manual in POC-3 (self-signed), can automate in MVP
- 🔄 **Performance** - Performance is excellent for POC-3 needs

---

## Implementation Notes

- Use nginx latest stable version
- Configure reverse proxy for API Gateway
- Setup load balancing (least-conn algorithm)
- Configure SSL/TLS (self-signed certificates in POC-3)
- Setup rate limiting
- Configure compression (gzip, brotli)
- Add security headers
- Configure caching headers

**Example Configuration:**

```nginx
# nginx/nginx.conf
upstream api_gateway {
    least_conn;
    server api-gateway-1:3000;
    server api-gateway-2:3000;
    keepalive 32;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    # SSL Configuration (self-signed in POC-3)
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;
    limit_req zone=api_limit burst=20 nodelay;

    location /api/ {
        proxy_pass http://api_gateway;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Migration Path

### POC-2 → POC-3

- Add nginx in front of API Gateway
- Configure reverse proxy
- Setup SSL/TLS (self-signed certificates)
- Configure load balancing
- Add rate limiting

### POC-3 → MVP

- Replace self-signed certificates with real certificates
- Automate SSL certificate management (Let's Encrypt)
- Add advanced caching
- Add CDN integration

---

## Related Decisions

- **ADR-0001 (POC-2): Use Express Framework** - nginx sits in front of Express API Gateway
- Frontend nginx ADR (independent but related)

---

## References

- [nginx Official Documentation](https://nginx.org/en/docs/)
- `docs/adr/poc-3/0001-nginx-reverse-proxy.md` - Frontend nginx ADR (for reference)
- `docs/backend-poc3-architecture.md` - POC-3 architecture documentation
- `docs/backend-poc3-tech-stack.md` - POC-3 tech stack documentation
- `docs/security-strategy-banking.md` - Security strategy (includes nginx security)

---

**Last Updated:** 2026-01-XX

