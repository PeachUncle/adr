# ADR 0020: Markdown Quality Automation and Regression Prevention

**Status:** Accepted
**Date:** 2025-10-18
**Deciders:** AI Agent, Project Maintainers
**Tags:** `documentation`, `quality`, `automation`, `tooling`

## Context

As of October 2025, the project contains 93+ markdown files with 75+ linting violations detected by markdownlint. Key issues include:

1. **Code fence violations (MD040):** 11 instances of code fences without language specifiers
2. **Blank line violations (MD032):** 46 instances of lists without surrounding blank lines
3. **Heading violations (MD022):** 8 instances of headings without proper spacing
4. **No automated regression prevention:** Violations can be introduced without detection

**Impact:**

- Degraded documentation rendering in GitHub/IDE viewers
- Poor accessibility (missing language hints for screen readers)
- Inconsistent documentation quality
- Difficult maintenance and contribution

**Business Value:**

- Professional documentation appearance
- Improved developer experience
- Easier onboarding for contributors
- Better SEO and accessibility

## Decision

We will implement a **multi-layer markdown quality automation system** with the following components:

### Layer 1: Linting Tool (markdownlint-cli2)

**Decision:** Continue using markdownlint-cli2 as the primary markdown linter.

**Rationale:**

- Industry standard as of 2025 (1.2k+ stars, actively maintained)
- Built-in auto-fix for 24+ rules (handles 80% of violations)
- Excellent ecosystem support (pre-commit hooks, CI actions, IDE extensions)
- Custom rules support for project-specific needs
- Multiple configuration formats (JSONC, YAML, JS)

**Alternatives Considered:**

- `remark-lint`: More powerful (AST-based) but steeper learning curve, overkill for our needs
- `markdownlint-cli` (legacy): Simpler but fewer features, maintenance mode
- Custom scripts: High maintenance burden, reinventing the wheel

**Configuration:**

- Location: `.markdownlint-cli2.jsonc`
- Key rules enforced: MD040 (code fence languages), MD032 (list spacing), MD022 (heading spacing)
- Custom rules: `custom/no-closing-fence-info` (prevent language specifiers on closing fences)

### Layer 2: Pre-commit Hooks

**Decision:** Enhance existing pre-commit hook to auto-fix violations on commit.

**Rationale:**

- Immediate feedback during development
- Prevents violations from entering version control
- Auto-fix reduces developer friction

**Implementation:**

```yaml
- repo: https://github.com/DavidAnson/markdownlint-cli2
  rev: v0.18.1
  hooks:
    - id: markdownlint-cli2-docker
      args: [--fix, --config, .markdownlint-cli2.jsonc]
      exclude: ^(docs/archive/)
```

**Limitation:** Can be bypassed with `--no-verify` flag

### Layer 3: CI Validation (NEW)

**Decision:** Add GitHub Actions workflow to validate markdown in CI.

**Rationale:**

- Catches violations even if pre-commit bypassed
- Blocks merging of invalid markdown in PRs
- Provides clear failure feedback in PR checks

**Implementation:**

- Workflow: `.github/workflows/markdown-quality.yml`
- Triggers: On push/PR to main/develop when markdown files change
- Jobs: markdownlint validation + pytest quality tests

**Benefits:**

