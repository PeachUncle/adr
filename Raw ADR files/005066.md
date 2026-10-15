# ADR-001: Use PEP 723 Inline Script Dependencies

**Status:** Accepted
**Date:** 2025-11-19
**Context:** Plugin Marketplace Migration

## Context

The agent-skills repository contains Python scripts that require external dependencies (httpx, click, markdownify). We need a dependency management strategy that:

1. Allows scripts to be self-contained and portable
2. Works seamlessly with UV's script execution model
3. Avoids the complexity of managing requirements.txt files
4. Enables users to run scripts without manual dependency installation

## Decision

We will use **PEP 723 inline script dependencies** for all Python scripts in the marketplace.

Each script will declare its dependencies in a special comment block:

```python
# /// script
# dependencies = [
#   "httpx>=0.24.0",
#   "click>=8.1.0",
#   "markdownify>=0.11.0",
# ]
# ///
```

UV automatically detects this metadata and installs dependencies in an isolated environment when running scripts via `uv run script.py`.

## Rationale

### Advantages

1. **Self-Contained Scripts**: Each script declares its own dependencies, eliminating drift between requirements.txt and actual usage.

2. **UV Integration**: UV natively supports PEP 723, automatically creating isolated environments with correct dependencies.

3. **Version Transparency**: Dependencies and versions are visible at the top of each script, making it clear what the script requires.

4. **No Coordination Overhead**: No need to maintain a single requirements.txt file or coordinate dependency versions across multiple scripts.

5. **Portability**: Scripts can be copied or moved without losing their dependency information.

6. **Marketplace Compatibility**: Claude Code plugin marketplace supports PEP 723 scripts via UV execution.

### Trade-offs

1. **Duplication**: Common dependencies (httpx, click) are declared multiple times across scripts.
   - *Acceptable*: Scripts are small in number (2 for web-access, 10 for kalshi-markets), and duplication is minimal.

2. **Environment Overhead**: Each script execution may create separate UV environments.
   - *Mitigated*: UV caches environments efficiently, reusing them when dependency sets match.

3. **Dependency Conflicts**: Different scripts could specify incompatible versions of the same library.
   - *Unlikely*: Our scripts use different libraries or compatible version ranges.

## Alternatives Considered

### Alternative 1: Single requirements.txt

**Rejected** because:
- Requires coordination between all scripts
- Prone to drift (scripts use dependencies not in requirements.txt)
- Less portable (users must install dependencies separately)
- Doesn't align with UV's script-first execution model

### Alternative 2: pyproject.toml with optional dependencies

**Rejected** because:
- Requires installing the repository as a package
- Adds complexity for simple script execution
- Doesn't align with marketplace script execution model

### Alternative 3: No dependency management

**Rejected** because:
- Scripts would fail without manual dependency installation
- Poor user experience
- Incompatible with marketplace expectations

## Implementation

1. All Python scripts include PEP 723 dependency blocks
2. UV handles dependency installation automatically
3. Scripts execute via: `uv run plugins/*/skills/*/scripts/script.py`
4. Test suite validates PEP 723 syntax in all scripts

## Consequences

### Positive

- Scripts "just work" when executed with UV
- Clear dependency visibility
- Easy to add new scripts with different dependencies
- Marketplace-ready out of the box

### Negative

- Slight duplication of common dependencies
- Requires UV for script execution (documented requirement)

## References

- [PEP 723: Inline script metadata](https://peps.python.org/pep-0723/)
- [UV Script Support](https://docs.astral.sh/uv/guides/scripts/)
- [Claude Code Plugin Documentation](https://code.claude.com/docs/en/plugins)
