# ADR-011: GitHub Pro Ecosystem Analysis for TaskMan-v2

**Status**: Proposed  
**Date**: 2025-12-27  
**Deciders**: James (Owner)  
**Related**: ADR-010 (Auth Provider Selection), ADR-009 (Cloud Hosting Decision)

## Context and Problem Statement

The user pays for **GitHub Pro ($4/month)** and wants to maximize the GitHub ecosystem before adding external services. This analysis evaluates which GitHub services can replace or complement current recommendations for TaskMan-v2.

## Research Summary

```yaml
github_auth:
  viable: "partial"
  approach: "GitHub OAuth App (or GitHub App for fine-grained permissions)"
  limitations:
    - "Users must have GitHub accounts (appropriate for developer tool)"
    - "No built-in RBAC - must implement roles in your app layer"
    - "No MFA management - relies on GitHub's account MFA"
    - "No audit logging for auth events (must implement custom)"
    - "Token expiration requires refresh flow implementation"
    - "Cannot enforce organization membership without GitHub Teams"
  implementation_effort: "12-16 hours"
  best_for: "Internal developer tools, single-org teams"

github_hosting:
  frontend: "GitHub Pages - YES for React SPA"
  backend: "NOT POSSIBLE - static files only, no server-side code"
  recommendation: "Use GitHub Pages for frontend + Railway/Render for FastAPI backend"
  pages_features:
    - "Custom domains supported"
    - "HTTPS automatic with github.io"
    - "SPA routing via 404.html redirect trick"
    - "Deploy via GitHub Actions"

github_container_registry:
  use_case: "Store and deploy Docker images for backend"
  cost: "1 GB included with Pro (shared with Packages storage)"
  authentication: "Use GITHUB_TOKEN in Actions, PAT for external pulls"
  deployment: "Pull from ghcr.io to Railway/Render/Cloud Run"

github_actions_pro_features:
  included:
    - "3,000 minutes/month (vs 2,000 on Free)"
    - "180 Codespaces core hours/month"
    - "20 GB Codespaces storage/month"
    - "Protected branches"
    - "Code owners"
    - "Required reviewers"
    - "Repository insights"
  costs_after_quota:
    - "Linux: $0.008/minute"
    - "Windows: $0.016/minute"
    - "macOS: $0.08/minute"
  storage:
    - "1 GB artifact/cache storage included"
    - "Shared with GitHub Packages"
    - "10 GB cache per repository"

github_codespaces:
  included_pro:
    - "180 core hours/month"
    - "20 GB storage/month"
  use_case: "Standardized dev environment via devcontainer.json"
  value: "Onboard contributors instantly, consistent environments"

github_packages:
  included: "1 GB storage with Pro"
  use_case: "npm packages, container images, generic packages"
  recommendation: "Use for private npm packages if needed"

recommended_github_stack:
  auth: "GitHub OAuth App (save Auth0 cost, 12h implementation)"
  frontend_hosting: "GitHub Pages (free, integrated)"
  backend_hosting: "Railway or Render (GitHub cannot host)"
  ci_cd: "GitHub Actions (already planned, 3K min/mo included)"
  container_registry: "ghcr.io (1 GB free, integrated)"
  secrets: "GitHub Secrets (free, encrypted, environment-scoped)"

cost_savings:
  current_estimate: "$20-45/mo (Auth0 Free + Railway Hobby + Vercel Free)"
  with_github_max: "$0-10/mo (GitHub OAuth + GitHub Pages + Railway only)"
  monthly_savings: "$15-40/mo"
  annual_savings: "$180-480/year"
```

---

## Detailed Analysis

### 1. GitHub OAuth as Auth Provider

**Verdict**: ✅ VIABLE for TaskMan-v2 (internal developer tool)

#### How It Works

1. Register OAuth App at `github.com/settings/developers`
2. User clicks "Sign in with GitHub" → redirected to GitHub
3. GitHub returns auth code → exchange for access token
4. Use token to call `GET /user` for identity
5. Store user info in your database with role assignment

#### Implementation Pattern

```python
# FastAPI OAuth flow with github
from authlib.integrations.starlette_client import OAuth

oauth = OAuth()
oauth.register(
    name='github',
    client_id=settings.GITHUB_CLIENT_ID,
    client_secret=settings.GITHUB_CLIENT_SECRET,
    authorize_url='https://github.com/login/oauth/authorize',
    access_token_url='https://github.com/login/oauth/access_token',
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'read:user user:email'},
)

@app.get("/auth/github")
async def github_login(request: Request):
    redirect_uri = request.url_for('github_callback')
    return await oauth.github.authorize_redirect(request, redirect_uri)

@app.get("/auth/github/callback")
async def github_callback(request: Request):
    token = await oauth.github.authorize_access_token(request)
    user_info = await oauth.github.get('user', token=token)
    # Create/update user in database with your RBAC
    return create_session(user_info.json())
```

