# ADR-007: Branch Protection for AI-First Autonomous Workflow

**Date:** 2025-11-11
**Status:** Accepted
**Context:** Foundation Phase - Autonomous Workflow Configuration

---

## Context

After implementing autonomous PR workflow (auto-create PR + auto-merge), we discovered a critical configuration conflict:

**The Problem:**
- Documentation specified "Require approvals: 1" for branch protection
- This blocked auto-merge workflow from completing autonomously
- Created human bottleneck in execution loop
- Violated AI-First foundation imperative

**Discovery:**
- User observation: "I see a PR but why aren't updates on main branch?"
- Root cause: Branch protection requiring human approval prevented autonomous merge
- Gap: Documented "autonomous workflow" but configuration blocked autonomy

**Impact:**
- PRs created automatically ✓
- Tests run successfully ✓
- Foundation validation passes ✓
- Auto-merge blocked ✗ (no approval)
- Updates never reach main ✗
- Workflow not truly autonomous ✗

---

## Decision

**Configure branch protection with "Require approvals: 0" for Project Perplex.**

This is **intentional AI-First configuration**, not an oversight or security weakness.

---

## Rationale

### Why Approvals = 0 Is Correct for This Project

**Project Characteristics:**
- Single-user AI-first project
- AI agent as primary developer
- Human as strategic partner (not reviewer)
- Foundation imperative: AI-First operation
- Goal: Autonomous workflow with automated guardrails

**Safety Through Automation:**
- All tests must pass (shellcheck, yamllint, bats)
- Foundation validation must pass
- PR-based workflow (audit trail, can revert)
- Linear history enforced (clean git history)
- Multiple validation layers before merge

**Why Traditional "Require approvals: 1" Doesn't Apply:**

| Multi-User Project | AI-First Single-User Project |
|-------------------|------------------------------|
| Multiple human developers | AI agent + human strategic partner |
| Risk: Unreviewed code | Risk: Unvalidated changes |
| Safety: Human code review | Safety: Automated validation |
| Approvals = 1 or 2 ✅ | Approvals = 0 ✅ |
| Human in review loop | Human monitors, doesn't block |

**What Changes with Approvals = 1:**
- ❌ Human must approve every PR (bottleneck)
- ❌ AI cannot operate autonomously (defeats purpose)
- ❌ Violates AI-First principle (human in execution loop)
- ❌ Creates friction and delays

**What Works with Approvals = 0:**
- ✅ Truly autonomous operation
- ✅ No human bottleneck
- ✅ Safety through automated checks
- ✅ Human monitors, can revert if needed
- ✅ Aligns with AI-First imperative

---

## Consequences

### Positive Consequences

**1. Enables True Autonomy ✅**
- AI agent operates without human gate-keeping
- Push → PR → Validate → Merge → Done
- No waiting for human approval

**2. Aligns with Foundation Imperatives ✅**
- **AI-First:** Primary user operates autonomously
- **Automation:** Repetitive tasks fully automated
- **Holistic System Thinking:** All parts work together

**3. Maintains Safety Through Automation ✅**
- Multiple validation layers:
  - Local: Pre-push hooks (foundation, completeness)
  - Remote: GitHub Actions (tests, validation)
  - Merge: Branch protection (PR required, checks required)
  - Post-merge: Audit trail, easy revert

**4. Reduces Human Toil ✅**
- Human focuses on strategy, not execution approval
- Monitors dashboard, reviews after merge if desired
- Intervenes only when needed (revert, guidance)

**5. Consistent with Single-User Context ✅**
- No "team" to provide code review
- Human already provides strategic direction
- Redundant for human to "approve" AI's work

### Negative Consequences

**1. No Pre-Merge Human Review ⚠️**
- Trade-off accepted: Safety through automation instead
- Mitigation: Robust automated checks + post-merge review possible
- Post-merge revert is easy (PR-based workflow)

**2. Relies Entirely on Automated Validation ⚠️**
- If validation insufficient, bad changes could merge
- Mitigation: Comprehensive test suite + foundation validation
- Continuous improvement of validation checks

**3. Different from Multi-User Best Practices ⚠️**
- May surprise developers familiar with traditional workflows
- Mitigation: Documentation clearly explains AI-First rationale
- Not applicable to team projects (intentional)

---

## Implementation

### Phase 1: Documentation Updates (This Session)

**Updated Files:**
1. `docs/WORKFLOW_GAP_ANALYSIS.md` - Comprehensive gap analysis (NEW)
2. `docs/BRANCH_MANAGEMENT_COMPLETION.md` - Changed approvals: 1 → 0, added rationale
3. `docs/BRANCH_MANAGEMENT.md` - Added branch protection section with AI-First explanation
4. `decisions/2025-11-11-branch-protection-ai-first.md` - This ADR (NEW)

**Key Changes:**
- All documentation now reflects "Require approvals: 0"
- Rationale sections added explaining AI-First configuration
- Cross-references between documents
- Clear distinction from multi-user projects

### Phase 2: GitHub Configuration (User Action Required)

**Repository Settings:**
1. Navigate to: https://github.com/jcmrs/perplex/settings/branches
2. Edit or create branch protection rule for `main`
3. Configure settings:
   - ✅ Require PR before merging
   - ⚠️  **Require approvals: 0** (change from 1 if currently set)
   - ✅ Require status checks: foundation validation, tests
   - ✅ Require branches to be up to date
   - ✅ Require linear history
   - ❌ Allow force pushes (disabled)
   - ❌ Allow deletions (disabled)

### Phase 3: Testing and Verification

