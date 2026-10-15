# ADR: V2 RBAC Implementation

* Status: Proposed
* Date: 2025-04-19

## Context

The V2 specification requires Role-Based Access Control (RBAC) to support distinct user roles (Admin, Participant, Judge, Team Member) with specific permissions (Req 3.1.2). The existing system uses Supabase Auth (Magic Link) but lacks granular role enforcement beyond basic authentication for the admin section. We need a way to manage roles and enforce permissions across the application (frontend routes, backend data access).

## Decision

We will implement RBAC by:
1.  Creating a `profiles` table in Supabase, linked one-to-one with `auth.users`.
2.  Adding a `role` column (e.g., using a PostgreSQL `ENUM` type: `user_role AS ENUM ('admin', 'participant', 'judge', 'team_member')`) to the `profiles` table.
3.  Assigning roles initially manually via Supabase Studio or a future admin interface.
4.  Enforcing roles via:
    *   **Next.js Middleware:** Checking the user's session and role (fetched from the `profiles` table) for protected routes (e.g., `/admin`, `/judge`, `/submit`) and redirecting if unauthorized.
    *   **Supabase Row Level Security (RLS):** Implementing policies on relevant tables (e.g., `submissions`, `teams`, `profiles`, `team_notes`) based on the user's role retrieved via `auth.uid()` and a lookup in the `profiles` table.

## Consequences

*   **Pros:**
    *   Leverages existing Supabase infrastructure (Auth, DB).
    *   Centralizes role definition and assignment.
    *   Enables fine-grained data access control via RLS.
    *   Provides route protection via middleware.
    *   Relatively straightforward to implement compared to integrating a third-party RBAC system.
    *   Allows for future automation of role assignment (e.g., based on registration status).
*   **Cons:**
    *   Requires careful implementation and testing of RLS policies and middleware logic.
    *   Initial role assignment is manual.
    *   Fetching the role might add a small overhead to requests/data access checks (though Supabase is generally efficient).