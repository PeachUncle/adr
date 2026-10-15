# ADR-004: Deployment Strategy

**Status**: Accepted
**Date**: 2025-10-22
**Decision Makers**: System Architecture Designer
**Context**: Multi-tier deployment strategy for frontend, backend, and infrastructure

## Context and Problem Statement

Love Rank Pulse requires a production deployment strategy that provides:
- High availability and reliability
- Cost-effective infrastructure
- Easy rollback capabilities
- Environment isolation (dev, staging, production)
- Automated deployments
- Scalability for growing user base

## Decision Drivers

- **Availability**: Minimize downtime during deployments
- **Cost**: Optimize infrastructure spending
- **Developer Experience**: Simple deployment workflow
- **Scalability**: Handle traffic growth
- **Security**: Protect sensitive data and credentials
- **Monitoring**: Visibility into application health

## Considered Options

### Option 1: Multi-Platform Strategy ✅ SELECTED

**Architecture:**
```
Frontend (Vercel) → API Gateway (Railway/Render) → Database (Supabase/Neon)
                                                  ↓
                                            Redis (Upstash)
```

**Components:**
- **Frontend**: Vercel (React SPA)
- **Backend**: Railway or Render (Express API)
- **Database**: Supabase or Neon PostgreSQL
- **Cache**: Upstash Redis
- **Monitoring**: Vercel Analytics + Backend logging

**Pros:**
- Leverages platform-specific strengths
- Vercel excels at static frontend hosting
- Railway/Render specialize in backend services
- Managed database reduces operational burden
- Built-in SSL certificates and CDN
- Cost-effective free tiers for development

**Cons:**
- Multiple platforms to manage
- Cross-platform monitoring complexity
- Potential vendor lock-in

### Option 2: Single Cloud Provider (AWS/GCP/Azure)

**Architecture:**
```
CloudFront/CDN → S3 (static) → ECS/Cloud Run → RDS/Cloud SQL
                                              ↓
                                         ElastiCache/Memorystore
```

**Pros:**
- Unified platform management
- Advanced configuration options
- Comprehensive monitoring tools

**Cons:**
- Higher infrastructure costs
- Steeper learning curve
- Manual configuration overhead
- Overkill for current scale

### Option 3: Self-Hosted Infrastructure (DigitalOcean/Linode)

**Architecture:**
```
Nginx → Docker Containers → PostgreSQL
                          ↓
                        Redis
```

**Pros:**
- Full control over infrastructure
- Predictable monthly costs
- No vendor lock-in

**Cons:**
- Manual DevOps overhead
- Requires security expertise
- No automatic scaling
- Single point of failure without clustering

## Decision Outcome

**Chosen Option**: Multi-Platform Strategy (Vercel + Railway + Supabase)

### Justification

The multi-platform approach optimizes for:

1. **Developer Productivity**: Git-based deployments, zero configuration
2. **Cost Efficiency**: Free tiers cover development, affordable production
3. **Reliability**: Platform-managed infrastructure with 99.9% SLAs
4. **Scalability**: Automatic scaling on Vercel, easy scaling on Railway
5. **Security**: Built-in SSL, DDoS protection, secret management

### Implementation Details

#### Frontend Deployment (Vercel)

**Configuration** (`vercel.json`):
```json
{
  "version": 2,
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "routes": [
    { "src": "/(.*)", "dest": "/index.html" }
  ],
  "env": {
    "VITE_API_URL": "https://api.loverankpulse.com",
    "VITE_ENABLE_REAL_TIME_UPDATES": "true"
  }
}
```

**Deployment Workflow:**
```bash
# Automatic deployment on git push
git push origin main → Vercel Build → Deploy to Production

# Manual deployment
vercel --prod
```

**Features:**
- Automatic SSL certificates
- Global CDN (300+ edge locations)
- Preview deployments for PRs
- Rollback to previous deployments
- Built-in analytics

**Estimated Cost:**
- Hobby Plan: $0/month (100GB bandwidth, 100 builds/day)
- Pro Plan: $20/month (1TB bandwidth, unlimited builds)

#### Backend Deployment (Railway)

**Configuration** (`railway.json`):
```json
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "npm run build"
  },
  "deploy": {
    "startCommand": "npm run start",
    "healthcheckPath": "/api/health",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

**Environment Variables:**
```bash
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
JWT_SECRET=${crypto.randomBytes(32).toString('hex')}
NODE_ENV=production
PORT=3000
```

**Deployment Workflow:**
```bash
# Automatic deployment
git push origin main → Railway Build → Deploy

