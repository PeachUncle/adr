# ADR-001: Use Ruff for Linting and Formatting

**Date:** 2025-11-02  
**Status:** Accepted  
**Deciders:** Development Team  

---

## Context

Python projects typically require multiple tools for code quality:
- Black for formatting
- isort for import sorting
- flake8 for linting
- pyupgrade for syntax upgrades
- bandit for security
- autoflake for unused imports

Managing 6+ tools with different configurations is complex and slow.

## Decision

Use **Ruff** as our single tool for linting and formatting.

Ruff is:
- **10-100x faster** than existing tools (written in Rust)
- **All-in-one** - replaces 10+ tools
- **Compatible** with existing configurations
- **Actively maintained** by Astral (creators of uv)

## Consequences

### Positive

- ✅ **Single tool** instead of 6+
- ✅ **Faster** - runs in milliseconds instead of seconds
- ✅ **Simpler** configuration (one pyproject.toml section)
- ✅ **Better** pre-commit experience
- ✅ **Modern** Python practices enforced

### Negative

- ⚠️  Newer tool (less mature than Black)
- ⚠️  Some rules still being added
- ⚠️  Team needs to learn one new tool

### Neutral

- 🔄 Existing code needs one-time reformatting
- 📚 Documentation uses Ruff examples

## Alternatives Considered

### Alternative 1: Keep Black + flake8 + isort

**Pros:**
- Well-established tools
- Team already familiar
- Extensive documentation

**Cons:**
- Slow (seconds vs milliseconds)
- Multiple configurations to maintain
- Dependency conflicts common
- Different formatters disagree

**Why not chosen:** Speed and maintenance burden too high

### Alternative 2: Use Pylint

**Pros:**
- Very comprehensive
- Catches many issues

**Cons:**
- Extremely slow
- Too opinionated
- Many false positives
- Difficult configuration

**Why not chosen:** Too slow and opinionated for modern development

## References

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Ruff GitHub](https://github.com/astral-sh/ruff)
- [Speed Comparisons](https://github.com/astral-sh/ruff#benchmarks)
- [Migration Guide](https://docs.astral.sh/ruff/formatter/#black-compatibility)

