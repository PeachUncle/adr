# ADR-002: Refusal Taxonomy as Configuration (Policy as Data)

**Status:** Accepted  
**Date:** 2025-01-05  
**Deciders:** Steve (PM)  
**Context:** Compliance Retrieval Assistant — Module 4 of Regulated AI Workflow Toolkit

---

## Context

The Compliance Retrieval Assistant must refuse to answer in certain situations — when it cannot ground an answer, when sources conflict, when the user lacks access, etc. These refusals are not failures; they are **features** that protect users and the organization.

We needed to decide how to implement refusal logic:

1. **Hardcoded in application code** — Refusal rules embedded in the Refusal Gate component
2. **Configuration-driven** — Refusal taxonomy defined in YAML, loaded at runtime

This decision affects:
- How quickly refusal behavior can be modified
- Who can change refusal policies (developers vs. compliance)
- Audit trail for policy changes
- Testability and governance review

---

## Decision

**Refusal logic is defined as configuration (policy-as-data), not hardcoded in application logic.**

The refusal taxonomy lives in `config/refusal-taxonomy.yaml` and defines:
- Refusal codes (NO_ELIGIBLE_DOCS, INSUFFICIENT_GROUNDING, POLICY_BLOCKED, AMBIGUOUS_QUERY, CONFLICTING_SOURCES)
- Severity levels (info, warning, escalate)
- User-facing guidance for each code
- Escalation triggers
- Audit requirements

The application code reads this configuration and applies it — it does not contain refusal policy decisions.

---

## Rationale

### 1. Refusal policy is a governance decision, not a technical one

Deciding when to refuse is fundamentally a policy question:
- What level of grounding is "good enough"?
- Which conflicts require escalation?
- What guidance should users receive?

These decisions should be made by Compliance, Legal, and Product — not embedded in code where only engineers can change them.

### 2. Policy changes should not require code deployment

In a regulated environment, refusal thresholds may need adjustment based on:
- Regulatory guidance changes
- Audit findings
- Operational experience
- Risk appetite shifts

Configuration changes can be reviewed, approved, and deployed without a full software release cycle.

### 3. Configuration is auditable

Version-controlled YAML files provide:
- Clear change history (who changed what, when)
- Diff-able policy changes for compliance review
- Snapshot capability for point-in-time reconstruction

Code changes are also version-controlled, but policy intent is harder to extract from code than from declarative configuration.

### 4. Enables governance review without code review

Compliance officers and legal counsel can review `refusal-taxonomy.yaml` directly:
- Is the user guidance appropriate?
- Are escalation triggers correct?
- Do severity levels match risk appetite?

They cannot meaningfully review application code for the same information.

### 5. Testability improves

With refusal logic externalized:
- Test cases can directly reference taxonomy codes
- Policy changes can be tested in isolation
- Compliance can validate behavior against documented policy

---

## Consequences

### Positive

- **Separation of concerns** — Policy decisions separated from implementation
- **Faster policy iteration** — Changes without code deployment
- **Governance-friendly** — Non-technical stakeholders can review and approve
- **Audit trail** — Configuration versioning provides clear change history
- **Testable** — Refusal behavior can be validated against documented taxonomy

### Negative

- **Configuration complexity** — Another file to maintain and validate
- **Runtime dependency** — Application requires valid configuration to start
- **Schema enforcement needed** — Invalid configuration could cause failures
- **Two places to look** — Debugging requires checking both code and config

### Mitigations

- Configuration schema validation at startup
- Configuration snapshot included in evidence packages
- Clear documentation linking code components to configuration
- Test suite validates all taxonomy codes are handled

---

## Taxonomy Structure

```yaml
refusal_codes:
  NO_ELIGIBLE_DOCS:
    description: "Query falls outside corpus scope"
    severity: info
    user_guidance: "Your question falls outside the topics covered..."
    next_action: suggest_alternatives
    
  INSUFFICIENT_GROUNDING:
    description: "Retrieved content cannot substantiate an answer"
    severity: warning
    user_guidance: "I found some related information, but not enough..."
    next_action: suggest_refinement
    
  POLICY_BLOCKED:
    description: "Access restriction prevents answering"
    severity: warning
    user_guidance: "You don't have access to materials needed..."
    next_action: contact_admin
    
  AMBIGUOUS_QUERY:
    description: "Query lacks sufficient specificity"
    severity: info
    user_guidance: "I need more detail to find the right information..."
    next_action: prompt_clarification
    
  CONFLICTING_SOURCES:
    description: "Authoritative sources provide contradictory guidance"
    severity: escalate
    user_guidance: "I found conflicting information in authoritative sources..."
    next_action: escalate_to_sme
```

---

## Alternatives Considered

### Alternative A: Hardcode refusal logic in application code

**Rejected.** Embeds policy decisions in technical implementation. Changes require engineering effort and code deployment. Compliance cannot review or approve without technical assistance.

### Alternative B: Database-driven policy with admin UI

**Rejected.** Adds infrastructure complexity (database, UI, access control). For a portfolio demonstration, file-based configuration is simpler and equally demonstrates the principle. Enterprise implementation could migrate to database-driven approach.

### Alternative C: Hybrid — some rules in code, some in config

**Rejected.** Creates ambiguity about where policy lives. "Is this refusal behavior defined in code or config?" becomes a recurring question. Clean separation is simpler to maintain and audit.

---

## Operational Implications

### Policy Change Process

1. Compliance or Product proposes change to taxonomy
2. Change documented in PR against `refusal-taxonomy.yaml`
3. Governance review (Compliance, Legal, Risk as appropriate)
4. Approval and merge
5. Configuration deployed (no code release required)
6. Change logged in audit trail

### Configuration Versioning

Every evidence package includes a snapshot of configuration at query time:
```
evidence-package-{trace_id}/
├── config-snapshot/
│   ├── policy-constraints.yaml
│   ├── refusal-taxonomy.yaml
│   └── role-permissions.yaml
```

This enables reconstruction: "What refusal policy was in effect when this interaction occurred?"

---

## Related Artifacts

- [config/refusal-taxonomy.yaml](../config/refusal-taxonomy.yaml) — The taxonomy definition
- [config/policy-constraints.yaml](../config/policy-constraints.yaml) — Related policy configuration
- [architecture/component-design.md](../architecture/component-design.md) — Refusal Gate component
- [docs/response-contract.md](../docs/response-contract.md) — How refusals appear to users
- [docs/trace-schema.md](../docs/trace-schema.md) — How refusals are logged

---

## References

- "Policy as Code" patterns in infrastructure management
- Configuration-driven systems in regulated industries
- Model Risk Management (SR 11-7) change control requirements