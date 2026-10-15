# ADR-001: Phase 1 Subagent Orchestration Strategy

**Status**: Accepted
**Date**: 2025-11-12
**Decision Makers**: Lead Architect Orchestrator
**Context**: Phase 1 (Repository Setup & Cleanup) implementation planning

---

## Context

Phase 1 of the MeatyMusic AMCS bootstrap implementation requires copying infrastructure from MeatyPrompts and removing domain-specific code. This involves multiple technical domains (backend, frontend, DevOps, documentation) with clear dependency relationships between tasks.

**Key Challenges**:
1. 50+ discrete tasks across 4 major categories
2. Strong dependencies between some tasks (e.g., structure must exist before copying files)
3. Opportunities for parallelization in others (e.g., backend and frontend copy are independent)
4. Need to maintain clean separation of concerns across specialist agents
5. Critical to avoid MeatyPrompts domain code leaking into MeatyMusic

**Goals**:
- Minimize Phase 1 duration (target: 3-5 days)
- Maximize parallel execution where possible
- Ensure clean handoffs between specialists
- Maintain architectural integrity throughout

---

## Decision

Adopt a **4-phase sequential-parallel hybrid execution model** with 6 specialized subagents:

### Execution Model

```
Phase 1A (Sequential): Structure Analysis → Directory Creation → Root Config Copy
    ↓
Phase 1B (Parallel): Backend Copy + Frontend Copy + Claude Code Copy + DevOps Copy
    ↓
Phase 1C (Sequential): Domain Code Removal → Cleanup Verification
    ↓
Phase 1D (Parallel): Documentation + Validation
```

### Subagent Assignments

1. **system-architect**: Structure analysis, Claude Code configuration, architectural decisions
2. **devops-architect**: Monorepo setup, root configs, Docker, CI/CD, infrastructure validation
3. **python-backend-engineer**: Backend infrastructure copy, backend validation
4. **frontend-developer**: Frontend infrastructure copy, frontend validation
5. **refactoring-expert**: Domain code removal, cleanup verification
6. **documentation-writer**: All documentation updates and migration logs
7. **task-completion-validator**: Final compliance review and sign-off

### Critical Path

**Day 1** (Sequential - 6 hrs):
- system-architect: Analyze MeatyPrompts (2 hrs) → BLOCKER
- devops-architect: Create structure + root config (4 hrs) → BLOCKER

**Day 2** (Parallel - 6 hrs):
- python-backend-engineer: Backend copy (6 hrs)
- frontend-developer: Frontend copy (6 hrs) [parallel]
- system-architect: Claude Code (2 hrs) [parallel]
- devops-architect: DevOps infrastructure (4 hrs) [parallel]

**Day 3** (Sequential then Parallel - 8 hrs):
- refactoring-expert: Remove domain code (6 hrs) → BLOCKER
- Then parallel validation (2 hrs)

**Day 4** (Sequential - 6 hrs):
- documentation-writer: Docs (4 hrs) → BLOCKER
- task-completion-validator: Review (2 hrs) → GATE

**Total Duration**: 3.5-4 days with parallelization vs 7+ days sequential

---

## Rationale

### Architectural Principles Applied

1. **Separation of Concerns**: Each subagent operates within their domain expertise
   - system-architect: Strategic architecture decisions
   - devops-architect: Build systems and infrastructure
   - python-backend-engineer: Python/FastAPI implementation
   - frontend-developer: React/Next.js implementation
   - refactoring-expert: Code cleanup and removal
   - documentation-writer: Human-facing documentation
   - task-completion-validator: Quality gates

2. **Dependency Management**: Sequential phases enforce hard dependencies
   - Can't copy files before directory structure exists (1A → 1B)
   - Can't remove domain code before infrastructure is copied (1B → 1C)
   - Can't validate before cleanup is complete (1C → 1D)

3. **Parallelization Optimization**: Independent tasks run concurrently
   - Backend, frontend, Claude Code, DevOps copies are independent (Phase 1B)
   - Validation tasks are independent once cleanup completes (Phase 1D)
   - Estimated 50% time savings vs sequential execution

4. **Clean Handoffs**: Each phase produces clear deliverables for next phase
   - 1A outputs: Structure + root config → enables 1B
   - 1B outputs: Copied infrastructure → enables 1C
   - 1C outputs: Clean codebase → enables 1D
   - 1D outputs: Validated + documented system → Phase 2 ready

5. **Quality Gates**: task-completion-validator at end ensures:
   - All success criteria met
   - No MeatyPrompts domain references remain
   - CI/CD pipelines pass
   - Documentation is complete

