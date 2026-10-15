# ADR-003: Storage Abstraction

**Status**: Accepted
**Date**: 2026-01-03

## Context

QuizzMe must persist user data (quiz answers, profile state, astro calculations) across two deployment modes:

- **Static mode**: No server, browser-only storage
- **Server mode**: Cloud persistence with Supabase

Business logic (Trait Engine, profile calculations) should not know or care where data is stored. Direct coupling to storage implementation would:

1. Require branching logic throughout the codebase
2. Make testing difficult (need real storage in tests)
3. Violate single responsibility principle

## Decision

Abstract storage behind a **common interface** in `/packages/storage`.

### Interface Definition

```typescript
// /packages/storage/src/types.ts
export interface Store {
  // Profile operations
  getProfile(userId: string): Promise<ProfileSnapshot | null>;
  saveProfile(userId: string, profile: ProfileSnapshot): Promise<void>;

  // Quiz answer operations
  saveQuizAnswers(userId: string, quizId: string, answers: QuizAnswers): Promise<void>;
  getQuizAnswers(userId: string, quizId: string): Promise<QuizAnswers | null>;

  // Astro data (server mode only - graceful null in static)
  getAstroProfile(userId: string): Promise<AstroProfile | null>;
  saveAstroProfile(userId: string, astro: AstroProfile): Promise<void>;
}
```

### Implementations

```
/packages/storage/
  src/
    types.ts           # Store interface
    local-store.ts     # LocalStorage implementation
    supabase-store.ts  # Supabase implementation
    index.ts           # Factory function
```

### Factory Pattern

```typescript
// /packages/storage/src/index.ts
export function createStore(mode: 'static' | 'server'): Store {
  if (mode === 'static') {
    return new LocalStorageStore();
  }
  return new SupabaseStore();
}
```

### Usage in Domain

```typescript
// Domain code - storage agnostic
export async function contributeQuizAnswers(
  store: Store,
  userId: string,
  quizId: string,
  answers: QuizAnswers
): Promise<ProfileSnapshot> {
  await store.saveQuizAnswers(userId, quizId, answers);
  const updatedProfile = calculateProfile(answers);
  await store.saveProfile(userId, updatedProfile);
  return updatedProfile;
}
```

## Consequences

### Positive

- **Decoupled business logic**: Domain layer never imports storage implementations
- **Testability**: Mock Store for unit tests
- **Swappable**: Can add IndexedDB, SQLite, or other backends without touching domain
- **Type safety**: Interface enforces contract across implementations

### Negative

- **Interface maintenance**: Changes require updating all implementations
- **Abstraction overhead**: Simple operations go through interface layer
- **Feature asymmetry**: Some operations only work in server mode

### Feature Asymmetry Handling

```typescript
// LocalStorageStore
async getAstroProfile(_userId: string): Promise<AstroProfile | null> {
  // Not available in static mode - graceful null
  return null;
}

async saveAstroProfile(_userId: string, _astro: AstroProfile): Promise<void> {
  // No-op in static mode - logged warning in dev
  console.warn('[Storage] Astro profiles not persisted in static mode');
}
```

## Database Schema (Supabase)

```sql
-- /services/migrations/001_initial.sql
CREATE TABLE psyche_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  snapshot JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE astro_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  compute_hash TEXT NOT NULL,
  data JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE quiz_answers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  quiz_id TEXT NOT NULL,
  answers JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## References

- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
- [Supabase JavaScript Client](https://supabase.com/docs/reference/javascript)
