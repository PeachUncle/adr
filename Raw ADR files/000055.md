# Strategic Decision: Policy: Strategic-Change Reminder via Guard
**Status:** DRAFT
**Timestamp:** 2025-12-24 11:46:25

---

## 1. Objective
To introduce a "gentle friction" mechanism that reminds users/agents to use the `DECISION_BOX` framework when attempting strategic changes (policy, strategy, architecture), ensuring the new governance model is adopted without blocking routine work.

## 2. Context
- **Facts:** 
  - `tools/guard_runtime.zsh` exists and supports regex warnings.
  - `g/decision/DECISION_BOX.md` template is ready.
  - Humans/Agents often skip "thinking steps" for speed.
- **Unknowns:** 
  - Will the warning cause "alert fatigue" if triggered too often?

## 3. Options
- **Option A (Chosen):** **WARN-only Guard Rule.** Detect keywords in commit messages (`policy|strategy|architecture`) and print a helpful reminder with paths. Does not block execution.
- **Option B:** **Hard BLOCK.** Prevent commits entirely until a Decision Box exists. (Too high friction).
- **Option C:** **Do Nothing.** Rely on memory/discipline. (Historically fails).

## 4. Trade-offs
| Option | Upside | Downside | Risk |
| :--- | :--- | :--- | :--- |
| **A (Warn)** | Awareness w/o blocking | Might be ignored | Warning fatigue |
| **B (Block)** | Forced compliance | Frustration / Slowdown | Shadow IT (bypassing guard) |
| **C (None)** | Zero friction | No adoption of new system | System entropy |

## 5. Assumptions
- A1: Users read warnings in the terminal.
- A2: `commit -m` is the primary intent signal we can intercept cheaply.

## 6. Recommendation
Implement Option A. It aligns with 02luka's philosophy of "Guardrails, not Gates."

## 7. Decision (Human)
- **Chosen Option:** Option A
- **Reason:** It changes behavior via visibility, not force. It validates the "Consultant Mode" infrastructure immediately.

## 8. Confidence & Next Check
- **Confidence:** High
- **Revisit Trigger:** If "Warning Fatigue" is reported in 2 weeks.

---
TODO: Run LAC Mirror checks: /Users/icmini/02luka/g/decision/LAC_REASONING_MIRROR.md