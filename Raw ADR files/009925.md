# ADR 002: Component Showcase as Standalone Static App

**Status:** Accepted  
**Date:** 2025-01-18  
**Deciders:** Jeff Crosley (Architect)

## Context

The JeffApp portfolio includes a component gallery showcasing Stencil and native Web Components. This gallery must be:

- Accessible as a standalone application for direct viewing
- Embeddable within the Angular `nav-shell` via iframe
- Independently deployable with its own versioning and cache policies
- Hosted on a custom domain (`https://components.jeffcrosley.com`)

### Requirements

- Decouple component showcase lifecycle from nav-shell
- Enable independent updates without redeploying shell
- Preserve SPA routing in both standalone and iframe contexts
- Maintain consistent dev/prod URL patterns

## Decision

Implement `apps/component-showcase` as a standalone Vite static site with:

- Output directory: `dist/apps/component-showcase`
- Deployment: Render static site with webhook from GitHub Actions
- Custom domain: `https://components.jeffcrosley.com`
- Integration: iframe in nav-shell, URL sourced from runtime config
- Dev mode: localhost on dedicated port, auto-detected by nav-shell

### Implementation Details

```typescript
// apps/component-showcase/project.json
{
  "targets": {
    "build": {
      "executor": "@nx/vite:build",
      "outputs": ["{workspaceRoot}/dist/apps/component-showcase"],
      "options": {
        "outputPath": "dist/apps/component-showcase"
      }
    }
  }
}

// apps/nav-shell/src/app/pages/components.component.ts
template: `
  <iframe
    [src]="showcaseUrl"
    sandbox="allow-scripts allow-same-origin"
    title="Component Gallery">
  </iframe>
`

// apps/nav-shell/public/config.json (prod)
{
  "showcaseUrl": "https://components.jeffcrosley.com"
}
```

**Render Configuration (Dashboard):**

- Build Command: `npx nx build component-showcase --configuration=production`
- Publish Directory: `dist/apps/component-showcase`
- Rewrite Rules: `/* → /index.html` (SPA routing)
- Custom Domain: `components.jeffcrosley.com`

## Consequences

### Positive

- **Independent deployments:** Showcase updates don't require nav-shell rebuild/redeploy
- **Cache optimization:** Separate CDN/cache policies per app (showcase has longer TTL for stable components)
- **Standalone value:** Gallery accessible directly at custom domain for sharing
- **Version flexibility:** Can deploy showcase beta versions without affecting production shell
- **Build efficiency:** Smaller shell bundle; showcase assets not duplicated

### Negative

- **Iframe constraints:** Cross-origin communication requires postMessage; limited direct DOM access
- **Security considerations:** Must configure sandbox attributes and CSP headers carefully
- **Routing complexity:** Nested routing requires careful URL handling between shell and iframe
- **Additional deploy:** Extra webhook/service to maintain in Render

### Mitigation

- Use restrictive sandbox: `allow-scripts allow-same-origin` (no forms, popups, top navigation)
- Implement CSP `frame-ancestors` directive in showcase to prevent embedding outside jeffcrosley.com
- Handle iframe load errors gracefully with fallback UI
- Document security model in deployment guide

## Alternatives Considered

### Bundle Showcase into Nav-Shell

```bash
# Rejected: monolithic approach
nx build nav-shell  # includes showcase assets
```

**Rejected because:**

- Couples lifecycles (showcase update requires shell redeploy)
- Bloats shell bundle (components loaded even when page not visited)
- No independent versioning
- Harder to share standalone component gallery

### Host in ui-components/www

```bash
# Rejected: library output hosting
nx build ui-components  # generates www/ with showcase
```

**Rejected because:**

- Mixes library distribution output with application hosting
- `ui-components/www` is for component dev/preview, not production app hosting
- Cannot apply separate deploy/cache strategies
- Confuses library consumers (is www/ part of the package?)

### Microfrontend Module Federation

```typescript
// Rejected: federated module approach
remotes: {
	showcase: 'https://components.jeffcrosley.com/remoteEntry.js'
}
```

**Rejected because:**

- Over-engineered for read-only component gallery
- Adds webpack complexity and runtime overhead
- Tight coupling between host and remote module versions
- iframe solution simpler and sufficient for use case

## References

- Related: ADR 001 (Runtime Configuration)
- Related: ADR 003 (CI/CD Pipeline)
- Deployment: `.github/workflows/main.yml` (deploy_component_showcase job)
- Security: `docs/guides/render-deployment-guide.md` (CSP guidance)
- Implementation: `apps/component-showcase/` and `apps/nav-shell/src/app/pages/components.component.ts`