### Trade-offs Considered

**Alternative 1: Fully Sequential Execution**
- Pros: Simpler coordination, no race conditions
- Cons: 7+ days duration, inefficient resource utilization
- Verdict: REJECTED - Too slow

**Alternative 2: Fully Parallel Execution**
- Pros: Maximum parallelization (could be 1.5 days)
- Cons: Complex coordination, race conditions, dependency violations
- Verdict: REJECTED - Too risky, would cause merge conflicts and missing dependencies

**Alternative 3: Single Generalist Agent**
- Pros: No coordination overhead, consistent decisions
- Cons: No specialist expertise, slower overall, higher error rate
- Verdict: REJECTED - Doesn't leverage specialist strengths

**Selected: Hybrid Sequential-Parallel (4 phases)**
- Pros: Balances speed with safety, leverages specialist expertise, clear gates
- Cons: Requires orchestration overhead, phase transitions add slight delay
- Verdict: ACCEPTED - Optimal balance

---

## Consequences

### Positive

1. **Time Efficiency**: 3.5-4 days vs 7+ days sequential (50% reduction)
2. **Risk Mitigation**: Sequential phases prevent dependency violations
3. **Specialist Expertise**: Each domain handled by appropriate expert
4. **Clear Accountability**: Each subagent owns specific deliverables
5. **Quality Assurance**: task-completion-validator ensures clean handoff to Phase 2
6. **Parallel Validation**: Independent validation streams speed up Day 3-4

### Negative

1. **Orchestration Overhead**: Requires coordination between 6 subagents
2. **Blocking Points**: 3 critical blockers (Day 1, Day 3 start, Day 4) where progress stops
3. **Context Switching**: Subagents must wait for their phase (idle time)
4. **Communication**: Clear handoff documentation required between phases

### Mitigation Strategies

1. **Orchestration Overhead**: Lead architect monitors progress tracker, unblocks issues
2. **Blocking Points**: Start next phase immediately when blocker clears
3. **Context Switching**: Pre-assign tasks so subagents know when they're needed
4. **Communication**: Progress tracker updated at phase boundaries with clear deliverables

---

## Implementation Notes

### Phase Transition Checklist

**1A → 1B Transition**:
- [ ] Structure analysis document exists
- [ ] Monorepo directories created
- [ ] Root config files copied
- [ ] pnpm workspace initialized
- → **GATE**: devops-architect confirms structure ready

**1B → 1C Transition**:
- [ ] Backend infrastructure copied
- [ ] Frontend infrastructure copied
- [ ] Claude Code configuration copied
- [ ] DevOps infrastructure copied
- → **GATE**: All 4 parallel streams complete

**1C → 1D Transition**:
- [ ] Backend domain code removed
- [ ] Frontend domain code removed
- [ ] Placeholder files created
- [ ] Initial grep audit passes
- → **GATE**: refactoring-expert confirms cleanup complete

**1D → Phase 2 Transition**:
- [ ] Backend starts without errors
- [ ] Frontend builds successfully
- [ ] Docker Compose services start
- [ ] CI/CD pipelines pass
- [ ] Documentation updated
- [ ] task-completion-validator approves
- → **GATE**: Phase 1 complete, Phase 2 can begin

### Subagent Coordination Protocol

Each subagent updates progress tracker with:
1. **Tasks started**: Mark in-progress in checklist
2. **Tasks completed**: Mark complete + add to "Completed Tasks" section
3. **Blockers encountered**: Add to "Blocked" section with details
4. **Files changed**: Update "Files Changed" section
5. **Phase transition**: Notify lead architect for gate review

Lead architect reviews gates and approves phase transitions.

---

## References

- [Phase 1 Progress Tracker](/Users/miethe/dev/homelab/development/MeatyMusic/docs/project_plans/impl_tracking/bootstrap-phase-1/progress/phase-1-progress.md)
- [Phase 1 Implementation Plan](/Users/miethe/dev/homelab/development/MeatyMusic/docs/project_plans/bootstrap-from-meatyprompts/phase-1-repository-setup.md)
- [Bootstrap Overview](/Users/miethe/dev/homelab/development/MeatyMusic/docs/project_plans/bootstrap-from-meatyprompts.md)

---

## Approval

**Decision**: ACCEPTED
**Date**: 2025-11-12
**Approver**: Lead Architect Orchestrator
**Next Review**: After Phase 1 completion (retrospective on orchestration effectiveness)
