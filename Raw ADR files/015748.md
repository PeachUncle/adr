---
status: "accepted"
date: 2025-06-14
---

# 0005 – Container Strategy ( One Dev + CI Image, Devcontainer‑First )

## Context and Problem Statement
The template must guarantee **identical behaviour** on:
1. A contributor’s workstation (Linux, macOS, Windows/WSL)
2. GitHub Actions runners

A container image removes host‑toolchain drift, but we must choose **how many
images** and **where they live**.

## Decision Drivers
* **Environment parity** – “works on my machine” is equal to CI.
* **Low maintenance** – single source of truth for packages.
* **Fast inner loop** – devcontainer should not rebuild layers for every task.
* **Simple CI** – avoid duplicating `apt install …` inside workflow YAML.

## Considered Options
* **(A) Single `Dockerfile.dev` used by devcontainer *and* CI** *(chosen)*
* (B) Separate images: `Dockerfile.dev` for editors, `Dockerfile.ci` slimmed for CI
* (C) No container at all; rely on host + CI install scripts
* (D) Publish a pre‑built image in GHCR, pin CI to it

## Decision Outcome
Chosen option: **(A) One Dockerfile.dev**.  CI builds the image, caches layers
(`actions/cache@v3` with BuildKit), then runs `just all` in that container.
Devcontainer re‑uses the same Dockerfile guaranteeing parity.

### Consequences
* **Positive:** Zero duplication of install logic; Dockerfile is single source.
* **Positive:** Contributors can reproduce CI locally via `docker run -v $PWD …`.
* **Positive:** Image caching keeps CI time acceptable (~1‑2 min incremental).
* **Negative:** First‐time CI build cost (≈ 2–3 min) vs pulling a prebuilt image.
* **Negative:** Image includes dev‑only tools (e.g., bash‑completion) that CI
  doesn’t strictly need → slightly larger image size (acceptable  <300 MB).

### Confirmation
* Workflow `build.yml` builds with `--cache-from`/`--cache-to`; failing layer
  cache will surface as increased runtimes.
* Devcontainer launch in Codespaces succeeds (parity check).

## Pros and Cons of the Options
### (A) One Image (chosen)
* **Good:** Single point of change; no drift.
* **Neutral:** Bigger image than CI‑only build.
* **Bad:** Slight extra CI minutes on cold cache.

### (B) Separate dev vs CI images
* **Good:** CI can be ultra‑slim.
* **Bad:** Two Dockerfiles to maintain; risk of divergence.

### (C) No container
* **Good:** Fastest CI startup.
* **Bad:** Host drift; Windows/Mac tooling mismatch; onboarding friction.

### (D) Publish pre‑built image
* **Good:** Fast CI & Codespaces launch.
* **Bad:** Requires release & tagging discipline; external registry outages.

## More Information
If CI times become prohibitive we may add an ADR to push the built image to
GitHub Container Registry and pull on subsequent jobs (see option D).
