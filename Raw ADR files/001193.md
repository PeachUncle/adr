## ADR CF-202: Legacy Config in cf_cli.py — Deprecation vs Retention

Status: Proposed
Date: 2025-12-04
Decision Owner: CF-Work Architecture Team
Related Issues: CF-190, CF-201, CF-202, CF-203, CF-204

---

### Context
cf_cli.py already loads CFSettings via get_cf_settings(), applies CLI overrides,
and bridges legacy env via apply_to_environment(). About ~180 lines of legacy
configuration helpers remain to preserve backward compatibility
(CF_CLI_LAZY_MODE, fallback paths). We must decide whether to remove,
deprecate behind a flag, or retain.

### Options
- Option A — Staged deprecation behind feature flag
  - Add CF_FORCE_FALLBACK=false default; when true, legacy path is used.
  - Emit warnings when legacy path activates; log artifact_emit events.
  - Timeline: 2 sprints; remove after usage falls <5%.
- Option B — Retain with hardening
  - Keep legacy code; add stricter validation and unified logging.
  - Document risks and maintenance cost; freeze surface.

### Decision Matrix
- Reliability: A=High (controlled), B=Medium
- Maintainability: A=High, B=Low
- Backward compatibility: A=Medium (opt-in), B=High
- Developer experience: A=High, B=Medium
- Risk: A=Managed with guardrails, B=Ongoing

### Decision
Proceed with Option A: staged deprecation using CF_FORCE_FALLBACK feature flag. Retain code for one cycle with clear warnings, telemetry, and rollback path.

### Guardrails
- Feature flag: CF_FORCE_FALLBACK (bool), default false
- Warning: "Legacy config path activated (CF_FORCE_FALLBACK=true)"
- Telemetry: unified_logger event decision=legacy_fallback
- Tests: ensure both paths covered; ≥90% coverage maintained
- Docs: Update docs/11-Configuration-Management.md and plan file

### Rollback Plan
If regressions detected or customer mandate requires, set CF_FORCE_FALLBACK=true in environment or per-CLI option to restore legacy behavior. Keep code until Sprint+1 after deprecation announcement.

### Validation
- Smoke and full test suites executed with artifacts
- Coverage retained (cf_settings.py 94.12%)
- Quality gate passes (ruff/mypy)

### Implementation Notes
- Leave legacy helpers in cf_cli.py for now
- Add warnings + telemetry lines near apply_to_environment/fallback block
- Provide CLI switch --force-fallback mapping to CF_FORCE_FALLBACK
