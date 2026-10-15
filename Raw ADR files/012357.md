# ADR 0001 — Serverless Proxy for NewsAPI

**Status**: Proposed
**Date**: 2025-12-15
**Context**
The frontend (React+Vite) needs to query NewsAPI while avoiding exposing the NewsAPI key in public builds. The MVP uses the free tier and issues a single request per user-selected topic; however, keys embedded in client bundles are discoverable and risk quota abuse.

**Decision**
Introduce a simple serverless proxy (Vercel Functions / Netlify Functions / Cloudflare Workers) as the recommended production integration point. The proxy hides the NewsAPI key, implements shared caching and basic rate-limit guards, and exposes a small, documented contract to the frontend.

**Consequences**
- Pros:
  - API key not exposed in client bundles.
  - Shared cache reduces overall NewsAPI requests and smooths bursty usage.
  - Centralized place to monitor errors and apply backoff/alerts.
- Cons:
  - Adds a tiny server component to the deployment surface and operational overhead.

**Proxy Contract (API)**
- Endpoint: `POST /.netlify/functions/news` or `/api/news` (Vercel)
- Request JSON:
  - `topics`: string[] (max 8)
  - `country`: optional ISO2 string
  - `pageSize`: optional number (default 10)
- Response JSON:
  - `articles`: Article[] (merged, deduplicated by `url`)
  - `source`: string ("cache" | "newsapi")
  - `cachedAt`: ISO timestamp when cache entry was produced

**Caching & TTL**
- In-proxy cache TTL: 15 minutes (configurable). Short TTL reduces staleness while lowering calls.
- Frontend local cache (IndexedDB): retain articles for 24 hours for offline experience and fallback when proxy indicates rate-limited.

**Rate-Limit & Backoff**
- Proxy should detect NewsAPI quota errors (HTTP 429) and return a 503 with `x-proxy-rate-limited: 1` header and a JSON payload explaining the fallback.
- Proxy implements exponential backoff to NewsAPI on repeated 429s and increases cache TTL temporarily to reduce calls.

**Security**
- Store the NewsAPI key as an environment variable in hosting provider secrets (do not check into source control).
- Validate request payload size and topics to avoid abuse.
- Consider optional lightweight authentication (signed deploy token) for production if public growth is expected.

**Monitoring & Observability**
- Emit metrics for: requests, cache hit/miss, 429s, latency, and errors.
- Integrate with provider logs and alerts (email/Slack) when 429 rates exceed threshold.

**Implementation Notes (illustrative)**
- Vercel function: accept `topics` + `country`, build the NewsAPI query for each topic or call NewsAPI `top-headlines` with multiple queries aggregated, dedupe by `url`, cache result in in-memory/Redis provider and return.
- Keep proxy logic thin: validation → cache lookup → call NewsAPI (if miss) → merge/dedupe → store cache → respond.

**Open Questions**
- Do we want server-side paging and sorting, or return a simple merged set and let the client rank?
- Which hosting provider and cache store do we prefer (Vercel + in-memory or Redis on managed DB)?

**Decision Rationale**
The proxy reduces the chance of key leakage and enables shared caching to keep us within free-tier quotas more efficiently. For a small team the added overhead is minimal and provides operational control.
