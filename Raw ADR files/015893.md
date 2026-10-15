# ADR-003: Environment Strategy

## Status

Accepted

## Context

Rule Bound needs clear environment separation for:

- **Development**: Local development with hot reload
- **Preview/Staging**: Testing PRs before merge
- **Production**: Live site for end users

Considerations:

- Environment-specific configuration (API URLs if added later, analytics, feature flags)
- Build-time vs runtime configuration
- Vite's environment variable handling
- Future scalability (e.g., adding backend services)

## Options Considered

### 1. Single Environment (Production Only)

**Pros:**

- Simplest setup
- No configuration complexity

**Cons:**

- No way to test changes before production
- Risky deployments

### 2. Two Environments (Preview + Production)

**Pros:**

- Preview deployments for testing
- Production for stable releases
- Matches Netlify's natural model

**Cons:**

- Limited flexibility for staged rollouts

### 3. Three Environments (Development + Preview + Production)

**Pros:**

- Clear separation of concerns
- Local development isolated
- Preview for PR testing
- Production for releases

**Cons:**

- More configuration to maintain

## Decision

We will use a **Three Environment Strategy** with Vite's built-in environment variable support:

| Environment | Purpose    | URL Pattern                              | Build Mode    |
| ----------- | ---------- | ---------------------------------------- | ------------- |
| Development | Local dev  | `localhost:5173`                         | `development` |
| Preview     | PR testing | `deploy-preview-*.netlify.app`           | `production`  |
| Production  | Live site  | `rulebound.netlify.app` or custom domain | `production`  |

### Environment Variables

Vite environment variables must be prefixed with `VITE_` to be exposed to client code.

```
.env                 # Shared defaults (committed)
.env.local           # Local overrides (gitignored)
.env.production      # Production-specific (committed)
```

### Initial Variables

For now, the app is fully static with no environment-specific config. We'll set up the infrastructure for future use:

```env
# .env
VITE_APP_NAME=Rule Bound
VITE_APP_VERSION=$npm_package_version

# .env.production
VITE_ENABLE_ANALYTICS=true
```

### Netlify Environment Contexts

Netlify supports environment contexts in `netlify.toml`:

```toml
[context.production]
  environment = { VITE_DEPLOY_CONTEXT = "production" }

[context.deploy-preview]
  environment = { VITE_DEPLOY_CONTEXT = "preview" }
```

## Consequences

### Positive

- Clear environment separation
- Vite handles env vars automatically at build time
- Ready for future features (analytics, API endpoints)
- Netlify contexts provide automatic environment detection

### Negative

- Need to maintain multiple env files
- Build-time variables require rebuild for changes

### Neutral

- Currently minimal env config needed (app is static)
- Can expand as features require
