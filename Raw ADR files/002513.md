# ADR-001: Customization Versioning Strategy

**Status:** Accepted  
**Date:** 2025-11-27  
**Deciders:** Framework Architecture & Tooling Team  
**Tags:** `[SPEC-CLI]`, `[SPEC-ARTIFACTS]`, `[PRD §5.1]`, `[TECH §11]`

## Context

The Loaded Vibes framework distributes shipped assets via `dist/**` that are mirrored into `.loaded-vibes/` during installation. Users may customize these assets (prompts, instructions, toolsets, configurations) to suit their project needs. When running `loaded-vibes upgrade`, the CLI must reconcile upstream framework changes with local user customizations without data loss.

### Problem Statement

WHEN a user runs `loaded-vibes upgrade`, THE SYSTEM SHALL preserve user customizations while applying upstream changes, detect conflicts, and provide actionable resolution paths `[PRD §5.1]`.

### Requirements Driving This Decision

- `[PRD §5.1]` Distribution & Installation: Detect conflicts in `.github`, `.vscode`, or `dist/**` and offer Mirror, Merge, or Sandbox strategies.
- `[TECH §5.1]` CLI Distribution Model: Preflight, download, extract, init workflow.
- Open Question (resolved by this ADR): Design versioning strategy for user customizations (semantic versions + diff hints).
- `[SPEC-CLI §3]` Distribution & Bootstrap Coupling: Bootstrapper status feeds CLI for readiness/drift detection.
- `[SPEC-ARTIFACTS §4]` Validation & Tagging: Artifact presence, schema compliance, and manifest references.

## Decision

We adopt a **three-tier versioning strategy** that tracks framework versions, asset checksums, and user modification timestamps to enable intelligent upgrade decisions.

### 1. Semantic Versioning Scheme

#### 1.1 Framework Version Tracking

The `.loaded-vibes/manifest.json` file stores:

```jsonc
{
  "frameworkVersion": "1.2.3",           // Semantic version of installed framework
  "installedAt": "2025-11-27T03:00:00Z", // ISO 8601 timestamp
  "upgradeHistory": [
    {
      "from": "1.2.2",
      "to": "1.2.3",
      "at": "2025-11-27T03:00:00Z",
      "strategy": "merge"
    }
  ]
}
```

#### 1.2 Asset Version Tracking

Each shipped asset includes metadata in `.loaded-vibes/assets.json`:

```jsonc
{
  "assets": {
    ".github/prompts/initialization.prompt.md": {
      "frameworkChecksum": "sha256:abc123...",  // Checksum of shipped version
      "localChecksum": "sha256:def456...",      // Current file checksum
      "frameworkVersion": "1.2.3",              // Version when last synced
      "lastModified": "2025-11-27T03:00:00Z",   // Local modification time
      "status": "modified"                       // pristine | modified | conflict
    }
  }
}
```

#### 1.3 Version Semantics

| Version Bump | Scope | Upgrade Impact |
|--------------|-------|----------------|
| **Major** (X.0.0) | Breaking changes to manifest schema, toolset APIs, or DevCycle contracts | Requires manual review; auto-upgrade blocked |
| **Minor** (1.X.0) | New DevCycles, prompts, toolsets, or non-breaking enhancements | Auto-merge safe for unmodified assets |
| **Patch** (1.2.X) | Bug fixes, documentation updates, security patches | Silent update for pristine assets |

### 2. Diff Hint Generation

#### 2.1 Pre-Upgrade Analysis

Before applying upgrades, `loaded-vibes upgrade --analyze` generates a diff report:

```
📊 Upgrade Analysis: v1.2.2 → v1.2.3

📁 Asset Changes:
  ✅ 12 assets unchanged (will auto-update)
  ⚠️  3 assets modified locally:
     - .github/prompts/features.prompt.md
     - .github/instructions/security.instructions.md
     - .vscode/settings.json
  ❌ 1 conflict detected:
     - .github/toolsets/data.toolset.jsonc

📝 Diff Hints:
  features.prompt.md:
    + Added: New context variable {{env.copilot.workspace}}
    ~ Modified: Updated tool references (lines 45-52)
    Your changes: Custom project-specific focus section (lines 12-18)

  security.instructions.md:
    + Added: HSTS preload requirement
    Your changes: Extended CSP directives (lines 89-95)
```

#### 2.2 Diff Hint Format