#### RBAC Implementation (Your Responsibility)

```python
# models/user.py
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    github_id = Column(BigInteger, unique=True)  # From GitHub
    github_username = Column(String(255))
    email = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.VIEWER)  # YOUR RBAC
    created_at = Column(DateTime, default=datetime.utcnow)

class UserRole(enum.Enum):
    ADMIN = "admin"
    DEVELOPER = "developer"  
    VIEWER = "viewer"
    GUEST = "guest"
```

#### Comparison: GitHub OAuth vs Auth0

| Aspect | GitHub OAuth | Auth0 |
|--------|-------------|-------|
| **Cost** | $0 | $0-240/mo |
| **Implementation** | 12-16 hours | 18 hours |
| **Built-in RBAC** | ❌ (build yourself) | ✅ |
| **Audit Logging** | ❌ (build yourself) | ✅ (Enterprise) |
| **MFA** | GitHub's account MFA | ✅ Built-in |
| **User Requirements** | Must have GitHub | Email/password |
| **Best For** | Developer tools | Public-facing apps |

**Recommendation**: For TaskMan-v2 (internal tool for developers), GitHub OAuth is sufficient and saves $0-240/month.

---

### 2. GitHub Pages for Frontend Hosting

**Verdict**: ✅ SUITABLE for React SPA

#### What GitHub Pages Can Do

- ✅ Host static files (HTML, CSS, JS)
- ✅ Serve React/Vue/Angular SPA builds
- ✅ Custom domains with HTTPS
- ✅ Deploy via GitHub Actions
- ✅ Free with Pro (private repos supported)

#### What GitHub Pages CANNOT Do

- ❌ Run server-side code (Node.js, Python, etc.)
- ❌ Server-side rendering (SSR)
- ❌ API endpoints
- ❌ Database connections
- ❌ Environment variables at runtime

#### SPA Routing Solution

React Router requires a workaround for client-side routing:

```yaml
# .github/workflows/deploy-pages.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
    paths: ['frontend/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install and Build
        working-directory: frontend
        run: |
          npm ci
          npm run build
      
      - name: Create 404.html for SPA routing
        run: cp frontend/dist/index.html frontend/dist/404.html
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./frontend/dist
```

#### Comparison: GitHub Pages vs Vercel

| Aspect | GitHub Pages | Vercel |
|--------|-------------|--------|
| **Cost** | $0 | $0 (Hobby) |
| **SSR/SSG** | Static only | ✅ Full support |
| **Edge Functions** | ❌ | ✅ |
| **Preview Deploys** | ❌ | ✅ Per branch |
| **Analytics** | ❌ | ✅ Basic free |
| **Build Caching** | Via Actions | Built-in |
| **Integration** | Native | Excellent |

**Recommendation**: GitHub Pages works fine for a React SPA that calls an external API. Use Vercel only if you need SSR or preview deployments.

---

### 3. GitHub Container Registry (ghcr.io)

**Verdict**: ✅ USE for Docker images

#### Included with GitHub Pro

- 1 GB storage (shared with Packages)
- Unlimited pulls for public images
- Private image support

#### Workflow Example

```yaml
# .github/workflows/build-push.yml
name: Build and Push Docker Image

on:
  push:
    branches: [main]
    paths: ['backend-api/**']

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}/taskman-api

jobs:
  build-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      
    steps:
      - uses: actions/checkout@v4
      
      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and Push
        uses: docker/build-push-action@v5
        with:
          context: ./backend-api
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
```

#### Deploy from ghcr.io to Railway/Render

```yaml
# Railway/Render can pull from ghcr.io
# In Railway: Settings → Source → Docker Image
# Image URL: ghcr.io/username/taskman-api:latest
# Add GITHUB_TOKEN as deploy key for private images
```

---

### 4. GitHub Actions Pro Features

**Verdict**: ✅ ALREADY PLANNED, 3,000 min/mo is sufficient

#### GitHub Pro Includes

| Resource | Free | Pro | Estimate for TaskMan |
|----------|------|-----|---------------------|
| Minutes | 2,000 | 3,000 | ~200-500/mo needed |
| Storage | 500 MB | 1 GB | ~100-200 MB needed |
| Codespaces | 120 hrs | 180 hrs | Nice to have |

#### Advanced Features to Leverage

