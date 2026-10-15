# 2. Decoupling Manifest Generation to Resolve Concurrency Issues

*   **Status:** Proposed
*   **Date:** 2025-11-21
*   **Deciders:** Gemini System Owner, jcmrs Vision Owner

## Context and Problem Statement

The `catalogue/manifest.json` file, which serves as the central log for all generated artifacts, is subject to a classic **concurrency control problem**. The current architecture requires every `agent-intake` workflow run to read, modify, and then overwrite this single file.

When multiple workflow runs execute in parallel (for different issues), they start from the same baseline state of `manifest.json`. This leads to a **race condition** where each run generates a new version of the manifest that is unaware of the others. The result is merge conflicts, data loss when one PR overwrites another's changes, and a fragile, unreliable system.

## Decision

We will re-architect the manifest generation process to follow a standard, robust architectural pattern that decouples event generation from state consolidation.

The new architecture will have two parts:

1.  **Event (Fragment) Generation:** The `agent-intake` workflow will be modified. Instead of altering the master `manifest.json`, it will now generate a **new, unique "manifest fragment" file** for each run (e.g., `catalogue/fragments/issue-123.json`). This fragment will contain only the manifest data for the artifacts created in that specific run. This is an atomic, conflict-free operation.

2.  **State Consolidation:** A new, asynchronous GitHub Actions workflow (`consolidate.yml`) will be created. This workflow will trigger automatically on every push to the `main` branch. Its sole responsibility will be to run a script that:
    *   Scans the `catalogue/fragments/` directory.
    *   Reads all individual fragment files.
    *   Consolidates them into a single, complete list.
    *   Overwrites the master `catalogue/manifest.json` and `catalogue/index.md` files with this new, authoritative state.
    *   Commits the updated files directly back to `main`.

## Rationale and Consequences

This decision is based on established software architecture principles for handling concurrency in distributed systems.

*   **Rationale:**
    *   **Eliminates Race Conditions:** By having each process write to a unique file, we remove the resource contention entirely.
    *   **Ensures Data Integrity:** No data can be lost due to one PR overwriting another.
    *   **Scalability:** The system can now handle any number of parallel workflow runs without issue.
    *   **Separation of Concerns:** The responsibility of "generating data" is now cleanly separated from "consolidating data."

*   **Consequences:**
    *   `generate_artifacts.py` will be modified to write a new fragment file instead of modifying the master manifest.
    *   A new directory, `catalogue/fragments/`, will be created to store these fragments.
    *   A new script, `consolidate_manifest.py`, will be created to perform the consolidation logic.
    *   A new workflow file, `consolidate.yml`, will be created to automate the consolidation process.
    *   The existing `agent-intake.yml` will no longer need to handle the complexity of reading the old manifest.
