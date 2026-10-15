# ADR-0005: Standardize Build Automation with Makefile

## Status
**Proposed**

## Context

Development environment setup and common operations currently require developers to remember multiple commands, specific Python package versions, and manual setup procedures. This creates several problems:

- Inconsistent development environments across team members
- Manual setup steps that are error-prone and time-consuming  
- Different approaches to running tests, linting, and CI validation locally
- No standardized way to reproduce CI environment locally
- Barrier to entry for new team members and contributors

The AgenticOps Value Train™ emphasizes reproducible, automated workflows that work consistently across different environments and team members.

## Decision

We will implement a standardized build automation system using a Makefile that provides:

### Standard Targets
1. **Environment Management**
   - `make venv`: Create and configure virtual environment
   - `make install`: Install dependencies from requirements.txt
   - `make clean`: Remove build artifacts and temporary files

2. **Development Operations**
   - `make lint`: Run all linting tools (flake8, black, isort, mypy)
   - `make test`: Execute complete test suite with coverage
   - `make ci`: Run full CI pipeline locally (lint + test + validation)

3. **Convenience Operations**
   - `make format`: Auto-format code using black and isort
   - `make check`: Quick validation without full test suite
   - `make help`: Display available targets and descriptions

### Implementation Principles
- **Idempotent Operations**: Targets can be run multiple times safely
- **Fail Fast**: Stop immediately on first error
- **Verbose Output**: Clear feedback on what's happening
- **Cross-Platform**: Work on Linux, macOS, and Windows (where possible)
- **CI Alignment**: Local `make ci` mirrors GitHub Actions exactly

## Consequences

### Positive
- **Consistency**: Same commands work for all developers regardless of local setup
- **Onboarding**: New team members can get productive quickly with `make venv && make install`
- **CI Alignment**: `make ci` provides exact local reproduction of CI environment
- **Documentation**: Makefile serves as executable documentation of build process
- **Automation Ready**: Supports both human and automated (Auto-Pilot) execution

### Negative
- **Make Dependency**: Requires GNU Make to be installed (standard on most systems)
- **Learning Curve**: Team must learn Makefile syntax for modifications
- **Platform Limitations**: Some Windows environments may have limited Make support
- **Abstraction Layer**: Adds layer between developers and underlying tools

### Neutral
- **Tool Lock-in**: Standardizes on specific versions of linting and testing tools
- **Maintenance Overhead**: Makefile requires updates as tooling evolves

## Rationale

Makefile was chosen for build automation because:

1. **Universal Tool**: Available on virtually all development platforms
2. **Industry Standard**: Well-understood approach to build automation
3. **Simple Syntax**: Easy to read, modify, and maintain
4. **Dependency Management**: Built-in support for target dependencies
5. **Integration Friendly**: Works seamlessly with CI/CD systems

### Alternatives Considered
- **Shell Scripts**: Less portable, no dependency management
- **Task Runners**: (npm scripts, invoke, etc.) Add unnecessary dependencies
- **Docker**: Overkill for basic build automation, adds complexity
- **IDE-Specific**: Doesn't work across different development environments

### Integration Strategy
- Mirror all Makefile operations in GitHub Actions CI
- Document Makefile usage in README and development guides
- Include Makefile validation in git hooks
- Provide Windows-specific instructions where needed

## Related Decisions
- Supports ADR-0001 (AgenticOps Value Train) by enabling consistent automation
- Enables ADR-0002 (Auto-Pilot) by providing standardized execution interface
- Integrates with ADR-0003 (Git Hooks) for consistent validation
- Required for ADR-0004 (Session Context) automated updates

## References
- [GNU Make Manual](https://www.gnu.org/software/make/manual/) for syntax reference
- [Value Train Alignment Plan](../../value-train-alignment-plan.md) - CRD-A tasks
- [Planning Tasks](../../planning-tasks.md) for linting requirements
- [CI Workflow](.github/workflows/ci.yml) for alignment requirements