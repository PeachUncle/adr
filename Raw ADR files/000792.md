---
docid: ADR-082
title: ADR 039 Instruction Protection
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿---
docid: ADR-039
title: Agent Instruction Protection Strategy
status: Accepted
date: 2026-01-05
decision-makers:
  - "@SARAH"
  - "@CopilotExpert"
  - "@TechLead"
  - "@Security"
---

# ADR-039: Agent Instruction Protection Strategy

## Status

**Accepted** - 5. Januar 2026

## Context

The B2X project uses a sophisticated multi-agent AI system with:
- **18 specialized agents** defined in `.github/agents/`
- **5 instruction files** in `.github/instructions/`
- **15+ prompt templates** in `.github/prompts/`

These files control AI behavior, permissions, and workflows. Unauthorized modifications could:
1. **Bypass governance** - Agents could gain unauthorized permissions
2. **Inject malicious behavior** - Prompt injection via instruction tampering
3. **Break coordination** - @SARAH's quality-gate could be circumvented
4. **Violate compliance** - Security policies could be weakened

Per [GL-008] Governance Policies, @CopilotExpert has **exclusive authority** over these files, but this was only enforced through documentation, not technical controls.

## Decision

Implement a **multi-layered protection strategy** for agent instruction files:

### Layer 1: Git-Based Protection (CODEOWNERS)

```
.github/agents/**/*.md          @CopilotExpert @SARAH
.github/instructions/**/*.md    @CopilotExpert @TechLead
.github/prompts/**/*.md         @CopilotExpert @SARAH
.github/copilot-instructions.md @CopilotExpert @SARAH @TechLead
.vscode/mcp.json                @CopilotExpert @DevOps
```

**Enforcement**: GitHub requires approval from designated owners before merge.

### Layer 2: CI/CD Validation Pipeline

Automated pipeline `.github/workflows/protect-instructions.yml` validates:

| Check | Purpose |
|-------|---------|
| **Structure Validation** | Ensures files have required frontmatter and sections |
| **Security Check** | Scans for sensitive patterns (passwords, tokens, etc.) |
| **Checksum Audit** | Generates SHA256 checksums for audit trail |
| **Governance Compliance** | Verifies Document Registry and CODEOWNERS alignment |

### Layer 3: Audit Trail

All changes generate:
- GitHub PR summary with modified files and checksums
- Audit log entries with timestamp, author, and file hashes
- Warnings for Document Registry updates when new files are added

### Layer 4: Process Controls

| Action | Required Approvals |
|--------|-------------------|
| Edit existing agent | @CopilotExpert |
| Create new agent | @CopilotExpert + @SARAH |
| Modify prompts | @CopilotExpert + @SARAH |
| Policy-level changes | @CopilotExpert + @SARAH + @TechLead |

## Consequences

### Positive

1. **Technical enforcement** of [GL-008] governance policies
2. **Audit trail** for compliance and incident investigation
3. **Early detection** of accidental or malicious changes
4. **Consistent validation** through automated pipeline
5. **Clear ownership** via CODEOWNERS

### Negative

1. **Friction for legitimate changes** - Requires approvals even for typo fixes
2. **CI pipeline overhead** - Additional pipeline runs for instruction changes
3. **False positives** - Security patterns might flag legitimate content

### Mitigations

- Document expedited review process for minor changes
- Tune security patterns based on false positive feedback
- Cache checksum baselines to speed up audits

## Alternatives Considered

### 1. Branch Protection Only
**Rejected**: Doesn't provide content validation or audit trail.

### 2. Pre-Commit Hooks
**Partially adopted**: Good for local development, but can be bypassed. CI pipeline is authoritative.

### 3. Immutable Core + Override Pattern
**Deferred**: Adds complexity. May revisit for enterprise multi-tenant scenarios.

### 4. Signed Commits Requirement
**Deferred**: GPG signing adds friction. Consider for v1.0 hardening.

## Implementation

### Files Created/Modified

| File | Action | Purpose |
|------|--------|---------|
| `.github/CODEOWNERS` | Modified | Added protected paths with @CopilotExpert |
| `.github/workflows/protect-instructions.yml` | Created | CI validation pipeline |
| `.ai/decisions/ADR-039-instruction-protection.md` | Created | This document |

### Verification

```bash
# Verify CODEOWNERS coverage
grep -E "\.github/(agents|instructions|prompts)" .github/CODEOWNERS

# Test pipeline locally (if act is installed)
act pull_request -W .github/workflows/protect-instructions.yml
```

## Related Documents

- [GL-008] Governance Policies - Authority definitions
- [GL-010] Agent & Artifact Organization - File structure
- [ADR-020] PR Quality Gate - Review process
- [AGT-018] CopilotExpert - Owner of protected files

## Review Schedule

- **Next Review**: 2026-04-01
- **Trigger**: Any security incident involving agent files
- **Owner**: @CopilotExpert + @Security

---

**Decision Date**: 5. Januar 2026  
**Last Updated**: 5. Januar 2026
