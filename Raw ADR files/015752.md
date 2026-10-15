---
status: "accepted"
date: 2025-06-14
---

# 0012 – Docker Layer Caching Strategy in CI

## Context and Problem Statement
ADR‑0005 and ADR‑0011 prescribe building the **devcontainer image on‑demand**
in every GitHub Actions run.  Without caching this would reinstall Debian
packages and Rust/Cargo dependencies on every push, adding ~2‑3 minutes per
job.

GitHub Actions supports several caching back‑ends (Docker BuildKit’s
`type=gha`, `actions/cache`, or self‑hosted registry).  We must choose which to
adopt to maximise speed while keeping the workflow portable and free.

## Decision Drivers
* **Build speed** – minimise incremental CI time.
* **No external services** – avoid maintaining a private registry.
* **Cost‑free on public repositories** – leverage free GitHub runner minutes.
* **Simplicity** – readable YAML; avoid Docker login secrets.

## Considered Options
* **(A) BuildKit inline cache + `actions/cache@v3`** *(chosen)*
* (B) Push image to GitHub Container Registry (GHCR) after build, pull on next run
* (C) Rely on GitHub’s opaque layer cache (docker/build‑push‑action default)
* (D) No caching at all

## Decision Outcome
Chosen option: **(A)**.  Workflow:

```yaml
- uses: actions/cache@v3
  with:
    path: /tmp/.buildx-cache
    key: ${{ runner.os }}-buildx-${{ github.sha }}
    restore-keys: ${{ runner.os }}-buildx-

- docker build \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --cache-from=type=local,src=/tmp/.buildx-cache \
    --cache-to=type=local,dest=/tmp/.buildx-cache-new \
    -t rompatch-ci -f .devcontainer/Dockerfile.dev .
```

### Consequences
* **Positive:** Incremental builds reuse `apt` and `cargo` layers; typical CI
  runtime drops from ~3 min to <1 min.
* **Positive:** No need for docker login / pushing images.
* **Negative:** Cache directory counts toward GitHub’s cache quota (5 GB per
  repository).  Mitigated by small image size and automatic pruning.

### Confirmation
* CI job prints BuildKit cache hits; reviewers monitor runtime changes.
* Cache key prefixes ensure cache is re‑used across branches and PRs.

## Pros and Cons of the Options
### (A) BuildKit + actions/cache (chosen)
* **Good:** No registry setup; entirely free.
* **Good:** Works for forks (cache is read‑only).
* **Bad:** Cache missing on first build; still ~1.5 min cold start.

### (B) GHCR push/pull
* **Good:** Fastest after initial publish.
* **Bad:** Requires registry‑login secrets; forks cannot push.

### (C) build‑push‑action default cache
* **Good:** Minimal YAML.
* **Bad:** Cache is runner‑local; cold cache every workflow.

### (D) No cache
* **Good:** Simplicity.
* **Bad:** Long CI runtimes; wasted minutes.

## More Information
If GitHub cache quota is exceeded collaborators can manually clear
`rompatch-ci` cache keys in the repository Actions tab; future ADR may cover
migrating to GHCR if image size or build complexity grows.
