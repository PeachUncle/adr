# ADR 001: Runtime Configuration via APP_INITIALIZER

**Status:** Accepted  
**Date:** 2025-01-18  
**Deciders:** Jeff Crosley (Architect)

## Context

The Angular `nav-shell` application must load environment-specific URLs (component showcase, API gateway) before app bootstrap. During local development, the app must use localhost URLs regardless of what's configured in production settings, ensuring developers can work against local services without manual configuration changes.

### Requirements

- URLs must be available before any component renders
- Dev/prod switching without rebuilds
- Safe localhost overrides during development
- Single source of truth for runtime URLs
- Type-safe access to configuration

## Decision

Use `config.json` in `apps/nav-shell/public/` loaded via Angular's `APP_INITIALIZER` pattern. Centralize access through `EnvironmentService` with automatic dev detection:

- When hostname is `localhost`, `127.0.0.1`, or ends with `.local`, prefer local URLs
- Load config at app initialization (before bootstrap completes)
- Provide typed getters for showcase and API gateway URLs
- Include sensible defaults for dev environments

### Implementation Details

```typescript
// apps/nav-shell/public/config.json
{
  "showcaseUrl": "https://components.jeffcrosley.com",
  "apiGatewayUrl": "https://api.jeffcrosley.com"
}

// APP_INITIALIZER in app.config.ts
{
  provide: APP_INITIALIZER,
  useFactory: (env: EnvironmentService) => () => env.loadConfig(),
  deps: [EnvironmentService],
  multi: true
}

// Dev detection in EnvironmentService
isLocalDev(): boolean {
  const hostname = window.location.hostname;
  return hostname === 'localhost' ||
         hostname === '127.0.0.1' ||
         hostname.endsWith('.local');
}
```

## Consequences

### Positive

- **Predictable startup order:** URLs guaranteed available before component rendering
- **Zero-rebuild switching:** Change `config.json` and refresh to switch environments
- **Developer-friendly:** Automatic localhost detection prevents accidental prod API calls during dev
- **Type-safe:** TypeScript interfaces enforce contract between config and consumers
- **Cloud-ready:** Config can be injected at deploy time without rebuilding

### Negative

- **Minor startup latency:** Single synchronous fetch before bootstrap (~10-50ms)
- **Error handling required:** Must handle missing/malformed config gracefully
- **Global state:** Service maintains singleton config state (acceptable for this use case)

### Mitigation

- Provide fallback defaults for all URLs
- Log clear errors when config load fails
- Cache config in service after first load
- Consider preloading config.json in index.html if latency becomes issue

## Alternatives Considered

### Angular Environment Files

```typescript
// Rejected: environment.ts approach
export const environment = {
  showcaseUrl: 'http://localhost:4201',
  production: false,
};
```

**Rejected because:**

- Requires rebuild for each environment
- Cannot be changed at runtime or deploy time
- Forces commit of environment-specific values

### Build-Time Environment Variable Injection

```bash
# Rejected: build arg approach
ng build --configuration=production --showcase-url=$SHOWCASE_URL
```

**Rejected because:**

- Static at build time, not runtime
- Requires custom build scripts per environment
- Cannot switch environments without rebuild
- Poor DX for local development

### Query String Toggles

```typescript
// Rejected: URL parameter approach
const showcaseUrl = new URLSearchParams(location.search).get('showcase') || defaultUrl;
```

**Rejected because:**

- Fragile (parameters must be on every navigation)
- Not suitable for global configuration
- Poor UX (URLs polluted with config)
- Security concerns (config exposed in URLs)

## References

- Angular APP_INITIALIZER: https://angular.io/api/core/APP_INITIALIZER
- Related: ADR 002 (Component Showcase Deployment)
- Implementation: `apps/nav-shell/src/app/services/environment.service.ts`
- Config: `apps/nav-shell/public/config.json`
