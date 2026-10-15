# ADR-004: SPA Routing Configuration for Deployment

## Status

Accepted

## Context

Rule Bound uses React Router with `BrowserRouter`, which relies on the HTML5 History API. This creates clean URLs like:

- `/rules`
- `/rules/1.2.3`
- `/bookmarks`
- `/search`

The challenge: when users directly navigate to these URLs (or refresh), the web server tries to find a file at that path. Since these are client-side routes (not real files), the server returns a 404.

**Solution needed**: Configure the hosting platform to serve `index.html` for all routes, allowing React Router to handle routing client-side.

## Options Considered

### 1. Switch to HashRouter

**Pros:**

- Works without server configuration
- URLs like `/#/rules` always work

**Cons:**

- Ugly URLs with `#`
- Poor SEO (if needed in future)
- Worse user experience
- Requires code changes

### 2. Netlify `_redirects` File

**Pros:**

- Simple single-line configuration
- No code changes needed
- Standard Netlify approach

**Cons:**

- Netlify-specific

### 3. Netlify `netlify.toml` Redirects

**Pros:**

- All Netlify config in one file
- More powerful redirect options
- Can combine with other settings

**Cons:**

- Slightly more verbose

## Decision

We will use **`netlify.toml` redirects** to handle SPA routing:

```toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

This tells Netlify: "For any path that doesn't match a real file, serve `index.html` with a 200 status (not a redirect)."

### Why `netlify.toml` over `_redirects`

1. **Single Source of Truth**: All Netlify configuration in one file
2. **Future-Proofing**: Can add headers, build settings, environment contexts
3. **Documentation**: TOML is more readable and self-documenting

### Full Configuration Context

The redirect is part of the larger `netlify.toml` configuration:

```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

## Consequences

### Positive

- Clean URLs preserved (`/rules`, not `/#/rules`)
- No changes to React Router code needed
- Direct link sharing works correctly
- Browser refresh on any route works

### Negative

- Netlify-specific configuration (would need equivalent for other hosts)

### Neutral

- Real static files (in `/public`, `/dist/assets`) are served normally—the redirect only applies to paths without matching files
