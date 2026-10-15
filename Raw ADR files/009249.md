# ADR-012: uv as Python Package Manager

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2025-12-05 |
| **Decision Makers** | Project Team |

## Context

The project-starter backend requires a Python dependency management solution that addresses several concerns:

1. **Installation Speed**: CI/CD pipelines and developer workflows suffer from slow dependency installation. pip with large dependency trees (FastAPI, SQLAlchemy, cryptography) can take 30-60+ seconds
2. **Reproducibility**: Production deployments must use exact same dependency versions as development and CI
3. **Modern Standards Compliance**: Python packaging has evolved significantly (PEP 517, 518, 621, 660). The chosen tool should embrace these standards
4. **Developer Experience**: Simple commands, clear error messages, and minimal configuration
5. **Docker Integration**: Container builds should be fast and cacheable

The backend uses Python 3.13 with async FastAPI, SQLAlchemy, and modern type hints. The tooling should align with this forward-looking technology stack.

## Decision

We chose **uv** as the Python package manager for generated backend projects.

uv is an extremely fast Python package installer and resolver, written in Rust by Astral (the same team behind Ruff). Key implementation details:

**pyproject.toml Configuration** (`backend/pyproject.toml`):
```toml
[project]
name = "{{cookiecutter.project_slug}}-backend"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "fastapi==0.115.0",
    "sqlalchemy[asyncio]==2.0.35",
    # ... pinned dependencies
]

[tool.uv]
dev-dependencies = [
    "pytest==8.3.3",
    "ruff==0.7.2",
]
```

**Lock File Generation** (`uv.lock`):
- Generated via `uv lock` during post-generation hook
- Contains cryptographic hashes for all dependencies
- Ensures byte-for-byte reproducible installations

**Dockerfile Integration**:
```dockerfile
# Install uv in base image
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies from lock file
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev
```

**Runtime Commands**:
```bash
uv run uvicorn app.main:app --reload    # Development server
uv run pytest tests/ -v                  # Test execution
uv run alembic upgrade head              # Database migrations
```

## Consequences

### Positive

1. **Dramatic Speed Improvement**: uv installs dependencies 10-100x faster than pip. Cold installs that took 60+ seconds now complete in 2-5 seconds. This compounds across CI runs and developer workflows

2. **Reproducible Builds**: The `uv.lock` file ensures identical dependency versions across all environments. Unlike pip's `requirements.txt`, it includes transitive dependency hashes

3. **Modern Standards Compliance**: Uses `pyproject.toml` (PEP 621) as the single source of truth for project metadata. No separate `setup.py`, `setup.cfg`, or `requirements.txt` files needed

4. **Simplified Dependency Groups**: Dev dependencies defined in `[tool.uv.dev-dependencies]` section. Production builds exclude dev dependencies with `--no-dev` flag

5. **Consistent Virtual Environment**: uv manages virtual environments automatically. `uv run` ensures commands execute in the correct environment without manual activation

6. **Docker Layer Caching**: Lock file changes only when dependencies change, enabling efficient Docker layer caching:
   ```dockerfile
   COPY pyproject.toml uv.lock ./
   RUN uv sync --frozen  # Cached unless lock file changes
   COPY . .              # Application code layer
   ```

7. **Rust-Powered Reliability**: Memory-safe implementation with robust error handling. Clear error messages for resolution conflicts

### Negative

1. **Tool Maturity**: uv is newer (2024) than established tools like pip (2008) or poetry (2018). While rapidly maturing, edge cases may exist

2. **Team Learning Curve**: Developers familiar with pip or poetry need to learn new commands (`uv sync`, `uv lock`, `uv run`)

3. **Ecosystem Integration**: Some CI/CD platforms and IDE plugins have better support for pip/poetry. Custom setup may be needed

4. **Dependency on External Binary**: uv must be installed separately (not a pure Python tool). Requires curl during Docker build

### Neutral

1. **Lock File Format**: uv uses its own lock file format (not `poetry.lock` or `requirements.txt`). Migration from other tools requires regenerating the lock file

2. **No Built-in Publishing**: uv focuses on dependency management, not package publishing. Use `hatch` or `twine` for PyPI publishing if needed

## Alternatives Considered

### pip + requirements.txt

**Approach**: Traditional pip with requirements files and optional pip-tools for compilation.

**Why Not Chosen**:
- Significantly slower (10-100x) for dependency installation
- No native lock file format (pip-compile adds complexity)
- Manual virtual environment management
- requirements.txt doesn't capture full dependency metadata

### Poetry

**Approach**: Feature-rich dependency management with `pyproject.toml` and `poetry.lock`.

**Why Not Chosen**:
- Notably slower than uv (though faster than pip)
- Custom metadata format in `pyproject.toml` predates PEP 621 (being migrated)
- Larger tool footprint with built-in virtual environment and publishing
- Shell activation workflow less elegant than `uv run`

### pipenv

**Approach**: Combined pip and virtualenv with Pipfile and Pipfile.lock.

**Why Not Chosen**:
- Performance issues with large dependency trees (resolution can be very slow)
- Less active maintenance compared to alternatives
- Non-standard Pipfile format (not pyproject.toml)
- Complex lock file format

### pip-tools

**Approach**: pip + pip-compile + pip-sync for requirements management.

**Why Not Chosen**:
- Still uses pip for installation (slow)
- Requires multiple tools (pip-compile, pip-sync)
- More manual workflow than modern alternatives
- No unified configuration (separate requirements.in files)

### PDM

**Approach**: Modern PEP 621-compliant package manager.

**Why Not Chosen**:
- Slower than uv (Python-based resolver)
- Smaller community and ecosystem than poetry
- Less momentum than uv despite similar goals

---

## Related ADRs

- [ADR-001: FastAPI as Backend Framework](./001-fastapi-backend-framework.md) - Framework whose dependencies uv manages
- [ADR-010: Docker Compose for Development](./010-docker-compose-development.md) - Container environment using uv

## Implementation References

- `template/{{cookiecutter.project_slug}}/backend/pyproject.toml` - Project configuration and dependencies
- `template/{{cookiecutter.project_slug}}/backend/Dockerfile` - Container build using uv
- `hooks/post_gen_project.py` - Generates `uv.lock` after project creation
