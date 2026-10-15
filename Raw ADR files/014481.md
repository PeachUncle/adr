# ADR-001: Policy Engine Selection

**Status:** Accepted
**Date:** 2025-12-21 (Draft), 2025-12-28 (Accepted)
**Deciders:** @jayers99

---

## Context

Praxis requires a policy engine to enforce governance rules across the lifecycle. The engine must:

1. Encode domain and lifecycle rules declaratively
2. Enforce privacy invariants at validation time
3. Validate stage transitions and reclassification
4. Guarantee deterministic, order-independent composition
5. Remain human-readable for solo-author workflows

This is a foundational choice that affects all downstream tooling.

---

## Decision Drivers

- **Composability** — Rules should combine without order dependency
- **Type safety** — Catch errors at validation time, not runtime
- **Readability** — Non-experts should understand policies
- **Ecosystem** — Tooling, docs, community support
- **Portability** — Not locked to a specific runtime or platform
- **Learning curve** — Acceptable for a solo author / small team
- **Pragmatism** — Start simple, evolve as needed

---

## Options Considered

### Option 1: CUE

**Description:** Configuration language with types, constraints, and unification.

| Pros | Cons |
| --- | --- |
| Strong composition via unification | Smaller ecosystem than alternatives |
| Types and constraints in one language | Learning curve for unification model |
| Can validate AND generate configs | Less tooling than JSON Schema |
| Good fit for "dimensions compose" model | Additional runtime dependency |

**Fit for Praxis:** Medium — powerful but adds complexity not yet needed

### Option 2: JSON Schema + Custom Validator

**Description:** Standard schema language with hand-written validation logic.

| Pros | Cons |
| --- | --- |
| Widely understood | No native composition |
| Excellent tooling | Verbose for complex constraints |
| Language-agnostic | Validation-only (no generation) |
| | Custom code for cross-field rules |

**Fit for Praxis:** Medium — works but requires more custom code

### Option 3: OPA/Rego

**Description:** Policy-as-code engine from CNCF.

| Pros | Cons |
| --- | --- |
| Powerful policy language | Overkill for solo/small use |
| Strong in authorization domain | Steep learning curve |
| Good for multi-tenant scenarios | Heavier runtime |
| | Less natural for config generation |

**Fit for Praxis:** Low — designed for different scale and use case

### Option 4: Custom DSL

**Description:** Create a Praxis-specific policy language.

| Pros | Cons |
| --- | --- |
| Tailored exactly to needs | Maintenance burden |
| No external dependencies | Reinventing solved problems |
| | No ecosystem |
| | Documentation burden |

**Fit for Praxis:** Low — premature optimization

### Option 5: Python with Pydantic (CHOSEN)

**Description:** Use Python dataclasses/Pydantic for schema, custom validators for rules.

| Pros | Cons |
| --- | --- |
| Familiar to Python developers | Policy mixed with implementation |
| Strong typing with Pydantic v2 | Less declarative than CUE |
| Easy to start and iterate | Harder to audit/review policies separately |
| Excellent test tooling | |
| No additional runtime | |
| Rich validation with clear errors | |

**Fit for Praxis:** High — pragmatic, well-supported, proven effective

---

## Decision

**Python with Pydantic (Option 5)** is selected as the policy engine.

### Rationale

After implementing the validation model through worked projects (Issue #4, uat-praxis-code), Pydantic proved to be the right choice:

1. **Sufficient for current needs** — Pydantic handles schema validation, custom validators, and clear error messages effectively
2. **No additional learning curve** — Python developers can contribute immediately
3. **Fast iteration** — Easy to add new rules and modify existing ones
4. **Strong typing** — Pydantic v2 provides excellent type inference and validation
5. **Ecosystem integration** — Works seamlessly with Typer CLI and Python tooling

### Why not CUE?

CUE remains interesting for future consideration but was deferred because:

- Adds a runtime dependency and learning curve
- Current validation needs are well-served by Pydantic
- The "unification model" benefits aren't realized until we have more complex policy composition
- Pragmatism favors starting simple

CUE may be reconsidered if:
- Multi-domain projects require complex policy composition
- Policy definition needs to be externalized for non-developers
- Cross-language policy sharing becomes important

---

## Implementation Details

The current implementation uses:

- **Pydantic BaseModel** for `PraxisConfig` schema
- **Pydantic validators** for field-level validation
- **Custom service layer** for cross-field rules (artifact checks, regression detection)
- **Infrastructure layer** for git integration and file system checks

Key files:
- `src/praxis/domain/models.py` — Pydantic models
- `src/praxis/application/validate_service.py` — Validation orchestration
- `src/praxis/infrastructure/` — Git, filesystem, YAML adapters

---

## Consequences

### Enables

- Fast development with familiar tooling
- Easy testing with pytest
- Clear error messages from Pydantic
- No external runtime dependencies
- Simple deployment (pure Python)

### Limits

- Policy is code (not a separate declarative layer)
- Harder for non-developers to modify rules
- No built-in policy composition primitives

### Deferred

- CUE exploration for complex multi-domain scenarios
- Externalized policy definition
- Policy-as-data format

---

## Related

- ADR-002 (Validation Model) — Defines what the policy engine validates
- Issue #4 (template-python-cli) — First worked project validating this choice
- Issue #7 — ADR finalization
