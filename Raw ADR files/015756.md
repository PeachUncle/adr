---
status: "accepted"
date: 2025-06-14
---

# 0016 – Toolchain Naming Convention (`<platform>-<method>`)

## Context and Problem Statement
With ADR‑0003 and ADR‑0014 we established a folder‑per‑toolchain strategy.  As
the number of consoles and techniques grows, **predictable naming** becomes
critical for:

* Human discoverability (`ls toolchains/` should be self‑explanatory).
* Avoiding name collisions.
* CI matrix patterns (e.g. `grep -l "^gba-"`).

## Decision Drivers
* **Clarity** – contributors instantly know what `snes-bps` does.
* **Alphabetical grouping** – all Genesis toolchains cluster together.
* **Extensibility** – new methods (e.g. `disasm`, `elf`) append naturally.
* **Script simplicity** – dispatcher only parses first “-” for platform.

## Considered Options
* **(A) `<platform>-<method>`** *(chosen — e.g. `genesis-bps`, `snes-disasm`)*
* (B) `<method>-<platform>` (`bps-genesis`)
* (C) Game‑specific names (`sonic3`, `smw`)
* (D) Numeric IDs (`01-genesis`, `02-snes`)

## Decision Outcome
Chosen pattern: **`<platform>-<method>`**, lowercase, words separated by a single hyphen.  Examples:
```
# Cartridge patching
  genesis-bps/
  snes-bps/
# Source‑compile workflows
  genesis-disasm/
  gba-arm-elf/
```
If a platform has only one obvious method, “method” may be omitted (`nes`), but
folders should still avoid collisions.

### Consequences
* **Positive:** Visual grouping in directory listings.
* **Positive:** Regex `^[a-z0-9]+-[a-z0-9]+$` validates names; linter can enforce.
* **Negative:** Folder rename required if a new method appears for same
  platform (`snes` → `snes-bps`).

### Confirmation
* Shell linter checks that every folder matches regex and contains `build.sh`.
* CI matrix can glob `*-bps` to run patch‑only toolchains.

## Pros and Cons of the Options
### (A) platform‑method (chosen)
* **Good:** Clear, scalable.
* **Bad:** Two words even when redundant.

### (B) method‑platform
* **Good:** Groups by technique.
* **Bad:** Less intuitive for newcomers (they search by console first).

### (C) Game‑specific names
* **Good:** Immediate for single‑game repo.
* **Bad:** Not reusable; violates generic template goal.

### (D) Numeric IDs
* **Good:** Sorting stable.
* **Bad:** Opaque; documentation mandatory.

## More Information
If sub‑methods arise (e.g. `snes-bps-kasm` vs `snes-bps-lz`), an extended
pattern `<platform>-<method>-<variant>` may be proposed in a future ADR.
