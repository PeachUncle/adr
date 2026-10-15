# ADR-003: Simplified Architecture (No Backend)

**Status:** Accepted  
**Date:** 2025-12-16  
**Deciders:** Development Team

## Context

The original plan (see [Development Plan](../archive/development-plan.md)) included:
- Flutter mobile/web client
- Node.js/TypeScript backend service
- Supabase for database and auth
- Backend handling aggregations, exports, and analytics

However, this introduced significant complexity:
- Need to maintain and deploy a Node.js service
- Extra layer of authentication and authorization
- More points of failure (client ↔ backend ↔ Supabase)
- Harder to develop and test locally
- Increased hosting costs

For a volleyball stats app used by individual coaches, a simpler architecture could meet all requirements without the overhead.

## Decision

We will use a **simplified architecture with no backend service**:

1. **Flutter client does all processing locally** - Aggregations, calculations, exports happen in Dart
2. **Direct Supabase connection** - Client talks directly to Supabase for cloud sync (when online)
3. **Row Level Security (RLS)** - Supabase RLS policies protect coach data without backend middleware
4. **Edge Functions for complex operations** - Only if truly needed (e.g., scheduled aggregations)
5. **Client-side exports** - Generate CSV/PDF directly in Flutter using packages like `csv`, `pdf`

## Consequences

### Positive
- **Simpler deployment** - Only need to deploy Flutter web app, no backend service
- **Lower costs** - No backend hosting, only Supabase free tier or modest paid plan
- **Faster development** - One codebase (Dart) instead of two (Dart + TypeScript)
- **Better offline experience** - All logic runs locally, no dependence on backend availability
- **Easier testing** - Test Flutter app in isolation without mocking backend APIs
- **Faster performance** - No backend round-trips, calculations happen on device

### Negative
- **Limited server-side processing** - Can't run scheduled jobs or background tasks easily
- **Client bundle size** - More logic in Flutter app increases size
- **Calculation limits** - Very large datasets (years of matches) might be slow on device
- **Code duplication risk** - If we add admin tools later, might duplicate logic

### Neutral
- **Supabase Edge Functions** - Available if we need server-side processing later
- **RLS complexity** - Need careful RLS policy design, but would need similar auth logic in backend anyway
- **Analytics limitations** - Device-side analytics are fine for single coach; multi-coach analytics would need rethinking

## Alternatives Considered

1. **Full Backend Service (Original Plan)**
   - **Rejected**: Too complex for single-coach use case, overkill for MVP
   - Could revisit if we build multi-coach/team features later

2. **Firebase Functions**
   - **Rejected**: Would lock us into Firebase ecosystem; we already chose Supabase
   - Firebase and Supabase serve similar purposes

3. **GraphQL API (Hasura)**
   - **Rejected**: Another service to maintain, Supabase REST API + RLS is sufficient
   - GraphQL is overkill for simple CRUD and queries

## References

- [Simplified Development Plan](../archive/simplified-dev-plan.md) - Revised plan without backend
- [Repository Guidelines](../guidelines.md) - Notes simplified architecture
- Supabase RLS: `supabase/migrations/` - Database migrations with RLS policies
- Flutter packages: `supabase_flutter` for direct database access
- Export packages: `csv`, `pdf`, `path_provider` for local file generation