Diff hints are stored in `.loaded-vibes/upgrade-hints/v{version}.json`:

```jsonc
{
  "version": "1.2.3",
  "generatedAt": "2025-11-27T03:00:00Z",
  "assets": {
    ".github/prompts/features.prompt.md": {
      "action": "review",
      "reason": "Local modifications conflict with upstream changes",
      "upstreamChanges": [
        { "type": "added", "description": "New context variable", "lines": [45, 52] }
      ],
      "localChanges": [
        { "type": "modified", "description": "Custom focus section", "lines": [12, 18] }
      ],
      "suggestedStrategy": "merge",
      "diffPreview": "--- upstream\n+++ local\n@@ -12,6 +12,12 @@..."
    }
  }
}
```

### 3. Conflict Handling Strategies

Based on `[PRD §5.1]` Mirror/Merge/Sandbox requirements:

#### 3.1 Mirror Strategy

**Use Case:** User wants exact parity with upstream framework.

**Behavior:**
- Overwrites all `.loaded-vibes/` assets with shipped versions
- Backs up local modifications to `.loaded-vibes/backup/v{timestamp}/`
- Logs decision to `.loaded-vibes/logs/upgrade-YYYYMMDD.ndjson`

**CLI Interaction:**
```
$ loaded-vibes upgrade --strategy mirror

⚠️  Mirror Strategy Selected
This will replace all local customizations with upstream versions.

Backing up 4 modified files to .loaded-vibes/backup/v20251127/
  ✓ features.prompt.md
  ✓ security.instructions.md
  ✓ settings.json
  ✓ data.toolset.jsonc

Applying upstream assets...
  ✓ 16 assets updated

📝 Backup location: .loaded-vibes/backup/v20251127/
💡 To restore: loaded-vibes restore --from v20251127
```

#### 3.2 Merge Strategy

**Use Case:** User wants to preserve customizations while incorporating upstream changes.

**Behavior:**
- Auto-merges non-conflicting changes
- Presents interactive conflict resolution for overlapping edits
- Generates `.loaded-vibes/merge-markers/` for manual review
- Updates `assets.json` with merged checksums

**CLI Interaction:**
```
$ loaded-vibes upgrade --strategy merge

🔀 Merge Strategy Selected

Auto-merging 12 pristine assets... ✓
Auto-merging 2 compatible modifications... ✓

⚠️  1 conflict requires manual resolution:
   .github/toolsets/data.toolset.jsonc

Opening conflict resolution...

┌─────────────────────────────────────────────────────────┐
│ data.toolset.jsonc: Lines 23-31                         │
├─────────────────────────────────────────────────────────┤
│ <<<<<<< UPSTREAM (v1.2.3)                               │
│ "tools": ["prisma", "postgres", "redis"]                │
│ =======                                                 │
│ "tools": ["prisma", "postgres", "mongodb"]              │
│ >>>>>>> LOCAL                                           │
├─────────────────────────────────────────────────────────┤
│ [U]se upstream | [K]eep local | [E]dit | [S]kip         │
└─────────────────────────────────────────────────────────┘
```

**Conflict Markers:**

When conflicts cannot be auto-resolved, the CLI writes standard markers:

```markdown
<<<<<<< UPSTREAM (v1.2.3)
[upstream content]
=======
[local content]
>>>>>>> LOCAL (modified 2025-11-20)
```

#### 3.3 Sandbox Strategy

**Use Case:** User wants to evaluate upstream changes before committing.

**Behavior:**
- Extracts upstream version to `.loaded-vibes/sandbox/v{version}/`
- Leaves current `.loaded-vibes/` untouched
- Generates comparison report
- User can selectively apply changes via `loaded-vibes sandbox apply <asset>`

**CLI Interaction:**
```
$ loaded-vibes upgrade --strategy sandbox

📦 Sandbox Strategy Selected

Extracting v1.2.3 to .loaded-vibes/sandbox/v1.2.3/... ✓

Comparison Report:
  .github/prompts/features.prompt.md
    ├── Current:  .loaded-vibes/.github/prompts/features.prompt.md
    └── Upstream: .loaded-vibes/sandbox/v1.2.3/.github/prompts/features.prompt.md

Commands:
  loaded-vibes sandbox diff features.prompt.md
  loaded-vibes sandbox apply features.prompt.md
  loaded-vibes sandbox apply --all
  loaded-vibes sandbox discard
```

### 4. Upgrade Workflow Integration

