---
status: "accepted"
date: 2025-06-14
---

# 0003 – Toolchain Layout ( `toolchains/<name>/{pre.sh,build.sh,post.sh}` )

## Context and Problem Statement
Each supported console or build methodology requires its own set of commands
(e.g., compile a disassembly, apply a hex patch, compress assets).  We need a
structure that keeps these concerns isolated while allowing **one universal
entry‑point** (`just build`) and a shared CI pipeline.

Requirements:
* **Ease of extension** – adding SNES or GBA support should not touch core
  scripts.
* **Hooks** – optional pre/post steps for cleanup or verification.
* **Zero external deps** – pure POSIX shell, no Python/Rust mandatory.
* **Predictable discovery** – avoid guessing file names or config keys.

## Decision Drivers
* Simplicity for contributors who may only know shell.
* Parity between local dev and CI (no hidden magic).
* Clear, conventional file names for grep/search.
* Allow incremental migration to more advanced tooling in the future.

## Considered Options
* **(A) Folder‑per‑toolchain with `pre.sh`,`build.sh`,`post.sh`** *(chosen)*
* **(B) Single monolithic `build.sh` with `case $TOOLCHAIN` blocks**
* **(C) `just` recipe per toolchain (`just build:genesis`)**
* **(D) Python/Rust plugin discovery via entry‑points**

## Decision Outcome
Chosen option: **(A) Folder‑per‑toolchain with lifecycle hooks**, because it
maximises separation of concerns while staying entirely in Bash.  A new
console requires creating one folder and three clearly‑named scripts (only
`build.sh` is mandatory).

### Consequences
* **Positive:** Adding or refactoring a toolchain never touches global logic.
* **Positive:** Hooks allow reusable cleanup/validation patterns.
* **Positive:** Works identically on Linux/macOS/WSL and inside Docker.
* **Negative:** Slightly more files to manage vs. one mega‑script.
* **Negative:** Cannot express advanced dependency graphs (mitigated by
  delegating to `make` or other tools *inside* `build.sh` if needed).

### Confirmation
* `scripts/build-and-patch.sh` fails fast if `toolchains/$TOOLCHAIN/build.sh`
  is missing or not executable.
* CI runs at least one reference toolchain (`genesis-bps`) on every commit.

## Pros and Cons of the Options
### (A) Folder + Hooks (chosen)
* **Good:** Clear, grepable, and incremental.
* **Good:** Pre/post hooks optional but powerful.
* **Neutral:** Small file sprawl.
* **Bad:** No dynamic discovery of capabilities (future work).

### (B) Monolithic switch‑case script
* **Good:** Single file.
* **Bad:** Grows unmaintainable; merge conflicts; hard to test.

### (C) `just` namespacing
* **Good:** Very little Bash needed.
* **Bad:** CI must know which recipe to call; unclear discoverability.

### (D) Python/Rust plugins
* **Good:** Type safety, complex graphs possible.
* **Bad:** Requires full runtime + packaging; over‑kill for small shell tasks.

## More Information
Should a toolchain outgrow Bash, `build.sh` can delegate to any language or
binary (`cargo run`, `make`, etc.) while preserving the external contract.
