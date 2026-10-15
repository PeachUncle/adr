# ADR-001: Hardcoded Community Routes for MVP

## Revision log

| Date | Description |
|------|-------------|
| 2025-12-14 | Document created |

## Context

ParkBoard implements a multi-tenant architecture where each condo community has a unique community code (e.g., `lmr_x7k9p2` for Lumiere Residences). While the database schema and authentication system support multiple communities, the MVP routing is hardcoded to the `/LMR/` path prefix instead of using dynamic routing based on the user's `session.user.communityCode`.

**Current Implementation:**
- Login redirects to `/LMR/slots` (hardcoded in `app/(auth)/login/page.tsx:122`)
- All routes use path-based prefixes: `/LMR/slots`, `/LMR/bookings`, etc.
- Community code is stored in session but not used for routing decisions
- Middleware and UI components assume single-community deployment

**Problem:**
This hardcoded approach prevents serving multiple communities from the same deployment. Each new community would require code changes and redeployment.

## Decision

We will use hardcoded `/LMR/` route prefixes for the MVP deployment instead of implementing dynamic routing based on `session.user.communityCode`.

**Rationale:**
1. **MVP Focus** - Initial deployment serves only Lumiere Residences (LMR)
2. **Reduced Complexity** - Simpler routing logic accelerates time-to-market
3. **Testing Simplicity** - Fixed URLs are easier to test (no dynamic route segments)
4. **SEO Benefits** - Consistent paths improve search engine indexing
5. **Known Migration Path** - Single-route architecture already designed (see Future Considerations)

## Consequences

**Benefits:**
- Faster MVP development and deployment
- Simpler routing logic (no middleware rewrites or dynamic segments)
- Easier to test with fixed URLs
- SEO-friendly consistent paths (`/LMR/slots` vs `/${code}/slots`)
- Clear community branding in URL structure

**Tradeoffs:**
- Cannot serve multiple communities from single deployment
- Requires code changes to add new communities
- Migration effort needed when scaling beyond LMR
- URL structure differs from long-term architecture
- Community code exposed in URLs (minor security consideration)

**Operational Implications:**
- Single-community deployment model for MVP
- New communities require separate deployments or code changes
- Future migration to single-route architecture will require:
  - Route restructuring from `/LMR/slots` to `/slots`
  - Middleware updates to extract `communityCode` from session
  - Internal link updates across all components
  - Backward compatibility redirects

## Implementation

Current implementation uses hardcoded routes in three areas:

1. **Login Redirect** (`app/(auth)/login/page.tsx:122`):
```typescript
if (result?.ok) {
  // TODO: Implement single-route architecture (/dashboard)
  // Current MVP uses path-based routing (/LMR, /SRP, etc.)
  // For now, use /LMR as default until Phase 4 migration completes
  router.push('/LMR/slots')
}
```

2. **File Structure** (`app/LMR/`):
```
app/
└── LMR/
    ├── slots/
    │   ├── page.tsx           # Browse slots
    │   ├── new/page.tsx       # Create slot
    │   └── [id]/page.tsx      # View slot details
    └── bookings/
        └── page.tsx           # User's bookings
```

3. **Navigation Links** (components use `/LMR/` prefix):
```typescript
<Link href="/LMR/slots">Browse Slots</Link>
<Link href="/LMR/bookings">My Bookings</Link>
```

## Related Decisions

This ADR relates to the overall multi-tenant architecture and future migration plans.

**Constrains**:
- **Phase 4 Migration** (documented in `docs/MULTI_TENANCY_IMPROVEMENTS.md` lines 827-872) - The single-route architecture design is constrained by this hardcoded routing decision until migration completes

## Future Considerations

### Migration to Single-Route Architecture

When expanding beyond the MVP, implement dynamic routing to eliminate hardcoded community paths:

**Target Architecture:**
- All routes use community-agnostic paths: `/slots`, `/bookings`, `/dashboard`
- Community context comes from `session.user.communityCode` (not URL)
- Middleware enforces tenant isolation via session validation
- Users see data only from their community (enforced by database queries)

**Migration Steps:**

1. **Update Route Structure**
   - Move `app/LMR/*` to `app/(community)/*` or `app/*`
   - Change paths from `/LMR/slots` to `/slots`
   - Remove community prefix from all internal links

