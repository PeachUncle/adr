# ADR-0007: Adopt Test Coverage Visibility Standards

**Status**: Proposed
**Date**: 2025-10-19
**Decision Makers**: pytest-jux maintainers
**Consulted**: OpenSSF Best Practices Badge criteria, Python packaging community standards
**Informed**: pytest-jux contributors and users

## Context

### Current State

pytest-jux has comprehensive test coverage implemented:
- Automated test suite using pytest
- Tests for all core modules (signer, verifier, canonicalizer, config, metadata, storage)
- CLI command tests (keygen, sign, verify, inspect, cache, config_cmd)
- Security-focused testing for cryptographic code

**However**, we lack **visibility** into coverage metrics:
- ❌ No coverage percentage tracking
- ❌ No coverage reporting in CI/CD
- ❌ No coverage badges on README
- ❌ No coverage trends over time
- ❌ Cannot identify untested code paths
- ❌ No PR coverage diff feedback

### Problem Statement

**Coverage visibility gaps create risks:**

1. **Quality Risk**: Cannot identify untested code paths
2. **Security Risk**: Cryptographic code may have untested branches
3. **Regression Risk**: Coverage drops go unnoticed
4. **Contribution Risk**: Contributors don't know if tests are sufficient
5. **Trust Risk**: Users cannot verify testing rigor
6. **Compliance Risk**: OpenSSF Best Practices Badge requires coverage metrics

### OpenSSF Best Practices Badge Requirements

To achieve OpenSSF Passing badge, we must meet:

**[test_statement_coverage80]** (SHOULD):
> "The project SHOULD have FLOSS automated test suite(s) that provide at least 80% statement coverage if there is at least one FLOSS tool that can measure this criterion in the selected language."

**Current Status**: We have tests but no measurement → Cannot claim compliance.

### Security Positioning

pytest-jux positions itself as a **security-focused** plugin:
- XMLDSig signature generation and verification
- Cryptographic key management
- SLSA Build Level 2 compliance
- Supply chain security focus

**Coverage visibility reinforces security credibility** by demonstrating thorough testing of security-critical code.

### Industry Standards

**Industry standard coverage thresholds** (research from 2025):
- **60%**: Acceptable minimum
- **70-80%**: Reasonable goal for most projects
- **80-90%**: Strong (industry standard)
- **90%+**: Exemplary
- **100%**: Required for safety-critical systems (aviation DO-178B)

**Coverage metrics types:**
- **Statement Coverage**: % of code lines executed (primary metric)
- **Branch Coverage**: % of if/else paths taken (secondary metric)
- **Function Coverage**: % of functions called
- **Path Coverage**: % of all possible paths (complex, rarely used)

### Available Tools

**Coverage Services Comparison (2025):**

| Tool | Open Source Pricing | GitHub Integration | Features | Community Adoption |
|------|---------------------|--------------------|-----------|--------------------|
| **Codecov** | Free | Excellent | PR comments, trends, flags | High |
| **Coveralls** | Free | Good | Simple reports, public | Medium |
| **Codacy** | Free | Good | Quality + coverage | Medium |
| **SonarCloud** | Free | Excellent | Security + coverage | High (enterprise) |

**Tool Selection Criteria:**
1. Free for open source (essential)
2. GitHub Actions integration (essential)
3. PR diff coverage comments (highly desirable)
4. Coverage trends over time (highly desirable)
5. Badge generation (essential)
6. pytest-cov compatibility (essential)
7. Community trust (important)

## Decision

**We will implement comprehensive test coverage visibility using:**

### 1. Coverage Measurement
- **Tool**: pytest-cov (pytest integration layer for coverage.py)
- **Metrics**: Statement coverage (primary), branch coverage (secondary)
- **Thresholds**:
  - **85%** statement coverage overall (strong standard)
  - **90%+** for cryptographic modules (security-critical)
  - **70%** branch coverage (secondary goal)

