---
docid: ADR-054
title: ADR 020 Pr Quality Gate
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿# PR Quality Gate Implementation - ADR

**DocID**: `ADR-020`  
**Title**: PR Quality Gate with Free Code Quality Tools  
**Date**: 2. Januar 2026  
**Status**: ✅ Accepted  
**Deciders**: @Architect, @TechLead, @DevOps, @QA, @Security

---

## Context

B2X needs a comprehensive PR quality gate to ensure:
- All code is tested before merge (80%+ backend, 70%+ frontend coverage)
- Security vulnerabilities are caught early
- Code quality standards are maintained
- No breaking changes without approval
- Compliance requirements are met

**Requirements**:
- Must be **free** (no SonarQube Enterprise costs)
- Must be **automated** (no manual gates)
- Must be **fast** (<20 min total)
- Must block PR merges if quality fails

---

## Decision

Implement **5-stage PR quality gate** using free tools:

```
Stage 1: Fast Checks (2 min)
  ├─ Lint (ESLint, dotnet format)
  ├─ Type Check (TypeScript)
  └─ Secret Detection (TruffleHog)

Stage 2: Unit Tests (5 min)
  ├─ Backend tests + coverage (≥80%)
  └─ Frontend tests + coverage (≥70%)

Stage 3: Integration Tests (10 min)
  ├─ API integration tests
  ├─ Database integration tests
  └─ Service integration tests

Stage 4: E2E Tests (15 min)
  └─ Critical user flows (Playwright)

Stage 5: Security & Quality (10 min)
  ├─ Mega-Linter (code quality)
  ├─ GitHub CodeQL (security)
  ├─ Dependency scanning (npm audit, dotnet vulnerable)
  └─ License compliance

Final: Quality Gate ✅/❌
```

**NEW (2025-01-02): Single-Topic Enforcement**
- ✅ Branch naming convention validated
- ✅ Topic declaration in PR template
- ✅ Automated mixed-topic detection
- ✅ SARAH quality gate for topic coherence

---

## Tool Selection

| Tool | Purpose | Cost | Why Selected |
|------|---------|------|--------------|
| **Mega-Linter** | Code quality (50+ linters) | FREE | Comprehensive, well-maintained |
| **GitHub CodeQL** | Security analysis | FREE | Advanced security scanning |
| **Roslynator** | C# code analysis | FREE | Best-in-class for .NET |
| **ESLint** | JS/TS linting | FREE | Industry standard |
| **TruffleHog** | Secret detection | FREE | High accuracy |
| **npm audit** | Frontend dependencies | FREE | Built-in |
| **dotnet vulnerable** | Backend dependencies | FREE | Built-in |
| **Coverage** | Test coverage | FREE | Built-in (.NET, Vitest) |

**Total Cost**: $0/month (vs $150-500/mo for SonarCloud/Enterprise)

---

## Alternatives Considered

### 1. SonarQube Enterprise
- ❌ **Rejected**: Costs $150-500/month
- ✅ **Alternative**: SonarQube Community Edition (free, self-hosted)
- ⚠️ **Decision**: Use Mega-Linter + CodeQL instead (no hosting needed)

### 2. CodeClimate
- ❌ **Rejected**: Limited free tier, costs for private repos
- ✅ **Alternative**: Mega-Linter (fully free)

### 3. Codacy
- ❌ **Rejected**: Costs for private repos
- ✅ **Alternative**: Mega-Linter + CodeQL

### 4. Manual Code Review Only
- ❌ **Rejected**: Too slow, inconsistent, error-prone
- ✅ **Decision**: Automated gates + human review

---

## Implementation

### GitHub Branch Protection Rules
```yaml
Require before merging:
  ✅ Status checks must pass:
    - fast-checks
    - unit-tests (with coverage)
    - integration-tests
    - e2e-tests
    - security-compliance
    - quality-gate
  ✅ Require 2 approvals
  ✅ Require review from code owners
  ✅ Dismiss stale approvals when new commits pushed
  ✅ Require conversation resolution
  ✅ Require linear history
  ❌ Do not allow bypassing (except emergency hotfixes)
```

### Coverage Thresholds
```yaml
Backend:
  Unit Tests: ≥80% line coverage
  Critical Paths: 100% coverage
  New Code: ≥85% coverage

Frontend:
  Unit Tests: ≥70% line coverage
  Components: ≥75% coverage
  New Code: ≥75% coverage

Integration:
  API Endpoints: ≥90% coverage
```

