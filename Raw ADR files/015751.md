---
status: "accepted"
date: 2025-06-14
---

# 0011 – CI Execution Model ( Devcontainer‑First, Docker‑Run `just all` )

## Context and Problem Statement
The repository must build, test and release patches automatically on GitHub
Actions.  Earlier ADR‑0005 locked us into a single `Dockerfile.dev` for parity.
We now define **how CI invokes the build**:

1. **Script‑heavy YAML:** apt‑install tools, run scripts directly on runner.
2. **Container build + `docker run just all`** (chosen).
3. Pre‑built GHCR image pulled, then run tasks.

## Decision Drivers
* **Parallels local dev flow** – developers run `just all`; CI should too.
* **Minimal duplication** – same Dockerfile supplies both devcontainer & CI.
* **Layer caching** – speed up consecutive builds.
* **Flexibility for matrix builds** – easy to swap toolchain/env via env vars.

## Considered Options
* **(A) Build devcontainer image & execute `just all` in `docker run`** *(chosen)*
* (B) Shell install steps in YAML (no Docker)
* (C) Pull pre‑built image from GHCR

## Decision Outcome
Chosen option: **(A)**.  Workflow steps:

```yaml
- docker build -t rompatch-ci -f .devcontainer/Dockerfile.dev .
- docker run --rm -u $(id -u):$(id -g) -v ${{ github.workspace }}:/work -w /work rompatch-ci just all
```

### Consequences
* **Positive:** Absolute parity with devcontainer; zero drift.
* **Positive:** Works on any self‑hosted runner with Docker.
* **Positive:** Docker‑layer cache keeps runtime reasonable (~1–2 min).
* **Negative:** First build incurs image build cost (~2–3 min) vs prebuilt pull.

### Confirmation
The `build.yml` workflow will fail if `just all` exits non‑zero.  Docker cache
performance is monitored in job summary.

## Pros and Cons of the Options
### (A) Build + `docker run just all` (chosen)
* **Good:** Single source of truth (`Dockerfile.dev`).
* **Good:** Easy to reproduce locally (`docker run … just all`).
* **Bad:** Cold‑start penalty on first build.

### (B) YAML installs only
* **Good:** Slightly faster hot path if packages cached by GitHub.
* **Bad:** Duplicates install logic; risk of drift.

### (C) Pull prebuilt image
* **Good:** Fastest CI once image is published.
* **Bad:** Extra release pipeline; external registry availability.

## More Information
If CI times rise, ADR‑0005 open door to adopt option (C) by publishing
`rompatch-dev` to GHCR and updating workflow to `docker pull` instead of build.
