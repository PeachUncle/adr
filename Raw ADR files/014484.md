# ADR-004: Versioning and Naming Schemes

**Status:** Accepted  
**Date:** 2026-01-05  
**Deciders:** @jayers99  
**Relates to:** Issue #4 (template-python-cli), ADR-003 (Extension Manifest Schema)

---

## Context

As Praxis evolves from initial specification (v0.3) to a working ecosystem with templates, extensions, and CLI tooling, we need clarity on what gets versioned, how versions are expressed, and where version information lives. This spike explores versioning across multiple layers of the Praxis system.

### What Needs Versioning?

Multiple components exist at different abstraction levels:

1. **Praxis Framework/Specification** — The core conceptual model (lifecycle, domains, privacy)
2. **praxis.yaml Schema** — The project configuration format
3. **Extension Manifest Schema** — The extension API contract (already defined in ADR-003)
4. **Stage Templates** — Generated document templates (CAPTURE.md, SOD, etc.)
5. **Project Templates** — Scaffolding for new projects (e.g., template-python-cli)
6. **CLI Tool** — The `praxis` command-line interface
7. **Projects Using Praxis** — Individual user projects with deliverables

Each has different change frequencies, audiences, and backward compatibility concerns.

### Research Context

Similar template systems were analyzed:

| System | Template Versioning | Scheme | Location |
|--------|---------------------|--------|----------|
| Cookiecutter | Git tags | SemVer | Git tags, cookiecutter.json |
| Copier | Git tags + manifest | SemVer | copier.yml `_version`, git tags |
| Yeoman | npm packages | SemVer | package.json |
| Cargo Generate | Git tags | SemVer | Git tags, Cargo.toml (post-gen) |

**Key patterns observed:**
- Template versioning and project versioning are separate concerns
- Git tags are dominant for template versions
- SemVer is the de facto standard
- Manifest files track metadata (not just versions)
- Update mechanisms vary (most are "generate once")

---

## Decisions

### 1. Praxis Framework/Specification Versioning

**Decision:** Use SemVer (v0.x during validation, v1.0 when stable).

**Version location:** `core/spec/VERSION.md` (centralized) + individual spec headers

**Current state:** v0.3 (noted in sod.md, lifecycle.md)

**Rationale:**
- Spec is the conceptual foundation; clarity on its stability is critical
- v0.x signals "under validation, subject to change"
- v1.0 signals "validated through real projects, stable for wide use"
- MAJOR = breaking changes to lifecycle/domains/privacy model
- MINOR = refinements, clarifications, new features
- PATCH not used at spec level (reserved for tooling)

**Example progression:**
- v0.3 → v0.4: Add new domain or refine stage definitions
- v0.9 → v1.0: Spec validated, committed to stability
- v1.0 → v2.0: Breaking change to lifecycle or privacy model

---

### 2. praxis.yaml Schema Versioning

**Decision:** Add optional `schema_version` field to praxis.yaml.

**Default behavior:** If missing, assume latest schema (backward compatibility).

**Future state:**
```yaml
# praxis.yaml
schema_version: "1.0"  # Optional, defaults to latest
domain: code
stage: execute
privacy_level: personal
environment: Home
```

**Rationale:**
- Enables migration tooling when schema changes
- Allows deprecation warnings without breaking old projects
- Follows extension manifest pattern (ADR-003)
- Optional field maintains backward compatibility

**Implementation plan:**
1. Add `schema_version` as optional field in `PraxisConfig` model (default: None)
2. `praxis validate` warns if schema_version missing or outdated
3. `praxis migrate --to-schema X.Y` provides automated migration (future)
4. Core supports N and N-1 schema versions simultaneously

**Schema versioning rules:**
- MAJOR.MINOR format (no PATCH)
- MAJOR = breaking changes (required field changes, type changes)
- MINOR = new optional fields, deprecations
- Version 1.0 = current implicit schema (first explicit version)

---

### 3. Extension Manifest Schema Versioning

**Decision:** Continue ADR-003 approach (manifest_version: "MAJOR.MINOR").

**No changes needed.** ADR-003 already defines:
- v0.x = experimental, subject to change
- v1.0 = stable after 2 first-party packs validate API
- Praxis supports N and N-1 manifest versions
- Deprecation warnings before removing support

---

### 4. Stage Template Versioning

**Decision:** No separate versioning. Stage templates evolve with Praxis spec.

**Rationale:**
- Stage templates are generated from `core/spec/` and `src/praxis/templates/`
- Template changes only affect new generations (existing docs unaffected)
- Git history provides version tracking for template evolution
- Coupling to Praxis version is appropriate (templates implement spec)

**Implication:** When Praxis spec bumps version, stage templates implicitly version with it.

---

### 5. Project Template Versioning (e.g., template-python-cli)

**Decision:** Use SemVer + Git tags.

**Version location:**
- **Primary:** Git tags (v1.0.0, v1.1.0, etc.)
- **Optional:** Template metadata file (`.praxis-template.yaml`)