#### 4.1 Pre-Upgrade Checklist

1. **Checksum Validation:** Verify current assets against `assets.json` checksums `[SPEC-SECURITY §1]`
2. **Backup Creation:** Auto-backup modified assets before any changes
3. **Diff Analysis:** Generate upgrade hints for user review
4. **Strategy Selection:** Prompt user for Mirror/Merge/Sandbox choice
5. **Bad Vibes Firewall:** Warn if destructive operations detected `[PRD §5.5]`

#### 4.2 Post-Upgrade Actions

1. **Asset Registry Update:** Refresh `assets.json` with new checksums
2. **Manifest Update:** Record upgrade in `manifest.json` history
3. **Log Generation:** Write NDJSON log to `.loaded-vibes/logs/upgrade-YYYYMMDD.ndjson`
4. **Doctor Check:** Run `loaded-vibes doctor` to validate post-upgrade state
5. **TODO/CHANGELOG:** Append upgrade summary with requirement IDs `[TECH §7]`

#### 4.3 NDJSON Log Format

```jsonc
{"timestamp":"2025-11-27T03:00:00Z","event":"upgrade_start","from":"1.2.2","to":"1.2.3","strategy":"merge","requirementId":"TECH§11"}
{"timestamp":"2025-11-27T03:00:01Z","event":"backup_created","path":".loaded-vibes/backup/v20251127","files":4}
{"timestamp":"2025-11-27T03:00:02Z","event":"asset_updated","asset":".github/prompts/initialization.prompt.md","action":"auto-merge"}
{"timestamp":"2025-11-27T03:00:03Z","event":"conflict_resolved","asset":".github/toolsets/data.toolset.jsonc","resolution":"keep-local"}
{"timestamp":"2025-11-27T03:00:05Z","event":"upgrade_complete","status":"success","updatedAssets":16,"conflicts":1}
```

### 5. Rollback & Recovery

#### 5.1 Automatic Backup Retention

- Keep last 5 upgrade backups in `.loaded-vibes/backup/`
- Prune older backups during `loaded-vibes doctor --cleanup`
- Backups include full asset tree plus `assets.json` snapshot

#### 5.2 Rollback Commands

```bash
# List available restore points
loaded-vibes restore --list

# Restore specific version
loaded-vibes restore --from v20251127

# Restore single asset
loaded-vibes restore --from v20251127 --asset .github/prompts/features.prompt.md
```

## Consequences

### Positive

- Users retain full control over customizations during upgrades
- Checksum-based tracking provides deterministic conflict detection
- Three strategies accommodate different user preferences and risk tolerances
- NDJSON logging enables auditability per `[SPEC-OBS §3]` requirements
- Backup/restore capabilities reduce upgrade anxiety

### Negative

- Increased storage requirements for backup retention
- More complex upgrade flow compared to simple overwrite
- Users must understand three strategies to make informed choices

### Neutral

- Aligns with existing Mirror/Merge/Sandbox terminology from `[PRD §5.1]`
- Extends existing NDJSON logging patterns from `[TECH §4.5]`

## Compliance

| Requirement | Implementation |
|-------------|----------------|
| `[PRD §5.1]` Conflict detection | Asset checksum comparison in `assets.json` |
| `[PRD §5.1]` Mirror/Merge/Sandbox | Three upgrade strategies with CLI flags |
| `[PRD §5.1]` Decision logging | NDJSON logs in `.loaded-vibes/logs/` |
| `[PRD §5.5]` Bad Vibes Firewall | Pre-upgrade warnings for destructive changes |
| `[TECH §5.1]` Preflight checks | Doctor validation before/after upgrades |
| `[TECH §11]` Semantic versions | Framework version in `manifest.json` |
| `[TECH §11]` Diff hints | Generated hints in `upgrade-hints/` |
| `[SPEC-CLI §3]` Bootstrap coupling | Manifest feeds CLI readiness status |
| `[SPEC-ARTIFACTS §4]` Validation | Schema compliance checks during upgrade |
| `[SPEC-SECURITY §1]` Checksum verification | SHA256 validation for all assets |

## Related Documents

- `docs/PRD.md` – Product requirements for distribution and installation
- `docs/TECH_REQUIREMENTS.md` – Technical requirements §5, §11
- `spec/cli.spec.md` – CLI behavior specification
- `spec/artifact.spec.md` – Artifact taxonomy and validation
- `spec/security.spec.md` – Security constraints