2. **Update Middleware**
   ```typescript
   // middleware.ts
   export async function middleware(request: NextRequest) {
     const session = await auth()

     if (!session?.user?.communityCode) {
       return NextResponse.redirect(new URL('/login', request.url))
     }

     // No URL rewriting needed - community comes from session
     return NextResponse.next()
   }
   ```

3. **Update API Routes**
   ```typescript
   // No change needed - already use session.user.communityCode
   const { communityCode } = await getSessionWithCommunity()
   const slots = await db.query(
     'SELECT * FROM parking_slots WHERE community_code = $1',
     [communityCode]
   )
   ```

4. **Update Login Redirect**
   ```typescript
   if (result?.ok) {
     router.push('/slots')  // Community-agnostic path
   }
   ```

5. **Implement Backward Compatibility**
   ```typescript
   // middleware.ts - Redirect old URLs to new structure
   if (request.nextUrl.pathname.startsWith('/LMR/')) {
     const newPath = request.nextUrl.pathname.replace('/LMR/', '/')
     return NextResponse.redirect(new URL(newPath, request.url))
   }
   ```

**Benefits of Migration:**
- Support multiple communities from single deployment
- Cleaner URLs without community prefix
- Community code not exposed in browser address bar
- Simplified routing logic (no path-based tenant isolation)

**Estimated Effort:** 2-3 days for migration + testing

**Trigger for Migration:**
- Second community onboarding begins
- Product decision to unify all communities under single deployment
- Security requirement to hide community identifiers from URLs

### Alternative: Subdomain Routing

**Pattern:** `lmr.parkboard.app`, `srp.parkboard.app`

**Pros:**
- Clear community separation
- SEO benefits per community
- Supports community-specific branding

**Cons:**
- DNS configuration complexity
- SSL certificate management per subdomain
- Increased infrastructure cost
- More complex deployment pipeline

**Decision:** Defer to post-MVP. Single-route architecture is simpler and achieves same isolation goals.

## Appendix A: Related Architecture Documents

### Multi-Tenant Architecture
- **`docs/MULTI_TENANCY_IMPLEMENTATION_SUMMARY.md`** - Complete implementation overview of multi-tenant system
- **`docs/MULTI_TENANCY_IMPROVEMENTS.md` (lines 827-872)** - Single-route architecture design specification
- **`docs/SECURITY_ARCHITECTURE.md`** - Tenant isolation enforcement patterns

### Authentication Flow
- **`lib/auth/auth.ts`** - NextAuth.js configuration with community code in session
- **`app/(auth)/login/page.tsx`** - Login page with hardcoded `/LMR/slots` redirect (line 122)

### Routing Structure
- **`app/LMR/`** - Hardcoded community routes directory
- **`middleware.ts`** - Route protection (currently community-agnostic)

### Database Schema
- **`db/migrations/002_multi_tenant_communities_idempotent.sql`** - Multi-tenant schema with community codes
- **`db/schema_optimized.sql`** - Current database schema (single source of truth)

## Appendix B: Security Consideration - Community Codes in URLs

**Current Situation:** The `/LMR/` prefix exposes the community abbreviation in the URL, but NOT the full community code (`lmr_x7k9p2`).

**Security Analysis:**

**What is exposed:**
- Community abbreviation (`LMR` = Lumiere)
- URL structure pattern

**What is NOT exposed:**
- Full community code with random suffix (`lmr_x7k9p2`)
- Community code is never in URL, query parameters, or browser storage
- Authentication still requires 3-field validation (Community Code + Email + Password)

**Risk Assessment:**
- **Low Risk** - Abbreviation alone is insufficient for unauthorized access
- Community code (`lmr_x7k9p2`) remains a shared secret distributed via trusted channels
- Enumeration attacks prevented by generic error messages
- Path prefix is primarily for routing, not authentication

**Mitigation:**
- Single-route architecture eliminates even the abbreviation from URLs
- Authentication layer remains the primary security boundary
- Defense-in-depth via application-level tenant filtering in database queries

**Conclusion:** The hardcoded `/LMR/` route prefix is acceptable for MVP. It does not weaken the security model, as authentication and tenant isolation are enforced at the application and database layers, not via URL structure.