**Template metadata schema (future):**
```yaml
# .praxis-template.yaml
template_name: "praxis-template-code-cli"
template_version: "1.2.0"
praxis_min_version: "0.3"
domain: code
subtype: cli
description: "Python CLI project with Poetry, Typer, pytest"
```

**Rationale:**
- Git tags are standard practice (cookiecutter, copier, cargo-generate)
- Enables rollback to specific template versions
- Metadata file enables introspection and validation
- Generated projects can record source template version (provenance)

**Template naming convention:** See Decision #7 below.

**Update strategy:**
- **Phase 1 (current):** Generate once, projects are independent
- **Phase 2 (future):** Template update mechanism (like Copier)
  - `praxis template update` checks for new versions
  - Applies template changes while preserving project customizations

---

### 6. CLI Tool Versioning

**Decision:** Use SemVer in pyproject.toml (standard Python packaging).

**Current state:** `version = "0.1.0"` in pyproject.toml

**Versioning rules:**
- MAJOR = breaking CLI changes (removed commands, incompatible flags)
- MINOR = new features (new commands, new flags)
- PATCH = bug fixes, docs, non-breaking improvements

**Version independence:**
- CLI version can diverge from Praxis spec version
- Example: Praxis spec v0.3, CLI tool v0.1.0
- Rationale: Spec = conceptual model stability, CLI = implementation maturity

**Version check:** `praxis --version` outputs CLI tool version.

---

### 7. Naming Schemes

#### Template Naming

**Pattern:** `praxis-template-{domain}-{type}`

**Examples:**
- `praxis-template-code-cli` — Python CLI project
- `praxis-template-code-library` — Python library
- `praxis-template-code-api` — REST API service
- `praxis-template-write-article` — Technical article
- `praxis-template-learn-course` — Learning curriculum
- `praxis-template-create-design` — Design exploration

**Rationale:**
- `praxis-template-` prefix clearly identifies Praxis templates
- `{domain}` maps to Praxis domains (code, create, write, learn, observe)
- `{type}` provides specificity within domain
- Consistent with extension naming (`praxis-extension-{name}`)
- Searchable, predictable, scoped

**Repository naming:** Template repos follow this pattern exactly.

#### Extension Naming

**Pattern:** `praxis-extension-{name}` (already established)

**Examples:**
- `praxis-extension-mobile-pack`
- `praxis-extension-devops-opinions`
- `praxis-extension-security-audit`

**Rationale:** Already defined in ADR-003, consistent with template pattern.

#### Stage File Naming

**Pattern:** `{STAGE}.md` (existing, no change)

**Examples:** CAPTURE.md, SENSE.md, FORMALIZE.md, EXECUTE.md

**Rationale:**
- Stage files are living documents in user projects
- Git history provides versioning
- No need for version suffixes (`formalize-v1.md` is anti-pattern)

#### Branch Naming

**No change:** Already defined in CLAUDE.md global rules (outside spike scope).

---

### 8. Projects Using Praxis

**Decision:** Project versioning is domain-specific and user-controlled.

**Examples:**
- **Code domain (Python):** `version = "1.0.0"` in pyproject.toml
- **Code domain (Node):** `"version": "1.0.0"` in package.json
- **Write domain:** Version in frontmatter or N/A
- **Create domain:** Version in metadata or N/A

**Rationale:**
- Praxis governs lifecycle and privacy, not deliverable versioning
- Projects follow ecosystem conventions (npm, cargo, poetry, etc.)
- Overriding domain standards would add friction without value

---

## Backward Compatibility Strategy

### praxis.yaml Schema Evolution

**Challenge:** Old projects may have old schema.

**Solution:**
1. `schema_version` field is optional (defaults to latest)
2. `praxis validate` warns if schema outdated
3. `praxis migrate --to-schema X.Y` provides automated migration (future)
4. Core supports N and N-1 schema versions simultaneously

**Example migration:**
```bash
$ praxis validate
⚠ Warning: praxis.yaml uses schema 1.0 (current is 2.0)
  Run 'praxis migrate --to-schema 2.0' to upgrade

$ praxis migrate --to-schema 2.0
✓ Migrated praxis.yaml to schema 2.0
  Changes: Added required field 'execution_model'
```

### Extension Manifest Evolution

**Already addressed in ADR-003:**
- N and N-1 version support
- Deprecation warnings
- Graceful degradation

### Template Evolution

**Phase 1 (current):** Generate once, projects independent.

**Phase 2 (future):** Template update mechanism.
- Templates record version in generated projects
- `praxis template update` detects changes
- User resolves conflicts (like Copier)

### CLI Tool Versioning

**Standard SemVer practices:**
- Breaking changes = MAJOR bump
- Feature additions = MINOR bump
- Bug fixes = PATCH bump
- Clear upgrade guides in CHANGELOG.md

---

## Implementation Plan

### Immediate (this spike)

- [x] Research similar systems
- [x] Document versioning recommendations (this ADR)
- [x] Define naming conventions

### Short-term (Issue #4 completion)

- [ ] Add template naming to template-python-cli design
- [ ] Document template versioning in extension authoring guide
- [ ] Consider adding `schema_version` to PraxisConfig (optional, not required)

### Medium-term (post-Issue #4)