```yaml
# Use matrix builds efficiently
jobs:
  test:
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
        os: [ubuntu-latest]  # Linux only = cheapest
    
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'  # Cache dependencies

# Use caching aggressively
      - name: Cache pip dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

---

### 5. GitHub Secrets Management

**Verdict**: ✅ USE for all secrets

#### Secret Types

1. **Repository Secrets** - Available to all workflows
2. **Environment Secrets** - Scoped to deployment environments
3. **Organization Secrets** - Shared across repos (if using org)

#### Best Practice Setup

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-staging:
    environment: staging  # Uses staging secrets
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Staging
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          JWT_SECRET: ${{ secrets.JWT_SECRET }}
        run: |
          # Deploy script here

  deploy-production:
    needs: deploy-staging
    environment: 
      name: production
      url: https://taskman.example.com
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Production
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}  # Different in prod
          JWT_SECRET: ${{ secrets.JWT_SECRET }}
        run: |
          # Deploy script here
```

---

### 6. GitHub Codespaces for Development

**Verdict**: 🔶 OPTIONAL but valuable for onboarding

#### Setup devcontainer.json

```json
// .devcontainer/devcontainer.json
{
  "name": "TaskMan-v2 Dev",
  "image": "mcr.microsoft.com/devcontainers/python:3.12",
  "features": {
    "ghcr.io/devcontainers/features/node:1": {
      "version": "20"
    },
    "ghcr.io/devcontainers/features/docker-in-docker:2": {}
  },
  "forwardPorts": [8002, 5173, 5432],
  "postCreateCommand": "pip install -e . && cd frontend && npm install",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "bradlc.vscode-tailwindcss",
        "dbaeumer.vscode-eslint"
      ]
    }
  }
}
```

#### Monthly Budget with Pro

- 180 core hours = ~22 hours of 8-core machine
- 20 GB storage = sufficient for most projects
- Good for occasional use, not full-time development

---

## Decision Outcome

### Recommended GitHub-Maximized Stack

| Component | GitHub Service | External Service | Monthly Cost |
|-----------|---------------|------------------|--------------|
| **Auth** | GitHub OAuth | - | $0 |
| **Frontend** | GitHub Pages | - | $0 |
| **Backend** | - | Railway (Hobby) | $5 |
| **Database** | - | Railway PostgreSQL | $5 |
| **CI/CD** | GitHub Actions | - | $0 |
| **Containers** | ghcr.io | - | $0 |
| **Secrets** | GitHub Secrets | - | $0 |
| **Dev Env** | Codespaces (optional) | - | $0 (included) |
| **TOTAL** | | | **$10/mo** |

### Comparison with Original Recommendations

| Scenario | Auth | Frontend | Backend | Total |
|----------|------|----------|---------|-------|
| **Original (ADR-010)** | Auth0 ($0-240) | Vercel ($0) | Railway ($5) | $5-245/mo |
| **GitHub Maximized** | GitHub OAuth ($0) | Pages ($0) | Railway ($5) | $5-10/mo |
| **Savings** | | | | **$0-235/mo** |

---

## Implementation Plan

### Phase 1: GitHub OAuth (Week 1)
1. Register GitHub OAuth App (0.5 hours)
2. Implement FastAPI OAuth flow with `authlib` (4 hours)
3. Implement RBAC in user model (4 hours)
4. Add React OAuth button with callback (3 hours)
5. Test complete flow (2 hours)
**Total: ~14 hours**

### Phase 2: GitHub Pages Frontend (Week 2)
1. Configure Vite for production build (1 hour)
2. Create GitHub Actions deploy workflow (2 hours)
3. Set up custom domain if desired (1 hour)
4. Test SPA routing with 404.html (1 hour)
**Total: ~5 hours**

### Phase 3: ghcr.io for Backend (Week 2)
1. Create Dockerfile for FastAPI (2 hours)
2. Create GitHub Actions build workflow (2 hours)
3. Configure Railway to pull from ghcr.io (1 hour)
**Total: ~5 hours**

---

## Trade-offs and Risks

### Choosing GitHub OAuth

| Benefit | Risk | Mitigation |
|---------|------|------------|
| $0 cost | Users need GitHub | Fine for dev tool |
| Simpler integration | No built-in RBAC | Build simple role table |
| Native ecosystem | No audit logs | Log to database |
| Trusted auth | Limited scopes | Only need `user:email` |

### Choosing GitHub Pages

| Benefit | Risk | Mitigation |
|---------|------|------------|
| $0 cost | No SSR | Not needed for SPA |
| Native integration | No preview deploys | Use branch deploys |
| Automatic HTTPS | Limited to static | Backend handles logic |

---

## Links

* [GitHub OAuth Apps](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps)
* [GitHub Pages SPA](https://docs.github.com/en/pages)
* [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
* [GitHub Actions Billing](https://docs.github.com/en/billing/managing-billing-for-github-actions)
* [ADR-010 Auth Provider Selection](ADR-010-Auth-Provider-Selection.md)
