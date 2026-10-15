# ADR-005: Railway as Primary Hosting Platform

## Status
**Accepted**

## Date
2025-01-XX

## Context

MyUglyRocks needs hosting for:
- **Frontend**: Next.js application (SSR + static)
- **Backend**: ASP.NET Core Web API
- **Database**: PostgreSQL
- **Cache**: Redis

### Requirements
1. **Simplicity**: Minimize operational complexity for a small team
2. **Cost-effective**: Reasonable pricing for hobby/startup scale
3. **Developer Experience**: Easy deployments, good logs, preview environments
4. **Flexibility**: Ability to scale or migrate if needed
5. **Next.js Support**: SSR, ISR, and App Router features

### Options Considered

#### Option A: Railway (Everything)
- Single platform for all services
- Built-in PostgreSQL and Redis
- Good Next.js support
- Simple pricing ($5/month hobby, usage-based pro)

#### Option B: Vercel (Frontend) + Railway (Backend + DB)
- Best Next.js experience on Vercel
- Split infrastructure across platforms
- More complex deployment pipeline
- Higher combined cost

#### Option C: Vercel (Everything)
- Vercel Postgres and KV for data
- Vercel Functions for backend
- Limited .NET support (would need to rewrite)

#### Option D: DigitalOcean App Platform
- Familiar platform
- Good container support
- Less specialized for Next.js or .NET

#### Option E: Self-hosted (VPS)
- Full control
- Lowest cost at scale
- Highest operational burden

## Decision

**Use Railway as the primary hosting platform for all services, with Vercel as a backup option for the frontend if needed.**

### Rationale

1. **Single Platform Simplicity**
   - One dashboard for frontend, backend, database, and Redis
   - Unified logs and monitoring
   - Single billing relationship
   - Easier onboarding for new team members

2. **Cost Efficiency**
   - Hobby plan: $5/month with generous limits
   - Usage-based Pro plan scales with actual usage
   - No surprise egress fees between services (internal networking)

3. **Good Next.js Support**
   - Railway supports Next.js with SSR
   - Automatic detection and configuration
   - While not Vercel-level optimized, sufficient for our needs

4. **Excellent .NET Support**
   - Railway handles ASP.NET Core well
   - Docker-based deployment if needed
   - Good documentation for .NET projects

5. **Vercel as Backup**
   - If Next.js performance becomes critical, frontend can move to Vercel
   - Backend stays on Railway (cross-origin is already handled)
   - No code changes needed, just deployment config

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         RAILWAY PROJECT                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐    ┌──────────────────┐                  │
│  │   myuglyrocks-   │    │   myuglyrocks-   │                  │
│  │       web        │────│       api        │                  │
│  │   (Next.js)      │    │   (ASP.NET)      │                  │
│  │                  │    │                  │                  │
│  │  Public Domain:  │    │  Public Domain:  │                  │
│  │  myuglyrocks.com │    │  api.myuglyrocks │                  │
│  └──────────────────┘    └────────┬─────────┘                  │
│                                   │                             │
│           ┌───────────────────────┼───────────────────────┐    │
│           │                       │                       │    │
│           ▼                       ▼                       │    │
│  ┌──────────────────┐    ┌──────────────────┐            │    │
│  │    PostgreSQL    │    │      Redis       │            │    │
│  │   (Railway DB)   │    │  (Railway or     │            │    │
│  │                  │    │   Upstash)       │            │    │
│  └──────────────────┘    └──────────────────┘            │    │
│                                                           │    │
└───────────────────────────────────────────────────────────┼────┘
                                                            │
                         ┌──────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │  Cloudflare R2   │
              │  (Image Storage) │
              └──────────────────┘
```

### Service Configuration

| Service | Railway Service | Domain |
|---------|----------------|--------|
| Frontend | `myuglyrocks-web` | `myuglyrocks.com` |
| Backend | `myuglyrocks-api` | `api.myuglyrocks.com` |
| Database | Railway PostgreSQL | Internal only |
| Cache | Railway Redis or Upstash | Internal only |

### Environment Strategy

| Environment | Railway Setup |
|-------------|---------------|
| Production | Main project, `main` branch |
| Staging | Separate project or PR environments |
| Development | Local (Docker Compose) |

## Consequences

### Positive

- **Operational Simplicity**: One platform to learn and manage
- **Cost Predictable**: Single bill, usage-based scaling
- **Fast Iteration**: Deploy both services together easily
- **Internal Networking**: Services communicate without public internet
- **Unified Logging**: All logs in one place

### Negative

- **Not Vercel-Optimized**: Some Next.js edge features may not work
- **Smaller Community**: Less Next.js-specific documentation than Vercel
- **Vendor Lock-in**: Railway-specific configuration (though easy to migrate)
- **No Edge Functions**: Limited edge computing compared to Vercel

### Migration Path to Vercel (if needed)

If we need Vercel's Next.js optimizations later:

1. **No Code Changes Required**
   - Next.js app is standard, works on any platform
   - API calls already use `NEXT_PUBLIC_API_URL` env var

2. **Deployment Steps**
   - Create Vercel project
   - Connect GitHub repo
   - Set environment variables
   - Update DNS for frontend domain

3. **Keep Backend on Railway**
   - Backend stays at `api.myuglyrocks.com`
   - Already configured for cross-origin requests
   - No backend changes needed

### When to Consider Vercel

Consider moving frontend to Vercel if:
- ISR/on-demand revalidation becomes critical
- Edge functions are needed for performance
- Vercel-specific features (Analytics, Speed Insights) are valuable
- Traffic patterns favor edge computing

## Cost Comparison

| Setup | MVP (100 users) | Growth (1K users) |
|-------|-----------------|-------------------|
| **Railway Only** | ~$10/month | ~$40/month |
| Vercel + Railway | ~$20/month | ~$70/month |
| Self-hosted VPS | ~$20/month | ~$40/month |

Railway-only provides the best cost efficiency at MVP scale.

## Related Decisions
- [ADR-001-database.md](./ADR-001-database.md) - PostgreSQL on Railway
- [ADR-004-frontend-framework.md](./ADR-004-frontend-framework.md) - Next.js framework choice

## References
- [Railway Documentation](https://docs.railway.app/)
- [Railway Next.js Guide](https://docs.railway.app/guides/nextjs)
- [Railway Pricing](https://railway.app/pricing)