### 2. Coverage Reporting Service
- **Tool**: Codecov (recommended over Coveralls)
- **Reason**: Best GitHub integration, PR comments, trends, free for OSS

**Alternative**: Coveralls (if Codecov unavailable)

### 3. Visibility Channels
- **Local Development**: Terminal output + HTML reports
- **Pull Requests**: Codecov PR comments with diff coverage
- **README**: Coverage badge (green ≥80%, yellow 60-79%, red <60%)
- **Dashboard**: Codecov web UI for trends and analysis

### 4. CI/CD Integration
- Upload coverage on every push (main, develop, PRs)
- Fail PRs if coverage drops >5% (threshold for noise reduction)
- Track coverage trends over time
- Generate HTML artifacts for manual review

### 5. Configuration Standards

**pytest-cov configuration:**
```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = [
    "--cov=pytest_jux",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-report=xml",
    "--cov-fail-under=85",
]

[tool.coverage.run]
source = ["pytest_jux"]
branch = true  # Enable branch coverage
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/venv/*",
    "*/.venv/*",
]

[tool.coverage.report]
precision = 2
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]
```

**Codecov configuration:**
```yaml
# codecov.yml
coverage:
  status:
    project:
      default:
        target: 85%
        threshold: 5%  # Allow 5% drop before failing
    patch:
      default:
        target: 80%    # New code must be 80% covered
        threshold: 10%

comment:
  layout: "diff, flags, files"
  behavior: default
  require_changes: false

ignore:
  - "tests/**/*"
  - "**/__pycache__/**/*"
```

**GitHub Actions integration:**
```yaml
# .github/workflows/test.yml
- name: Run tests with coverage
  run: pytest --cov=pytest_jux --cov-report=xml --cov-report=term

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v4
  with:
    token: ${{ secrets.CODECOV_TOKEN }}
    files: ./coverage.xml
    flags: unittests
    name: pytest-jux-coverage
    fail_ci_if_error: true
```

### 6. Coverage Quality Standards

**What we measure:**
- ✅ Statement coverage (primary)
- ✅ Branch coverage (secondary)
- ✅ Missing lines identified
- ✅ Coverage trends over time
- ✅ PR diff coverage (new code)

**What we DON'T optimize for:**
- ❌ 100% coverage (diminishing returns)
- ❌ Path coverage (too complex)
- ❌ Testing getters/setters (low value)
- ❌ Artificial inflation (quality over quantity)

**Exemptions** (use `pragma: no cover` sparingly):
- Defensive assertions (should never execute)
- Type checking blocks (`if TYPE_CHECKING:`)
- Abstract methods (implemented in subclasses)
- `__repr__` methods (low security risk)
- Platform-specific code (if not testable in CI)

### 7. Module-Specific Thresholds