### Quality Gate Failure Conditions
- Any test fails → ❌ Block merge
- Coverage below threshold → ❌ Block merge
- Security vulnerability (high/critical) → ❌ Block merge
- Secrets detected → ❌ Block merge
- License compliance failure → ❌ Block merge
- Required reviews missing → ❌ Block merge

### Override Process (Emergency Only)
1. Document reason in PR
2. Get approval from @SARAH + @TechLead + domain expert
3. Create follow-up issue to fix quality gaps
4. Merge with override
5. Post-merge: Fix within 24 hours

---

## Benefits

### For Developers
- ✅ Immediate feedback (fast checks in 2 min)
- ✅ Clear quality requirements
- ✅ Automated fixes suggested (Mega-Linter)
- ✅ Consistent standards enforced
- ✅ Learning from code quality feedback

### For Team
- ✅ Higher code quality
- ✅ Fewer bugs in production
- ✅ Easier code reviews (basics handled by automation)
- ✅ Enforced testing culture
- ✅ Security vulnerabilities caught early

### For Project
- ✅ Zero cost ($0/month)
- ✅ Reduced technical debt
- ✅ Compliance requirements met
- ✅ Faster development (less debugging)
- ✅ Confidence in deployments

---

## Risks & Mitigations

### Risk: CI Pipeline Too Slow
- **Mitigation**: Fast-fail pattern (stop at first failure)
- **Mitigation**: Parallel execution where possible
- **Mitigation**: Cache dependencies aggressively
- **Target**: <20 min total (currently ~15 min)

### Risk: False Positives
- **Mitigation**: Tunable linter rules (`.mega-linter.yml`)
- **Mitigation**: Suppress specific warnings (with justification)
- **Mitigation**: Review and adjust thresholds quarterly

### Risk: Coverage Gaming
- **Mitigation**: Code review checks test quality
- **Mitigation**: Mutation testing (quarterly)
- **Mitigation**: E2E tests verify real behavior

### Risk: Developer Friction
- **Mitigation**: Clear documentation and training
- **Mitigation**: Local testing before push
- **Mitigation**: Helpful error messages
- **Mitigation**: Quick feedback loop

---

## Monitoring & Success Metrics

### Track Weekly
- % PRs passing first CI run (target: >80%)
- Average time from PR open to merge (target: <2 days)
- Number of quality gate overrides (target: 0)
- Test coverage trend (should increase)
- Production bugs traced to missing tests (target: 0)

### Review Monthly
- Adjust coverage thresholds if needed
- Review and tune linter rules
- Update tool versions
- Analyze false positive rate

### Review Quarterly
- Run mutation testing
- Review quality metrics dashboard
- Update ADR with learnings
- Consider new tools/practices

---

## Migration Plan

### Week 1: Setup (✅ COMPLETED)
- [x] Create GitHub Actions workflow
- [x] Configure Mega-Linter
- [x] Configure CodeQL
- [x] Create CODEOWNERS file
- [x] Create PR template
- [x] Document tools
- [x] **Add single-topic enforcement** (2025-01-02)
  - [x] Update PR template with topic declaration
  - [x] Create branch naming guidelines (GL-004)
  - [x] Create PR topic validation workflow
  - [x] Document SARAH quality gate criteria

### Week 2: Testing
- [ ] Test on sample PRs
- [ ] Tune linter rules
- [ ] Adjust coverage thresholds if needed
- [ ] Train team on workflow

### Week 3: Rollout
- [ ] Enable branch protection rules
- [ ] Make quality gate required
- [ ] Monitor for issues
- [ ] Collect feedback

### Week 4: Optimization
- [ ] Review metrics
- [ ] Fix any bottlenecks
- [ ] Document lessons learned
- [ ] Celebrate success! 🎉

---

## References

- [Mega-Linter Documentation](https://megalinter.io/)
- [GitHub CodeQL Documentation](https://codeql.github.com/)
- [Free Code Quality Tools Guide](.ai/knowledgebase/tools-and-tech/free-code-quality-tools.md)
- [GitHub Branch Protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)

---

## Lessons Learned (To be updated)

**Post-implementation updates**:
- [To be added after Week 2-4]

---

**Decision Made**: 2. Januar 2026  
**Implemented**: GitHub Actions workflow, Mega-Linter, CodeQL, CODEOWNERS  
**Next Review**: 1. Februar 2026  
**Status**: ✅ Accepted and implemented
