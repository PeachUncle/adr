# ADR-003: Deployment Architecture (Vercel + Render)

**Status:** Accepted  
**Date:** 2025-01-27  
**Deciders:** Architecture Team

## Context

AIDevelo.ai needed a deployment strategy that:
- Separates frontend and backend deployments
- Supports serverless frontend (SPA)
- Provides Node.js backend hosting
- Minimizes DevOps overhead
- Supports environment-specific configurations

## Decision

We use a **split deployment architecture**:
- **Frontend**: Cloudflare Pages (originally Vercel, migrated to Cloudflare)
- **Backend**: Render (Node.js service)

## Rationale

### Frontend: Cloudflare Pages

**Advantages:**
1. **Global CDN**
   - Fast content delivery worldwide
   - Edge caching for static assets

2. **SPA Support**
   - Automatic SPA routing handling
   - No server-side rendering needed

3. **Easy Deployment**
   - Git-based deployments
   - Automatic builds on push
   - Preview deployments for PRs

4. **Cost-Effective**
   - Free tier for reasonable traffic
   - Pay-as-you-grow pricing

5. **Cloudflare Functions**
   - Serverless functions for API proxying
   - Same-origin requests (CSP compliance)

### Backend: Render

**Advantages:**
1. **Node.js Support**
   - Native Node.js runtime
   - Easy environment variable management
   - Automatic deployments from Git

2. **Database Integration**
   - Easy connection to Supabase
   - Health checks and auto-restart

3. **Scaling**
   - Auto-scaling based on traffic
   - Horizontal scaling support

4. **Monitoring**
   - Built-in logs and metrics
   - Health check endpoints

5. **Cost-Effective**
   - Free tier for development
   - Reasonable pricing for production

### Architecture Flow

```
User Request
    ↓
Cloudflare Pages (Frontend)
    ↓
Cloudflare Function (API Proxy)
    ↓
Render Backend (Node.js/Express)
    ↓
Supabase (Database/Auth)
```

## Alternatives Considered

1. **Monolithic Deployment (Single Server)**
   - Simpler but less scalable
   - Frontend and backend coupled
   - Harder to scale independently

2. **AWS/GCP/Azure**
   - More complex setup
   - Higher DevOps overhead
   - More expensive for small scale

3. **Vercel for Both**
   - Vercel doesn't support long-running Node.js processes well
   - Better for serverless functions
   - Render better for persistent connections (WebSockets)

## Consequences

- **Positive:**
  - Independent scaling of frontend and backend
  - Optimal deployment for each component
  - Global CDN for frontend
  - Easy Git-based deployments

- **Negative:**
  - Two separate deployment pipelines
  - CORS configuration needed
  - API proxy adds slight latency
  - Environment variables in two places

## Implementation Details

### Frontend Deployment (Cloudflare Pages)

- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Environment Variables:** `VITE_*` prefix required
- **Routing:** SPA mode (all routes → index.html)

### Backend Deployment (Render)

- **Build Command:** `cd server && npm install && npm run build`
- **Start Command:** `cd server && npm start`
- **Health Check:** `/health` endpoint
- **Environment Variables:** All backend secrets

### API Proxy (Cloudflare Functions)

- **Location:** `functions/api/[[splat]].ts`
- **Purpose:** Proxy `/api/*` requests to Render backend
- **Benefits:** Same-origin requests, CSP compliance

## Migration Notes

- Originally used Vercel for frontend
- Migrated to Cloudflare Pages for better performance
- Backend always on Render (better for WebSockets)

## References

- [Cloudflare Pages Documentation](https://developers.cloudflare.com/pages/)
- [Render Documentation](https://render.com/docs)
- [Deployment Guide](docs/DEPLOY.md)
