# ADR-005: CI/CD Staging Deployment with Firebase

**Status:** ✅ Accepted  
**Date:** 2025-10-18  
**Decision Makers:** Engineering Team  
**Related Tasks:** T-005 (CI/CD Staging Deploy)

---

## Context

With the core infrastructure complete (monorepo, backend API, Firebase auth, Firestore schema), we need automated deployment to a staging environment. This enables:

1. **Continuous Integration:** Automatic deployment on every push to `main`
2. **Testing in Production-like Environment:** Validate changes before releasing to users
3. **Fast Iteration:** Reduce manual deployment overhead
4. **Monitoring:** Early detection of issues through health checks

### Requirements
- Deploy backend API as Cloud Functions
- Deploy web dashboard via Firebase Hosting
- Automated deployment on `main` branch pushes
- Health check verification after deployment
- Easy manual deployment via GitHub Actions UI

---

## Decision

**We will use Firebase Cloud Functions + Hosting with GitHub Actions for automated staging deployments.**

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    GitHub Repository                     │
│                                                          │
│  Push to main → GitHub Actions Workflow                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              GitHub Actions Runner                       │
│                                                          │
│  1. Checkout code                                       │
│  2. Install dependencies (Node.js 18)                   │
│  3. Build Functions (TypeScript → JavaScript)           │
│  4. Deploy to Firebase (CLI)                            │
│  5. Verify health endpoint                              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                 Firebase Platform                        │
│                                                          │
│  ┌────────────────────┐  ┌─────────────────────────┐   │
│  │  Cloud Functions   │  │   Firebase Hosting      │   │
│  │                    │  │                         │   │
│  │  • Fastify API     │  │  • Web Dashboard        │   │
│  │  • Health check    │  │  • /api/** → Functions  │   │
│  │  • OpenAPI docs    │  │  • Static assets        │   │
│  │  • Auto-scaling    │  │  • Global CDN           │   │
│  └────────────────────┘  └─────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Implementation Details

#### 1. Cloud Functions Setup
- **File:** `backend/functions/src/index.ts`
- **Runtime:** Node.js 18
- **Region:** us-central1
- **Memory:** 512MB
- **Timeout:** 60s
- **Scaling:** 0 min → 10 max instances

The Cloud Function wraps our existing Fastify backend:
```typescript
export const api = functions
  .region('us-central1')
  .runWith({ memory: '512MB', timeoutSeconds: 60 })
  .https.onRequest(async (req, res) => {
    const server = await getServer();
    server.server.emit('request', req, res);
  });
```

#### 2. Hosting Configuration
- **File:** `firebase.json`
- **Public Directory:** `public/`
- **Rewrites:** `/api/**` → Cloud Functions
- **Static Assets:** Web dashboard landing page

#### 3. GitHub Actions Workflow
- **File:** `.github/workflows/staging-deploy.yml`
- **Trigger:** Push to `main` branch + manual dispatch
- **Steps:**
  1. Checkout code
  2. Setup Node.js 18
  3. Install Firebase CLI
  4. Install & build Functions
  5. Deploy to Firebase
  6. Verify health endpoint
  7. Display deployment summary

#### 4. Deployment Process
```bash
# Local development
firebase emulators:start --only functions,hosting

# Automatic deployment (GitHub Actions)
git push origin main

# Manual deployment
firebase deploy --only functions,hosting
```

---

## Endpoints

### Staging Endpoints
- **API Health:** `https://us-central1-basketball-ai-ecosystem.cloudfunctions.net/api/healthz`
- **API Root:** `https://us-central1-basketball-ai-ecosystem.cloudfunctions.net/api/`
- **API Docs:** `https://us-central1-basketball-ai-ecosystem.cloudfunctions.net/api/docs`
- **Web Dashboard:** `https://basketball-ai-ecosystem.web.app`

### Local Development (Emulators)
- **API Health:** `http://127.0.0.1:5001/basketball-ai-ecosystem/us-central1/api/healthz`
- **Web Dashboard:** `http://127.0.0.1:5050`
- **Emulator UI:** `http://127.0.0.1:4040`

---

## Alternatives Considered

### 1. ❌ Separate VPS/Container Hosting (Docker + DigitalOcean)
**Pros:**
- Full control over infrastructure
- Traditional deployment model
- Easy to migrate later

**Cons:**
- Manual DevOps setup (Nginx, SSL, monitoring)
- No auto-scaling (need to configure)
- Higher operational overhead
- Slower iteration (more moving parts)

**Rejected because:** Firebase provides faster iteration for MVP stage. We can migrate to VPS later if needed.

### 2. ❌ Cloud Run for Backend
**Pros:**
- Containerized deployments
- Better for long-running processes
- More CPU/memory options

**Cons:**
- Requires Docker setup
- More complex CI/CD pipeline
- Cold starts still exist
- Overkill for simple REST API

**Rejected because:** Cloud Functions is simpler for HTTP APIs and integrates better with Firebase ecosystem.

### 3. ❌ Vercel/Netlify Hosting
**Pros:**
- Excellent developer experience
- Built-in CI/CD
- Fast deployments

**Cons:**
- Doesn't integrate with Firebase Auth/Firestore
- Requires separate backend hosting
- Additional vendor lock-in

**Rejected because:** We're already using Firebase for auth and database. Keeping everything in one platform simplifies architecture.

---

## Consequences

### Positive ✅
1. **Fast Deployments:** Automatic deployment on every push to `main` (< 5 minutes)
2. **Zero Infrastructure Management:** No servers, load balancers, or SSL certs to manage
3. **Auto-scaling:** Handles traffic spikes automatically (0 → 10 instances)
4. **Global CDN:** Firebase Hosting uses Google's CDN for static assets
5. **Cost-effective:** Pay only for invocations (generous free tier)
6. **Easy Rollback:** Firebase Console allows instant rollback to previous versions
7. **Integrated Monitoring:** Cloud Functions logs appear in Firebase Console

### Negative ⚠️
1. **Cold Starts:** First request after idle period (5-10s delay)
   - **Mitigation:** Set `minInstances: 1` in production for critical endpoints
2. **Vendor Lock-in:** Tight coupling to Firebase platform
   - **Mitigation:** Backend code is standard Fastify (portable to any Node.js host)
3. **Limited Customization:** Can't customize HTTP server (Nginx, middleware)
   - **Mitigation:** Fastify provides extensive middleware ecosystem
4. **Function Timeout:** Max 60s for HTTP functions (540s for non-HTTP)
   - **Mitigation:** Long-running tasks will use Cloud Run or Pub/Sub later

### Neutral ➖
1. **Node.js 18 Required:** Older than local dev (Node 24)
   - **Mitigation:** TypeScript compilation ensures compatibility
2. **Regional Deployment:** Single region (us-central1) initially
   - **Mitigation:** Can add more regions later if needed

---

## Migration Path

If we need to migrate off Firebase later:

### Backend API → VPS/Cloud Run
```typescript
// Current: Cloud Function wrapper
export const api = functions.https.onRequest(async (req, res) => {
  const server = await getServer();
  server.server.emit('request', req, res);
});

// Migrate to: Standalone Fastify server
// backend/src/index.ts already has this!
const server = Fastify({ logger: true });
// ... register routes ...
server.listen({ port: 3000, host: '0.0.0.0' });
```

**Effort:** Low (< 1 day). Backend code is already portable Fastify.

### Firebase Auth → Custom JWT
- Gradual migration: Support both Firebase JWT + custom JWT
- Update middleware to validate both token types
- Migrate users in batches

**Effort:** Medium (3-5 days)

### Firestore → Postgres
- Already planned (see ADR-004)
- Schema compatibility confirmed
- Prisma ORM ready

**Effort:** Medium (5-7 days)

---

## Security Considerations

### 1. GitHub Secrets
- `FIREBASE_TOKEN`: Firebase CLI auth token (required for deployment)
- **Setup:** `firebase login:ci` → Add token to GitHub Secrets

### 2. Cloud Functions IAM
- Functions run with default service account
- Has access to Firestore, Storage, Auth (intended)
- No external API keys stored in code

### 3. CORS Policy
- `cors: { origin: true }` allows all origins (API is public)
- Future: Restrict to mobile app domains + web dashboard

### 4. Rate Limiting
- Firebase provides basic DDoS protection
- Future: Add Fastify rate limiting middleware for API abuse

---

## Testing Strategy

### Local Testing (Emulators)
```bash
# Start emulators
firebase emulators:start --only functions,hosting

# Test health endpoint
curl http://127.0.0.1:5001/basketball-ai-ecosystem/us-central1/api/healthz

# View logs
firebase emulators:logs --only functions
```

### Staging Testing (Production)
```bash
# Deploy to staging
firebase deploy --only functions,hosting

# Test health endpoint
curl https://us-central1-basketball-ai-ecosystem.cloudfunctions.net/api/healthz

# View logs
firebase functions:log
```

### Automated Testing (CI)
- GitHub Actions runs health check after deployment
- Fails deployment if health check returns non-200 status
- Future: Add integration tests (Playwright, Postman)

---

## Monitoring & Observability

### Firebase Console
- **Functions Logs:** Real-time logs with request IDs
- **Performance:** Invocation count, duration, errors
- **Quota:** Track usage against free tier limits

### Health Check Endpoint
```json
{
  "status": "ok",
  "version": "1.0.0",
  "timestamp": "2025-10-18T05:08:18.791Z",
  "uptime": 18.79,
  "environment": "development",
  "checks": {
    "database": "ok",
    "storage": "ok"
  },
  "memory": {
    "used": 45678912,
    "total": 67108864,
    "percentage": 68
  }
}
```

### Future Enhancements
- Sentry for error tracking
- Prometheus metrics export
- Uptime monitoring (UptimeRobot, Pingdom)

---

## Cost Estimation

### Firebase Free Tier (Spark Plan)
- **Cloud Functions:** 2M invocations/month, 400K GB-seconds
- **Hosting:** 10 GB storage, 360 MB/day transfer
- **Firestore:** 50K reads, 20K writes, 1 GB storage

### Expected MVP Usage
- **API Calls:** ~10K/day = 300K/month (15% of free tier)
- **Hosting Transfer:** ~100 MB/day (28% of free tier)
- **Firestore:** ~5K reads/day, 2K writes/day (30% of free tier)

**Estimated Cost:** $0/month (within free tier)

### Production Scaling (Blaze Plan)
- **100K users, 10 API calls/day:** $50-100/month
- **Cloud Functions:** $0.40/million invocations
- **Hosting:** $0.15/GB transfer
- **Firestore:** $0.06/100K reads

---

## Success Metrics

### Deployment Metrics
- ✅ **Deployment Time:** < 5 minutes (target: 3 minutes)
- ✅ **Success Rate:** 100% (with automatic rollback on failure)
- ✅ **Health Check:** 200 OK response within 10 seconds

### Performance Metrics
- **Cold Start:** < 5 seconds (first request after idle)
- **Warm Response:** < 200ms (subsequent requests)
- **P95 Latency:** < 500ms
- **Error Rate:** < 0.1%

### Operational Metrics
- **Manual Deployments:** 0 (all automated via GitHub Actions)
- **Rollbacks:** < 1/week
- **Downtime:** < 30 minutes/month

---

## Action Items

- [x] Create Cloud Functions wrapper (`backend/functions/src/index.ts`)
- [x] Configure `firebase.json` with Functions + Hosting
- [x] Create GitHub Actions workflow (`.github/workflows/staging-deploy.yml`)
- [x] Test locally with Firebase emulators
- [ ] Generate Firebase CI token (`firebase login:ci`)
- [ ] Add `FIREBASE_TOKEN` to GitHub Secrets
- [ ] Deploy to staging (trigger workflow)
- [ ] Verify endpoints work in production
- [ ] Update `mvp-tracking.md` to mark T-005 complete
- [ ] Document deployment process in `README.md`

---

## References

- **Firebase Cloud Functions Docs:** https://firebase.google.com/docs/functions
- **Firebase Hosting Docs:** https://firebase.google.com/docs/hosting
- **GitHub Actions Docs:** https://docs.github.com/en/actions
- **Fastify Docs:** https://www.fastify.io/docs/latest/
- **Related ADRs:**
  - ADR-001: Monorepo & Tooling
  - ADR-002: Backend Health & OpenAPI
  - ADR-003: Firebase JWT Auth
  - ADR-004: Firebase Schema v1

---

**Decision:** Use Firebase Cloud Functions + Hosting with GitHub Actions for staging deployments.  
**Next Steps:** Configure GitHub secrets and trigger first deployment.
