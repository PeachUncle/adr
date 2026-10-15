# ADR-008: Deployment Strategy

## Status

Accepted

## Context

We need to deploy:

- **Backend API** (NestJS + PostgreSQL)
- **Frontend SPA** (Vue 3)
- **Database** (PostgreSQL)

Requirements:

- Simple deployment for solo developer
- Low cost for MVP phase (~$5-10/month acceptable)
- Easy to maintain and monitor
- Room to scale if project grows
- Automated deploys from GitHub

## Decision Drivers

- **Developer experience**: Minimal DevOps complexity
- **Cost**: Budget-conscious but not free-only
- **Deployment speed**: Fast, automated deployments
- **Monitoring**: Basic observability built-in
- **Database**: Managed PostgreSQL included
- **Scalability**: Can scale if project succeeds

## Options Considered

### Option A: Railway (Backend) + Cloudflare Pages (Frontend)

**Railway for Backend:**

**Pros:**

- ✅ **Dead simple** - connect GitHub repo, auto-deploy
- ✅ **Managed PostgreSQL** - included, automatic backups
- ✅ **Environment variables** - easy config management
- ✅ **Logs & monitoring** - built-in
- ✅ **Reasonable pricing** - $5/month hobby, $20/month pro
- ✅ **Scales easily** - vertical + horizontal scaling
- ✅ **Zero config** - detects NestJS automatically

**Cons:**

- ⚠️ **Cost can grow** - usage-based billing
- ⚠️ **Less control** - PaaS abstraction

**Cloudflare Pages for Frontend:**

**Pros:**

- ✅ **Free forever** - no cost for static sites
- ✅ **Lightning fast** - global CDN
- ✅ **Auto-deploy** - push to GitHub = deploy
- ✅ **Custom domains** - free SSL
- ✅ **Edge network** - low latency worldwide

**Cons:**

- ⚠️ **Static only** - but perfect for Vue SPA

**Total Cost: ~$5-10/month**

### Option B: AWS (Fargate + RDS + S3 + CloudFront)

**Pros:**

- ✅ **Enterprise-grade** - full control
- ✅ **Scalable** - can handle massive growth
- ✅ **Resume value** - AWS experience

**Cons:**

- ❌ **Complex setup** - VPC, security groups, ECS tasks, load balancers
- ❌ **Time-consuming** - days to set up properly
- ❌ **Higher cost** - $30-50/month minimum
- ❌ **Monitoring complexity** - need to set up CloudWatch
- ❌ **Overkill** - way too complex for MVP

### Option C: Vercel (Full Stack)

**Pros:**

- ✅ **All-in-one** - frontend + serverless backend
- ✅ **Great DX** - excellent dashboard

**Cons:**

- ❌ **Not designed for NestJS** - serverless functions, not long-running apps
- ❌ **Database external** - need Supabase/PlanetScale/Neon
- ❌ **Serverless doesn't fit** - NestJS is designed for long-running processes
- ❌ **Cost scaling** - expensive at scale

### Option D: [Fly.io](http://Fly.io) + Cloudflare Pages

**Pros:**

- ✅ **Good pricing** - free tier + reasonable costs
- ✅ **Managed PostgreSQL** - available
- ✅ **Global edge** - deploy to multiple regions

**Cons:**

- ⚠️ **More config** - Fly.toml, Dockerfile required
- ⚠️ **Learning curve** - less intuitive than Railway

## Decision

**We will use Railway for the backend + Cloudflare Pages for the frontend.**

### Deployment Architecture

```
┌───────────────────────┐
│  Cloudflare Pages       │
│  (Vue 3 SPA)           │
│  - Auto-deploy on push │
│  - Global CDN          │
│  - Free                │
└───────────────────────┘
         │
         │ HTTPS requests
         │
         ↓
┌───────────────────────┐
│  Railway               │
│  ┌──────────────────┐ │
│  │ NestJS API       │ │
│  │ - Auto-deploy    │ │
│  │ - Env vars       │ │
│  │ - Logs           │ │
│  └──────────────────┘ │
│         │              │
│         ↓              │
│  ┌──────────────────┐ │
│  │ PostgreSQL       │ │
│  │ - Managed        │ │
│  │ - Auto backups   │ │
│  └──────────────────┘ │
└───────────────────────┘
```

### Background Jobs & Async Work

**Phase 1:**

- Use Railway's built-in cron for scheduled tasks
- Use BullMQ (NestJS queue) for background jobs
- Redis on Railway (if needed for BullMQ)

**Phase 2+ (if needed):**

- Offload heavy tasks to serverless functions (AWS Lambda, Cloudflare Workers)
- Keep simple async in NestJS BullMQ queue

### Rationale

1. **Railway is the fastest path to production** for NestJS + PostgreSQL
2. **Cloudflare Pages is free and fast** for static Vue SPA
3. **Minimal DevOps** - focus on building features, not infrastructure
4. **Cost-effective** - $5-10/month is sustainable for MVP
5. **Can migrate later** - if project grows, can move to AWS/GCP

## Consequences

### Positive

- Deploy backend in minutes, not hours/days
- Automated deployments from GitHub
- Managed database with automatic backups
- Built-in monitoring and logs
- Free CDN for frontend (Cloudflare)
- Low cost for MVP phase
- Simple environment variable management
- Can scale vertically easily (upgrade Railway plan)

### Negative

- Less control than AWS (PaaS abstraction)
- Cost can increase with usage (but predictable)
- Vendor lock-in to Railway (but can migrate if needed)

### Risks

- **Railway pricing changes**: Could get more expensive
  - _Mitigation_: Monitor usage, can migrate to [Fly.io](http://Fly.io) or AWS if needed
- **Outages**: Dependent on Railway uptime
  - _Mitigation_: Railway has good SLA; can move to AWS later if business-critical

## Follow-up Actions

- [ ] Create Railway account and project
- [ ] Add PostgreSQL addon in Railway
- [ ] Connect GitHub repo to Railway
- [ ] Configure environment variables in Railway
- [ ] Set up custom domain for API (if needed)
- [ ] Create Cloudflare Pages project
- [ ] Connect frontend repo to Cloudflare Pages
- [ ] Configure build command: `pnpm build`
- [ ] Set up API URL environment variable in Cloudflare
- [ ] Test deployment pipeline
- [ ] Document deployment process in README
