# ADR: V2 Content Management Strategy

* Status: Proposed
* Date: 2025-04-19

## Context

The V2 specification requires a centralized system for managing core event information (dates, schedule, deadlines - Req 3.3.1) and a way to handle expanded descriptions for theme pages (Req 3.3.2). The V1 system used Supabase for basic theme/workshop/FAQ data but relied on Markdown files for some detailed content, leading to potential inconsistencies.

## Decision

We will adopt a database-driven approach using Supabase for both core event information and expanded theme content, confirming the recommendations in the V2 specification:
1.  **Core Event Information (Req 3.3.1 - Option A):** Create new Supabase tables (e.g., `event_details`, `schedule_items`) to store structured data like event dates, schedule details, and deadlines. Build corresponding CRUD interfaces in the `/admin` section using the established Server Action pattern.
2.  **Expanded Theme Content (Req 3.3.2 - Option C):**
    *   **Storage:** Add a new `description_expanded` column (type `text`) to the existing `themes` table in Supabase. This column will store the detailed theme description as **Markdown** text.
    *   **Admin UI:** Update the Admin theme form (`/admin/themes/edit`, `/admin/themes/new`) to include a multi-line textarea for editing the `description_expanded` field. Consider adding a Markdown preview feature to the admin form for better usability.
    *   **Frontend Rendering:** Update the dynamic theme page (`/themes/[id]`) to:
        *   Fetch the `description_expanded` Markdown content from Supabase.
        *   Use a library like `react-markdown` to parse and render the Markdown string into HTML.
        *   Apply Tailwind Typography plugin classes (e.g., `prose prose-invert`) to the container rendering the Markdown output to ensure proper formatting of headings, lists, paragraphs, code blocks, etc., consistent with other Markdown-rendered content on the site.

## Consequences

*   **Pros:**
    *   Creates a single source of truth for all dynamic content within Supabase.
    *   Allows non-technical admins to update core event details and theme descriptions easily via the Admin UI without requiring code changes or redeployments.
    *   Leverages the existing Supabase backend and Admin UI patterns.
    *   Avoids the need to build and maintain separate Markdown parsing logic.
    *   Ensures consistency between summary and detailed theme information.
*   **Cons:**
    *   Requires schema changes (new tables, altered `themes` table).
    *   Requires updates to the Admin UI (new forms/fields for event details, updated theme form).
    *   Storing potentially large Markdown content in a database `text` field is generally acceptable and simplifies the architecture, though file storage might be theoretically better for extremely large or complex documents (not expected here). The combination with `react-markdown` and Tailwind Typography provides good rendering flexibility.