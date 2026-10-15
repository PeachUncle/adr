# ADR-0001: Execution Summary Format

**Status:** Accepted  
**Date:** 2025-11-27  
**Deciders:** Framework Architecture & Tooling Team  
**Issue:** #35  
**References:** [SPEC-OBS §3], [TECH §4.5], [TECH §5.3], [TECH §11], [PRD §5.4]

## Context

Before enabling CI gating, the framework must decide on a standard format for persisted execution summaries. The question [TECH §11] poses is: JSON vs Markdown. This decision affects:

- TODO/CHANGELOG update workflows  
- CLI dashboard rendering  
- CI pipeline artifact consumption  
- Human-readable review during PR workflows  
- Traceability linking (requirement IDs, NDJSON log correlation)

### Current State

| Artifact Type | Current Format | Purpose |
| --- | --- | --- |
| Raw event logs | NDJSON (`.loaded-vibes/logs/*.ndjson`) | Machine-readable telemetry with `devCycleId`, `phase`, `requirementId`, `severity`, `checkpointId` fields [SPEC-OBS §3] |
| Engine state | JSON (`dist/genaiscript/state/state.json`) | Orchestrator timeline reconstruction [TECH §4.5] |
| TODO/CHANGELOG | Markdown | Human-readable summaries [PRD §5.3] |
| CLI export | Markdown export from NDJSON | Developer review snapshots [TECH §5.3] |

## Decision Drivers

1. **CI Gating Compatibility**: CI tools must parse summaries to gate deployments.
2. **Diff readability**: PR reviews need human-friendly diffs.
3. **Interoperability**: Dashboards, tooling, and external integrations need machine-readable access.
4. **Storage Efficiency**: Avoid redundant data in multiple formats.
5. **Developer Experience**: Summaries should be readable without specialized tooling.

## Considered Options

### Option A: JSON-Only

- ✅ Machine-parseable by CI, dashboards, integrations
- ✅ Consistent with NDJSON logs and state.json
- ✅ Easy programmatic aggregation
- ❌ Poor diff readability in PRs
- ❌ Requires tooling for human review
- ❌ Harder to include in TODO/CHANGELOG entries

### Option B: Markdown-Only

- ✅ Human-readable, excellent diff display
- ✅ Consistent with TODO/CHANGELOG expectations
- ✅ No additional tooling for reviews
- ❌ Parsing requires regex or frontmatter extraction
- ❌ Difficult to correlate programmatically with NDJSON logs
- ❌ Limits CI automation without structured data

### Option C: Dual-Mode (JSON + Markdown)

- ✅ Machine-readable JSON for CI, dashboards, integrations
- ✅ Human-readable Markdown for diffs and PR reviews
- ✅ Each format serves its intended audience
- ✅ Markdown embeds structured frontmatter for light parsing
- ✅ Aligns with existing pattern: NDJSON logs → Markdown export [TECH §5.3]
- ❌ Slightly higher storage (mitigated by separate concerns)
- ❌ Requires synchronization between formats

## Decision

**Adopt Dual-Mode Output (Option C)** with the following implementation:

### Primary Formats

| Output | Format | Location | Purpose |
| --- | --- | --- | --- |
| Execution Summary (structured) | JSON | `.loaded-vibes/summaries/<devCycleId>-<timestamp>.json` | CI gating, dashboard rendering, programmatic queries |
| Execution Summary (human) | Markdown | `.loaded-vibes/summaries/<devCycleId>-<timestamp>.md` | PR attachments, TODO/CHANGELOG references, manual review |

### JSON Schema (Minimal)

```json
{
  "devCycleId": "string",
  "phase": "string",
  "startTime": "ISO8601",
  "endTime": "ISO8601",
  "status": "success | failure | skipped",
  "requirementIds": ["string"],
  "checkpoints": [
    { "id": "string", "approved": "boolean", "approver": "string" }
  ],
  "validationResult": {
    "passed": "boolean",
    "details": "string"
  },
  "artifacts": ["string"],
  "logFile": "relative path to .ndjson"
}
```

### Markdown Template

```markdown
# Execution Summary: {devCycleId}

**Phase:** {phase}  
**Status:** {status}  
**Duration:** {startTime} → {endTime}

## Requirements Addressed

- {requirementId}: {description}

## Checkpoints

| Checkpoint | Approved | Approver |
| --- | --- | --- |
| {id} | {approved} | {approver} |

## Validation

{validationResult.details}

## Artifacts

- {artifact path}

## Logs

See [{logFile}](./{logFile})
```

### Synchronization Rule

- The orchestrator generates both files atomically at phase completion.
- The Markdown file includes YAML frontmatter with the JSON fields for light machine parsing when needed.
- CI pipelines consume `.json`; PR templates reference `.md`.

## Consequences

### Positive

- CI gating can use `jq` or native JSON parsing without fragile regex.
- Developers see readable summaries in PR diffs.
- TODO/CHANGELOG can reference or inline the Markdown version.
- Dashboards and tooling parse JSON for real-time status.
- Pattern aligns with existing NDJSON → Markdown export flow.

### Negative

- Two files per execution increases storage marginally.
- Implementations must emit both formats; shared utility required.

### Migration Guidance

1. Create shared utility in `dist/genaiscript/shared/summary-writer.js` that emits both JSON and Markdown.
2. Update orchestrator to call the utility at each phase completion.
3. Add `.loaded-vibes/summaries/` to CLI log viewer scope.
4. Update CI workflows to consume `*.json` summaries for gating decisions.
5. Extend `loaded-vibes logs` command to display/export both formats.

## Compliance

- [x] JSON trade-offs documented
- [x] Markdown trade-offs documented
- [x] Decision Record committed
- [x] Aligns with SPEC-OBS §3 (NDJSON logs → Markdown summaries)
- [x] Supports TECH §11 CI gating requirement
