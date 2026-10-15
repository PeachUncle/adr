---
status: "proposed"  
date: 2025-06-14
---

# 0015 – Future Rust CLI (`romdev`) Exploration

## Context and Problem Statement
Current automation relies on **Bash scripts + Justfile** (see ADR‑0004).  While
simple, Bash becomes brittle as logic grows (argument parsing, coloured output,
sub‑commands, Windows portability).  A compiled Rust CLI could unify tasks,
improve UX, and enable richer features (e.g. BPS parsing, diff visualisation)
without external runtimes.

## Decision Drivers
* **Maintainability** – typed codebase, testable units, dependency management.
* **Cross‑platform binaries** – native Windows support without WSL.
* **Extensibility** – sub‑command framework (build / patch / snapshot / release).
* **Performance** – faster hashing, multi‑threading for future features.

## Considered Options
* **(A) Incrementally develop a Rust CLI (`romdev`) and phase‑in** *(recommended)*
* (B) Rewrite everything in Rust immediately & drop Bash
* (C) Stay 100 % Bash indefinitely
* (D) Use Python (or Node) CLI instead of Rust

## Decision Outcome (Proposed)
We **defer full adoption** of Rust for now but agree on the following path:

1. Start a separate workspace `romtools/` with a minimal `romdev` binary.
2. Implement non‑critical functionality first (e.g. JSON validation).
3. Keep Bash as the canonical path until Rust reaches feature parity.
4. Revisit via a successor ADR when ready to switch CI and Justfile to Rust.

### Consequences
* **Positive (future):** Single fast binary, improved Windows support.
* **Positive:** Strong typing reduces shell‑quote bugs.
* **Negative:** Additional toolchain (Rust) in Docker image; longer build.
* **Negative:** Two paths (Bash & Rust) during transition → duplication.

### Confirmation
* Proof‑of‑concept CLI lives behind a `--experimental` guard.
* A follow‑up ADR will move status to _accepted_ when Rust covers ≥80 % of existing Bash tasks.

## Pros and Cons of the Options
### (A) Incremental Rust (recommended)
* **Good:** Risk‑free migration path.
* **Bad:** Temporary duplication.

### (B) Full rewrite now
* **Good:** Clean slate.
* **Bad:** Large one‑off effort; delays template release.

### (C) Stay Bash only
* **Good:** No new dependencies.
* **Bad:** Scaling issues, Windows friction.

### (D) Python CLI
* **Good:** Easy scripting, many libraries.
* **Bad:** Heavy runtime; packaging pain on Windows.

## More Information
If adopted, the Rust binary will be cached via Docker BuildKit and optionally released on GitHub as a statically linked artefact.
