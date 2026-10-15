You are the Logical Architecture Council (LAC) Mirror for 02luka.
Your Goal: Apply a "Reviewer Pass" (Option B: Ask + Risk + Evidence) to the draft below.
Do not rewrite the draft. Append your analysis.

TOPIC: Gemini Topic

DRAFT CONTENT TO REVIEW:
## 1. Objective
*   Establish the operational framework and integration strategy for the Gemini (`gmx`) agent within the `02luka` system.
*   Ensure strict alignment with `02luka Workflow Protocol v1` and `PR_AUTOPILOT_RULES` to maintain system integrity and safety.

## 2. Context
*   **Environment:** `02luka` is a strictly governed codebase with established protocols (Decision Gates, Two Worlds model, PR flow).
*   **Identity:** Gemini is identified as `gmx`.
*   **Current Status:** Migration/Setup artifacts exist (`gmx_migration_temp.patch`, `gmx_todo.txt`).
*   **Requirement:** `gmx` must function effectively without violating safety guards (e.g., direct pushes to main, undocumented strategic changes).

## 3. Options
*   **Option A: Full Native Integration (Standard)**
    *   `gmx` fully adopts existing protocols: Phase 0 Discovery, Decision Boxes for strategy, and PR-based code changes.
    *   `gmx` acts as a compliant operator similar to `CLS`.
*   **Option B: Isolated Sandbox**
    *   `gmx` operates only within a specific scope (e.g., `gmx/` directory) or read-only mode.
    *   All changes require human manual intervention to propagate to core.
*   **Option C: Parallel Workflow (Exempt)**
    *   `gmx` bypasses standard protocols for speed, operating outside existing governance.

## 4. Trade-offs

| Dimension | Option A (Full Native) | Option B (Sandbox) | Option C (Parallel) |
| :--- | :--- | :--- | :--- |
| **System Integrity** | **High** (Guarded) | **Very High** (Isolated) | **Low** (Risk of drift) |
| **Velocity** | **Medium** (Process overhead) | **Low** (Manual bottlenecks) | **High** (Unchecked) |
| **Compliance** | **100%** | **N/A** (Limited scope) | **0%** (Violation) |
| **Collaboration** | **Seamless** (Standard artifacts) | **Friction** (Siloed) | **Confusing** (Dual standards) |

## 5. Assumptions
*   `gmx` possesses the necessary tool capabilities to execute the full workflow (Git, filesystem, analysis).
*   The user ("Boss") intends for `gmx` to perform active software engineering tasks, not just passive queries.
*   The `02luka` governance documentation is the single source of truth (SOT).

## 6. Recommendation (Non-binding)
*   **Adopt Option A: Full Native Integration.**
*   **Rationale:** To act as an effective engineer, `gmx` must be a first-class citizen within the system's governance. Bypassing rules creates technical debt and risk; sandboxing limits utility.
*   **Immediate Next Steps:**
    1.  Acknowledge `WORKFLOW_PROTOCOL v1` as the fundamental working method.
    2.  Treat `gmx_todo.txt` items as individual tasks following the Discovery → Plan → Verify loop.

REQUIREMENTS:
1. Ask 3 Hard Questions (Pressure Test) that challenge the assumptions.
2. Identify Top 3 Risks (Pre-mortem) if this decision goes wrong.
3. List 3 Key Evidence items (logs, metrics, tests) required to validate success.
4. Create a Quick Comparison/Risk Table.

OUTPUT FORMAT:
## LAC Mirror Pass
### 1. Pressure Test
...
### 2. Risks (Pre-mortem)
...
### 3. Required Evidence
...
### 4. Quick Table
...
