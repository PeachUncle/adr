# ADR-004: Auth Flow Architecture Migration

## Context

The original authentication flow used a modal-based approach with `AuthComponent.jsx` and `SignupModal.tsx` components that appeared as overlays in the navbar. This approach had several limitations:
- Inconsistent styling between modal and main site
- Security concerns with API calls to localhost:8000 for storing user background data
- Complex session management between modal and main app
- Poor user experience with modal overlay approach

## Decision

We decided to migrate from a modal-based authentication flow to separate themed page-based authentication with Better Auth metadata storage approach.

## Approach

1. **Component Structure Change**:
   - Removed modal-based components (AuthComponent.jsx, SignupModal.tsx)
   - Created separate page-based auth flows (signup.tsx, signin.tsx)
   - Implemented proper routing for auth pages

2. **UI/UX Improvements**:
   - Applied consistent Matrix-style theming to both auth pages
   - Added proper error handling and validation
   - Implemented responsive design with proper form layouts

3. **Data Storage Migration**:
   - Replaced localhost API calls with Better Auth metadata approach
   - Store user personalization data directly in auth service
   - Eliminated security concerns with localhost API calls

4. **Integration**:
   - Personalization questions integrated directly into signup flow
   - Proper redirects after authentication
   - Consistent session management

## Consequences

### Positive
- ✅ Improved security by eliminating localhost API calls
- ✅ Consistent UI/UX with proper theming
- ✅ Better maintainability with page-based architecture
- ✅ Simplified session management
- ✅ Enhanced user experience with dedicated auth pages

### Negative
- ❌ Requires navbar integration component to handle auth state
- ❌ Migration from existing modal approach may require user re-education
- ❌ Additional routing considerations

### Neutral
- ⚪ Changes require updates to navigation integration
- ⚪ Existing auth functionality preserved

## Status

Implemented in branch `004-better-auth-implementation`

## Date

2025-12-18

## Decision Makers

- Development team