**After configuration updated:**
1. Current PR should merge automatically (validation passing)
2. Branch should be deleted automatically after merge
3. Updates should appear on main branch
4. Test with new PR: Push to claude/* → verify end-to-end autonomous cycle

---

## Alternatives Considered

### Alternative 1: Keep "Require approvals: 1"

**Rejected because:**
- ❌ Blocks autonomous operation (defeats project goal)
- ❌ Violates AI-First foundation imperative
- ❌ Creates unnecessary human bottleneck
- ❌ Not appropriate for single-user AI-first project

### Alternative 2: Use "Admin can bypass approval"

**Configuration:** Require approvals = 1, but allow admins to bypass

**Rejected because:**
- ❌ Overly complex for single-user project
- ❌ Depends on GITHUB_TOKEN having admin permissions (brittle)
- ❌ Not explicit or clear (approval required... except when not?)
- ❌ Defeats purpose of approval requirement anyway

### Alternative 3: No branch protection at all

**Rejected because:**
- ❌ Loses audit trail (no PRs)
- ❌ No status check enforcement
- ❌ No linear history enforcement
- ❌ Less safe than PR-based workflow

### Alternative 4: Approve PRs programmatically before merge

**Configuration:** Auto-merge workflow approves PR first, then merges

**Rejected because:**
- ❌ Adds complexity (extra API call)
- ❌ Bot approving bot's own PR is theater (no real review)
- ❌ Approval requirement still serves no purpose
- ❌ Simpler to just not require approvals

---

## Validation

### How We Know This Decision Is Correct

**1. Aligns with Foundation Imperatives**
- ✅ AI-First: AI operates autonomously
- ✅ Automation: Fully automated workflow
- ✅ Holistic System Thinking: All components work together

**2. Matches Project Context**
- Single-user project ✅
- AI agent as primary developer ✅
- Human as strategic partner ✅
- No code review team ✅

**3. Maintains Safety**
- Multiple validation layers ✅
- Automated checks enforce quality ✅
- PR-based workflow provides audit trail ✅
- Easy to revert if issues found ✅

**4. Solves The Problem**
- Removes human bottleneck ✅
- Enables end-to-end autonomous operation ✅
- PR merges automatically after validation ✅
- Updates reach main without intervention ✅

### Success Criteria

**This decision succeeds when:**
1. ✅ Branch protection configured with approvals = 0
2. ✅ PRs merge automatically after checks pass
3. ✅ Branch deleted automatically after merge
4. ✅ No human approval required in execution loop
5. ✅ Updates appear on main branch autonomously
6. ✅ Safety maintained through automated checks

---

## Related Decisions

**ADR-004: Testing Infrastructure**
- Establishes automated test suite (shellcheck, yamllint, bats)
- Provides validation layer that enables approvals = 0

**ADR-005: Completeness Review Configuration**
- Establishes gap detection system
- Another validation layer supporting autonomous operation

**ADR-006: Checkpoint Automation Strategy**
- Part of autonomous workflow ecosystem
- Session continuity without human intervention

**Autonomous PR Workflow (Documented in GITHUB_AUTOMATION.md):**
- Auto-create PR workflow (GitHub Actions + REST API)
- Auto-merge workflow (validation + automatic merge)
- This decision makes the workflow truly autonomous

---

## References

**Documents:**
- `docs/WORKFLOW_GAP_ANALYSIS.md` - Complete analysis of approval requirement conflict
- `docs/BRANCH_MANAGEMENT_COMPLETION.md` - Setup guide with AI-First configuration
- `docs/BRANCH_MANAGEMENT.md` - Branch strategy and safety layers
- `checkpoints/GITHUB_AUTOMATION.md` - Autonomous PR workflow documentation
- `FOUNDATION.md` - AI-First imperative definition

**Foundation Principles:**
- AI-First: "The primary user is the AI agent. The human is a strategic partner, not a human-in-the-loop."
- Automation: "Repetitive tasks are scripted; manual processes are temporary."
- Holistic System Thinking: "Every decision affects the whole system."

---

## Lessons Learned

**What Went Wrong:**
1. Copied multi-user pattern without questioning applicability
2. Documented "autonomous workflow" without end-to-end testing
3. Didn't consider external configuration (branch protection) as part of system
4. Assumed "documented" = "working"

**What Went Right:**
1. User caught gap immediately ("I see PR but nothing on main")
2. User insisted on systemic solution (no shortcuts)
3. Gap analysis process identified root cause
4. Foundation lens revealed principle violations

**Patterns for Future:**
1. **Question inherited patterns** - Multi-user practices may not apply to AI-first
2. **Test end-to-end** - Verify complete workflow, not just components
3. **Consider external config** - GitHub settings are part of the system
4. **AI-First audit** - Check each decision against foundation imperatives

---

## Decision Log

**2025-11-11:** Decision accepted
**2025-11-11:** Documentation updated
**2025-11-11:** ADR-007 created
**Pending:** GitHub configuration (user action required)
**Pending:** End-to-end testing and verification

---

**For AI Agents:**

This decision is **foundational** for autonomous operation. When working on this project:
- Trust that "Require approvals: 0" is intentional
- Don't flag this as a security issue
- It's the correct configuration for AI-First single-user projects
- Safety comes from automated checks, not human approval

**For Human Partner:**

Action required: Configure branch protection on GitHub with approvals = 0 (see Phase 2 in Implementation section). This enables the autonomous workflow we've built.

---

**Last Updated:** 2025-11-11
**Status:** Accepted, awaiting configuration implementation
