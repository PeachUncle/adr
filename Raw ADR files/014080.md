# ADR 0001: CI/PR/Issue Workflow for Traceable Deliverables

## Status

**Accepted (Phase 1 - Foundations)** – Templates & lightweight linkage adopted (2025-11-03)  
⏭ **Planned (Phase 2 - Automation)** – CI validation & PR commentary (earliest 2025-11-17)  
⏳ **Future (Phase 3 - Enforcement)** – Optional strict checks & metrics (post evaluation)

Blockers from preflight have been partially remediated. Heavy automation intentionally deferred.

Summary of remediation:

- Added issue templates (`feature.md`, `bug.md`, `chore.md`)
- Added pull request template (`pull_request_template.md`)
- Adopted lightweight workflow first (no hard CI failure yet)

See Implementation Plan section for phased rollout.

## Context

In our development workflow, clarity around the purpose of changes (i.e., the "Why") is crucial to ensure everyone involved understands the problem being solved, the rationale behind changes, and the impact they will have on the product. As we work with multiple teams, stakeholders, and developers, we need a system that tracks not only what changes are being made but also **why** those changes are being made.

Currently, PRs and issues are disconnected from the high-level goals, and the justification for work is often vague or undocumented. Additionally, there is no clear linkage between the CI pipeline results, the PR itself, and the issues that explain the origin of the work.

### Goals:

1. **Traceability**: Ensure every PR is linked to an issue that explains "Why" the work is being done.
2. **Clarity**: Define the purpose and context of each change explicitly.
3. **Accountability**: Ensure that PRs serve as the glue between the issue (Why), the code (What), and the delivery pipeline (How).
4. **Simplicity**: Maintain a simple and consistent process with minimal overhead for developers.
5. **CI Integration**: Ensure that the CI process is linked to the PR and provides evidence of the changes being made without requiring external documentation.

## Decision

The process will be formalized with the following components:

### 1. **Issue Creation and Linking**

- **Action**: Every new piece of work must begin with creating an issue.
- **Requirement**: The issue must include:
  - A section labeled **“Why this matters”** to describe the reason behind the change.
  - A section for **Acceptance Criteria** outlining the deliverables and expected outcomes.
  - A **Priority** label to ensure proper attention.

- **Rationale**: This ensures that the developer knows what the problem is and why it’s worth solving. The issue acts as the source of truth for all work.

### 2. **PR Creation**

- **Action**: When a developer is ready to begin work on an issue, they must create a PR that links back to the relevant issue.
- **Requirement**: The first line of the PR description must link to the issue number and reference the “Why.”
- **Rationale**: The PR becomes the record of what is being done, with a direct link to the issue for context. It must reflect the scope of the work and the rationale for the changes.

### 3. **CI Pipeline Integration**

- **Action**: The CI pipeline will be integrated to run automatically whenever a PR is pushed or updated.
- **Requirement**: The pipeline will:
  - Run tests, lint checks, and build validation.
  - Produce a downloadable **CI report** summarizing the status of each test, lint, and build step.
  - Post a summary comment in the PR linking back to the report.
  - Include the **next steps** or next issue to work on if applicable.
  - Flag if the issue is missing or if the “Why” is not provided in the linked issue.

- **Rationale**: CI is essential to ensure that changes meet the required quality standards. By linking CI directly to the PR and the issue, we ensure that we maintain traceability and accountability.

### 4. **PR Review and Approval**

- **Action**: The PR will be reviewed by a code owner or team lead.
- **Requirement**: The review must ensure that:
  - The issue is correctly referenced and has a valid "Why" section.
  - The CI pipeline has successfully passed.
  - Acceptance criteria are met.
  - Next steps are clearly defined if the issue is part of a larger effort.

- **Rationale**: This ensures that all work is thoroughly reviewed for technical quality and alignment with project goals, ensuring the team maintains a shared understanding of the purpose behind changes.

### 5. **Merge and Deployment**

- **Action**: Once the PR is approved and all checks are green, the PR can be merged.
- **Requirement**: The PR must:
  - Have a valid **next steps** issue linked, or be marked as complete with no further action required.
  - Update the linked issue to **Done** and automatically link to any related issues.

- **Rationale**: Merging ensures that the code is integrated and deployable. The status change in the issue reflects that the work is complete and deployed.

### 6. **Rollback**

- **Action**: If a change needs to be reverted, a new PR must be created that explicitly reverts the original changes.
- **Requirement**: The revert PR must:
  - Reference the original PR and issue.
  - Contain the same "Why" and acceptance criteria.

- **Rationale**: This maintains full traceability of actions, even when reverting changes, and ensures that reverts are handled as part of the ongoing workflow.

---

## Consequences

### Positive Outcomes:

