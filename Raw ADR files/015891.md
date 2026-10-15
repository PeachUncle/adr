# ADR-001: Hosting Platform Selection

## Status

Accepted

## Context

Rule Bound needs a hosting platform for live environment testing. The application is a static single-page application (SPA) built with React + Vite that:

- Serves static HTML, CSS, JS files
- Uses client-side routing (React Router's `BrowserRouter`)
- Has no server-side requirements
- Needs to be accessible for testing by stakeholders
- Should support preview deployments for PR review

Key constraints:

- Free or low-cost hosting (this is an open-source project)
- Automated deployments from GitHub
- Preview/staging environments for testing
- Must handle SPA routing (redirect all paths to index.html)

## Options Considered

### 1. GitHub Pages

**Pros:**

- Free, integrated with GitHub
- Simple setup via GitHub Actions
- Custom domain support

**Cons:**

- Requires `HashRouter` or manual 404.html workaround for SPA routing
- No built-in preview deployments for PRs
- Limited build configuration

### 2. Netlify

**Pros:**

- Free tier generous (100GB bandwidth, 300 build minutes/month)
- Automatic preview deployments for every PR
- Built-in SPA routing support (`_redirects` file)
- Excellent developer experience
- Built-in form handling, edge functions (future use)
- Easy rollbacks
- GitHub integration

**Cons:**

- Third-party service (vendor dependency)
- Build minutes could be a concern for very active development

### 3. Vercel

**Pros:**

- Free tier (100GB bandwidth)
- Automatic preview deployments
- SPA routing support
- Excellent performance
- GitHub integration

**Cons:**

- Third-party service
- Free tier has team/commercial use limitations
- Optimized for Next.js, less focus on vanilla Vite

### 4. Cloudflare Pages

**Pros:**

- Generous free tier (unlimited bandwidth)
- Edge deployment (fast globally)
- SPA routing support
- Preview deployments

**Cons:**

- Less mature than Netlify/Vercel
- Fewer integrations
- Dashboard less polished

## Decision

We will use **Netlify** as the hosting platform because:

1. **Preview Deployments**: Every PR automatically gets a unique URL for testing—critical for the team workflow
2. **SPA Routing**: Simple `_redirects` file handles all client-side routing without code changes
3. **Free Tier**: Generous limits suitable for this project's scale
4. **Developer Experience**: Excellent GitHub integration, easy configuration, good documentation
5. **Future-Proofing**: Edge functions, forms, and other features available if needed

## Consequences

### Positive

- Zero changes to React Router configuration (keep `BrowserRouter`)
- Every PR gets a preview URL automatically
- Simple deployment configuration via `netlify.toml`
- Production deployments triggered automatically on main branch
- Easy rollbacks if issues are found

### Negative

- Vendor dependency on Netlify
- Team needs Netlify accounts for dashboard access
- Build minutes are limited (300/month on free tier)—monitor usage

### Neutral

- Will need to create a Netlify account and connect to GitHub repo
- Configuration file (`netlify.toml`) added to repository
