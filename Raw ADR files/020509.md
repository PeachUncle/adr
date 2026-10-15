# ADR 0005: Quality Gates and Testing Requirements

**Status**: Accepted  
**Date**: 2026-01-05  
**Context**: Feature 003 - Automated Binary Release Pipeline  
**Related**: [spec.md](../../specs/003-automated-release-pipeline/spec.md), FR-007, FR-008, T062-T065

## Context

To ensure code quality and prevent regressions, we need automated quality gates that:

1. Run tests on all branches before allowing merge to main
2. Report code coverage to Codacy for visibility
3. Enforce minimum quality standards
4. Balance strictness with developer productivity

The specification defines:

- **FR-007**: All feature/fix branches tested before merge
- **FR-008**: Code coverage reported to Codacy
- **SC-002**: Target 80% code coverage (aspirational, not blocking)

## Decision

### Test Execution: Mandatory and Blocking

**Rule**: All tests MUST pass before merging to main.

**Implementation**: GitHub branch protection rule + `.github/workflows/test.yml`

**Configuration**:

```yaml
# Repository Settings → Branches → main → Branch protection rules
- Require status checks to pass before merging
- Required status check: "Test and Coverage / Run Tests"
```

**Behavior**:

- ❌ **Test failure** → Merge blocked, PR shows red status
- ✅ **Test success** → Merge allowed, PR shows green status

**Rationale**:

1. **Regression Prevention**: Broken code cannot reach main branch
2. **Quality Assurance**: Every release is backed by passing tests
3. **Developer Confidence**: Failures caught early in PR review
4. **Compliance**: Meets FR-007 requirement

### Code Coverage: Warning Only (Non-Blocking)

**Rule**: Code coverage reported to Codacy, but coverage drops do NOT block merge.

**Implementation**: Codacy integration in `.github/workflows/test.yml`

**Configuration**:

```yaml
- name: Upload coverage to Codacy
  uses: codacy/codacy-coverage-reporter-action@a38818475bb21847788496e9f0fddaa4e84955ba
  with:
    project-token: ${{ secrets.CODACY_PROJECT_TOKEN }}
    coverage-reports: ${{ steps.coverage.outputs.coverage-file }}
  continue-on-error: true  # Coverage upload failure does not block PR
```

**Behavior**:

- 📊 **Coverage < 80%** → Codacy comment on PR (warning), merge allowed
- 📉 **Coverage drops** → Codacy comment shows decrease, merge allowed
- 📈 **Coverage increases** → Codacy comment shows improvement, merge allowed
- ❌ **Codacy upload fails** → Warning logged, merge allowed (transient failure tolerance)

**Rationale**:

1. **Visibility**: Coverage trends visible in Codacy dashboard and PR comments
2. **Non-Blocking**: Allows pragmatic balance between coverage and velocity
3. **Aspirational Goal**: 80% is a target, not a hard requirement
4. **Transient Failure Tolerance**: Codacy API outages do not block development
5. **Developer Accountability**: Coverage warnings encourage but do not enforce coverage improvements

### Quality Gate Policy Summary

| Check                        | Status        | Blocks Merge? | Rationale                                    |
| ---------------------------- | ------------- | ------------- | -------------------------------------------- |
| **Test Execution**           | Required      | ✅ Yes        | Prevents regressions, ensures correctness    |
| **Code Coverage**            | Informational | ❌ No         | Encourages improvement, tolerates pragmatism |
| **Coverage Threshold (80%)** | Aspirational  | ❌ No         | Goal, not requirement (SC-002)               |
| **Codacy Upload Failure**    | Warning       | ❌ No         | Transient API failures should not block work |

## Alternatives Considered

### Alternative 1: Strict Coverage Threshold (80% Blocking)

**Approach**: Require 80% code coverage before allowing merge

**Pros**:

- Forces high test coverage
- Ensures comprehensive testing

**Cons**:

- Blocks pragmatic development (e.g., integration tests vs. unit tests)
- Encourages "gaming the system" (meaningless tests to hit threshold)
- Slows velocity for diminishing returns (80% → 85% may require disproportionate effort)
- Transient failures (Codacy API outage) block all PRs

**Rejected**: Too strict, reduces developer productivity without proportional quality gain.

### Alternative 2: No Coverage Reporting

**Approach**: Run tests, but do not report coverage

**Pros**:

- Simplest implementation
- No external service dependency

**Cons**:

- Violates FR-008 requirement (Codacy integration)
- No visibility into coverage trends
- Cannot track quality improvements over time

**Rejected**: Does not meet specification requirement.

### Alternative 3: Coverage Threshold on Main Only

**Approach**: Enforce 80% coverage only on main branch, not on feature branches

**Pros**:

- Allows experimentation on feature branches
- Ensures main branch quality

**Cons**:

- Requires post-merge enforcement (revert bad merges)
- Poor developer experience (surprises after merge)
- Defeats purpose of PR review

**Rejected**: Post-merge enforcement is too late.

## Consequences

### Positive