| Module Type | Statement Coverage | Branch Coverage | Rationale |
|-------------|-------------------|-----------------|-----------|
| **Cryptographic** (signer.py, verifier.py, canonicalizer.py) | ≥90% | ≥80% | Security-critical, must be thoroughly tested |
| **Core Logic** (config.py, metadata.py, storage.py) | ≥85% | ≥70% | Important functionality, standard threshold |
| **CLI Commands** (commands/*.py) | ≥80% | ≥65% | User-facing, less critical than crypto |
| **Plugin Integration** (plugin.py) | ≥85% | ≥70% | Core integration point |

**Enforcement**: Use coverage flags to track module groups separately.

## Consequences

### Positive Consequences

#### Quality Improvements
- ✅ **Identify untested code**: HTML reports show missing lines
- ✅ **Prevent regressions**: Coverage drops trigger PR failures
- ✅ **Guide testing efforts**: Low-coverage modules prioritized
- ✅ **Improve security**: Crypto code tested to 90%+
- ✅ **Enable refactoring**: High coverage = safe refactoring

#### Developer Experience
- ✅ **Clear expectations**: 85% threshold documented
- ✅ **Immediate feedback**: PR comments show coverage changes
- ✅ **Local visibility**: Terminal output shows missing lines
- ✅ **Visual analysis**: HTML reports for detailed inspection
- ✅ **Trend tracking**: Codecov dashboard shows progress

#### Project Credibility
- ✅ **Trust signal**: Badge demonstrates testing rigor
- ✅ **Security credibility**: High coverage for crypto code
- ✅ **OpenSSF compliance**: Meets badge requirements
- ✅ **Professional image**: Industry-standard practices
- ✅ **Transparency**: Public coverage metrics

#### Compliance
- ✅ **OpenSSF Best Practices**: Meets test_statement_coverage80 criterion
- ✅ **NIST SSDF**: Demonstrates quality assurance (PW.8)
- ✅ **EU CRA preparation**: Testing evidence for compliance
- ✅ **Audit trail**: Coverage history in Codecov

### Negative Consequences

#### Development Overhead
- ⚠️ **Initial setup time**: ~4 hours to configure tools
- ⚠️ **Test writing time**: May need tests for existing code
- ⚠️ **CI runtime**: +30 seconds per run (coverage upload)
- ⚠️ **Maintenance**: Quarterly review of coverage trends

**Mitigation**: Automate as much as possible, invest upfront.

#### Potential Misuse
- ⚠️ **Gaming metrics**: Developers may write weak tests for coverage
- ⚠️ **False security**: High coverage ≠ bug-free code
- ⚠️ **Over-optimization**: Chasing 100% wastes time

**Mitigation**:
- Emphasize quality over quantity in documentation
- Code review focuses on test quality, not just coverage %
- Accept 85% as "good enough", not 100%

#### Threshold Debates
- ⚠️ **Arbitrary thresholds**: 85% vs 80% vs 90% debates
- ⚠️ **Module exceptions**: Special cases for low-value code
- ⚠️ **Threshold drift**: Pressure to lower thresholds over time

**Mitigation**:
- Document rationale for 85% (industry standard, OpenSSF requirement)
- Use `pragma: no cover` sparingly with justification
- Periodic review (annual) of thresholds

### Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|---------|------------|
| **Codecov service outage** | Low | Medium | Have Coveralls as backup, archive coverage.xml |
| **Coverage drops below 85%** | Medium | Low | Fix immediately or document exception |
| **Gaming metrics** | Medium | Medium | Code review focuses on test quality |
| **False confidence** | Low | High | Educate: coverage ≠ correctness |
| **Threshold inflation** | Low | Low | Document 85% rationale, resist pressure |

### Alternatives Considered

#### Alternative 1: Coveralls
**Pros**: Simple, free for OSS, public reports
**Cons**: Less feature-rich than Codecov, fewer integrations
**Decision**: Codecov preferred for better GitHub integration

#### Alternative 2: SonarCloud
**Pros**: Quality + coverage + security scanning
**Cons**: Heavyweight, more complex setup
**Decision**: Overkill for pytest-jux, may reconsider for Silver badge

#### Alternative 3: No Coverage Service (Local Only)
**Pros**: No external dependencies, complete control
**Cons**: No PR comments, no trends, no badge
**Decision**: Rejected - visibility is the goal

#### Alternative 4: Higher Threshold (90%)
**Pros**: Demonstrates exceptional rigor
**Cons**: Diminishing returns, slows development
**Decision**: Rejected - 85% is industry standard, 90% for crypto only

#### Alternative 5: Lower Threshold (70%)
**Pros**: Easier to achieve, less pressure
**Cons**: Doesn't meet OpenSSF SHOULD criteria (80%)
**Decision**: Rejected - want "strong" standard, not "acceptable"

### Implementation Plan

**Phase 1: Local Setup** (Week 1, Day 1-2)
1. Add pytest-cov to dev dependencies
2. Configure pyproject.toml with coverage settings
3. Test locally: `pytest --cov=pytest_jux`
4. Verify HTML reports work
5. Ensure coverage ≥85% (write tests if needed)

**Phase 2: CI Integration** (Week 1, Day 3-4)
1. Create Codecov account
2. Add CODECOV_TOKEN to GitHub Secrets
3. Update .github/workflows/test.yml
4. Test coverage upload on push
5. Verify Codecov dashboard populates

**Phase 3: PR Integration** (Week 1, Day 5)
1. Create codecov.yml configuration
2. Test PR comment generation
3. Verify coverage diff works
4. Set project/patch thresholds

**Phase 4: Visibility** (Week 2, Day 1)
1. Add coverage badge to README.md
2. Link to Codecov dashboard
3. Document coverage standards in CONTRIBUTING.md
4. Update OpenSSF badge application

**Phase 5: Validation** (Week 2, Day 2-3)
1. Review all module coverage percentages
2. Identify gaps in crypto modules
3. Write additional tests if needed
4. Verify all thresholds met

### Rollback Plan

If Codecov integration fails:
1. **Immediate**: Remove Codecov upload from CI (keep pytest-cov)
2. **Short-term**: Use Coveralls as alternative
3. **Long-term**: Self-host coverage reports (GitHub Pages)

If coverage threshold blocks development:
1. **Immediate**: Lower threshold to 80% temporarily
2. **Short-term**: Identify problematic modules
3. **Long-term**: Write tests or document exemptions

### Success Criteria

**Technical Success:**
- [ ] pytest-cov configured in pyproject.toml
- [ ] Coverage ≥85% overall
- [ ] Coverage ≥90% for crypto modules
- [ ] Codecov account created and integrated
- [ ] Coverage uploaded on every push
- [ ] PR comments show coverage diff
- [ ] Badge displayed on README
- [ ] HTML reports generated in CI

**Process Success:**
- [ ] Developers run coverage locally
- [ ] PRs fail if coverage drops >5%
- [ ] Coverage trends visible in Codecov
- [ ] Gaps identified and prioritized
- [ ] OpenSSF badge criteria met

**Community Success:**
- [ ] Badge shows green (≥80%)
- [ ] Users trust testing rigor
- [ ] Contributors know coverage expectations
- [ ] Security researchers see crypto coverage

## Related Decisions

- **ADR-0002**: Adopt Development Best Practices (TDD foundation)
- **ADR-0005**: Adopt Python Ecosystem Security Framework (quality standards)
- **ADR-0006**: Adopt SLSA Build Level 2 Compliance (security posture)
- **Sprint 1**: Core Infrastructure (implemented test suite)
- **Sprint 6**: OpenSSF Best Practices Badge (requires coverage visibility)

## References

### Standards and Frameworks
- [OpenSSF Best Practices Badge Criteria](https://www.bestpractices.dev/en/criteria)
- [NIST SSDF PW.8: Quality Assurance](https://csrc.nist.gov/publications/detail/sp/800-218/final)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)

### Research and Best Practices
- [Scientific Python Coverage Guide](https://learn.scientific-python.org/development/guides/coverage/)
- [Minimum Acceptable Code Coverage](https://www.bullseye.com/minimum.html)
- [Atlassian Code Coverage Guide](https://www.atlassian.com/continuous-delivery/software-testing/code-coverage)
- Stack Overflow: [Reasonable Code Coverage %](https://stackoverflow.com/questions/90002/)

### Tools and Services
- [Codecov Documentation](https://docs.codecov.com/)
- [Coveralls Documentation](https://docs.coveralls.io/)
- [GitHub Actions Coverage Integration](https://github.com/codecov/codecov-action)

### Industry Data
- **70-80%**: Reasonable goal for most projects (Bullseye)
- **80-90%**: Strong coverage (Atlassian)
- **60/75/90%**: Acceptable/Commendable/Exemplary (TechTarget)
- **100%**: Required for DO-178B aviation safety

---

**Decision Date**: 2025-10-19
**Status**: Proposed (to be accepted after Sprint 6 Week 1)
**Next Review**: 2026-01-19 (quarterly review of thresholds)
