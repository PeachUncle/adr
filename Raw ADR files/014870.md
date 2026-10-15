# ADR-0010: Remove Database Dependencies from pytest-jux

**Status**: Accepted
**Date**: 2025-10-20
**Decision Makers**: Georges Martin
**Supersedes**: ADR-0003 (database-related sections only)
**Related**: ADR-0003 (technology stack)

## Context

ADR-0003 established the technology stack for pytest-jux, including:
- XML processing: lxml, signxml, cryptography
- **Database layer**: SQLAlchemy, Alembic, psycopg
- pytest integration and CLI tools

However, as the project architecture evolved and was documented in CLAUDE.md and project documentation, the **client-server separation became clear**:

### Current Architecture

**pytest-jux (Client-Side)**:
- Signs JUnit XML reports with XMLDSig
- Computes canonical hashes (C14N + SHA-256)
- Captures environment metadata
- **Publishes signed reports to Jux REST API via HTTP**
- Provides local storage/caching (filesystem, XDG-compliant)

**Jux API Server (Separate Project, Server-Side)**:
- **Receives signed reports via REST API**
- **Verifies XMLDSig signatures**
- **Stores reports in database (SQLite/PostgreSQL)**
- **Detects duplicates via canonical hash comparison**
- Provides query API and Web UI

### The Problem

pytest-jux currently has SQLAlchemy, Alembic, and psycopg as **required dependencies**, but:

1. **Not Used**: No database models exist in `pytest_jux/` codebase
2. **No Imports**: No SQLAlchemy imports anywhere in the source code
3. **Wrong Layer**: Database functionality belongs in Jux API Server, not the client plugin
4. **Unnecessary Bloat**: Forces users to install ~15MB of database libraries they don't need
5. **Confusing Documentation**: ADR-0003 implies pytest-jux does database operations

### Evidence of Non-Use

```bash
$ grep -r "from sqlalchemy" pytest_jux/
# No results

$ grep -r "import sqlalchemy" pytest_jux/
# No results

$ grep -r "from alembic" pytest_jux/
# No results
```

The only reference to SQLAlchemy in the project is **documentation** (CLAUDE.md, ADR-0003), not code.

## Decision

**Remove SQLAlchemy, Alembic, and psycopg dependencies from pytest-jux.**

### What's Being Removed

From `pyproject.toml` dependencies:
```python
"sqlalchemy>=2.0",      # REMOVED
"alembic>=1.12",        # REMOVED
"psycopg[binary]>=3.1", # REMOVED
```

### What Remains

All other dependencies stay:
- **lxml, signxml, cryptography**: XML signing and canonicalization
- **pytest, pytest-metadata**: Plugin framework and metadata
- **configargparse, pydantic**: Configuration management
- **rich**: Terminal output
- **requests**: REST API client (for publishing to Jux API Server)

### Architectural Clarity

**pytest-jux responsibilities**:
- ✅ Sign JUnit XML reports (client-side)
- ✅ Compute canonical hashes
- ✅ Capture environment metadata
- ✅ Publish to REST API
- ✅ Local filesystem caching
- ❌ Database storage (server-side, Jux API Server)
- ❌ Duplicate detection via database (server-side)

## Alternatives Considered

### 1. Keep Dependencies "For Future Use"

**Pros**:
- No immediate breaking change
- Might be useful someday

**Cons**:
- Bloated installation (~15MB unused libraries)
- Confusing architecture (is this client or server?)
- Violates single responsibility principle
- Users pay installation/dependency cost for unused features

