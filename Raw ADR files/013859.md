# ADR: V2 Submission Portal Architecture

* Status: Proposed
* Date: 2025-04-19

## Context

The V2 specification requires a submission portal (Req 3.6) accessible only to accepted team members, allowing them to upload deliverables. It also requires a judge portal (Req 3.7) for reviewing these submissions. Secure storage and access control based on roles (Team Member, Judge, Admin) are critical.

## Decision

We will implement the submission and judge portals using **Supabase Storage** for file handling and **Supabase Row Level Security (RLS)** for access control.
1.  **Storage:** Create a Supabase Storage bucket (e.g., `submissions`) to store uploaded files. Files can be organized by team ID within the bucket (e.g., `submissions/{team_id}/{file_name}`).
2.  **Metadata:** Create a `submissions` table in the Supabase database to store metadata about each upload (e.g., `id`, `team_id`, `submitter_user_id`, `file_path` in storage, `file_name`, `submitted_at`, `version`).
3.  **Access Control (RLS):**
    *   Implement RLS policies on the `submissions` metadata table:
        *   Team members can `SELECT` their own team's submissions.
        *   Team members can `INSERT` submissions linked to their `team_id`.
        *   Judges can `SELECT` all submissions.
        *   Admins can `SELECT`, `INSERT`, `UPDATE`, `DELETE` all submissions.
    *   Implement RLS policies on the Supabase Storage bucket (`submissions`):
        *   Team members can `INSERT` (upload) files into their team's path (`submissions/{team_id}/...`).
        *   Team members can `SELECT` (download) files from their team's path.
        *   Judges can `SELECT` files from any team's path.
        *   Admins can perform all operations (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) on the bucket.
4.  **Portal UI:** Create dedicated sections in the Next.js app:
    *   `/submit`: Protected route for users with the `team_member` role. UI allows file selection and upload using the Supabase Storage client library, creating a corresponding entry in the `submissions` metadata table. Displays submission history for the user's team.
    *   `/judge`: Protected route for users with the `judge` role. UI lists teams/submissions (fetched from the `submissions` table) and provides links to download files directly from Supabase Storage.
5.  **Notifications:** Use a Supabase Edge Function triggered by inserts into the `submissions` table to send email receipts (Req 3.6.5) to team members.

## Consequences

*   **Pros:**
    *   Leverages integrated Supabase features (Storage, RLS, Edge Functions), minimizing external dependencies.
    *   Provides fine-grained, policy-based security for file access directly within the backend.
    *   Scalable file storage solution.
    *   Relatively straightforward integration with the Next.js frontend using Supabase client libraries.
*   **Cons:**
    *   Requires careful design and testing of RLS policies for both the database table and the storage bucket to ensure correct permissions.
    *   Judge/Admin UI for browsing potentially large numbers of submissions needs thoughtful design (pagination, filtering).