- **Regression Prevention**: Broken tests cannot merge to main
- **Developer Experience**: Clear pass/fail status in PR checks
- **Quality Visibility**: Coverage trends visible in Codacy dashboard
- **Pragmatic Balance**: Strict on correctness (tests), lenient on metrics (coverage)
- **Resilience**: Transient Codacy failures do not block development

### Negative

- **Coverage Not Enforced**: Projects may drift below 80% coverage without intervention
- **Manual Oversight Required**: Team must review Codacy warnings and act on them
- **Potential Technical Debt**: Low-coverage code may accumulate over time

### Mitigation Strategies

1. **Regular Coverage Reviews**: Monthly review of Codacy dashboard in team meetings
2. **Coverage Targets in PRs**: Encourage reviewers to request tests for low-coverage changes
3. **Codacy Quality Goals**: Set Codacy project goal to 80%, track progress
4. **Documentation**: Document coverage expectations in `CONTRIBUTING.md`

## Implementation

### Branch Protection Rules (GitHub Repository Settings)

```yaml
# Settings → Branches → main → Branch protection rules
protection:
  required_status_checks:
    strict: true  # Require branch to be up to date before merging
    checks:
      - "Test and Coverage / Run Tests"  # Required
  # Note: Codacy checks are NOT required
```

### Test Workflow Configuration

```yaml
# .github/workflows/test.yml
jobs:
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    steps:
      - name: Run tests with coverage
        run: |
          dotnet test wt.sln \
            --configuration Release \
            --no-build \
            --verbosity normal \
            --collect:"XPlat Code Coverage" \
            --results-directory ./coverage \
            --logger "trx;LogFileName=test-results.trx"

      - name: Upload coverage to Codacy
        uses: codacy/codacy-coverage-reporter-action@a38818475bb21847788496e9f0fddaa4e84955ba
        with:
          project-token: ${{ secrets.CODACY_PROJECT_TOKEN }}
          coverage-reports: ${{ steps.coverage.outputs.coverage-file }}
        continue-on-error: true  # Non-blocking

      - name: Publish test results
        if: always()
        uses: dorny/test-reporter@bdab7eb6dfb6be17ac3d72352f67e559a72c8db1
        with:
          name: Test Results
          path: '**/TestResults/*.trx'
          reporter: dotnet-trx
          fail-on-error: true  # Test failures block merge
```

### Release Workflow Quality Gate

```yaml
# .github/workflows/release.yml
build:
  name: Build Binaries
  needs: calculate-version
  if: needs.calculate-version.outputs.should-release == 'true'
  # Implicitly depends on test.yml passing (branch protection)
```

**Note**: Release workflow only runs on main branch, which already has passing tests (enforced by branch protection).

## Testing Requirements Documentation

### Developer Guide (docs/ja/CONTRIBUTING.md)

- **Test Expectations**: All new features must include tests
- **Coverage Goal**: Aim for 80% coverage, but not strictly enforced
- **Test Types**: Unit tests (required), integration tests (recommended)
- **Test Failures**: Must be fixed before merge

### Pull Request Template (.github/PULL_REQUEST_TEMPLATE.md)

```markdown
## Testing Checklist

- [ ] All tests pass locally (`dotnet test`)
- [ ] New features include unit tests
- [ ] Coverage is maintained or improved (check Codacy comment)
- [ ] No test warnings or errors in output
```

## Monitoring and Metrics

### Metrics to Track

1. **Test Pass Rate**: % of PRs with passing tests (target: 100%)
2. **Average Coverage**: Project-wide coverage (target: 80%)
3. **Coverage Trend**: Month-over-month coverage change
4. **Codacy Upload Success Rate**: % of coverage reports successfully uploaded (target: > 95%)

### Alerts

- **Test Failure Spike**: > 10% of PRs failing tests → Investigate test flakiness
- **Coverage Drop**: > 5% coverage decrease in 1 month → Team review required
- **Codacy Upload Failures**: > 20% failures → Check Codacy service health

## Documentation

- **User Guide**: [quickstart.md](../../specs/003-automated-release-pipeline/quickstart.md)
- **Developer Guide**: [docs/ja/CONTRIBUTING.md](../ja/CONTRIBUTING.md) (to be created)
- **Testing Guide**: [specs/003-automated-release-pipeline/testing-guide.md](../../specs/003-automated-release-pipeline/testing-guide.md) (T070)

## References

- [GitHub Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [Codacy Coverage Reporter Action](https://github.com/codacy/codacy-coverage-reporter-action)
- [FR-007: Test Automation](../../specs/003-automated-release-pipeline/spec.md)
- [FR-008: Coverage Reporting](../../specs/003-automated-release-pipeline/spec.md)
- [SC-002: Coverage Goal](../../specs/003-automated-release-pipeline/spec.md)

## Review Schedule

This ADR should be reviewed:

- If test pass rate drops below 90%
- If average coverage drops below 70% (10% below goal)
- If quality gates prove too strict or too lenient
- Quarterly during team retrospectives
