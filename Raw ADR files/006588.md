# ADR-0002: Upstream Repository Management

## Status

Accepted

## Date

2024-10-18

## Context

The project converts [Awesome-CV](https://github.com/posquit0/Awesome-CV) LaTeX templates to Jinja2. Awesome-CV cannot be installed via pip, but we need to:

- Track upstream updates
- Convert `.tex` files to `.tex.j2`
- Keep installation simple for end users

## Options Considered

### Option 1: Git Submodule

Include Awesome-CV as a git submodule.

**Pros:**

- Explicit version tracking
- Standard git workflow

**Cons:**

- Complicates `pip install` (submodules not fetched automatically)
- Packaging and distribution problems
- Users must run extra commands (`git submodule update --init`)
- CI/CD complexity

### Option 2: Vendoring (copy files)

Copy Awesome-CV files directly into the repository.

**Pros:**

- Simple distribution
- No external dependencies

**Cons:**

- Manual update process
- License compliance concerns
- Large repository size
- No clear upstream tracking

### Option 3: Dev-only Clone

Clone upstream to a gitignored directory. Commit only converted templates.

**Pros:**

- Simple `pip install` for users
- Clean separation of dev and user workflows
- Easy upstream tracking for developers
- Small package size

**Cons:**

- Two-step process for contributors
- Converted files may diverge from upstream

## Decision

Use dev-only clone approach:

```
dev/upstream/awesome-cv/  — git clone (gitignored)
src/.../templates/        — converted .tex.j2 files (committed)
```

Track upstream version in `UPSTREAM_VERSION` file.

## Consequences

### Positive

- End users get ready-to-use templates via `pip install`
- Developers can track and update upstream easily
- No submodule complexity
- Clear separation of concerns

### Negative

- Contributors must manually clone upstream
- Converted templates may lag behind upstream
- Need to document update workflow

## Workflow

1. Clone upstream: `git clone https://github.com/posquit0/Awesome-CV dev/upstream/awesome-cv`
2. Convert templates: `uv run python dev/scripts/convert.py` (future)
3. Validate: `uv run python dev/scripts/check_templates.py`
4. Commit only converted `.tex.j2` files
5. Update `UPSTREAM_VERSION` with commit SHA

## References

- [Awesome-CV Repository](https://github.com/posquit0/Awesome-CV)
- [Python Packaging Guide](https://packaging.python.org/)
