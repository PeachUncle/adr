# ADR 008: Favorites System with MongoDB Persistence

**Date:** 2025-11-02  
**Status:** Implemented  
**Decision Makers:** Engineering Team  
**Tags:** `feature`, `database`, `authentication`, `ux`

---

## Context

The existing favorites system used browser `localStorage` for storing user's favorite prompts. This approach had several critical flaws:

### Problems with localStorage Approach:

1. **Data Loss:** Favorites lost when browser data cleared
2. **No Sync:** Can't access favorites across devices
3. **No Auth Required:** Anyone can "favorite" but meaningless
4. **No Analytics:** Can't track which prompts are actually valuable
5. **Inconsistent UX:** Heart icon on cards, star icon in modal
6. **Not Enterprise-Ready:** Fake data anti-pattern

### Business Requirements:

- Users need persistent favorites across sessions/devices
- Product team needs engagement metrics (which prompts are popular)
- Marketing wants to showcase "most favorited" prompts
- Enterprise customers expect professional, persistent data

---

## Decision

Implement a **MongoDB-backed favorites system** with the following architecture:

### 1. Database Schema

```typescript
// User collection (already exists)
{
  _id: ObjectId,
  email: string,
  favoritePrompts: string[],  // ✓ Already in schema
  ...
}
```

**Rationale:** Leverage existing `favoritePrompts` field in user profile schema (`src/lib/schemas/user-profile.ts` line 22).

### 2. API Endpoints

**`GET /api/favorites`**

- Returns array of prompt IDs for authenticated user
- Rate limited (authenticated tier)
- No RBAC required (user's own data)

**`POST /api/favorites`**

- Add prompt to favorites
- Validates prompt exists and is active
- Uses `$addToSet` to prevent duplicates
- Audit logged: `user.favorite.added`

**`DELETE /api/favorites`**

- Remove prompt from favorites
- Uses `$pull` for atomic removal
- Audit logged: `user.favorite.removed`

**Common Features:**

- Zod schema validation
- Rate limiting (prevents abuse)
- Audit logging (compliance)
- Optimistic UI updates with rollback

### 3. Frontend Hook (`useFavorites`)

```typescript
export function useFavorites() {
  const { data: session } = useSession();

  // Authenticated: MongoDB via API
  // Non-auth: localStorage (legacy fallback)

  return {
    favorites: string[],
    isAuthenticated: boolean,
    toggleFavorite: (id: string) => Promise<void>,
    isFavorite: (id: string) => boolean,
  };
}
```

**Key Features:**

- Graceful degradation for non-auth users
- Optimistic updates (instant UI feedback)
- Error rollback (revert on API failure)
- `useSession` integration for auth state

### 4. UI Consistency

- **Heart Icon Everywhere:** Remove star from modal
- **Proper Labels:** "Testing" not "testing", "Engineer" not "engineer"
- **Auth Gating:** Non-auth users see "Sign in to save" toast

---

## Consequences

### ✅ Positive:

1. **Real Data Persistence**
   - Favorites survive browser clear
   - Sync across all devices
   - Professional enterprise feature

2. **Engagement Analytics**
   - Track which prompts are most favorited
   - Inform content strategy
   - Show "Popular Prompts" section

3. **Better UX**
   - Consistent heart icon
   - Clear auth requirements
   - Instant feedback (optimistic updates)

4. **Enterprise Compliance**
   - Audit logging for all actions
   - Rate limiting prevents abuse
   - Zod validation ensures data integrity

### ⚠️ Negative:

1. **Auth Requirement**
   - Non-auth users can't save (by design)
   - Slight friction for anonymous visitors
   - **Mitigation:** Show clear "Sign in" prompt

2. **Increased Complexity**
   - API endpoints to maintain
   - Auth state management
   - Error handling and rollback logic

3. **Performance Considerations**
   - Extra API calls on page load
   - MongoDB queries for large favorite lists
   - **Mitigation:**
     - Client-side caching
     - Optimistic updates
     - Consider pagination for 100+ favorites

### 🔄 Trade-offs:

| Aspect            | localStorage | MongoDB      |
| ----------------- | ------------ | ------------ |
| Setup Complexity  | Simple       | Medium       |
| Data Persistence  | ❌ Ephemeral | ✅ Permanent |
| Cross-Device Sync | ❌ No        | ✅ Yes       |
| Analytics         | ❌ No        | ✅ Yes       |
| Auth Required     | ❌ No        | ✅ Yes       |
| Performance       | ⚡ Instant   | 🌐 Network   |
| Enterprise-Ready  | ❌ No        | ✅ Yes       |

**Winner:** MongoDB (enterprise requirements outweigh complexity)

---

## Implementation Details

### Files Modified:

- `src/app/api/favorites/route.ts` (NEW)
- `src/hooks/use-favorites.ts` (UPDATED)
- `src/components/features/PromptCard.tsx` (UPDATED)
- `src/components/features/PromptDetailModal.tsx` (UPDATED)

### Audit Events:

- `user.favorite.added` - User adds prompt to favorites
- `user.favorite.removed` - User removes prompt from favorites

### Rate Limits:

- Authenticated users: Default tier limits
- Anonymous: Not applicable (401 Unauthorized)

### Testing Requirements:

- [ ] Unit tests for `useFavorites` hook
- [ ] Integration tests for `/api/favorites` endpoints
- [ ] E2E test: Add favorite → sync across tabs
- [ ] E2E test: Non-auth user sees "Sign in" prompt

---

## Alternatives Considered

### 1. **Keep localStorage Only**

- ❌ **Rejected:** Not enterprise-ready, no analytics, data loss issues

### 2. **Hybrid: localStorage + Background Sync**

- ❌ **Rejected:** Complex race conditions, eventual consistency issues

### 3. **Client-Side Cookies**

- ❌ **Rejected:** Size limits (4KB), same device-only issue

### 4. **IndexedDB**

- ❌ **Rejected:** Still browser-only, no cross-device sync

### 5. **Third-Party Service (e.g., Firebase)**

- ❌ **Rejected:** Additional cost, vendor lock-in, already have MongoDB

---

## Future Enhancements

1. **Dashboard Integration**
   - Show "My Favorites" collection
   - Display favorite count in stats
   - "Recently Favorited" section

2. **Popularity Metrics**
   - Track global favorite counts per prompt
   - Show "Most Favorited" prompts
   - Use for content curation

3. **Batch Operations**
   - Add multiple prompts at once
   - Export favorites as JSON/CSV
   - Import from other platforms

4. **Smart Recommendations**
   - "Users who favorited X also liked Y"
   - ML-based prompt suggestions
   - Personalized homepage

5. **Offline Support**
   - Service worker for offline favorites
   - Sync when back online
   - Conflict resolution

---

## References

- [MongoDB `$addToSet` documentation](https://www.mongodb.com/docs/manual/reference/operator/update/addToSet/)
- [Next.js Server Actions best practices](https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations)
- [Optimistic UI updates pattern](https://www.apollographql.com/docs/react/performance/optimistic-ui/)
- User Profile Schema: `src/lib/schemas/user-profile.ts`
- Enterprise Compliance: `docs/ENTERPRISE_COMPLIANCE_AUDIT_DAY5.md`

---

## Related ADRs

- ADR 001: MongoDB as Primary Database
- ADR 003: Authentication with NextAuth.js
- ADR 005: Rate Limiting Strategy
- ADR 007: Audit Logging System

---

**Last Updated:** 2025-11-02  
**Review Date:** 2025-12-02 (1 month)
