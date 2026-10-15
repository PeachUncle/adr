# ADR 0003: Use Supabase as Backend-as-a-Service

**Status**: Accepted

**Date**: 2025-11-08 (Documented retroactively)

**Deciders**: AI Agent (with user approval)

## Context

Both applications needed:
- Persistent cloud storage
- Real-time data synchronization potential
- Low setup/maintenance overhead
- Cost-effective solution for personal projects

### Options Considered

1. **Custom Backend** - Build Express/NestJS API + PostgreSQL
2. **Firebase** - Google's BaaS platform
3. **Supabase** - Open-source Firebase alternative
4. **AWS Amplify** - AWS's BaaS offering

## Decision

Use **Supabase** as the Backend-as-a-Service platform.

## Rationale

### Chosen: Supabase

**Advantages**:
- ✅ **PostgreSQL Database**: Full SQL capabilities, not NoSQL limitations
- ✅ **Open Source**: Can self-host if needed
- ✅ **Generous Free Tier**: Perfect for personal projects
- ✅ **TypeScript SDK**: Excellent DX with type inference
- ✅ **Row-Level Security**: Built-in data access control (not yet utilized)
- ✅ **Real-time Subscriptions**: Available for future features
- ✅ **Auto-Generated APIs**: RESTful and GraphQL endpoints
- ✅ **Authentication**: Built-in auth system (not yet implemented)
- ✅ **File Storage**: Blob storage if needed later

**Disadvantages**:
- ⚠️ Vendor lock-in (mitigated by PostgreSQL underneath)
- ⚠️ Less mature than Firebase (but improving rapidly)

### Rejected: Custom Backend

**Why Rejected**:
- Significant development effort for auth, DB migrations, API
- Infrastructure setup and maintenance
- Not cost-effective for personal projects
- Overkill for current requirements

### Rejected: Firebase

**Why Rejected**:
- NoSQL Firestore limitations vs. relational PostgreSQL
- Pricing less predictable for read-heavy workloads
- Less SQL-friendly (Firestore not relational)

### Rejected: AWS Amplify

**Why Rejected**:
- More complex setup
- Steeper learning curve
- AWS cost management complexity

## Consequences

### Positive

**Rapid Development**:
- Database tables created via SQL schema files
- No backend API code to write or maintain
- Built-in admin UI for data management

**TypeScript Integration**:
```typescript
const { data, error } = await supabase
  .from('events')
  .select('*')
  .gte('start_date', today);
```

**Future-Proof**:
- Can add auth with minimal code changes
- Real-time subscriptions ready to use
- File storage available if needed

### Negative

**Bundle Size**: Supabase SDK adds ~80KB to bundle
- Acceptable for personal apps
- Could be optimized with tree-shaking

**Direct Database Access**: No API layer abstraction
- Risk: Schema changes directly impact frontend
- Mitigation: Careful schema design, RLS when multi-tenant

**Not Implemented Yet**:
- ⚠️ Authentication (currently anonymous access)
- ⚠️ Row-Level Security policies
- ⚠️ Real-time subscriptions

### Neutral

**Fallback Strategy**: Family Calendar has localStorage fallback
```typescript
if (!this.supabaseService.isConfigured()) {
  this.loadEventsFromStorage();
}
```

## Implementation

**Current Usage**:

**Reward Chart Schema**:
```sql
CREATE TABLE family_members (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  type TEXT NOT NULL, -- 'child' or 'parent'
  color TEXT,
  display_order INTEGER
);

CREATE TABLE stars (
  id UUID PRIMARY KEY,
  family_member_id UUID REFERENCES family_members,
  day TEXT NOT NULL,
  habit_id UUID REFERENCES habits,
  week_start DATE NOT NULL
);
```

**Service Pattern**:
```typescript
@Injectable({ providedIn: 'root' })
export class SupabaseService {
  private supabase: SupabaseClient;

  async insertStar(starData: StarData) {
    const { data, error } = await this.supabase
      .from('stars')
      .insert(starData);
    return { data, error };
  }
}
```

## Follow-up

- 🔲 Implement Supabase Auth for multi-user support
- 🔲 Add Row-Level Security policies
- 🔲 Consider real-time subscriptions for family calendar
- 🔮 Future: Extract Supabase service into shared library

## References

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase JS Client](https://supabase.com/docs/reference/javascript/introduction)
- Database Schemas: `docs/supabase-schema.sql`, `docs/supabase-schema-simple.sql`
- Implementation: `apps/*/src/app/services/supabase.service.ts`
