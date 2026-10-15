---
status: "accepted"
date: 2025-06-14
---

# 0013 – Release Assets Strategy ( Upload `.bps` + `.json` on Tag )

## Context and Problem Statement
The template should produce distributable artefacts that end‑users can easily
download.  GitHub Releases provide a first‑class channel for open‑source
projects, triggered by Git tags.  We must decide **which files to attach** and
**when**.

## Decision Drivers
* **One‑click download** – patch consumers should not clone or navigate CI.
* **Provenance** – tie artefacts to immutable Git tags.
* **Automation** – no manual upload steps.
* **Completeness** – include metadata for validation tools.

## Considered Options
* **(A) Upload `<patch>.bps` *and* `<patch>.bps.json` on every `v*.*.*` tag** *(chosen)*
* (B) Upload a ZIP containing patch + readme
* (C) CI artefacts only, no Release attachment
* (D) Manual release uploads

## Decision Outcome
Chosen option: **(A)**.  Workflow `build.yml` uses
`softprops/action-gh-release@v1` when `startsWith(github.ref,'refs/tags/')` is
true, attaching exactly two files per patch.

### Consequences
* **Positive:** Users download patch + metadata side‑by‑side; hash validation
  possible without extra steps.
* **Positive:** Release page auto‑generates changelog from tag message.
* **Negative:** Maintainers must tag with SemVer before merging to main.

### Confirmation
* CI job fails if Release upload returns non‑zero.
* Downloaded files’ SHA‑1 hashes are compared against those in `.json` as part
  of Release smoke test (future pipeline improvement).

## Pros and Cons of the Options
### (A) Attach `.bps` + `.json` (chosen)
* **Good:** Minimal user confusion; small payloads.
* **Good:** Preserves metadata integrity.
* **Bad:** Two files instead of one bundle.

### (B) ZIP bundle
* **Good:** Single download.
* **Bad:** Users must unzip; CLI patchers cannot stream.

### (C) CI artefacts only
* **Good:** Zero release management.
* **Bad:** Artefacts expire after 90 days; link stability poor.

### (D) Manual upload
* **Good:** Flexible.
* **Bad:** Error‑prone; time‑consuming.

## More Information
If multiple patches are built per tag we may adopt a Release asset naming
convention or a ZIP bundle; captured in follow‑up ADR when needed.
