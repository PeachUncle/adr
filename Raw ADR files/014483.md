# ADR-003: Extension Manifest Schema and Conflict Resolution

**Status:** Accepted  
**Date:** 2026-01-04  
**Deciders:** Product Owner, Architect, Developer, QA, Security

---

## Context

Praxis core cannot scale to support infinite domain/subtype variations. As the ecosystem grows, we need a stable contract for extensions to contribute templates, opinions, and audit checks without requiring core code changes.

This ADR documents the manifest schema (v0.1) and conflict resolution policy for the Plugin/Contribution API, focusing on Story 1 (opinions integration).

---

## Decision

### 1. Manifest Schema v0.1

Extensions declare their contributions via `praxis-extension.yaml`:

```yaml
manifest_version: "0.1"  # REQUIRED: Schema version (MAJOR.MINOR)
name: extension-name      # REQUIRED: Must match directory name
description: "..."        # OPTIONAL: Human-readable description

contributions:
  opinions: []            # List of OpinionContribution objects
  # templates: []         # Story 2 (deferred)
  # audits: []            # Story 3 (deferred)
```

**OpinionContribution Schema:**

```yaml
- source: opinions/code/subtypes/mobile.md  # Path in extension dir
  target: code/subtypes/mobile.md           # Path in opinions tree
```

### 2. Discovery Model

- Extensions are discovered via `workspace-config.yaml` installed_extensions list
- Each installed extension is scanned for `praxis-extension.yaml`
- Extensions without manifests are silently skipped (backward compatibility)
- Invalid manifests generate warnings but don't block other extensions

### 3. Conflict Resolution Policy

**Precedence:** Core > Alphabetical extension order (Z > A)

| Scenario | Resolution | Logging |
|----------|-----------|---------|
| Core + Extension contribute same file | Core wins | Warning: Extension attempted override |
| Extension A + Extension B contribute same file | Alphabetically later wins (B > A) | Warning: B overrides A |
| No conflict | File is added | None |

**Rationale:**
- **Core precedence** ensures Praxis maintainers control canonical guidance
- **Alphabetical order** provides deterministic resolution without configuration
- **Later wins** allows users to install "override packs" with Z-prefixed names

### 4. Provenance Tracking

Every opinion file tracks its source:

```python
class OpinionFile:
    source: str  # 'core' or extension name
```

Provenance is displayed in:
- `praxis opinions --list` output: `code/principles.md [mobile-pack]`
- OpinionsTree metadata for debugging
- Conflict warnings to help users understand resolution

### 5. Versioning Strategy

- Manifest version uses semver MAJOR.MINOR (no PATCH)
- v0.x = experimental, subject to breaking changes
- v1.0 = stable, requires 2 first-party packs using API before release
- Praxis supports N and N-1 manifest versions simultaneously
- Deprecation warnings before removing version support

### 6. Error Handling

| Error Type | Behavior | User Experience |
|------------|----------|-----------------|
| Missing manifest | Skip extension | Silent (backward compat) |
| Invalid YAML | Skip extension | Warning with extension name |
| Unsupported version | Skip extension | Warning with version and extension |
| Missing required field | Skip extension | Warning with field and extension |
| Name mismatch | Skip extension | Warning with expected vs actual |
| Missing contribution file | Load but mark as error | Parse error in opinion file |

All errors are non-blocking - Praxis continues loading other extensions.

---

## Consequences

### Positive

1. **Extensibility:** Third parties can contribute domain guidance without PRs to core
2. **Determinism:** Same inputs always produce same outputs (no randomness)
3. **Provenance:** Users can see where opinions come from
4. **Safety:** Core can override any extension contribution
5. **Simplicity:** File-based contributions only (no code execution in v0)

### Negative

1. **Alphabetical quirk:** Users must understand that "zzz-pack" beats "aaa-pack"
2. **Limited v0.x:** Cannot change manifest schema without breaking extensions
3. **No dependency resolution:** Extensions can't declare dependencies on each other

### Mitigations

1. **Documentation:** Clear explanation of conflict resolution in authoring guide
2. **Versioning:** v0.x experimental period allows iteration before v1.0 lock-in
3. **Future work:** Dependency resolution can be added in v1.x if needed

---

## Alternatives Considered

### A1: Configuration-based priority

**Rejected:** Adds complexity for limited benefit. Users would need to configure extension order in `workspace-config.yaml`. Alphabetical is simpler and deterministic.

### A2: First-wins conflict resolution

**Rejected:** Makes extension install order matter, which is non-deterministic and error-prone. Alphabetical is predictable.

### A3: Prompt user on conflicts

**Rejected:** Breaks automation and CLI workflows. Non-interactive resolution is required.

### A4: Allow glob patterns in contributions

**Rejected for v0.1:** Adds complexity to validation. Explicit paths are simpler. Can reconsider for v1.0 based on user feedback.

---

## Implementation Notes

**Files Created:**
- `src/praxis/domain/workspace.py`: ExtensionManifest, OpinionContribution models
- `src/praxis/infrastructure/manifest_loader.py`: Manifest parsing and validation
- `src/praxis/infrastructure/opinions_loader.py`: Extension opinion merging
- `src/praxis/application/opinions_service.py`: Discovery and integration

**Test Coverage:**
- 6 BDD scenarios in `tests/features/extension_opinions.feature`
- All scenarios passing
- Covers: valid manifests, invalid manifests, conflicts, provenance

**Reference Extension:**
- `praxis-extension-mobile-pack` demonstrates end-to-end flow
- Includes README, manifest, and mobile.md opinion

---

## Follow-up Work

- **Story 2:** Templates integration (same pattern, different contribution type)
- **Story 3:** Audits integration (same pattern, file-based audit checks)
- **v1.0:** Stabilize schema after 2 first-party packs validate API
- **Future:** Extension marketplace, dependency resolution (if needed)

---

## References

- [Opinions Contract](../core/governance/opinions-contract.md)
- Issue: Plugin/Contribution API - Manifest + Opinions (Story 1 of 3)
- Related: ADR-001 (Policy Engine), ADR-002 (Validation Model)
