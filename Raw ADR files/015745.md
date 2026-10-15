---
status: "accepted"
date: 2025-06-14
---

# 0001 – Configuration Medium – `.env` Files vs `config.json`

## Context and Problem Statement
The template must expose project‑specific paths, metadata, and build commands so that
both **local developers** and **CI pipelines** can read them easily.  Two obvious
candidates emerged:

* **`.env`** — flat key/value pairs, naturally consumed by Docker, `just`, and shell.
* **`config.json`** — hierarchical, descriptive, but requires a parser (`jq`, Python) in every script.

## Decision Drivers
* **Parity with Docker / devcontainers** (Docker respects `ENV`, `docker‑compose` supports `.env`).
* **Ease‑of‑use for shell scripts** — avoid mandatory JSON tooling.
* **CI simplicity** — GitHub Actions can load env directly (`env:` blocks).
* **Human readability / quick edits**.

## Considered Options
* Use flat **`.env`** for all variables (chosen).
* Use a hierarchical **`config.json`** parsed with `jq`.
* Hybrid: keep `.env` for paths, `config.json` only for patch metadata.

## Decision Outcome
**Chosen option: `.env`**, because it satisfies every driver with the least
complexity.  Docker and GitHub Actions consume it natively, and our Bash
scripts can `export $(grep … .env)` without additional tooling.

### Consequences
* **Good:** Zero external dependencies; developers can override variables ad‑hoc.
* **Good:** Works identically on Linux, macOS, WSL.
* **Bad:** Limited to flat key/value pairs; deeply nested config (if ever
  required) will need naming conventions (`PATCH_OUTPUT_SHA1`).

### Confirmation
Reviewed in pull‑request #1; CI expects `.env`; scripts fail fast if missing.

## Pros and Cons of the Options
### `.env`
* **Good:** Native to Docker and `just`.
* **Good:** No parsing library required.
* **Neutral:** Flat structure.
* **Bad:** Lacks comments (work‑around: prefix with `#`).

### `config.json`
* **Good:** Structured; can nest per‑toolchain details.
* **Neutral:** Needs `jq` (already present) but still extra typing.
* **Bad:** Harder to source in pure Bash; not consumed automatically by Docker.

## More Information
Migrating from `.env` to JSON later is low‑risk: generate JSON at build time.
