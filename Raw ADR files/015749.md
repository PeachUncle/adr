---
status: "accepted"
date: 2025-06-14
---

# 0006 – Patch Format Choice ( **BPS** over IPS / UPS / xdelta )

## Context and Problem Statement
A binary patch format is required so that the template can distribute ROM
hacks legally ‑ the patch must contain no copyrighted data yet be easy for end
users to apply.  Candidate formats include:

* **BPS (Beat Patch System)** – modern, checksummed, supports moved data.
* **IPS (International Patching System)** – venerable 8‑bit era standard.
* **UPS (Universal Patching System)** – IPS successor, larger ROM support.
* **xdelta / BSDiff** – generic binary deltas, not ROM‑specific.

The format must be *widely supported* in the ROM‑hacking community and
supported by CLI tools usable in CI.

## Decision Drivers
* **Community expectation** – Romhacking.net upload guidelines prefer BPS/IPS.
* **Input/output verification** – built‑in CRC/size checks.
* **Patch size efficiency** – handle pointer moves without bloating.
* **Cross‑platform patchers** – GUI (Flips) + CLI (flips), web (RomPatcher.js).

## Considered Options
* **BPS (via *flips*)** *(chosen)*
* IPS (via flips)
* UPS (via flips)
* xdelta3

## Decision Outcome
**Chosen option: BPS**, because it is the only option satisfying *all* drivers:
checksums, efficient moved‑data encoding, and ubiquitous support in modern
patchers.

### Consequences
* **Positive:** End‑users on any OS can apply patches with Flips or web tools.
* **Positive:** CI can verify correct base ROM via embedded CRC.
* **Positive:** Smaller patch files than IPS for pointer‑heavy ROMs.
* **Negative:** Legacy emulators that embed IPS autopatching will not auto‑load
  BPS (minor; standalone tools exist).

### Confirmation
* CI step generates `.bps` using `flips --create`.
* `validate-patch-json.sh` records SHA‑1 of the produced BPS.

## Pros and Cons of the Options
### BPS (chosen)
* **Good:** Checksums for both input and output.
* **Good:** Handles moved data efficiently.
* **Good:** Supported by Flips GUI/CLI and RomPatcher.js.
* **Neutral:** Slightly slower to create than IPS (<100 ms typical).
* **Bad:** Some very old patchers (e.g., Snes9x autopatch) only read IPS.

### IPS
* **Good:** Works everywhere since the 1990s.
* **Bad:** No integrity checks; fails silently on wrong ROM.
* **Bad:** 16 MB size limit; inefficient with pointer moves.

### UPS
* **Good:** Fixes IPS size limit.
* **Neutral:** Less ubiquitous than BPS.
* **Bad:** No built‑in input CRC; larger files than BPS.

### xdelta
* **Good:** Extremely generic; strongest compression.
* **Bad:** End‑users unfamiliar; few ROM front‑ends support it.
* **Bad:** Requires separate hash verification script.

## More Information
If a community emerges around another format (e.g., xdelta for CD‑based ROMs),
a new toolchain folder (e.g., `snes-xdelta`) can coexist with BPS.
