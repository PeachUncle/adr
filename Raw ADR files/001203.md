# ADR-011: Cloud Hosting Selection (GitHub-Maximized Strategy)

**Status**: Accepted  
**Date**: 2025-12-27  
**Updated**: 2025-12-27 (GitHub ecosystem optimization)  
**Deciders**: James (Owner)  
**Technical Story**: P0-006 CI/CD Pipeline, Production Deployment

## Context and Problem Statement

TaskMan-v2 needs a cloud hosting strategy. Given James has **GitHub Pro subscription**, we should maximize GitHub ecosystem value:
- GitHub Actions (3,000 min/month)
- GitHub Pages (free for private repos with Pro)
- GitHub Packages/Container Registry (2 GB storage)
- GitHub Environments (protection rules, secrets)

## Decision Drivers

* **GitHub Pro Already Paid** - Maximize existing investment
* **Unified Platform** - Reduce vendor sprawl
* **Cost Optimization** - Use included GitHub features
* **Time to Production** - Fast deployment path

## Decision Outcome

**Chosen option: GitHub Pages (frontend) + Railway (backend)**, because:
- GitHub Pages is **free and included** with GitHub Pro for private repos
- Eliminates Vercel dependency ($0 vs $20/month)
- Railway for FastAPI backend (~$5-10/month)
- ghcr.io for Docker images (free, 2 GB included)

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     GitHub Ecosystem                             │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   GitHub     │    │   GitHub     │    │   GitHub     │      │
│  │   Actions    │───▶│   Pages      │    │   Packages   │      │
│  │  (CI/CD)     │    │  (Frontend)  │    │  (ghcr.io)   │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │               │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              GitHub Environments                          │  │
│  │         (staging, production secrets)                     │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     External Services                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐                          │
│  │   Railway    │    │   Railway    │                          │
│  │  (FastAPI)   │◀───│ (PostgreSQL) │                          │
│  │   Backend    │    │   Database   │                          │
│  └──────────────┘    └──────────────┘                          │
│        $5-10/month                                              │
└─────────────────────────────────────────────────────────────────┘
```

## Cost Comparison

| Component | GitHub-Maximized | Original (Vercel+Railway) |
|-----------|------------------|---------------------------|
| Frontend Hosting | **$0** (GitHub Pages) | $0-20 (Vercel) |
| Backend Hosting | $5-10 (Railway) | $5-10 (Railway) |
| Container Registry | **$0** (ghcr.io, 2 GB) | $0 (included) |
| CI/CD | **$0** (Actions, 3K min) | $0 (Actions) |
| Auth | **$0** (GitHub OAuth) | $240-480 (Auth0) |
| **Total** | **$5-10/month** | $5-510/month |
| **Annual Savings** | **$0-6,000/year** | Baseline |

## Implementation

### GitHub Pages Deployment Workflow

```yaml
# .github/workflows/deploy-frontend.yml
name: Deploy Frontend to GitHub Pages

on:
  push:
    branches: [main]
    paths: ['TaskMan-v2/src/**', 'TaskMan-v2/package.json']
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: TaskMan-v2/package-lock.json
      
      - name: Install dependencies
        working-directory: TaskMan-v2
        run: npm ci
      
      - name: Build
        working-directory: TaskMan-v2
        run: npm run build
        env:
          VITE_API_URL: ${{ vars.API_URL }}
          VITE_GITHUB_CLIENT_ID: ${{ vars.GITHUB_CLIENT_ID }}
      
      - name: Setup Pages
        uses: actions/configure-pages@v4
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: TaskMan-v2/dist

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### SPA Router Fix for GitHub Pages

```typescript
// TaskMan-v2/vite.config.ts
export default defineConfig({
  base: '/', // or '/TaskMan-v2/' if using project pages
  build: {
    outDir: 'dist',
  },
  plugins: [react()],
});
```

Create `TaskMan-v2/public/404.html` for SPA routing:
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Redirecting...</title>
  <script>
    // Redirect to index.html with the path as a query parameter
    sessionStorage.redirect = location.href;
  </script>
  <meta http-equiv="refresh" content="0;URL='/'">
</head>
</html>
```

Add to `TaskMan-v2/src/main.tsx`:
```typescript
// Handle SPA redirect from 404.html
const redirect = sessionStorage.redirect;
if (redirect) {
  delete sessionStorage.redirect;
  window.history.replaceState(null, '', redirect);
}
```

### Backend Docker Push to ghcr.io

```yaml
# .github/workflows/deploy-backend.yml
name: Deploy Backend

on:
  push:
    branches: [main]
    paths: ['TaskMan-v2/backend-api/**']

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}/taskman-api

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: TaskMan-v2/backend-api
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}

  deploy-railway:
    needs: build-and-push
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy to Railway
        run: |
          curl -X POST "${{ secrets.RAILWAY_DEPLOY_WEBHOOK }}"
```

### GitHub Environments Setup

1. Go to Repository Settings → Environments
2. Create environments:
   - `staging` - No protection rules
   - `production` - Add required reviewers (yourself)
   - `github-pages` - Auto-created by Pages

3. Add environment secrets:
   ```
   staging:
     - DATABASE_URL (Railway staging DB)
     - GITHUB_OAUTH_CLIENT_SECRET (staging OAuth app)
   
   production:
     - DATABASE_URL (Railway production DB)
     - GITHUB_OAUTH_CLIENT_SECRET (production OAuth app)
     - RAILWAY_DEPLOY_WEBHOOK
   ```

## Current GitHub Features Status

Based on account analysis:

| Feature | Current Status | Action Needed |
|---------|----------------|---------------|
| **GitHub Pages** | ❌ Disabled | Enable in Settings → Pages |
| **GitHub Actions** | ✅ 19 workflows active | Optimize for 3K min/month |
| **GitHub Packages** | ❌ Not used | Push Docker images to ghcr.io |
| **Environments** | ⚠️ Only 'copilot' | Create staging, production |
| **Branch Protection** | ⚠️ Check status | Enable required reviews |
| **Discussions** | ❌ Disabled | Optional for community |
| **Wiki** | ❌ Disabled | Optional for docs |
| **Repo Count** | 39 repos (30 active) | Consolidate if needed |

## Enable GitHub Pages

```bash
# Via Settings UI:
# 1. Go to Settings → Pages
# 2. Source: GitHub Actions
# 3. Save

# Or enable via workflow first push
```

## Links

* [GitHub Pages Documentation](https://docs.github.com/en/pages)
* [Deploy Pages Action](https://github.com/actions/deploy-pages)
* [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
* [GitHub Environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
