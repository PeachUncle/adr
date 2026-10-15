# 10. Extended Linting Strategy

Date: 2025-08-30

## Status

Accepted

## Context

While the project had established a strong code quality toolchain with ESLint, Prettier, and TypeScript (ADR-0006), we identified the need for comprehensive linting beyond just source code. Modern projects contain various file types that benefit from consistent formatting and validation:

- **Markdown files**: Documentation, README files, and ADRs
- **YAML files**: Configuration files, CI/CD workflows
- **JSON files**: Configuration, package manifests, data files
- **GitHub Actions workflows**: Complex YAML with specific syntax requirements

Key requirements:

- Consistent formatting across all file types
- Early detection of syntax errors and common mistakes
- Integration with existing pre-commit hooks and CI/CD pipeline
- Minimal impact on developer workflow
- Clear error messages and automatic fixing where possible

## Decision

We implemented a comprehensive linting strategy covering all major file types:

1. **Markdown Linting**: markdownlint-cli2 for documentation consistency
2. **YAML Linting**: yamllint for configuration file validation
3. **JSON Linting**: jsonc-eslint-parser integrated with ESLint
4. **GitHub Actions Linting**: actionlint for workflow validation

### Implementation Details

- **Markdown Linting (markdownlint-cli2)**:
  - Enforces consistent heading hierarchy
  - Ensures proper list formatting and spacing
  - Validates link syntax and references
  - Automatic fixing with `pnpm lint:markdown:fix`
  - Configuration in `.markdownlint.json`

- **YAML Linting (yamllint)**:
  - Validates YAML syntax and structure
  - Enforces consistent indentation (2 spaces)
  - Checks for duplicate keys and empty values
  - Excludes generated files (pnpm-lock.yaml)
  - Configuration in `.yamllint`

- **JSON Linting (ESLint with jsonc-parser)**:
  - Integrated into existing ESLint configuration
  - Supports JSON with comments (JSONC)
  - Validates package.json structure
  - Automatic fixing through ESLint

- **GitHub Actions Linting (actionlint)**:
  - Validates workflow syntax before push
  - Catches common workflow mistakes
  - Checks for deprecated actions
  - Shell script wrapper for portability
  - Runs in CI to prevent broken workflows

- **Integration**:
  - All linters run in pre-commit hooks via lint-staged
  - Parallel execution in CI/CD for performance
  - Integrated into `pnpm precommit` command
  - Clear error messages with fix suggestions

## Consequences

### Positive

- **Documentation Quality**: Consistent, well-formatted documentation
- **Configuration Safety**: Early detection of configuration errors
- **CI/CD Reliability**: Workflow errors caught before deployment
- **Developer Experience**: Automatic fixing reduces manual work
- **Maintainability**: Consistent formatting across all file types
- **Learning**: Clear linting rules help developers learn best practices
- **Reduced Reviews**: Less time spent on formatting in code reviews

### Negative

- **Additional Dependencies**: More development dependencies to maintain
- **Learning Curve**: Developers need to understand multiple linting tools
- **Configuration Overhead**: Multiple configuration files to maintain
- **Performance Impact**: Additional ~3-5 seconds to pre-commit checks
- **False Positives**: Occasionally flags intentional formatting choices

### Mitigation

- **Documentation**: Clear documentation of linting rules and exceptions
- **Automatic Fixing**: Most issues can be auto-fixed with `:fix` commands
- **Selective Enforcement**: Critical rules enforced, stylistic rules as warnings
- **Performance**: Linters run in parallel where possible
- **Escape Hatches**: Clear documentation for disabling rules when needed
- **Training**: Team guidance on working with various linters

## References

- [markdownlint Documentation](https://github.com/DavidAnson/markdownlint)
- [yamllint Documentation](https://yamllint.readthedocs.io/)
- [ESLint JSON Plugin](https://ota-meshi.github.io/eslint-plugin-jsonc/)
- [actionlint Documentation](https://github.com/rhysd/actionlint)
- [PR #87: Add markdown linting](https://github.com/sapientpants/agentic-node-ts-starter/pull/87)
- [PR #88: Add YAML linting](https://github.com/sapientpants/agentic-node-ts-starter/pull/88)
