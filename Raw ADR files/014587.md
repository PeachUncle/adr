# 1. Refactoring the Artifact Scaffolding Workflow for Robustness

*   **Status:** Proposed
*   **Date:** 2025-11-21
*   **Deciders:** Gemini System Owner, jcmrs Vision Owner

## Context and Problem Statement

The system is initiated when a user assigns a GitHub Issue to the "Copilot" AI entity via the GitHub UI. This external "Copilot" entity then reads the repository for context and triggers the `agent-intake.yml` workflow to perform the artifact scaffolding.

The problem is that the `agent-intake` workflow, once it is correctly triggered by the Copilot entity, is internally brittle and designed to fail silently. Our analysis (documented in `.research/workflow_brittleness_analysis.md`) has identified several critical flaws in the workflow's implementation:

1.  **Brittle Parsing:** `extract_issue_vars.py` uses fragile regular expressions.
2.  **Hardcoded Logic:** `generate_artifacts.py` uses a hardcoded dictionary, making it difficult to maintain.
3.  **Silent Failures:** The `agent-intake.yml` workflow uses `|| true` to suppress critical `git` errors, incorrectly reporting success even when no artifacts are produced.
4.  **Poor Practice:** The workflow attempts to push directly to the main branch instead of creating a Pull Request.

This implementation violates our core principles of Robustness, Clarity, and Completeness. The workflow must be re-engineered to be a reliable tool for the Copilot entity to use.

## Decision Drivers

*   The need for a reliable, predictable, and transparent workflow.
*   The need to eliminate silent failures.
*   The need for a maintainable and extensible system where adding new analysis types does not require complex code changes.
*   The need to follow repository best practices (e.g., using Pull Requests instead of direct pushes).
*   The need for a specific, reliable trigger mechanism.

## Considered Options

### Option 1: Iterative Patching

*   Patch the existing scripts and workflow.
*   Add more complex regex to handle more edge cases.
*   Remove `|| true` and add error-checking logic in the shell script.
*   Add a trigger condition.
*   Replace the `git push` with a PR-creation action.
*   **Pros:** Requires fewer structural changes initially.
*   **Cons:** Fundamentally retains the brittle architecture. The parsing logic will become more complex, not more robust. The tight coupling between components remains.

### Option 2: A Robust, Data-Driven Refactor (Recommended)

*   **Refactor the entire pipeline** to be data-driven and configuration-based.
*   **Parsing:** Replace the regex in `extract_issue_vars.py` with a more robust method. A good option is to embed a YAML or JSON block within the issue template. The script would then parse this structured data, which is far more reliable than free-form Markdown.
*   **Artifact Generation:** Modify `generate_artifacts.py` to read its instructions from a configuration file (e.g., `config/artifact_map.json`) instead of a hardcoded dictionary. This file would define the mapping between tool names, template files, and output paths, decoupling the logic from the data.
*   **Workflow:** Overhaul `agent-intake.yml` to:
    2.  Remove all error suppression (`|| true`).
    3.  Use a dedicated, robust action (like `peter-evans/create-pull-request`) to handle PR creation.
    4.  Ensure clear success/failure reporting.
*   **Pros:** Creates a robust, maintainable, and extensible system. Decouples the components. Eliminates silent failures.
*   **Cons:** Requires more significant upfront work to refactor the scripts and introduce a configuration file.

## Decision

We will proceed with **Option 2: A Robust, Data-Driven Refactor**.

This decision aligns with our core principles. It prioritizes long-term robustness and maintainability over short-term patching. It will provide a solid foundation for any future work, including a potential transition to a fully autonomous agent.

## Consequences

*   The `extract_issue_vars.py` script will be rewritten to parse structured data (e.g., YAML) from the issue body.
*   The GitHub Issue template will need to be updated to include this structured data block.
*   A new configuration file (e.g., `config/artifact_map.json`) will be created.
*   The `generate_artifacts.py` script will be rewritten to use this configuration file.
*   The `agent-intake.yml` workflow file will be completely overhauled to use proper triggers, error handling, and a PR-creation action.
*   This provides a stable baseline for future enhancements.