1. **Clearer Communication**: With well-documented issues and explicit reasoning in PRs, everyone in the team can understand the context and importance of the work being done.
2. **Better Traceability**: Linking issues, PRs, and CI results together ensures that changes can be traced back to their origins.
3. **Simplified Workflow**: By automating the linkage between issues, PRs, and CI, we reduce manual work and ensure that deliverables and statuses are always up-to-date.
4. **Improved Quality**: Integrating CI directly into the PR process helps catch bugs and errors early, ensuring higher-quality code.
5. **Improved Visibility**: The next steps in the project are always clearly identified, allowing for better planning and resource allocation.

### Risks:

1. **Increased Initial Complexity**: The process adds overhead for developers who must create issues and ensure PR descriptions are formatted correctly.
2. **Possible Resistance to Change**: Team members who are used to less formal processes may resist adopting this new workflow.
3. **Potential for Missing Information**: If the "Why" or acceptance criteria aren’t filled out properly in the issue or PR, it can delay the process.
4. **Dependency Management**: As the number of issues and PRs grows, managing the links and ensuring that dependencies are tracked may become more complex.

### Mitigation:

- **Training and documentation**: Provide clear guidelines and examples for developers to follow.
- **Automated Checks**: Use CI to flag when the issue is missing or when the PR does not follow the required structure.
- **Constant Feedback**: Regular retrospectives to gather feedback and refine the process.

---

## Alternatives Considered

1. **No Formal Link Between PR and Issue**:
   - **Rejected**: While simpler, it would sacrifice traceability and context, leading to confusion about the purpose of changes and potential duplication of work.

2. **Manual Documentation for Each Change**:
   - **Rejected**: Relying on manual documentation would add significant overhead and risk inconsistency, especially as the team scales.

---

## Conclusion

By implementing this CI/PR/Issue workflow, we ensure that our work is well-documented, traceable, and aligned with the broader goals of the team. This structure encourages transparency and accountability, reducing the likelihood of mistakes and misunderstandings. This approach will help streamline the development process, reduce cognitive load on developers, and improve the overall quality of our work.

---

## Implementation Plan

### Phase 1 (Foundations) – COMPLETE

Deliverables:

- Issue templates with Why / Acceptance / Priority
- PR template with Related Issue / Why / Summary / Acceptance Alignment
- ADR updated to Phase 1 Accepted

