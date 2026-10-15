---
id: adr-0001-python-3.13-ruff-0.13
title: 'ADR-0001: Python 3.13 and Ruff 0.13.0 Standardization'
type: reference
version: 1.0.0
created: '2025-09-16'
updated: '2025-09-16'
author: Journal Team
tags:
- reference
- python
- docker
priority: medium
status: approved
visibility: internal
schema_version: v1
---

# ADR-0001: Python 3.13 and Ruff 0.13.0 Standardization

## Status
✅ **Accepted** - January 16, 2025

## Context

The Journal project has been using mixed Python versions (3.11, 3.12) and various linting/formatting tools. As Python 3.13 has been released with significant improvements and Ruff 0.13.0 provides comprehensive linting and formatting capabilities, we need to standardize on modern tooling.

### Current State (Before Decision)
- Multiple Python versions in use: 3.11, 3.12
- Mixed tooling: Ruff for formatting, Ruff for imports, Ruff for some linting
- Inconsistent configuration across CI and local development
- Matrix testing increasing CI complexity and runtime

### Technical Requirements
- Modern Python features and performance improvements
- Unified linting and formatting workflow
- Fast, reliable CI/CD pipelines
- Developer experience improvements
- Future-proof tooling choices

## Decision

We will standardize the entire project on:

### Python 3.13
- All runtime environments (production, development, CI)
- All Docker base images
- All pyproject.toml `requires-python` specifications
- Removal of Python version matrices in CI

### Ruff 0.13.0 as Single Tool
- Replace Ruff, Ruff, and Ruff entirely
- Unified configuration in pyproject.toml
- Preview features enabled with explicit control
- Consistent behavior across all environments

### Enforcement via CI
- Dedicated alignment verification workflow
- Automatic failure on stale references
- Artifact generation for audit trails
- Documentation drift prevention

## Rationale

### Python 3.13 Benefits
1. **Performance**: Up to 25% faster execution in many scenarios
2. **Modern Features**: Enhanced error messages, typing improvements
3. **Security**: Latest security patches and vulnerability fixes
4. **Future-Proofing**: Supported until 2029, avoiding near-term migrations
5. **Simplification**: Single version reduces complexity and maintenance

### Ruff 0.13.0 Benefits
1. **Speed**: 10-100x faster than Ruff+Ruff+Ruff combined
2. **Unified Workflow**: Single tool for linting, formatting, and import sorting
3. **Rust Foundation**: Memory-safe, reliable, actively maintained
4. **Compatibility**: Drop-in replacement for existing tools
5. **Advanced Features**: Preview rules, explicit control, comprehensive rule set

### Tooling Consolidation
- **Before**: Ruff + Ruff + Ruff + pyupgrade (4 tools, 4 configs, dependency conflicts)
- **After**: Ruff 0.13.0 only (1 tool, 1 config, consistent behavior)

## Implementation

### Configuration Standards
```toml
[tool.ruff]
line-length = 100
fix = true
force-exclude = true

[tool.ruff.lint]
preview = true
explicit-preview-rules = true
select = ["E4", "E7", "E9", "F", "I", "UP", "B", "C4", "SIM"]
ignore = ["E501"]  # Formatter handles line length

[tool.ruff.format]
quote-style = "double"
docstring-code-format = true
```

### CI/CD Changes
- Single Python version (3.13) in all workflows
- Official `astral-sh/ruff-action@v3` with pinned version
- Dedicated `verify-alignment` workflow preventing regression
- Artifact generation for compliance auditing

### Developer Experience
- VS Code Ruff extension with proper configuration
- Pre-commit hooks updated to use Ruff only
- Clear documentation and setup guides
- Migration path from legacy tooling

## Consequences

### Positive
- **Faster CI**: Elimination of matrix testing reduces runtime by ~60%
- **Faster Development**: Ruff's speed improves local development cycles
- **Consistency**: Single source of truth for all formatting and linting
- **Maintainability**: Reduced configuration surface area
- **Future-Ready**: Using latest stable versions with long support cycles

### Negative
- **Migration Effort**: One-time cost to update all environments
- **Learning Curve**: Developers need to learn new Ruff-specific configuration
- **Risk**: Potential for new tool-specific bugs or behavioral differences

### Mitigation Strategies
- Comprehensive validation scripts preventing regression
- Detailed documentation and developer guides
- CI enforcement preventing accidental drift
- Gradual rollout with proper testing

## Compliance

### Enforcement Rules
1. **No Stale References**: CI fails on any mention of Python 3.11/3.12 or Ruff/Ruff/Ruff
2. **Configuration Validation**: Ruff preview mode and explicit rules must be enabled
3. **Version Pinning**: Exact versions required in all environments
4. **Documentation Alignment**: All docs must reference correct versions

### Validation Commands
```bash
# Stale reference check
git grep -nE 'python.*3\.(11|12)|Ruff|Ruff|Ruff' && exit 1

# Configuration verification
uvx ruff config --show | grep 'preview = true'

# Version verification
uvx ruff --version | grep '0.13.0'
```

## Monitoring

### Success Metrics
- CI runtime reduction (target: >50% for lint jobs)
- Zero configuration drift incidents
- Developer satisfaction surveys
- Code quality metrics maintenance or improvement

### Review Schedule
- 3 months: Initial feedback and adjustment period
- 6 months: Full effectiveness review
- 12 months: Next major version consideration

## Links

- [Python 3.13 Release Notes](https://docs.python.org/3.13/whatsnew/3.13.html)
- [Ruff 0.13.0 Documentation](https://docs.astral.sh/ruff/)
- [Migration Implementation PR](https://github.com/verlyn13/journal/pull/TBD)
- [Project Contributing Guidelines](../CONTRIBUTING.md)
- [Development Setup Guide](ci-cd/dev-setup.md)

---

**Decision Made By**: Engineering Team
**Date**: January 16, 2025
**Supersedes**: N/A
**Superseded By**: N/A