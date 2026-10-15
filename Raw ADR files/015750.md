---
status: "accepted"
date: 2025-06-14
---

# 0010 – Metadata Validation (`validate-patch-json.sh`)

## Context and Problem Statement
ADR‑0007 defined a per‑patch **`<patch>.bps.json`** file containing SHA‑1 hashes
of the input ROM, output ROM, and the patch itself.  To keep repository
integrity high we must decide whether these recorded hashes are merely
informational or **actively enforced by CI and local workflows**.

## Decision Drivers
* **Integrity assurance** – detect accidental manual edits to either the JSON
  or the binary files.
* **Supply‑chain trust** – downstream consumers can rely on metadata.
* **Low overhead** – avoid heavyweight cryptographic tools.
* **Fast feedback** – fail in developer workflow *before* CI when possible.

## Considered Options
* **(A) Validate hashes on every `just check` and in CI** *(chosen)*
* (B) Validate only in CI, not locally
* (C) Provide validation script but do not call it automatically
* (D) Skip validation; assume developer discipline

## Decision Outcome
Chosen option: **(A) Always validate**.  The script
`scripts/validate-patch-json.sh` is invoked in `just check` and the GitHub
Actions workflow.  Any mismatch between recorded and actual SHA‑1 values
aborts the build.

### Consequences
* **Positive:** Corrupted or mismatched artefacts are caught instantly.
* **Positive:** Prevents scenario where developer commits edited JSON without
  regenerating the patch.
* **Negative:** Adds ~20 ms of SHA‑1 computation per build (negligible).

### Confirmation
* CI step fails if `validate-patch-json.sh` exits non‑zero.
* Local `just check` must pass before PR merge.

## Pros and Cons of the Options
### (A) Always validate (chosen)
* **Good:** Highest confidence in artefact integrity.
* **Neutral:** Small time overhead.
* **Bad:** Requires `jq` and `sha1sum` in runtime env (already present).

### (B) CI‑only validation
* **Good:** No local dependency on `jq`.
* **Bad:** Developers discover issues only after push.

### (C) Manual validation
* **Good:** Flexible.
* **Bad:** Relies on human diligence; easy to skip.

### (D) No validation
* **Good:** Simplest.
* **Bad:** Undetected drift; undermines trust.

## More Information
Future ADRs may upgrade SHA‑1 to SHA‑256 or add JSON Schema validation.  The
chosen script layout makes such changes trivial.
