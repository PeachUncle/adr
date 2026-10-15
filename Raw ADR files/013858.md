# ADR: V2 Registration System Implementation

* Status: Proposed
* Date: 2025-04-19

## Context

The V1 platform used an embedded Google Form for registration, requiring manual data export/import. The V2 specification requires a built-in registration system (Req 3.2) to streamline the process, collect enhanced data fields (Req 3.2.4) for team formation and personalization, and integrate directly with the platform's user accounts and database.

## Decision

We will replace the Google Form embed with a built-in, multi-step registration form within the Next.js application (`/register` route).
1.  **Form Implementation:** Use Next.js Server Components for structure and Client Components for interactive form elements, potentially breaking the form into logical steps managed by client state.
2.  **Data Submission:** Use Next.js Server Actions for secure form submission and validation.
3.  **Database Schema:** Extend the existing `registrations` table or create a related `registration_details` table in Supabase to store the new V2 fields (e.g., `prior_courses`, `preferred_working_style`, `skill_writing`, etc., using appropriate types like `text[]`, `integer`, `enum`).
4.  **User Linking:** Associate registration data with the authenticated user's profile (`profiles` table or `auth.users`).

## Consequences

*   **Pros:**
    *   Eliminates manual data handling associated with Google Forms.
    *   Keeps all participant data within the platform's database.
    *   Enables direct use of registration data for team formation algorithms and gamification personalization.
    *   Allows for a more integrated and potentially better user experience (e.g., multi-step form).
    *   Aligns with the strategy of using Supabase as the primary backend.
*   **Cons:**
    *   Requires development effort to build the form UI, validation logic, and Server Actions.
    *   The multi-step form needs careful UX design to avoid overwhelming users.
    *   Increases the complexity of the application compared to embedding an external form.