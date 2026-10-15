# ADR 009: Flexible Acquisition Discovery and Confirmation Workflow

*   **Status:** Proposed
*   **Date:** 2025-05-04
*   **Deciders:** Architect Mode
*   **Consulted:** User Feedback [Ref: SPARC Feedback 2025-05-03 18:40:43], Original Conflict Discussion [Ref: SPARC Feedback 2025-05-03 18:32:12]
*   **Affected:** `docs/project-specifications.md`, `docs/architecture/tier0_mvp_architecture.md`, `src/philograph/api/main.py`, `src/philograph/acquisition/service.py`, `src/philograph/cli/main.py`, `src/philograph/mcp/main.py` (MCP Tool Definitions)

## Context and Problem Statement

The initial Tier 0 design included a basic text acquisition workflow triggered via a `POST /acquire` endpoint. User feedback and subsequent analysis revealed several issues:

1.  **Lack of User Control:** The original concept of `find_missing_threshold` was too blunt and didn't allow users/agents to specify *which* missing texts to acquire.
2.  **Inflexible Discovery:** The trigger mechanism lacked support for diverse discovery criteria beyond a simple threshold (e.g., finding texts cited by a specific author, within a collection, related to a discourse topic).
3.  **Workflow Ambiguity:** The single `/acquire` endpoint conflated the discovery of potential candidates with the confirmation and triggering of the actual acquisition process.
4.  **API Mismatch:** The implemented `POST /acquire` endpoint (as observed in `src/philograph/api/main.py` context) primarily focused on direct acquisition based on provided title/author, not the intended discovery workflow.

A more flexible, user-controlled workflow is needed to allow targeted discovery of potentially missing texts, followed by an explicit review and confirmation step before triggering the resource-intensive acquisition process via the `zlibrary-mcp` server.

## Decision Drivers

*   **User Feedback:** Explicit request for a review step and more granular control over acquisition.
*   **Workflow Clarity:** Need to separate the discovery phase from the confirmation/acquisition phase.
*   **Flexibility:** Support diverse criteria for identifying potentially missing texts (citation count, cited by author, collection context, tags, discourse analysis).
*   **Resource Management:** Avoid unnecessary acquisition attempts by requiring explicit confirmation.
*   **API Design Principles:** Adhere to REST principles by using distinct endpoints for distinct actions (discover vs. confirm).

## Considered Options

1.  **Modify Existing `/acquire` Endpoint:** Add complex parameters to the existing `/acquire` endpoint to handle both discovery criteria and confirmation flags/lists.
    *   *Pros:* Fewer endpoints.
    *   *Cons:* Leads to a complex, overloaded endpoint violating single responsibility. Difficult to manage state between discovery and confirmation. Unclear API semantics.
2.  **Introduce Separate Discovery and Confirmation Endpoints:** Create `POST /acquire/discover` for finding candidates and `POST /acquire/confirm/{discovery_id}` for triggering acquisition of selected candidates.
    *   *Pros:* Clear separation of concerns. RESTful design. Explicit workflow steps. Allows state management via `discovery_id`. Supports flexible discovery criteria cleanly.
    *   *Cons:* Introduces two new endpoints. Requires managing the state associated with `discovery_id`.
3.  **Use Asynchronous Job Pattern:** Define a single `/acquire/jobs` endpoint. POSTing criteria creates a "discovery job", returning a job ID. GET `/acquire/jobs/{job_id}` retrieves candidates. PUT `/acquire/jobs/{job_id}` confirms candidates, transitioning the job to "acquisition".
    *   *Pros:* Follows a common async pattern. Centralized job management.
    *   *Cons:* More complex state management. Potentially overkill for Tier 0. Less intuitive for simple request-response interactions expected by CLI/MCP.

## Decision Outcome

**Chosen Option:** Option 2 - Introduce Separate Discovery and Confirmation Endpoints (`POST /acquire/discover` and `POST /acquire/confirm/{discovery_id}`).

**Rationale:** This option provides the clearest separation of concerns, aligns best with REST principles, and directly addresses the user feedback regarding the need for a distinct review and confirmation step. It allows for flexible discovery criteria in the `/discover` payload and explicit selection in the `/confirm` payload. Managing state via a `discovery_id` is a standard pattern for multi-step web workflows and is manageable for Tier 0.

### API Design Details

*   **`POST /acquire/discover`**
    *   **Input:** JSON body containing `criteria` (object with fields like `min_citation_threshold`, `cited_by_author`, `collection_id`, `tags`, `discourse_query`) and `exclude_existing` (boolean).
    *   **Output:** JSON body containing `discovery_id` (UUID) and `candidates` (list of objects with `candidate_id`, `title`, `author`, `year`, `reason`, `potential_sources`).
    *   **Behavior:** Acquisition Service uses criteria to query Relationship Service, Search Service, and DB. Generates and stores candidate list associated with `discovery_id`. Returns list and ID.
*   **`POST /acquire/confirm/{discovery_id}`**
    *   **Input:** Path parameter `discovery_id` (UUID). JSON body containing `confirmations` (list of objects with `candidate_id` and `acquisition_details` needed for `zlibrary-mcp`).
    *   **Output:** JSON body indicating status and potentially job IDs for triggered `zlibrary-mcp` tasks.
    *   **Behavior:** Acquisition Service retrieves candidates for `discovery_id`. For confirmed candidates, initiates acquisition via `zlibrary-mcp` (`search_books` then `download_book_to_file`). Triggers ingestion upon success.

## Consequences

*   **Positive:**
    *   Clearer, more user-controlled acquisition workflow.
    *   Supports flexible discovery methods.
    *   Reduces unnecessary acquisition attempts.
    *   Improved API clarity and adherence to REST principles.
*   **Negative:**
    *   Requires implementation of two new API endpoints and associated service logic.
    *   Introduces state management for `discovery_id` (needs a mechanism for storing/retrieving candidate lists, potentially in memory for Tier 0 or a simple DB table).
    *   Requires updates to CLI and MCP tool definitions to support the new workflow.
*   **Neutral:**
    *   Deprecates the previous vague `/acquire` endpoint logic.

## Implementation Plan (High-Level)

1.  **API:** Define Pydantic models for request/response bodies in `api/main.py`. Implement the two new FastAPI endpoints.
2.  **Acquisition Service:** Refactor `acquisition/service.py` to handle the discovery logic (querying other services/DB) and confirmation logic (calling `zlibrary-mcp`). Implement state management for `discovery_id`.
3.  **Relationship/Search Service:** Ensure these services can provide the necessary data for discovery criteria.
4.  **CLI:** Update `cli/main.py` to include `acquire discover` and `acquire confirm` subcommands reflecting the new API calls.
5.  **MCP:** Update MCP tool definitions (`mcp/main.py` or equivalent) to expose `philograph_acquire_discover` and `philograph_acquire_confirm` tools.
6.  **Documentation:** Update `project-specifications.md` and `tier0_mvp_architecture.md` (already partially done).
7.  **Testing:** Add unit and integration tests for the new API endpoints and service logic.

## References

*   `docs/project-specifications.md` (v2.3+)
*   `docs/architecture/tier0_mvp_architecture.md` (Updated)
*   User Feedback [Ref: SPARC Feedback 2025-05-03 18:40:43]