- 100% coverage (can't bypass)
- Automated PR comments with violations
- Integration with GitHub's check system

### Layer 4: Automated Tests (NEW)

**Decision:** Add pytest-based markdown quality tests.

**Rationale:**

- Programmatic verification of quality gates
- Can run in CI and locally
- Provides clear pass/fail status
- Enables regression testing

**Implementation:**

- File: `tests/test_markdown_quality.py`
- Tests:
  - `test_markdownlint_passes()` - All files pass linting
  - `test_code_fences_have_language_specifiers()` - MD040 enforcement
  - `test_no_trailing_whitespace()` - MD009 enforcement
  - `test_links_are_valid_format()` - Basic link validation

**Test Markers:**

- `@pytest.mark.unit` - Fast tests (run in pre-commit)
- `@pytest.mark.slow` - Slower tests (run in CI)

### Optional Layer: Prose Quality (Vale)

**Decision:** DEFER - Evaluate Vale integration after structural issues resolved.

**Rationale:**

- Current priority is structural quality (linting)
- Vale focuses on prose quality (grammar, style, readability)
- Adding Vale now would increase complexity without addressing root cause
- Can revisit in future initiative

**If Added Later:**

- Configuration: `.vale.ini`
- Styles: write-good (general prose), project-specific terminology
- Integration: Pre-commit hook (optional) + CI (non-blocking)

## Consequences

### Positive

1. **Comprehensive Quality Gates**
   - Multi-layer defense prevents regression
   - Auto-fix reduces manual work (80% of issues)
   - Clear feedback at multiple stages (IDE, commit, PR, tests)

2. **Improved Documentation Quality**
   - Consistent formatting across all markdown files
   - Better accessibility (code fence language specifiers)
   - Professional appearance in GitHub/IDE viewers

3. **Better Developer Experience**
   - Automated fixes reduce friction
   - Clear error messages guide corrections
   - IDE integration shows issues while editing

4. **Maintainability**
   - Automated tests prevent regression
   - CI blocks invalid markdown from merging
   - Standards documented and enforced

### Negative

1. **Initial Setup Cost**
   - Time to fix existing 75+ violations
   - Create and configure CI workflow
   - Write and maintain tests

2. **Ongoing Maintenance**
   - Keep markdownlint updated
   - Maintain test suite
   - Update configuration as rules evolve

3. **Developer Friction (Minor)**
   - Pre-commit hooks add latency (usually < 2 seconds)
   - Learning curve for markdown best practices
   - Occasional false positives requiring exceptions

### Mitigation Strategies

1. **Reduce Friction:**
   - Enable auto-fix in pre-commit (already done)
   - Provide clear error messages with fix suggestions
   - Document common patterns in `DOCUMENTATION_STANDARDS.md`

2. **Manage Maintenance:**
   - Pin tool versions for reproducibility
   - Use dependabot for automated updates
   - Document configuration decisions

3. **Handle Exceptions:**
   - Support inline disable comments where needed
   - Configure rules appropriately (e.g., line length for technical docs)
   - Document exceptions in `.markdownlint-cli2.jsonc`

## Compliance

### Security (OWASP LLM Top 10)

- **LLM02 (Insecure Output Handling):** N/A - No LLM interaction in markdown linting
- **LLM03 (Training Data Poisoning):** N/A - Static analysis only
- **LLM06 (Excessive Agency):** N/A - Automated tools, no agent decision-making

**Verdict:** No security concerns with markdown linting tooling.

### Testing (Section 1.2: Guiding Principles)

- ✅ Regression tests added (`tests/test_markdown_quality.py`)
- ✅ Tests run in CI (`.github/workflows/markdown-quality.yml`)
- ✅ Pre-commit hooks prevent violations
- ✅ Coverage: 4 test functions covering main quality gates

### Documentation (Section 1.1: Agent Persona)

- ✅ ADR created (this document)
- ✅ Configuration documented (`.markdownlint-cli2.jsonc` with comments)
- ✅ Standards to be updated (`docs/guides/DOCUMENTATION_STANDARDS.md` - Phase 6)
- ✅ Contributing guidelines to be updated (Phase 6)

## Implementation

### Phase 3: Automated Fixes (Current Phase)

1. Run `task docs:fix` to auto-fix 60 violations (MD032, MD022, MD031, MD009)
2. Review and commit auto-fixes
3. Verify no functionality broken

### Phase 4: Manual Fixes

1. Fix 11 MD040 violations (code fence language specifiers)
2. Fix 3 MD036 violations (emphasis vs headings)
3. Fix 1 MD024 violation (duplicate headings)

### Phase 5: Validation

1. Run `pytest tests/test_markdown_quality.py` (should pass)
2. Run `task docs:lint:markdown` (should show 0 errors)
3. Test pre-commit hooks (`pre-commit run --all-files`)
4. Verify CI workflow passes

### Phase 6: Documentation

1. Update `docs/guides/DOCUMENTATION_STANDARDS.md` with markdown best practices
2. Add quality checklist to contributing guidelines
3. Document common patterns and exceptions

## Alternatives Considered

### Alternative 1: Manual Review Only

**Description:** Rely on manual code review to catch markdown issues.

**Pros:**

- No tooling overhead
- Flexible (human judgment)

**Cons:**

- Error-prone (humans miss things)
- Inconsistent enforcement
- High review burden
- No automated regression prevention

**Rejected:** Automation provides better consistency and catches issues earlier.

### Alternative 2: IDE-only Validation

**Description:** Rely on IDE extensions (VS Code markdownlint) for validation.

**Pros:**

- Real-time feedback
- No CI overhead

**Cons:**

- Inconsistent (not all developers use same IDE)
- No enforcement (can commit invalid markdown)
- No automated tests

**Rejected:** IDE validation is complementary, not sufficient for enforcement.

### Alternative 3: Prose Quality First (Vale)

**Description:** Start with Vale for prose quality instead of structural linting.

**Pros:**

- Improves readability
- Enforces style guide

**Cons:**

- Doesn't address structural issues (code fences, spacing)
- More complex configuration
- Can be noisy without tuning
- Mismatches current problem (structural violations)

**Rejected:** Structural issues must be fixed first; prose quality can be added later.

## References

- [markdownlint Rules](https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md)
- [markdownlint-cli2 Documentation](https://github.com/DavidAnson/markdownlint-cli2)
- [CommonMark Specification](https://spec.commonmark.org/0.31.2/)
- [GitHub Flavored Markdown](https://github.github.com/gfm/)
- [Pre-commit Hooks Guide 2025](https://gatlenculp.medium.com/effortless-code-quality-the-ultimate-pre-commit-hooks-guide-for-2025-57ca501d9835)
- [MD040 Documentation](https://github.com/DavidAnson/markdownlint/blob/main/doc/md040.md)
- [Vale Documentation](https://vale.sh/) (for future consideration)

## Success Metrics

**Immediate (End of Initiative):**

- [ ] Zero markdownlint errors across all files
- [ ] All 4 markdown quality tests passing
- [ ] CI workflow successfully validating markdown
- [ ] Pre-commit hooks catching new violations

**Long-term (3 months):**

- [ ] Zero markdown violations introduced in PRs
- [ ] < 2% false positive rate on linting rules
- [ ] < 5 seconds pre-commit hook latency
- [ ] Documentation quality scores improve (subjective)

**Continuous:**

- Monitor violation trends (should stay at 0)
- Track false positive rate (adjust rules if needed)
- Gather contributor feedback (friction points)

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2025-10-18 | 1.0 | Initial decision for markdown quality automation |

## Related Decisions

- [ADR-0003: Documentation Standards and Structure](0003-documentation-standards-and-structure.md)
- [ADR-0002: Adopt Windsurf Workflow System](0002-adopt-windsurf-workflow-system.md)
