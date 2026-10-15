# ADR-002: Directory Structure Standardization

## Status

Accepted (2025-06-17)

## Context

The AI Logo Generator codebase contained duplicate directory structures with both `/app` and `/src/app` folders, which created several problems:

1. **Confusion**: Developers were unsure which directory should contain new components
2. **Maintenance Burden**: Changes had to be synchronized across multiple locations
3. **Import Inconsistency**: Some files used imports from `/app` while others from `/src/app`
4. **Non-Standard Patterns**: Next.js 14+ recommends the App Router directly at the project root

Both directories contained similar files:
- Page components (`page.tsx`)
- Layout definitions (`layout.tsx`) 
- Global styles (`globals.css`)
- API routes (`api/generate-logo/route.ts`)

However, the `/app` directory contained the production-ready implementation of the logo generator interface, while `/src/app` contained mostly the default Next.js template with an older implementation of the API routes.

## Decision

We will standardize on the `/app` directory structure at the project root, following Next.js 14+ best practices for the App Router.

This involves:
1. Using the existing `/app` directory for all App Router components
2. Migrating any unique functionality from `/src/app` to `/app` (notably the download API endpoint)
3. Updating configuration to explicitly support this structure
4. Deprecating and eventually removing the `/src/app` directory

## Consequences

### Positive

1. **Simplified Structure**: Clear and unambiguous location for App Router components
2. **Standardized Pattern**: Follows Next.js 14+ best practices for App Router
3. **Reduced Confusion**: Developers have a single source of truth for component location
4. **Improved Imports**: All imports can consistently use the `@/` alias from project root
5. **Better Onboarding**: New developers will find a standard, recognizable structure

### Negative

1. **Migration Effort**: Required careful analysis and migration of unique functionality
2. **Potential Breaking Changes**: Risk of breaking functionality during migration
3. **Legacy References**: Some documentation or older code might still reference the old structure

## Implementation Notes

1. **Migrated Files**:
   - `/src/app/api/download/route.ts` → `/app/api/download/route.ts`

2. **Retained Files**:
   - `/app/page.tsx` (Production logo generator interface)
   - `/app/api/generate-logo/route.ts` (Current streaming API implementation)

3. **Configuration**:
   - Updated `next.config.ts` with improved settings for the standard structure

4. **Future Cleanup**:
   - Remove `/src/app` directory after confirming all functionality is working correctly

## References

- [Next.js App Router Documentation](https://nextjs.org/docs/app)
- [Next.js Project Organization](https://nextjs.org/docs/app/building-your-application/routing/colocation)