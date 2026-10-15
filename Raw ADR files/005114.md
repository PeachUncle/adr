# 14. Extended Code Quality Toolchain

Date: 2025-08-30

## Status

Accepted

Supersedes: [ADR-0006](./0006-code-quality-toolchain-eslint-prettier-strict-typescript.md)

## Context

While ADR-0006 established a strong foundation with ESLint, Prettier, and TypeScript, the project's growth revealed the need for more comprehensive quality enforcement:

- **Documentation Quality**: Markdown files had inconsistent formatting
- **Configuration Safety**: YAML and JSON files lacked validation
- **CI/CD Reliability**: GitHub Actions workflows had no pre-push validation
- **Continuous Monitoring**: No centralized tracking of code quality trends
- **Technical Debt**: No systematic approach to managing and reducing debt

The original toolchain focused primarily on source code, but modern projects require quality enforcement across all file types and continuous monitoring of quality metrics.

## Decision

We extended the code quality toolchain to cover all aspects of the project:

1. **Extended Linting** (ADR-0010):
   - Markdown linting with markdownlint-cli2
   - YAML linting with yamllint
   - JSON linting via ESLint integration
   - GitHub Actions linting with actionlint

2. **Continuous Quality Monitoring** (ADR-0011):
   - Automated issue detection and remediation
   - Quality gates on pull requests
   - Historical tracking of metrics

3. **Runtime Validation** (ADR-0012):
   - Zod for runtime type validation
   - Schema-driven validation at system boundaries
   - Type inference from validation schemas

### Implementation Details

The extended toolchain maintains the original foundation while adding:

- **Unified Pre-commit Hooks**: All linters run via lint-staged
- **Parallel CI/CD Execution**: Linters run concurrently for performance
- **Automatic Fixing**: Most issues can be auto-fixed with `:fix` commands
- **Automated Remediation**: Claude commands for fixing common issues

## Consequences

### Positive

All benefits from ADR-0006, plus:

- **Comprehensive Coverage**: Quality enforcement for all file types
- **Early Detection**: Issues caught before they reach production
- **Continuous Improvement**: Trends visible over time
- **Reduced Manual Work**: Automated fixing and remediation
- **Better Documentation**: Consistent, well-formatted docs
- **Safer Configuration**: Validated YAML and JSON files

### Negative

All challenges from ADR-0006, plus:

- **Additional Tools**: More dependencies and configurations
- **Increased Complexity**: Multiple tools to understand
- **Longer Pre-commit**: Additional 3-5 seconds for all linters
- **Learning Curve**: Developers need to understand more tools

### Mitigation

Extends mitigations from ADR-0006:

- **Clear Documentation**: Comprehensive guides for all tools
- **Gradual Adoption**: Tools can be adopted incrementally
- **Escape Hatches**: Clear ways to bypass when necessary
- **Automation**: Most issues fixed automatically

## References

- [ADR-0006: Original Code Quality Toolchain](./0006-code-quality-toolchain-eslint-prettier-strict-typescript.md)
- [ADR-0010: Extended Linting Strategy](./0010-extended-linting-strategy.md)
- [ADR-0011: Runtime Validation with Zod](./0011-runtime-validation-with-zod.md)
