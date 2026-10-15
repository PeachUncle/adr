# ADR-004: Security — Authentication and Row-Level Security Policies

**Date:** 2025-10-27  
**Related ADRs:**  
- [ADR-001: Offline-First Architecture](./adr-001-offline-first-decision.md)
- [ADR-003: Offline-First Sync with PowerSync and Supabase](./adr-003-offline-sync.md)

---

## 1. Context

Our app stores user-specific data in a central Supabase PostgreSQL database. Users must be able to:

- Access only their own data.  
- Authenticate securely.  
- Ensure offline-first operations are eventually validated against server rules.  

We need a security model that enforces:

1. **Authentication:** Verify user identity before allowing API access.  
2. **Row-Level Security (RLS):** Restrict database operations at the row level so each user can only read or write their own data.

---

## 2. Decision

Use **Supabase Auth** for authentication and **PostgreSQL Row-Level Security (RLS)** for per-row access control on all tables containing sensitive or user-specific data.  

---

## 3. Rationale

### Authentication (Supabase Auth / GoTrue)

- Provides email/password, OAuth, magic links, and social login.  
- Issues **JWT tokens** for each user session.  
- Integrated with Supabase PostgREST endpoints, allowing secure server calls from the client.  
- Supports **token refresh** for long-lived sessions.  

**Why needed:**  
Without authentication, any client could read or modify any data. Supabase Auth ensures all requests are tied to a verified user.

### Row-Level Security (RLS)

- PostgreSQL feature that restricts which rows a user can read or modify.  
- Policies are defined per table and enforced **inside the database**, not in application code.  
- Works in tandem with Supabase Auth by using `auth.uid()` in policies to map the logged-in user to their data.

**Example:** Allow users to only access their own notes:

```sql
-- Enable RLS on the notes table
ALTER TABLE public.notes ENABLE ROW LEVEL SECURITY;

-- Policy: users can only access their own notes
CREATE POLICY "Users can manage their own notes"
ON public.notes
FOR ALL
USING (user_id = auth.uid());

-- Optional: automatically assign new notes to the authenticated user
CREATE POLICY "Insert notes with auth.uid()"
ON public.notes
FOR INSERT
WITH CHECK (user_id = auth.uid());
```

**Why needed:**  
- Protects sensitive data at the **database level**, independent of the client implementation.  
- Ensures offline operations cannot bypass security rules once synced.  
- Prevents privilege escalation or accidental data leaks in multi-user environments.

---

## 4. Combined Security Model

1. Client authenticates via **Supabase Auth** → receives JWT token.  
2. Client uses JWT in API requests (PostgREST / RPC endpoints).  
3. PostgreSQL enforces **RLS policies** on every operation:  
   - Only rows belonging to `auth.uid()` are accessible.  
   - Inserted rows automatically assigned to the authenticated user.  
   - Updates or deletes checked for ownership.

---

## 5. Additional Considerations

- **Offline-first scenario:** Local DB can store changes before syncing. Security is enforced **when operations reach the server**. PowerSync ensures eventual consistency and validates each operation.  
- **Storage Security:** Supabase Storage uses the same Auth + RLS model for object access. Only authorized users can access their files.  
- **Auditing & Logging:** Database logs record who performed each operation (via `auth.uid()`) for audit and debugging purposes.  
- **Token Expiry & Refresh:** Ensure mobile clients handle token refresh automatically to prevent unauthorized API errors.

---

## 6. Implications

- All tables with sensitive or user-specific data must have **RLS enabled**.  
- Supabase Auth is required for every API call; JWT tokens must be stored securely on the client.  
- Local DB operations are temporary and **cannot bypass server security** — eventual consistency is enforced by PowerSync.  
- Developers must design offline workflows assuming some operations may be rejected when synced due to security policies.