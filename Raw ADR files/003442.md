# 009 - Diagnostic Wizard Architecture

## Status
Accepted

## Context
The Diagnostic Wizard is a tool designed to guide users through a series of questions to identify and resolve issues with devices or services. Its core functionality relies on a tree-like structure of diagnostic nodes, where each node represents a question or a solution, and options lead to subsequent nodes. This ADR documents the architecture and structure of this wizard.

## Decision
The Diagnostic Wizard will be implemented with a backend-driven, tree-like structure using the following database schemas:

### `diagnostic_nodes` Table
This table stores the individual questions or solutions within the diagnostic tree.

-   `id`: UUID (Primary Key) - Unique identifier for the diagnostic node.
-   `question_text`: TEXT (NOT NULL) - The question posed to the user, or a title for a solution node.
-   `is_solution`: BOOLEAN (NOT NULL, DEFAULT FALSE) - Indicates if this node represents a final solution.
-   `solution_details`: TEXT (NULLABLE) - Detailed steps or information if `is_solution` is TRUE.
-   `parent_node_id`: UUID (NULLABLE, Foreign Key to `diagnostic_nodes.id`) - References the parent node, forming the tree structure. NULL for root nodes.

### `diagnostic_node_options` Table
This table stores the possible answers or choices for a `diagnostic_node` that is not a solution.

-   `id`: UUID (Primary Key) - Unique identifier for the option.
-   `diagnostic_node_id`: UUID (NOT NULL, Foreign Key to `diagnostic_nodes.id`) - The node to which this option belongs.
-   `option_text`: TEXT (NOT NULL) - The text displayed for this option (e.g., "Yes", "No", "Try this").
-   `next_node_id`: UUID (NULLABLE, Foreign Key to `diagnostic_nodes.id`) - The next diagnostic node to navigate to if this option is selected. If NULL, it implies the end of a path or a solution.

### `diagnostic_feedback` Table
This table stores user feedback on the utility of a diagnostic solution.

-   `id`: UUID (Primary Key) - Unique identifier for the feedback entry.
-   `node_id`: UUID (NOT NULL, Foreign Key to `diagnostic_nodes.id`) - The solution node for which feedback is provided.
-   `user_id`: UUID (NULLABLE, Foreign Key to `users.id`) - The user who provided the feedback (can be anonymous).
-   `is_helpful`: BOOLEAN (NOT NULL) - Indicates if the solution was helpful (true) or not (false).
-   `comments`: TEXT (NULLABLE) - Optional comments from the user.
-   `created_at`: TIMESTAMPTZ (NOT NULL, DEFAULT CURRENT_TIMESTAMP) - Timestamp of feedback submission.

### `diagnostic_history` Table
This table records the path a user takes through the diagnostic wizard for analytical purposes.

-   `id`: UUID (Primary Key) - Unique identifier for the history entry.
-   `user_id`: UUID (NULLABLE, Foreign Key to `users.id`) - The user who navigated (can be anonymous).
-   `session_id`: UUID (NOT NULL) - A unique ID to group all steps within a single diagnostic session.
-   `node_id`: UUID (NOT NULL, Foreign Key to `diagnostic_nodes.id`) - The diagnostic node visited.
-   `selected_option_id`: UUID (NULLABLE, Foreign Key to `diagnostic_node_options.id`) - The option selected to reach this node (if applicable).
-   `action`: VARCHAR(255) (NULLABLE) - Additional action context (e.g., 'go_back', 'restart_diagnostic').
-   `timestamp`: TIMESTAMPTZ (NOT NULL, DEFAULT CURRENT_TIMESTAMP) - Timestamp of the history event.

### Backend API Endpoints
-   `GET /api/diagnostics/root`: Fetches all diagnostic nodes with `parent_node_id IS NULL`.
-   `GET /api/diagnostics/:nodeId`: Fetches a specific diagnostic node by ID.
-   `GET /api/diagnostics/:nodeId/options`: Fetches options for a specific diagnostic node.
-   `POST /api/diagnostics/feedback`: Submits user feedback for a solution node.
-   `POST /api/diagnostics/history`: Records a step in the user's diagnostic journey.

### Frontend Implementation
-   **`DiagnosticWizard.tsx`:** Main component managing the state (current node, history, options) and orchestrating API calls.
-   **`DiagnosticNodeComponent.tsx`:** Renders a single diagnostic node (question or solution) and its associated options.
-   **`FeedbackForm.tsx`:** Component for collecting user feedback on solutions.
-   **State Management:** Uses React Query for efficient data fetching and caching.
-   **Navigation:** Implements breadcrumbs for easy navigation back through the history.
-   **Visual Feedback:** Includes loading indicators, error messages, and progress bar.
-   **Accessibility:** Utilizes Material-UI components and ARIA attributes for keyboard navigation and screen reader support.
-   **Animations:** Uses Framer Motion for smooth transitions between nodes.

## Consequences
-   **Positive:**
    -   Provides a flexible and extensible structure for building complex diagnostic flows.
    -   Enables tracking of user paths and feedback for continuous improvement.
    -   Ensures a responsive, accessible, and visually appealing user experience.
    -   Separation of concerns between backend (data/logic) and frontend (UI).
-   **Negative:**
    -   Initial setup requires careful definition of nodes and options.
    -   Managing a large diagnostic tree could become complex without proper tooling.
    -   The `parent_node_id` and `next_node_id` create a tree structure, but the `options` table is separate, which might require multiple queries to fully traverse a path. This could be optimized if needed.
