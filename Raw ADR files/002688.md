# ADR-001: Zero-Cost Architecture

Status: Accepted
Date: 2026-01-09
Owner: User
Related Features: All

---

## Context

The project requires a fully functional modpack creation platform with ZERO ongoing costs. This eliminates most traditional SaaS architectures that require paid databases, hosting, or APIs.

---

## Decision

Use a client-first architecture where all heavy processing happens in the browser, with minimal serverless functions only for API proxying.

Key points:

- Static site hosting on Netlify free tier (100GB bandwidth/month)
- Netlify Functions for CurseForge API proxy (125K invocations/month)
- Client-side ZIP generation with JSZip
- URL-based state sharing using lz-string compression
- Optional Turso database for future cloud saves (9GB free)

---

## Alternatives considered

### Vercel + Supabase

- Pros: Excellent DX, built-in auth
- Cons: Supabase requires credit card for some features, Vercel functions more limited
- Rejected because: Less generous free tiers

### Cloudflare Pages + D1

- Pros: Excellent performance, generous limits
- Cons: D1 is still beta, less React tooling
- Rejected because: Stability concerns

### Self-hosted

- Pros: Full control
- Cons: Requires server costs, maintenance
- Rejected because: Violates zero-cost requirement

---

## Consequences

### Positive

- Truly zero ongoing costs
- Fast client-side performance
- No vendor lock-in for core features
- Privacy-friendly (data stays in browser)

### Negative / risks

- Limited to 125K CurseForge API calls/month
- Mitigation: Aggressive caching, rate limiting
- URL sharing limited by URL length (~2000 chars)
- Mitigation: Cloud saves for large packs

---

## Impact

### Code

- All export logic in browser
- Netlify Functions for proxy only
- No traditional backend

### Data

- Primary: Browser localStorage + URL state
- Optional: Turso for authenticated users

---

## Verification

### Test environment

- Local: `netlify dev`
- CI: Netlify preview deploys

### Test commands

- build: `npm run build`
- test: `npm run test`
- dev: `netlify dev`
