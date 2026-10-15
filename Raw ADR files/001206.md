# ADR-014: Budget and Licensing Constraints

**Status**: Proposed (Needs Owner Input)  
**Date**: 2025-12-27  
**Deciders**: James (Owner)  
**Technical Story**: Infrastructure cost management

## Context and Problem Statement

The Stack Compatibility research identified "budget sensitivity" as UNKNOWN. This ADR documents cost estimates and requests owner input on acceptable spend levels.

## Estimated Monthly Costs (MVP)

| Service | Free Tier | Paid Estimate |
|---------|-----------|---------------|
| **Vercel** (Frontend) | 100GB bandwidth | $20/mo Pro |
| **Railway** (Backend + DB) | $5 credit | $20-35/mo |
| **Auth0** | 7,500 MAU | $240/mo Essentials |
| **GitHub Actions** | 2,000 min/mo | $0 (free tier sufficient) |
| **Domain** | N/A | $12/year |
| **Total MVP** | ~$5/mo | ~$280-300/mo |

## Cost Scenarios

### Scenario A: Minimum Viable ($5-35/month)
- Vercel free tier
- Railway free tier + $5 credit
- Auth0 free tier (7,500 MAU)
- Custom JWT if exceeds free tier

### Scenario B: Standard MVP ($100-150/month)
- Vercel Pro ($20)
- Railway Hobby ($20)
- Auth0 Essentials (skip, use Keycloak)
- Keycloak on Railway ($0 - self-hosted)

### Scenario C: Full Featured ($250-350/month)
- Vercel Pro ($20)
- Railway Team ($50)
- Auth0 Essentials ($240)
- Monitoring add-ons

## Decision Required

**Question for Owner**: What is the acceptable monthly infrastructure spend?

- [ ] A: Minimize cost (<$50/month) - Use free tiers, Keycloak
- [ ] B: Balanced ($100-150/month) - Paid hosting, self-hosted auth
- [ ] C: Full featured ($250-350/month) - All managed services

## Licensing Status

| Dependency | License | Risk |
|------------|---------|------|
| React | MIT | ✅ None |
| FastAPI | MIT | ✅ None |
| PostgreSQL | PostgreSQL License | ✅ None |
| Keycloak | Apache 2.0 | ✅ None |
| Auth0 | Proprietary (SaaS) | ⚠️ Vendor lock-in |
| shadcn/ui | MIT | ✅ None |

**All open-source dependencies are permissively licensed. No licensing constraints identified.**

## Recommendation

If budget is constrained, use **Scenario B** with Keycloak instead of Auth0. Total: ~$100/month with full enterprise features.

## Links

* [Vercel Pricing](https://vercel.com/pricing)
* [Railway Pricing](https://railway.app/pricing)
* [Auth0 Pricing](https://auth0.com/pricing)