**Decision**: Rejected - YAGNI (You Aren't Gonna Need It)

### 2. Move to Optional Dependencies

```python
[project.optional-dependencies]
database = [
    "sqlalchemy>=2.0",
    "alembic>=1.12",
    "psycopg[binary]>=3.1",
]
```

**Pros**:
- Available if needed
- Doesn't bloat default installation

**Cons**:
- Still implies database functionality exists
- No actual code to use these dependencies
- Misleading to users

**Decision**: Rejected - There's no database code to optionally enable

### 3. Complete Removal (Chosen)

**Pros**:
- Clean separation of client/server responsibilities
- Smaller installation size
- Clear architecture
- No misleading documentation
- Aligns with actual codebase

**Cons**:
- Breaking change for anyone who installed pytest-jux expecting database features (unlikely - none exist)
- Need to update documentation

**Decision**: Accepted - Reflects reality of the codebase

## Consequences

### Positive

1. **Clearer Architecture**: pytest-jux is unambiguously a client-side plugin
2. **Smaller Installation**: ~15MB fewer dependencies (SQLAlchemy + psycopg2 + Alembic)
3. **Faster Installation**: Fewer packages to download and compile (psycopg2-binary)
4. **Reduced Attack Surface**: Fewer dependencies = smaller CVE exposure
5. **Accurate Documentation**: ADR-0003 database sections clearly superseded
6. **Correct Responsibility**: Database logic stays in Jux API Server where it belongs

### Negative

1. **Documentation Updates Required**: ADR-0003, CLAUDE.md, README.md need clarification
2. **Breaking Change** (Theoretical): If anyone relied on these deps (unlikely - no code uses them)
3. **Git History**: Large change in dependency list

### Neutral

1. **No Code Changes**: No actual source code affected (dependencies weren't used)
2. **Server Unaffected**: Jux API Server still uses SQLAlchemy/PostgreSQL
3. **Functionality Unchanged**: pytest-jux still does everything it did before

## Migration Impact

### For Existing Users

**Impact**: None (positive)
- No code was using SQLAlchemy/Alembic/psycopg
- Functionality is identical
- Smaller, faster installation

**Upgrade Path**:
```bash
# Existing installation
pip install pytest-jux==0.1.8  # Had SQLAlchemy

# After upgrade
pip install --upgrade pytest-jux==0.1.9  # No SQLAlchemy
# Still works exactly the same
```

### For Jux API Server Development

**Impact**: None
- Jux API Server is a **separate project**
- It has its own dependencies
- Not affected by pytest-jux changes

## Documentation Updates

### ADR-0003 Status Update

Add note to ADR-0003:

```markdown
**Status**: Partially Superseded

**Note**: The database-related sections (SQLAlchemy, Alembic, psycopg) were
superseded by ADR-0010. Database functionality resides in the Jux API Server
(separate project), not in pytest-jux. The XML processing, pytest integration,
and REST API client sections remain valid.
```

### CLAUDE.md Clarifications

Already states:
> "This project does **NOT** include database models (`models.py`) or database
> integration. These are handled by the Jux API Server."

No changes needed - already accurate.

### README.md

Already states:
> "pytest-jux is the **client component** in a client-server architecture"

Already clear that database is server-side. No changes needed.

## Validation

### Dependency Check

```bash
# Before
$ pip list | grep -E "sqlalchemy|alembic|psycopg"
SQLAlchemy    2.0.23
alembic       1.13.0
psycopg       3.1.14

# After
$ pip list | grep -E "sqlalchemy|alembic|psycopg"
# (empty - not installed)
```

### Functionality Verification

```bash
# All existing functionality still works
$ pytest --junit-xml=report.xml --jux-sign --jux-key=key.pem
# ✓ Signs reports
# ✓ Computes canonical hashes
# ✓ Stores locally
# ✓ No database operations (never had any)
```

## References

### Internal

- **ADR-0003**: Technology stack (database sections superseded)
- **CLAUDE.md**: Client-server architecture documentation
- **README.md**: Project architecture overview

### Technology Stack (Remaining)

- **lxml**: XML processing and C14N
- **signxml**: XMLDSig signatures
- **cryptography**: Key management
- **pytest**: Plugin framework
- **requests**: REST API client for Jux API Server

### Jux API Server (Separate Project)

The following technologies are used by the **Jux API Server**, not pytest-jux:
- **Elixir/Phoenix**: Web framework (planned)
- **PostgreSQL/SQLite**: Database storage
- **Ecto**: Database ORM (Elixir's SQLAlchemy equivalent)

## Implementation

### Checklist

- [x] Remove dependencies from `pyproject.toml`
- [x] Verify no code uses removed dependencies (already verified)
- [x] Update ADR-0003 status
- [x] Update CHANGELOG.md
- [x] Create ADR-0010
- [x] Test installation without database dependencies
- [ ] Update ADR index (docs/adr/README.md)
- [ ] Verify all tests pass
- [ ] Tag next release (0.1.9)

### Version Impact

- **Breaking**: No (dependencies weren't used)
- **Next Version**: 0.1.9 (patch - removing unused deps is a bugfix)
- **Changelog Category**: Changed (dependencies removed)

## Success Criteria

1. ✅ SQLAlchemy, Alembic, psycopg removed from dependencies
2. ✅ All tests pass (no code changes)
3. ✅ Installation size reduced by ~15MB
4. ✅ Documentation accurately reflects client-side-only architecture
5. ⏳ Clean install works without database dependencies

## Timeline

- **2025-10-20**: ADR created and accepted
- **2025-10-20**: Dependencies removed from pyproject.toml
- **2025-10-20**: CHANGELOG.md updated
- **Next**: Test and release as v0.1.9

---

**Conclusion**: Removing unused database dependencies aligns pytest-jux with its actual architecture as a client-side plugin, reduces bloat, and improves clarity. Database functionality remains in the Jux API Server where it belongs.

**Adopted**: 2025-10-20
**Author**: Georges Martin
**Impact**: Low (removing unused dependencies)
**Effort**: Minimal (documentation updates)
