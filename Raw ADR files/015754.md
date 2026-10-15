---
status: "accepted"
date: 2025-06-14
---

# 0014 – Strategy for Supporting Additional Toolchains

## Context and Problem Statement
ADR‑0003 defined the folder‑with‑hooks pattern for a **single** toolchain.  The
project goal is to be *console‑agnostic*, so we must state how future
platforms (SNES, GBA, etc.) will be integrated without disrupting existing
workflows.

## Decision Drivers
* **Isolation** – Genesis logic must not bleed into SNES logic.
* **Zero‑touch core** – adding a toolchain should not modify global scripts.
* **Discoverability** – contributors can list available toolchains easily.
* **Consistent UX** – `TOOLCHAIN=<name> just build` works for all.

## Considered Options
* **(A) One folder per toolchain under `toolchains/` following the hooks contract** *(chosen)*
* (B) Sub‑directories within a platform folder (e.g., `toolchains/snes/bps`) 
* (C) Plugin registry discovered via naming convention (`toolchain-<name>.sh`)  
* (D) Separate branches or repos per console

## Decision Outcome
**Chosen option: (A) Top‑level folder per toolchain**.  Examples:
```
toolchains/
  genesis-bps/
  genesis-disasm/
  snes-bps/
  gba-arm-elf/
```
Each folder must provide at minimum an executable **`build.sh`**; optional
`pre.sh` and `post.sh` are honoured automatically by `scripts/build-and-patch.sh`.

### Consequences
* **Positive:** Adding a new console is a single PR touching only its folder
  and `.env` default recommendation.
* **Positive:** Core scripts stay untouched → low regression risk.
* **Neutral:** `toolchains/` will grow; addressed by naming convention (see ADR‑0016).
* **Negative:** No dynamic capability introspection yet (future Rust CLI can
  provide `romdev toolchains list`).

### Confirmation
* CI matrix builds can iterate over a list of toolchains when more than one is
  present.
* Lint script ensures every folder contains `build.sh` + executable bit.

## Pros and Cons of the Options
### (A) Folder per toolchain (chosen)
* **Good:** Completely decoupled; trivial to traverse.
* **Bad:** Flat namespace could collide; mitigated by prefixing with platform.

### (B) Platform sub‑dirs
* **Good:** Grouped by console.
* **Bad:** Deeper paths; core script needs two‑level lookup.

### (C) Naming‑convention plugins
* **Good:** No folder clutter.
* **Bad:** Harder for new contributors to discover.

### (D) Separate repos/branches
* **Good:** Absolute isolation.
* **Bad:** Splinters community; harder cross‑patch sharing.

## More Information
A future ADR may introduce a **Toolchain Registry file** (`toolchains/index.yml`)
to provide human‑readable descriptions, maintainers, and required host packs.