- [ ] Create `core/spec/VERSION.md` with Praxis spec version
- [ ] Add `schema_version` field to praxis.yaml schema (optional)
- [ ] Implement schema version warnings in `praxis validate`
- [ ] Create `.praxis-template.yaml` schema for template metadata

### Long-term (v1.0 readiness)

- [ ] Implement `praxis migrate` command for schema migrations
- [ ] Design template update mechanism (Copier-like)
- [ ] Stabilize Praxis spec to v1.0 (after multiple real projects)
- [ ] Stabilize extension manifest to v1.0 (after 2 first-party packs)

---

## Alternatives Considered

### A1: CalVer for Praxis spec

**Rejected:** SemVer is more appropriate.

- Breaking changes in the spec are meaningful events (MAJOR bump)
- CalVer implies time-based releases, but spec changes are event-driven
- SemVer is widely understood and communicates stability

### A2: Mandatory schema_version in praxis.yaml

**Rejected:** Too strict for v0.x phase.

- Would break all existing projects immediately
- Optional field provides migration path without friction
- Can reconsider if migration problems emerge

### A3: Stage-based versioning (e.g., formalize-v1, formalize-v2)

**Rejected:** Doesn't fit Praxis model.

- Stages are lifecycle positions, not versioned artifacts
- Files evolve continuously (git history is version tracking)
- Confuses stage progression with document versioning

### A4: Single version for entire Praxis ecosystem

**Rejected:** Different components evolve at different rates.

- Spec stabilizes slowly (conceptual validation)
- CLI evolves quickly (feature development)
- Templates have independent lifecycles
- Forcing alignment creates unnecessary coupling

### A5: Template naming without domain prefix (e.g., `python-cli`)

**Rejected:** Loses Praxis scoping.

- Generic names conflict with ecosystem (e.g., `cookiecutter-python-cli`)
- `praxis-template-` prefix makes ownership clear
- Domain inclusion (`-code-`) reinforces Praxis model

---

## Consequences

### Enables

1. **Clear versioning story** for each layer of Praxis
2. **Migration tooling** via schema_version field
3. **Template evolution** via git tags + metadata
4. **Independent pacing** for spec vs CLI vs templates
5. **Backward compatibility** via optional schema_version
6. **Ecosystem coherence** via naming conventions

### Limits

1. **Complexity**: Multiple versioning schemes to understand
2. **Coordination**: Breaking changes require multi-component updates
3. **Migration burden**: Users must track schema versions over time

### Mitigations

1. **Documentation**: Clear versioning guide in user-guide.md
2. **Tooling**: `praxis validate` warns about outdated schemas
3. **Conventions**: Naming patterns reduce cognitive overhead
4. **Pragmatism**: Optional schema_version delays migration pressure

---

## Open Questions Resolved

### Q: Should praxis.yaml include a version field?

**A:** Yes, optional `schema_version` field for future evolution.

### Q: How do templates indicate their version?

**A:** Git tags (primary) + optional `.praxis-template.yaml` metadata.

### Q: Do stage artifacts need versioning?

**A:** No, they evolve with projects. Git history tracks changes.

### Q: How does Praxis spec version relate to CLI version?

**A:** They can diverge. Spec = model stability, CLI = implementation maturity.

### Q: What about CalVer or stage-based versioning?

**A:** SemVer for all components. CalVer doesn't fit event-driven changes.

### Q: Where does version info live?

**A:** Component-specific:
- Praxis spec: `core/spec/VERSION.md` + spec headers
- praxis.yaml: `schema_version` field (optional)
- Extensions: `manifest_version` in praxis-extension.yaml
- Templates: Git tags + `.praxis-template.yaml`
- CLI: `pyproject.toml`
- Projects: Domain-specific (pyproject.toml, package.json, etc.)

---

## Summary

This ADR establishes a comprehensive versioning and naming strategy for Praxis:

1. **Praxis spec** → SemVer in `core/spec/VERSION.md`
2. **praxis.yaml schema** → Optional `schema_version` field
3. **Extension manifests** → Continue ADR-003 approach
4. **Stage templates** → No separate versioning (tied to spec)
5. **Project templates** → SemVer via git tags + metadata
6. **CLI tool** → SemVer in pyproject.toml
7. **User projects** → Domain-specific versioning

**Naming conventions:**
- Templates: `praxis-template-{domain}-{type}`
- Extensions: `praxis-extension-{name}`
- Stage files: `{STAGE}.md`

**Backward compatibility** via optional schema_version and N/N-1 version support.

**Next steps:** Apply naming to template-python-cli (Issue #4), consider schema_version in PraxisConfig, create VERSION.md for spec.

---

## References

- [ADR-001: Policy Engine Selection](001-policy-engine.md)
- [ADR-002: Validation Model](002-validation-model.md)
- [ADR-003: Extension Manifest Schema](003-extension-manifest-schema.md)
- [SOD v0.3](../core/spec/sod.md)
- [Lifecycle v0.3](../core/spec/lifecycle.md)
- Issue #4: template-python-cli
- Research: Cookiecutter, Copier, Yeoman, Cargo Generate
