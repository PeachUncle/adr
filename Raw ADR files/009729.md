# ADR-006: Authentication Strategy

## Status

**Accepted** - 2026-01-01

## Context

The game requires an authentication system that:
- Allows instant play without account creation (guest mode)
- Provides optional account registration for stat persistence
- Enables guest-to-account upgrade without losing session
- Supports banning and moderation

## Decision Drivers

- **Friction**: Minimize barriers to play
- **Persistence**: Stats/ratings require accounts
- **Security**: Prevent impersonation and abuse
- **Moderation**: Enable user banning
- **Upgrade Path**: Guests should easily become accounts

## Considered Options

### Option 1: Supabase Auth with Anonymous + Regular (Selected)

**Pros**:
- Anonymous auth provides guest sessions with real user IDs
- Seamless upgrade to email/OAuth accounts
- Built-in session management
- Works with RLS policies
- JWT-based, works with Edge Functions

**Cons**:
- Anonymous users count toward MAU limits
- Must handle anonymous user cleanup

### Option 2: Custom Guest Tokens + Supabase Auth

**Pros**:
- More control over guest sessions
- Guests don't count as Supabase users

**Cons**:
- Complex upgrade flow
- Two authentication systems to maintain
- RLS doesn't apply to guests

### Option 3: Required Accounts Only

**Pros**:
- Simpler implementation
- All users fully identified
- Easy moderation

**Cons**:
- High friction, lower conversion
- Users abandon before playing
- Against product requirements

## Decision

**We will use Supabase Auth with anonymous authentication for guests, upgradeable to email/password or OAuth.**

### User Flow

```
Landing Page
     │
     ├─► "Play as Guest"
     │        │
     │        ▼
     │   Enter Display Name
     │        │
     │        ▼
     │   createAnonymousUser()
     │        │
     │        ▼
     │   Redirect to Lobby
     │        │
     │        └─► Later: "Create Account"
     │                    │
     │                    ▼
     │             linkIdentity(email/password)
     │                    │
     │                    ▼
     │             Account Linked (same user_id)
     │
     ├─► "Sign In"
     │        │
     │        ▼
     │   Email/Password or OAuth
     │        │
     │        ▼
     │   Redirect to Lobby
     │
     └─► "Register"
              │
              ▼
         Email/Password
              │
              ▼
         Email Verification
              │
              ▼
         Redirect to Lobby
```

### Implementation

```typescript
// Guest login
async function loginAsGuest(displayName: string) {
  const { data, error } = await supabase.auth.signInAnonymously();
  if (error) throw error;

  // Set display name in profile
  await supabase
    .from('users')
    .update({ display_name: displayName, is_guest: true })
    .eq('id', data.user.id);

  return data.user;
}

// Upgrade to full account
async function upgradeAccount(email: string, password: string) {
  const { data, error } = await supabase.auth.updateUser({
    email,
    password
  });
  if (error) throw error;

  // Mark as non-guest
  await supabase
    .from('users')
    .update({ is_guest: false })
    .eq('id', data.user.id);

  return data.user;
}
```

### Database Schema

```sql
-- users table (extends Supabase auth.users)
CREATE TABLE users (
  id UUID PRIMARY KEY REFERENCES auth.users(id),
  username TEXT UNIQUE,          -- NULL for guests
  display_name TEXT NOT NULL,
  avatar_url TEXT,
  is_guest BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Trigger to create user record on auth signup
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, display_name, is_guest)
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data->>'display_name', 'Player'),
    NEW.is_anonymous
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();
```

## Rationale

1. **Supabase Anonymous Auth**: Provides real user IDs for guests, enabling RLS policies and consistent data model.

2. **Same User ID on Upgrade**: When guest upgrades, user_id stays the same. Stats, game history preserved.

3. **JWT Everywhere**: Same token format for guests and accounts. Edge Functions don't need special handling.

4. **Moderation Ready**: Even guests have user_ids, enabling bans and reports.

5. **Industry Pattern**: Anonymous-to-authenticated upgrade is common in gaming (similar to Firebase Anonymous Auth).

## Consequences

### Positive
- Zero-friction guest play
- Seamless upgrade path
- Unified user model
- RLS works for all users
- Ban system works for guests

### Negative
- Anonymous users count toward Supabase MAU
- Need cleanup job for abandoned guests
- Slightly more complex than accounts-only

### Guest Cleanup Strategy

```sql
-- Delete anonymous users who:
-- 1. Never played a game
-- 2. Created more than 30 days ago
-- 3. Never upgraded to account

DELETE FROM auth.users
WHERE is_anonymous = true
  AND id NOT IN (SELECT DISTINCT user_id FROM game_players)
  AND created_at < NOW() - INTERVAL '30 days';
```

## Security Considerations

| Concern | Mitigation |
|---------|------------|
| Guest spam | Rate limit guest creation by IP |
| Ban evasion | Track IP alongside user_id |
| Session hijacking | Short JWT expiry, refresh tokens |
| Account takeover | Email verification on upgrade |

## Related Decisions

- ADR-001: Real-time Architecture (auth for channels)
- ADR-003: Game Logic Location (auth in Edge Functions)
