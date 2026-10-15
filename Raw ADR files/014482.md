# ADR-002: Validation Model

**Status:** Accepted
**Date:** 2025-12-21 (Draft), 2025-12-28 (Accepted)
**Deciders:** @jayers99
**Relates to:** ADR-001 (Policy Engine Selection), Issue #4 (template-python-cli)

---

## Context

Before selecting a policy engine (ADR-001), we must define what the engine validates. This ADR establishes the validation model that any policy engine must support.

**Validation approach:** The model was discovered by working through Issue #4 (template-python-cli) and the uat-praxis-code project. The positions below are now validated through real-world usage.

---

## Decisions

### 1. Configuration Scope

**Decision: One `praxis.yaml` per project, at repository root.**

Rationale:

- Matches common conventions (package.json, pyproject.toml, Cargo.toml)
- Single source of truth for project governance
- Simplifies tooling (always look in one place)

```yaml
# praxis.yaml (project root)
domain: code
stage: formalize
privacy_level: personal
environment: Home
```

**Alternative rejected:** Per-directory configs. Adds complexity without clear benefit for solo/small-team use.

---

### 2. Validation Depth

**Decision: Config validation + filesystem checks for required artifacts.**

The validator:

1. Validates `praxis.yaml` schema and field values (via Pydantic)
2. Checks that required artifacts exist (by path convention)
3. Does NOT deeply inspect artifact contents

Example behavior:

- `stage: execute` + `domain: code` → validator checks `docs/sod.md` exists
- Validator does NOT parse SOD to verify it has all required sections

Rationale:

- Catches the most common failure mode (missing formalization)
- Avoids complexity of content parsing
- Content quality is author responsibility, not policy engine scope

**Artifact path conventions:**

| Domain | Formalize Artifact | Expected Path |
| --- | --- | --- |
| Code | SOD | `docs/sod.md` |
| Create | Creative Brief | `docs/brief.md` |
| Write | Writing Brief | `docs/brief.md` |
| Learn | Learning Plan | `docs/plan.md` |
| Observe | (none) | — |

---

### 3. Stage Tracking

**Decision: Explicit declaration in `praxis.yaml`, updated manually by author.**

The `stage` field is the single source of truth. The author updates it when transitioning stages.

Rationale:

- Simple and transparent
- No hidden state or event logs
- Git history provides audit trail naturally
- Aligns with "author is accountable" philosophy

**Validated learning:** Manual stage tracking feels natural. The cognitive overhead is minimal—updating one field when transitioning is not burdensome.

**Rejected alternatives:**

- Inferred from artifacts: Too magical, hard to debug
- Event-based transitions: Over-engineered for solo use

---

### 4. Regression Enforcement

**Decision: Advisory warnings, not blocking errors.**

Invalid regressions (per lifecycle.md table) produce warnings, not failures.

Rationale:

- Real work is messy; hard blocks cause friction
- Author should be informed, not prevented
- Trust the author to make intentional decisions
- Can tighten to errors later if abuse patterns emerge

Example output:

```text
⚠ Warning: Regression from Execute → Explore is not in allowed regression table.
  Allowed targets from Execute: Commit, Formalize
  Proceeding anyway (author override).
```

---

### 5. Transition History

**Decision: No explicit history tracking. Git is the audit log.**

The validator only sees current state. Historical transitions are visible via `git log` on `praxis.yaml`.

Rationale:

- Avoids duplicate state management
- Git already tracks changes with timestamps and authors
- Keeps the model simple

**Implementation note:** `praxis status` displays stage history extracted from git log.

---

### 6. Multi-Domain Projects

**Decision: Single primary domain per project. Secondary domains via subdirectories (future scope).**

For v1, each project has exactly one domain declared in `praxis.yaml`.

Rationale:

- Keeps resolution model simple: domain + stage + privacy → behavior
- Most real projects have a primary domain
- Multi-domain (e.g., Code + Write in one repo) is future scope

---

### 7. Privacy Composition

**Decision: Single privacy level per project. Highest sensitivity wins.**

If a project contains artifacts of varying sensitivity, declare the highest level.

Rationale:

- Simple mental model
- Conservative default (protects sensitive material)
- Per-artifact privacy is future scope if needed

---

## Resolved Open Questions

### Q: Does manual stage tracking feel natural or burdensome?

**A: Natural.** Updating one field when transitioning stages is minimal overhead. The explicit declaration makes project state immediately visible.

### Q: Is `docs/sod.md` the right convention, or should artifact paths be configurable?

**A: Convention is correct.** Simple, predictable, no configuration needed. Configurability would add complexity without demonstrated need.

### Q: What's the minimum useful validation that provides value without ceremony?

**A: Schema + artifact existence + regression warnings.** The current implementation validates:
1. praxis.yaml schema (errors)
2. Required artifact exists (errors)
3. Invalid stage regression (warnings)
4. Privacy downgrade (warnings)

This catches real mistakes without being overly restrictive.

### Q: Should `praxis validate` be run manually, or integrated into git hooks?

**A: Manual by default, CI-friendly flags available.**

The `--check-tests`, `--check-lint`, `--check-types`, and `--check-all` flags enable CI integration. Let users choose their workflow.

---

## Example `praxis.yaml`

```yaml
# Minimal valid config
domain: code
stage: formalize
privacy_level: personal

# Optional
environment: Home
```

---

## Validation Rules Summary

| Rule | Severity | Trigger |
| --- | --- | --- |
| Unknown domain | Error | `domain` not in allowed list |
| Unknown stage | Error | `stage` not in allowed list |
| Unknown privacy level | Error | `privacy_level` not in allowed list |
| Missing formalize artifact | Error | `stage` ≥ commit AND artifact not found |
| Invalid stage regression | Warning | Transition not in allowed table |
| Privacy downgrade | Warning | `privacy_level` decreased from prior commit |

---

## Consequences

### Enables

- Simple CLI: `praxis validate` checks config + artifact existence
- Clear error messages for common failures
- Git-native workflow (no external state)
- CI integration via `--check-*` flags

### Limits

- No content inspection (SOD could be empty and pass)
- No multi-domain support in v1
- No per-artifact privacy in v1

### Deferred

- Deep artifact validation
- Multi-domain projects
- Per-artifact privacy levels
- Stricter regression enforcement

---

## Related

- ADR-001 (Policy Engine Selection) — Pydantic chosen over CUE
- Issue #4 (template-python-cli) — First worked project
- Issue #7 — This ADR finalization
