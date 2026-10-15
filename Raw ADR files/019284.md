# ADR 0001: Contract discipline via `spec.lock` + deterministic spec bundles

## Status

Accepted

## Context

This system is spec-first and split across multiple repositories:

- Contract/spec in `trip-planner-spec`
- Service implementation in `trip-planner-api`
- Consumers in `trip-planner-cli` and `website-edge`

In a multi-repo spec-first system, the most common failure mode is **contract drift**:

- consumers generating code against different spec versions
- builds pulling spec from moving targets (e.g., `main`)
- releases shipping without clear evidence of contract compliance

We need a boring, repeatable approach suitable for a **solo developer** and **GitHub Actions**.

## Decision

We will enforce cross-repo contract discipline by:

- Requiring every consumer repo to pin a specific spec ref in **`spec.lock`**
- Publishing and consuming **deterministic spec bundles** (with manifests + hashes)
- Failing CI when:
  - the pinned ref is invalid
  - the fetched bundle does not match expected hashes
  - generated code is not reproducible from the pinned bundle

The operational “living standard” for this decision is:

- [`planning/contract-policy.md`](../planning/contract-policy.md)

## Consequences

- **Pros**
  - Deterministic builds and codegen across repos
  - Drift detection is explicit and CI-enforced
  - Adoption of a new spec version becomes a clear, reviewable change
- **Cons**
  - Slightly more CI complexity (fetch + verify + regenerate checks)
  - Developers must follow the adoption workflow when bumping the spec pin

## Alternatives considered

- **Consumers pull spec from `main`**
  - Rejected: non-reproducible, encourages drift, breaks release auditability.
- **Monorepo or enforced single version across all repos**
  - Rejected: does not fit the current multi-repo structure and increases coordination overhead.
- **Runtime negotiation / versioned endpoints**
  - Rejected for v1: adds complexity without solving build-time drift.

## Notes

This ADR is about the **discipline model**. The spec bundle format and publishing mechanism are defined in ADR 0002 and the living standard [`planning/spec-bundle-standard.md`](../planning/spec-bundle-standard.md).

