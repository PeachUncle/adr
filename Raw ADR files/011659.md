# Mile Quest MVP Technology Stack

**Version**: 2.0  
**Status**: Current  
**Last Updated**: 2025-01-12  
**Agent**: Architecture Agent  

## Overview

This document outlines the simplified technology stack for Mile Quest MVP, optimized for rapid development, low cost (~$70/month), and clear migration paths for future scaling.

## Frontend Stack

### Core Framework
- **Next.js 14** with App Router
  - Server-side rendering for performance
  - API routes for backend communication
  - Built-in image optimization
  - TypeScript for type safety

### Hosting
- **AWS Amplify** 
  - Git-based deployments from GitHub
  - Full Next.js SSR/SSG support
  - Built-in monitoring and analytics
  - CloudFront CDN included
  - Native AWS integration

### UI & Styling
- **TypeScript** - Type safety and better DX
- **Tailwind CSS** - Utility-first styling
- **Radix UI** - Accessible component primitives
- **CSS Modules** - Component-scoped styles (where needed)

### State Management
- **Zustand** - Simple state management (5KB)
- **React Query (TanStack Query)** - Server state caching
- **IndexedDB (via idb)** - Offline activity queue

### Real-time Updates
- **Pusher JS Client** - Managed WebSocket service
  - Free tier: 200 concurrent connections
  - Channels for team-based updates
  - Presence for online indicators

### PWA & Offline
- **next-pwa** - Service worker generation
- **Workbox** - Offline caching strategies
- **idb** - Promise-based IndexedDB wrapper

## Backend Stack

### API Layer
- **AWS API Gateway** (REST API)
  - $3.50 per million requests
  - Built-in rate limiting
  - CORS configuration
  - API key management

### Compute
- **AWS Lambda** (Node.js 20.x)
  - Pay-per-invocation
  - 512MB memory default
  - ARM/Graviton2 for 20% cost savings
  - TypeScript with esbuild

### Database
- **Amazon RDS PostgreSQL** (Multi-AZ)
  - db.t3.micro instance ($40/month)
  - PostGIS extension for geospatial
  - Automated backups
  - Multi-AZ for high availability

### Session Storage
- **Amazon DynamoDB**
  - On-demand pricing
  - User sessions
  - Hot data (last 7 days)
  - Activity queue


### CDN
- **Amazon CloudFront**
  - API response caching (5 min TTL)
  - Image delivery
  - Gzip compression
  - No additional caching layer

### Authentication
- **AWS Cognito**
  - User pools (50k users free)
  - Google Sign-In integration
  - Email/password support
  - JWT token management

### External Services
- **Pusher** - WebSocket management (abstracted for future migration)
  - Free: 200 connections, 500k messages/day
  - Channels for team communication
  - Presence for online status
  - Abstracted behind WebSocketService interface
  - Migration path to API Gateway WebSocket when >$100/month

## Development Stack

### Version Control
- **Git** with **GitHub**
- Conventional commits
- Branch protection rules
- PR templates

### Local Development
- **Node.js 20.x** LTS
- **pnpm** - Fast, efficient package manager
- **Docker** - For PostgreSQL local dev
- **AWS SAM CLI** - Lambda local testing

### Code Quality
- **ESLint** - Code linting
- **Prettier** - Code formatting
- **Husky** - Git hooks
- **lint-staged** - Pre-commit checks
- **TypeScript** - Static type checking

### Testing
- **Jest** - Unit testing
- **React Testing Library** - Component testing
- **Cypress** - E2E testing (critical paths only)
- **MSW** - API mocking

### CI/CD
- **GitHub Actions + AWS Amplify**
  - Automated testing via GitHub Actions
  - Type checking via GitHub Actions
  - Amplify preview deployments for PRs
  - Amplify handles frontend deployment
  - Lambda deployment via SAM

### Monitoring (Basic)
- **Amplify Monitoring** - Frontend metrics & logs
- **CloudWatch** - Unified logs & metrics
- **CloudWatch Alarms** - Error alerts
- **AWS Budget Alerts** - Cost monitoring
- **X-Ray** - Distributed tracing (optional)

## Key Technology Decisions

### What We're Using
1. **PostgreSQL over DynamoDB** for main data
   - Relational data model fits our use case
   - PostGIS for geospatial queries
   - Familiar SQL queries

2. **Pusher over custom WebSockets**
   - Managed service reduces complexity
   - Free tier sufficient for MVP
   - Built-in presence and channels

3. **AWS Amplify over Vercel**
   - Native AWS integration
   - Unified billing and monitoring
   - Better cost at scale
   - Same-account security benefits

4. **REST over GraphQL**
   - Simpler to implement
   - Team familiarity
   - Field filtering for efficiency

### What We're NOT Using (Yet)
1. **No Redis/ElastiCache** - CloudFront handles caching
2. **No EventBridge/SQS** - Direct Lambda invocations
3. **No Container orchestration** - Pure serverless
4. **No GraphQL** - REST with field filtering
5. **No Native apps** - PWA only

## Migration Paths

### When to Upgrade

| Component | Current | Upgrade To | Trigger |
|-----------|---------|------------|---------|
| Database | RDS PostgreSQL | Aurora Serverless v2 | >10k users OR >100 req/sec |
| WebSockets | Pusher | AWS IoT Core | >1000 concurrent users |
| Caching | CloudFront | + ElastiCache | DB CPU >70% |
| API | REST | + GraphQL | >60% mobile traffic |
| Hosting | AWS Amplify | ECS Fargate | Need persistent connections |

## Cost Breakdown

### Monthly Costs (Estimated)
- RDS PostgreSQL: $40
- Lambda + API Gateway: $10-15
- DynamoDB: $5
- CloudFront: $5
- AWS Amplify: $17 (build minutes + bandwidth)
- **Total: ~$80/month**

### Free Tier Usage
- Cognito: 50,000 MAU free
- Pusher: 200 connections free
- Lambda: 1M requests free
- API Gateway: 1M requests free

## Security Considerations

### MVP Security
- HTTPS everywhere (Amplify + CloudFront)
- JWT tokens (short-lived)
- API rate limiting
- Input validation (Zod schemas)
- SQL injection prevention (parameterized queries)

### Deferred Security (Phase 2)
- AWS WAF
- Secrets rotation
- Penetration testing
- SOC2 compliance
- Advanced DDoS protection

---

**Note**: This tech stack is optimized for MVP launch. See migration paths for scaling strategies.