# Railway CLI
railway up
```

**Features:**
- Automatic scaling (0-100 instances)
- Zero-downtime deployments
- Built-in metrics and logs
- Vertical scaling (RAM/CPU)
- Custom domains with SSL

**Estimated Cost:**
- Developer Plan: $5/month (512MB RAM, 1GB disk)
- Team Plan: $20/month (8GB RAM, 100GB disk)

#### Database (Supabase PostgreSQL)

**Configuration:**
```typescript
// /src/lib/prisma.ts
const prisma = new PrismaClient({
  datasources: {
    db: {
      url: process.env.DATABASE_URL,
    },
  },
});
```

**Connection String:**
```
postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres
```

**Features:**
- Managed PostgreSQL (version 15+)
- Automatic backups (daily)
- Point-in-time recovery
- Connection pooling (PgBouncer)
- Read replicas (Pro tier)

**Estimated Cost:**
- Free Tier: $0/month (500MB database, 2GB bandwidth)
- Pro Tier: $25/month (8GB database, 50GB bandwidth)

#### Cache (Upstash Redis)

**Configuration:**
```typescript
// /src/lib/redis.ts
const redis = new Redis({
  url: process.env.REDIS_URL,
  token: process.env.REDIS_TOKEN,
});
```

**Features:**
- Serverless Redis (pay-per-request)
- Global replication
- REST API fallback
- Durable storage

**Estimated Cost:**
- Free Tier: $0/month (10,000 commands/day)
- Pay-as-you-go: $0.2 per 100k commands

### Deployment Environments

#### Development
```
Frontend: localhost:5173 (Vite dev server)
Backend: localhost:3000 (Express)
Database: Local PostgreSQL (Docker)
Redis: Local Redis (Docker)
```

#### Staging
```
Frontend: staging-loverankpulse.vercel.app
Backend: staging-api.loverankpulse.com (Railway preview)
Database: Supabase staging project
Redis: Upstash staging database
```

#### Production
```
Frontend: loverankpulse.com (Vercel custom domain)
Backend: api.loverankpulse.com (Railway custom domain)
Database: Supabase production project
Redis: Upstash production database
```

### CI/CD Pipeline

**GitHub Actions** (`.github/workflows/deploy.yml`):
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm install
      - run: npm run test
      - run: npm run lint

  deploy-frontend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}

  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: bervProject/railway-deploy@v1
        with:
          railway-token: ${{ secrets.RAILWAY_TOKEN }}
          service: api
```

### Rollback Strategy

**Vercel Rollback:**
```bash
# List deployments
vercel ls

# Rollback to previous
vercel rollback [deployment-url]
```

**Railway Rollback:**
```bash
# View deployments
railway status

# Rollback to previous
railway rollback
```

**Database Migration Rollback:**
```bash
# Prisma migration rollback
prisma migrate resolve --rolled-back [migration-name]
```

### Monitoring and Alerting

**Frontend (Vercel):**
- Web Vitals (LCP, FID, CLS)
- Error tracking (Sentry integration)
- Analytics (built-in)

**Backend (Railway):**
- Application logs (Winston → Railway logs)
- Health checks (GET /api/health)
- Resource usage (CPU, RAM, Network)

**Database (Supabase):**
- Query performance
- Connection pool usage
- Slow query log

**Alerting:**
- Slack/Discord webhook for deployment failures
- Email alerts for service downtime
- PagerDuty integration for critical errors

## Consequences

### Positive
- **Fast Deployments**: Git-based workflow deploys in 2-5 minutes
- **Cost Effective**: Free tiers for development, ~$50/month for production
- **Developer Friendly**: Minimal DevOps overhead
- **Scalable**: Automatic scaling handles traffic spikes
- **Reliable**: 99.9% uptime SLAs from platforms

### Negative
- **Multi-Platform Complexity**: Managing multiple dashboards
- **Vendor Lock-In**: Platform-specific configurations
- **Limited Customization**: Less control than self-hosted

### Risks and Mitigation

**Risk**: Platform outage
**Mitigation**:
- Multi-region deployment on Vercel
- Database backups for quick restore
- Monitoring and alerting for rapid response

**Risk**: Cost overruns
**Mitigation**:
- Budget alerts on each platform
- Usage monitoring and optimization
- Auto-scaling limits

**Risk**: Data loss
**Mitigation**:
- Daily automated backups (Supabase)
- Point-in-time recovery (PITR)
- Backup verification tests

## Migration Path

### Phase 1: Initial Deployment (Current)
- Frontend: Vercel
- Backend: Local development
- Database: Docker PostgreSQL

### Phase 2: Backend Deployment (Week 2)
- Deploy backend to Railway
- Connect to Supabase database
- Integrate Upstash Redis

### Phase 3: Production Hardening (Week 3)
- Custom domains
- SSL certificates
- Monitoring setup
- Alert configuration

### Phase 4: Scaling (Future)
- Read replicas for database
- CDN for static assets
- Horizontal backend scaling

## Environment Variables

**Frontend (.env.production):**
```bash
VITE_API_URL=https://api.loverankpulse.com
VITE_WS_URL=wss://api.loverankpulse.com
VITE_ENABLE_REALTIME=true
VITE_ANALYTICS_ID=<vercel-analytics-id>
```

**Backend (Railway secrets):**
```bash
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
JWT_SECRET=<256-bit-secret>
NODE_ENV=production
PORT=3000
CORS_ORIGIN=https://loverankpulse.com
```

## Security Considerations

**Secret Management:**
- Environment variables stored in platform vaults
- JWT secret generated with crypto.randomBytes(32)
- No secrets in version control
- Rotate secrets quarterly

**Network Security:**
- HTTPS enforced on all endpoints
- CORS whitelisting
- Rate limiting on auth endpoints
- DDoS protection (Vercel/Railway)

**Database Security:**
- SSL connections required
- IP whitelisting (Railway only)
- Least-privilege database users
- Encrypted at rest and in transit

## Cost Optimization

**Current Estimate (Production):**
- Vercel Pro: $20/month
- Railway Team: $20/month
- Supabase Pro: $25/month
- Upstash: ~$5/month
- **Total**: ~$70/month

**Optimization Strategies:**
- Use free tiers for development/staging
- Implement Redis caching to reduce database load
- Optimize build sizes to reduce bandwidth
- Monitor usage and adjust plans quarterly

## Related Decisions
- ADR-001: Database Selection (Supabase PostgreSQL)
- ADR-003: Authentication Mechanism (JWT secret management)
- ADR-006: Caching Strategy (Upstash Redis)

## References
- [Vercel Documentation](https://vercel.com/docs)
- [Railway Documentation](https://docs.railway.app/)
- [Supabase Documentation](https://supabase.com/docs)
- [Upstash Documentation](https://docs.upstash.com/)
- Configuration: `/workspaces/love-rank-pulse/vercel.json`
