# Design Document: Static SPA Conversion

## Context

The Music Learning Games application is currently structured as a full-stack monorepo with:
- Express.js backend server
- React frontend (SPA)
- Vite for development and building
- Database infrastructure (Drizzle ORM + PostgreSQL) that is unused
- Session management infrastructure that is unused

However, the application actually:
- Makes zero API calls to the backend
- Stores no data server-side
- Has no authentication or user management
- Generates all audio client-side via Web Audio API
- Manages all game state in browser memory

This creates a mismatch between the architecture and actual usage, resulting in unnecessary complexity.

## Goals / Non-Goals

### Goals
- Eliminate all server-side code and dependencies
- Enable deployment to free static hosting platforms
- Simplify development workflow
- Maintain 100% feature parity with current application
- Support client-side routing on static hosts
- Reduce deployment complexity to a single command

### Non-Goals
- Adding new features or changing game behavior
- Implementing data persistence (can be done later with localStorage)
- Adding authentication or user accounts
- Changing the UI or UX
- Modifying the build tool (staying with Vite)

## Decisions

### Decision 1: Pure Static SPA Approach
**Choice**: Remove all server code and deploy as a static SPA served from CDN/static host.

**Rationale**:
- Application already works entirely client-side
- No backend functionality is actually used
- Static hosting is free on multiple platforms
- Better performance (CDN edge caching)
- Simpler mental model for contributors

**Alternatives considered**:
1. Keep minimal Express server - Rejected: Adds unnecessary complexity and hosting cost
2. Serverless functions - Rejected: No backend logic to execute
3. Static site with service worker - Deferred: Can add PWA features later if needed

### Decision 2: Use Vite's Native Dev Server
**Choice**: Use `vite` command directly instead of Express + Vite middleware.

**Rationale**:
- Vite's dev server has all features needed (HMR, SPA fallback)
- Removes 200+ lines of server code
- Standard Vite workflow familiar to most developers
- Faster startup and reload times

**Alternatives considered**:
1. Keep Express for development - Rejected: Unnecessary complexity
2. Use other dev servers (webpack-dev-server, etc.) - Rejected: Vite already chosen

### Decision 3: Client-Side Routing Configuration
**Choice**: Add configuration files for popular static hosts (Netlify, Vercel, GitHub Pages).

**Rationale**:
- Static hosts need to redirect all routes to index.html for SPA routing
- Different platforms use different configuration formats
- Adding config files makes deployment "just work"

**Configuration approach**:
- **Netlify**: `public/_redirects` file with `/* /index.html 200`
- **Vercel**: `vercel.json` with rewrites configuration
- **GitHub Pages**: Documentation for using 404.html trick or GitHub Actions

### Decision 4: Dependency Cleanup Strategy
**Choice**: Remove all server-related dependencies from package.json.

**Dependencies to remove**:
- Express ecosystem: express, @types/express
- Database: drizzle-orm, drizzle-zod, drizzle-kit, @neondatabase/serverless, pg-cloudflare
- Session: express-session, connect-pg-simple, memorystore, passport, passport-local
- Server tooling: tsx (TypeScript execution), esbuild (server bundling), ws (WebSocket)

**Dependencies to keep**:
- React ecosystem
- Vite and plugins
- UI libraries (Radix, Tailwind, Framer Motion)
- Client-side utilities (date-fns, wouter, etc.)
- Testing infrastructure (Vitest, Testing Library)

### Decision 5: Script Simplification
**Choice**: Update npm scripts to use Vite commands directly.

**New scripts**:
```json
{
  "dev": "vite",
  "build": "vite build",
  "preview": "vite preview",
  "check": "tsc",
  "test": "vitest run",
  "test:watch": "vitest"
}
```

**Removed scripts**:
- `predev`: No longer needed (no port to kill)
- `start`: No server to start in production
- `db:push`: No database

## Risks / Trade-offs

### Risk 1: Losing Future Backend Capability
**Mitigation**: If backend is needed later, can easily:
- Add serverless functions (Netlify/Vercel Functions)
- Add separate API server with CORS
- Keep git history - server code can be restored

**Probability**: Low - Application design is inherently client-side (musical education games)

### Risk 2: Deployment Configuration Errors
**Mitigation**:
- Provide tested configuration for each platform
- Include comprehensive DEPLOYMENT.md
- Test on all major platforms before archiving change

**Probability**: Medium, but low impact (easy to fix)

### Risk 3: Browser Compatibility
**Mitigation**:
- No changes to client code (same browser requirements)
- Web Audio API already requires modern browsers
- Static hosting often has better CDN/edge support than custom servers

**Probability**: Very low - actually improves compatibility

### Risk 4: Performance During Build
**Mitigation**:
- Vite builds are typically faster than dual build (client + server)
- Fewer dependencies means faster npm install
- Build output is smaller without server code

**Probability**: None - this improves build performance

## Migration Plan

### Phase 1: Preparation (Current State)
- [x] Create OpenSpec proposal
- [x] Validate proposal with stakeholders
- [ ] Review and approve proposal

### Phase 2: Implementation (Estimated: 1-2 hours)
1. Remove server directory and shared directory
2. Update package.json (dependencies and scripts)
3. Simplify vite.config.ts
4. Add static hosting configuration files
5. Update .replit for Replit compatibility
6. Create DEPLOYMENT.md documentation

### Phase 3: Testing (Estimated: 30 minutes)
1. Test `npm install` (should be faster)
2. Test `npm run dev` (Vite dev server)
3. Test `npm run build` (static build)
4. Test `npm run preview` (production preview)
5. Test all game routes work
6. Test Web Audio API functionality
7. Run `npm run check` (TypeScript)
8. Run `npm test` (unit tests)

### Phase 4: Deployment Testing (Estimated: 1 hour)
1. Deploy to Netlify (test environment)
2. Deploy to Vercel (test environment)
3. Deploy to GitHub Pages (optional)
4. Verify all routes work on each platform
5. Verify Web Audio API works on each platform

### Phase 5: Documentation and Finalization
1. Update main README if needed
2. Archive OpenSpec change
3. Merge to main branch

### Rollback Plan
If issues are discovered:
1. Git revert the change commit(s)
2. Run `npm install` to restore old dependencies
3. Previous server-based setup restored
4. Investigate issue before re-attempting

**Rollback time**: < 5 minutes

## Open Questions

1. **Q**: Should we support hosting on subpaths (e.g., `example.com/games/`)?
   **A**: Not initially. Can add base path configuration if needed. Most deployments use root path.

2. **Q**: Should we add a service worker for offline capability?
   **A**: Deferred to future enhancement. Not blocking for static deployment.

3. **Q**: Should we keep drizzle.config.ts for potential future use?
   **A**: No. Clean removal is better. Can add back if needed.

4. **Q**: Do we need to update any CI/CD pipelines?
   **A**: Current project doesn't appear to have CI/CD. DEPLOYMENT.md will cover GitHub Actions option.