Manual Rules (Phase 1):
| Requirement | Enforcement | Owner |
|-------------|-------------|-------|
| Issue includes Why & Acceptance | Manual triage | Author / Reviewer |
| PR links issue (Closes #) | Manual review | Reviewer |
| Priority selected | Manual triage | Author |
| Template sections filled | Manual review | Author |
| Next Steps (optional) | Manual | Author |

### Phase 2 (Automation) – PLANNED

Scope: Gentle CI hints (warnings, not hard fails).
Proposed:

- `scripts/checks/pr-linked-issue.mjs` (warn when missing link)
- `scripts/checks/issue-structure.mjs` (warn when missing Why/Acceptance)
- CI job comment summarizing structure compliance
- Auto-label missing priority (`needs:priority`)

Phase 2 Acceptance Criteria:

- ≥80% PRs contain issue link on first commit
- ≥70% issues contain Why + Acceptance
- ≤10% PR reviews require structural rework

### Phase 3 (Enforcement) – FUTURE / OPTIONAL

Scope: Hard failing CI + metrics dashboard; map Acceptance to tests.
Deferred until post-retrospective (Q1 2026 earliest).

### Timeline

| Date       | Milestone                                      |
| ---------- | ---------------------------------------------- |
| 2025-11-03 | Phase 1 accepted                               |
| 2025-11-17 | Phase 2 scoping earliest start                 |
| 2025-12-03 | Adoption checkpoint (30-day)                   |
| 2026-02-01 | Evaluate Phase 2 completion / consider Phase 3 |

### Lane Ownership

| Lane | Phase 1               | Phase 2                     | Phase 3                        |
| ---- | --------------------- | --------------------------- | ------------------------------ |
| A    | N/A                   | Validation helper functions | Metrics infra                  |
| B    | Templates / ADR edits | Update docs & guidance      | Maintain playbook patterns     |
| C    | N/A                   | CI scripts & PR comments    | Enforcement / dashboards       |
| D    | Coordinate baseline   | Track adoption / adjust     | KPI evaluation / retrospective |

### Exceptions (Phase 1)

| Case                        | Relaxation                                              |
| --------------------------- | ------------------------------------------------------- |
| Tiny PR (typo, config bump) | May inline short justification instead of full template |
| Emergency hotfix            | Issue may be created post-merge within 24h              |
| Internal chore/refactor     | Next Steps optional                                     |

### Rollback Strategy

If reviewer friction >30% at 30-day checkpoint:

- Relax mandatory Why for trivial changes
- Defer Phase 2 until improvement sustained

### Adoption Metrics (Baseline TBD)

Track starting 2025-11-04:

- % PRs with issue link on initial submission
- % issues with Why + Acceptance
- % PR template usage

Targets before Phase 2:
| Metric | Target |
|--------|--------|
| Issue link usage | ≥80% |
| Issue structural completeness | ≥70% |
| PR template usage | ≥90% |

## Lane D Preflight Assessment (2025-11-03) – Historical Appendix

**Reviewer:** Lane D (Program Operations & Cross-Lane Coordination)  
**Assessment Date:** November 3, 2025  
**Original Status:** ⚠️ BLOCKED (superseded by Phase 1 acceptance)

### Executive Summary

Lane D has reviewed this ADR against current project state, cross-lane dependencies, and recent governance changes (ideas workflow deprecation 2025-11-03). This proposal has **significant implementation gaps** and **conflicts with current project architecture**. **Recommendation: HOLD pending major revision.**

---

### Critical Blockers

#### 1. ⛔ No Issue/PR Templates Exist (Resolved)

**Finding:** The repository has **no GitHub issue templates or PR templates** configured.

**Evidence:**

- `.github/ISSUE_TEMPLATE/` - Does not exist
- `.github/pull_request_template.md` - Does not exist
- No template structure to enforce "Why this matters" or acceptance criteria

**Resolution:** Templates added; enforcement deliberately manual in Phase 1.

**Blocker Severity:** CRITICAL  
**Owner:** Lane B (must create templates) + Lane C (must validate templates in CI)

---

#### 2. ⛔ CI Pipeline Does Not Support Proposed Checks (Deferred)

**Finding:** The current CI pipeline (`.github/workflows/ci.yml`) does **not validate issue linkage** or PR structure.

**Evidence:**

- No job checks for issue references in PR descriptions
- No validation of "Why this matters" sections
- No automated commenting on PRs with status/reports
- Summary job only aggregates test results, doesn't check PR metadata

**Gap Analysis:**

| ADR Requirement                  | Current CI         | Implementation Required  |
| -------------------------------- | ------------------ | ------------------------ |
| Flag missing issue links         | ❌ Not implemented | New workflow job         |
| Validate "Why" section in issues | ❌ Not implemented | GitHub API integration   |
| Post CI summary comment on PR    | ❌ Not implemented | PR comment action        |
| Validate acceptance criteria     | ❌ Not implemented | Custom validation script |
| Track "next steps" links         | ❌ Not implemented | Issue graph analysis     |

**Resolution:** Deferred to Phase 2 scoped as warnings-first approach.

**Blocker Severity:** CRITICAL  
**Owner:** Lane C (DevOps & Automation) - New automation scripts required

---

#### 3. ⚠️ Conflicts with Recent Deprecation (Risk Mitigated)

**Finding:** This ADR was authored **before** the ideas workflow deprecation (2025-11-03) and references outdated governance patterns.

**Context:** As of 2025-11-03:

- Ideas workflow deprecated (86 files archived)
- Lane D no longer owns lifecycle governance or project stewardship
- GitHub Projects integration removed
- Standard GitHub issue/PR workflows now the norm

**Alignment Issues:**

- ADR proposes **heavyweight process** when we just simplified to **lightweight GitHub workflows**
- Proposes "next steps issue linking" which echoes deprecated idea checklists
- Introduces new mandatory overhead immediately after reducing overhead

**Resolution:** Adopted lightweight path; heavy automation postponed.

**Blocker Severity:** HIGH  
**Owner:** ADR Author + Lane D (must reconcile with current direction)

---

#### 4. ⚠️ No Templates in `scripts/_lib/github.mjs` (Deferred)

**Finding:** The ADR assumes GitHub API helper functions for issue validation, but current `scripts/_lib/github.mjs` does **not include**:

- Issue body parsing/validation functions
- PR description validation
- "Why" section extraction
- Acceptance criteria checking

**Resolution:** Scheduled for Phase 2 scoping; not required for Phase 1.

**Blocker Severity:** MEDIUM  
**Owner:** Lane A (must create validation utilities) → Lane C (must integrate)

---

### Non-Blocking Concerns

#### 5. 📋 Unclear Rollback Process Automation

**Issue:** Section 6 (Rollback) describes manual revert PR creation but doesn't specify:

- Who determines when revert is needed?
- How is original PR/issue linked automatically?
- Does CI treat reverts differently?

**Recommendation:** Clarify revert workflow and automation expectations.

---

#### 6. 📋 "Next Steps" Linking May Create Overhead

**Issue:** Requiring every PR to link "next steps" or mark complete adds cognitive load. This may slow velocity, especially for:

- Bug fixes
- Dependency updates
- Documentation typos
- Hotfixes

**Recommendation:** Consider making "next steps" optional for certain issue types (bug, chore, docs).

---

#### 7. 📋 Missing Lane Coordination Plan

**Issue:** This ADR impacts all lanes but doesn't specify:

- **Lane A:** Must build validation utilities
- **Lane B:** Must create issue/PR templates, document workflow
- **Lane C:** Must implement CI automation
- **Lane D:** Must coordinate rollout and training

**Recommendation:** Add implementation section with lane ownership and timeline.

---

### Cross-Lane Dependency Analysis

| Lane   | Required Actions                                  | Estimated Effort | Blocking? |
| ------ | ------------------------------------------------- | ---------------- | --------- |
| Lane A | Create validation utilities in `_lib/validation`  | 3-5 days         | ✅ Yes    |
| Lane B | Create issue/PR templates, write documentation    | 2-3 days         | ✅ Yes    |
| Lane C | Build CI automation for validation, PR commenting | 2-3 weeks        | ✅ Yes    |
| Lane D | Coordinate rollout, training, monitor adoption    | Ongoing          | No        |

**Total Estimated Effort:** 3-4 weeks of coordinated work across 3 lanes  
**Current State:** 0% implemented

---

### Recommendations

#### 🛑 Immediate (REQUIRED Before Unblock)

1. **Hold ADR** - Mark status as "Proposed - Blocked by Lane D Assessment"
2. **Create issue/PR templates** (Lane B) - Foundation for enforcement
3. **Build validation utilities** (Lane A) - Tooling for Lane C automation
4. **Scope CI automation** (Lane C) - Define what's automatable vs. manual
5. **Reconcile with deprecation** - Ensure proposal aligns with simplified direction

#### 📋 Short-term (Before Implementation)

1. **Add implementation section** - Lane ownership, timeline, acceptance criteria
2. **Create pilot plan** - Test with one lane before full rollout
3. **Define exceptions** - When is "next steps" required vs. optional?
4. **Document training plan** - How will developers learn the new workflow?
5. **Add ADR number** - This should be ADR-0002 (0001 is ideas deprecation)

#### 🎯 Long-term (Post-Implementation)

1. **30-day checkpoint** - Gather feedback, identify friction
2. **90-day review** - Refine automation, adjust mandatory vs. optional
3. **Retrospective** - Document lessons learned for future ADRs

---

### Lane D Decision (Historical)

**Status:** ⚠️ **BLOCKED - Cannot proceed without addressing critical blockers**

**Rationale:**

1. No infrastructure exists to enforce this workflow
2. ADR conflicts with recent simplification direction (ideas deprecation)
3. Cross-lane coordination required but not planned
4. Implementation effort (3-4 weeks) not acknowledged

**Next Steps:**

1. **ADR Author:** Revise proposal to address blockers
2. **Lane B:** Create templates as foundation (2-3 days)
3. **Lane A:** Build validation utilities (3-5 days)
4. **Lane C:** Scope automation feasibility (1 week)
5. **Lane D:** Re-review revised ADR after prerequisites met

**Estimated Timeline to Unblock:** 2-3 weeks (if lanes prioritize immediately)

---

### Alternative Recommendation

If the goal is **incremental traceability improvement**, Lane D recommends:

**Option A: Lightweight First (Faster)**

1. Add simple PR template with "Related Issue: #xxx" field (Lane B, 1 day)
2. Add CI check that PR has "Related Issue" or "Fixes #xxx" (Lane C, 2 days)
3. Document best practices without enforcing (Lane B, 1 day)
4. Monitor adoption for 30 days
5. Revisit automation if manual compliance is high

**Benefits:**

- Faster to implement (3-4 days vs. 3-4 weeks)
- Lower risk, easier rollback
- Tests cultural adoption before heavy automation

**Option B: Defer Until Templates Exist**

1. Block this ADR until issue/PR templates are created
2. Run a pilot with one lane using templates (manual process)
3. Validate "Why this matters" is useful before automating
4. Build automation only after proving value

---

**Lane D Sign-off (Historical):** Blocked (superseded)

## Current Sign-off (Phase 1)

| Lane            | Approval          | Date       |
| --------------- | ----------------- | ---------- |
| D (Program Ops) | ✅                | 2025-11-03 |
| B (Narrative)   | ✅                | 2025-11-03 |
| C (Automation)  | ✅ (Phase 1 only) | 2025-11-03 |
| A (Tooling)     | ✅                | 2025-11-03 |

Next Review: 2025-12-03 (Adoption checkpoint)

**Reviewed By:** Lane D (Program Operations)  
**Review Date:** November 3, 2025  
**Next Review:** After prerequisites addressed (estimated 2025-11-17 earliest)
