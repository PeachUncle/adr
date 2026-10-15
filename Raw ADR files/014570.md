---
title: "ADR-0002: Tech Stack and Architecture"
description: "Decision to use specific technologies for the startup landing page"
date: 2025-08-23
tags: ["tech stack", "architecture", "startup", "decisions"]
weight: 2
---



## Status

Accepted

## Date

2025-08-23

## Context

We need to establish the technology stack and architecture for our startup landing page. The requirements include:

- Fast development and deployment
- Cost-effective hosting (initially free tier)
- Scalable architecture for future growth
- Modern development experience
- SEO-friendly frontend
- Reliable backend API
- Robust database solution

## Decision

We have decided on the following tech stack:

### Frontend: Next.js on Vercel
- **Technology**: Next.js (React framework)
- **Hosting**: Vercel
- **Tier**: Free tier initially

### Backend: Go API on Render.com
- **Technology**: Go (Golang)
- **Hosting**: Render.com
- **Tier**: Free tier initially

### Database: Supabase
- **Technology**: PostgreSQL via Supabase
- **Hosting**: Supabase cloud
- **Tier**: Free tier initially

## Rationale

### Next.js on Vercel

**Advantages:**
- **Performance**: Built-in optimizations (Image optimization, automatic code splitting, SSR/SSG)
- **SEO**: Server-side rendering and static site generation capabilities
- **Developer Experience**: Hot reloading, TypeScript support, excellent debugging tools
- **Deployment**: Seamless integration with Vercel for zero-config deployments
- **Cost**: Generous free tier (100GB bandwidth, unlimited personal projects)
- **Scalability**: Automatic scaling with edge functions and CDN

**Free Tier Limits:**
- 100GB bandwidth per month
- 1000 serverless function invocations per day
- 100 GB-hours of serverless function execution time

### Go API on Render.com

**Advantages:**
- **Performance**: Go's excellent performance and low memory footprint
- **Simplicity**: Simple deployment model, single binary distribution
- **Concurrency**: Built-in goroutines for handling concurrent requests
- **Type Safety**: Strong typing system reduces runtime errors
- **Standard Library**: Comprehensive standard library reduces external dependencies
- **Cost**: Free tier available with automatic sleep after inactivity

**Free Tier Limits:**
- 512MB RAM
- 0.1 CPU
- Automatic sleep after 15 minutes of inactivity
- 750 hours per month of runtime

### Supabase Database

**Advantages:**
- **Technology**: PostgreSQL - battle-tested, ACID compliant, feature-rich
- **Real-time**: Built-in real-time subscriptions
- **Authentication**: Integrated auth system with multiple providers
- **API**: Auto-generated REST and GraphQL APIs
- **Dashboard**: User-friendly database management interface
- **Migrations**: Built-in database migration system
- **Cost**: Generous free tier with 500MB database storage

**Free Tier Limits:**
- Up to 500MB database space
- Up to 2GB bandwidth per month
- Up to 50,000 monthly active users
- 7 days of log retention

## Architecture Overview

```
[User Browser] 
    ↓ (HTTPS)
[Vercel CDN/Edge] 
    ↓ (Static Assets + SSR)
[Next.js Application]
    ↓ (API Calls)
[Render.com Go API]
    ↓ (Database Queries)
[Supabase PostgreSQL]
```

## Implementation Plan

1. **Phase 1**: Set up Next.js frontend with basic landing page
2. **Phase 2**: Deploy Go API with basic endpoints on Render.com
3. **Phase 3**: Set up Supabase database with initial schema
4. **Phase 4**: Integrate all components and implement core features
5. **Phase 5**: Optimize for production and monitor usage

## Migration Strategy

When free tier limits are exceeded:

### Vercel
- Upgrade to Pro plan ($20/month) for increased bandwidth and build minutes
- Consider Vercel Enterprise for high-traffic scenarios

### Render.com
- Upgrade to Starter plan ($7/month) for always-on service
- Scale to higher tiers as traffic grows

### Supabase
- Upgrade to Pro plan ($25/month) for increased storage and bandwidth
- Consider dedicated instances for high-performance requirements

## Alternative Considerations

### Alternatives Considered and Rejected

1. **Frontend Alternatives**:
   - Create React App: Less optimized, requires additional configuration
   - Gatsby: Overkill for simple landing page, static-first approach
   - Vue.js/Nuxt.js: Smaller ecosystem, less familiar to team

2. **Backend Alternatives**:
   - Node.js: Higher memory usage, callback complexity
   - Python/Django: Heavier runtime, slower cold starts
   - Serverless Functions: Vendor lock-in, cold start latency

3. **Database Alternatives**:
   - Firebase: NoSQL limitations, Google vendor lock-in
   - PlanetScale: MySQL-based, more complex branching model
   - Railway PostgreSQL: Less mature platform, fewer features

## Consequences

### Positive
- Rapid development and deployment cycle
- Zero infrastructure management initially
- Modern, scalable technology stack
- Cost-effective for startup phase
- Strong community support for all technologies
- Clear upgrade path as we scale

### Negative
- Potential vendor lock-in (mitigated by using standard technologies)
- Free tier limitations may require upgrades sooner than expected
- Cold start latency on Render.com free tier
- Multiple vendor relationships to manage

### Risks and Mitigation

1. **Free Tier Exhaustion**
   - Risk: Unexpected traffic spikes
   - Mitigation: Monitor usage closely, set up alerts

2. **Vendor Lock-in**
   - Risk: Difficulty migrating away from platforms
   - Mitigation: Use standard technologies, containerize applications

3. **Performance Issues**
   - Risk: Cold starts and free tier limitations
   - Mitigation: Plan upgrade path, implement caching strategies

## Success Metrics

- Page load times < 2 seconds
- API response times < 500ms
- 99.9% uptime
- Successful handling of traffic spikes
- Cost remains under $100/month for first 6 months

## Review Date

This decision will be reviewed in 3 months (November 2025) or when traffic exceeds free tier limitations, whichever comes first.
